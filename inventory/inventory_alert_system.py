import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="库存预警与订单建议系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用标题
st.title("📊 库存预警与订单建议系统")
st.markdown("---")

# 数据加载和缓存
@st.cache_data
def load_data():
    """加载和预处理数据"""
    try:
        df = pd.read_csv('/Users/willmbp/Documents/2024/My_projects/inventory/demo_inventory_data.csv')
        
        # 数据类型转换
        df['Date'] = pd.to_datetime(df['Date'])
        df['Inv.Value(RMB)'] = pd.to_numeric(df['Inv.Value(RMB)'], errors='coerce')
        df['IDS GIV'] = pd.to_numeric(df['IDS GIV'], errors='coerce')
        
        # 填充缺失值
        df['IDS GIV'] = df['IDS GIV'].fillna(0)
        
        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None

# 定义渠道分类
def define_channel_groups():
    """定义渠道分组"""
    retail_channels = ['HSM', 'MM', 'ICP', 'Grocery & Others', 'CVS', 'DCP']
    offline_channels = ['HSM', 'MM', 'Grocery & Others', 'CVS', 'DCP', 'ICP', 'WS']
    all_channels = ['HSM', 'MM', 'ICP', 'Grocery & Others', 'CVS', 'DCP', 'WS', 'B Store', 'CB', 'DKS', 'DMW', 'DP.com', 'EB']
    
    return {
        'retail': retail_channels,
        'offline': offline_channels,
        'all': all_channels
    }

# 计算日均销量和安全库存
def calculate_safety_stock(df, channel_groups, otd_days=7):
    """计算安全库存线"""
    # 按日期聚合数据
    daily_data = df.groupby('Date').agg({
        'Inv.Value(RMB)': 'first',  # 库存值（假设同一天所有记录的库存值相同）
        'IDS GIV': 'sum'  # 当日总销量
    }).reset_index()
    
    # 计算各渠道的日均销量
    retail_daily = df[df['Store Group Channel'].isin(channel_groups['retail'])].groupby('Date')['IDS GIV'].sum()
    offline_daily = df[df['Store Group Channel'].isin(channel_groups['offline'])].groupby('Date')['IDS GIV'].sum()
    all_daily = df[df['Store Group Channel'].isin(channel_groups['all'])].groupby('Date')['IDS GIV'].sum()
    
    # 过滤掉库存为0的异常数据进行计算移动平均
    valid_inventory_dates = daily_data[daily_data['Inv.Value(RMB)'] > 0]['Date']
    
    # 只使用有效库存日期的销量数据计算移动平均
    retail_valid = retail_daily[retail_daily.index.isin(valid_inventory_dates)]
    offline_valid = offline_daily[offline_daily.index.isin(valid_inventory_dates)]
    all_valid = all_daily[all_daily.index.isin(valid_inventory_dates)]
    
    # 计算移动平均（7天），但基于有效数据
    if len(retail_valid) > 0:
        retail_ma_value = retail_valid.rolling(window=min(7, len(retail_valid)), min_periods=1).mean().iloc[-1]
    else:
        retail_ma_value = retail_daily.mean() if len(retail_daily) > 0 else 0
        
    if len(offline_valid) > 0:
        offline_ma_value = offline_valid.rolling(window=min(7, len(offline_valid)), min_periods=1).mean().iloc[-1]
    else:
        offline_ma_value = offline_daily.mean() if len(offline_daily) > 0 else 0
        
    if len(all_valid) > 0:
        all_ma_value = all_valid.rolling(window=min(7, len(all_valid)), min_periods=1).mean().iloc[-1]
    else:
        all_ma_value = all_daily.mean() if len(all_daily) > 0 else 0
    
    # 计算完整的移动平均序列（用于图表显示）
    retail_ma = retail_daily.rolling(window=7, min_periods=1).mean().fillna(retail_ma_value)
    offline_ma = offline_daily.rolling(window=7, min_periods=1).mean().fillna(offline_ma_value)
    all_ma = all_daily.rolling(window=7, min_periods=1).mean().fillna(all_ma_value)
    
    # 计算安全库存线（考虑OTD时间）
    safety_stock_retail = retail_ma * otd_days
    safety_stock_offline = offline_ma * otd_days
    safety_stock_all = all_ma * otd_days
    
    # 合并数据
    result = daily_data.copy()
    result['Retail_Daily_Sales'] = retail_daily.reindex(result['Date']).fillna(0)
    result['Offline_Daily_Sales'] = offline_daily.reindex(result['Date']).fillna(0)
    result['All_Daily_Sales'] = all_daily.reindex(result['Date']).fillna(0)
    result['Safety_Stock_Retail'] = safety_stock_retail.reindex(result['Date']).fillna(0)
    result['Safety_Stock_Offline'] = safety_stock_offline.reindex(result['Date']).fillna(0)
    result['Safety_Stock_All'] = safety_stock_all.reindex(result['Date']).fillna(0)
    
    # 确保所有数值都是有效的（不是NaN）
    numeric_columns = ['Retail_Daily_Sales', 'Offline_Daily_Sales', 'All_Daily_Sales', 
                      'Safety_Stock_Retail', 'Safety_Stock_Offline', 'Safety_Stock_All']
    for col in numeric_columns:
        result[col] = result[col].fillna(0)
    
    return result

# 生成预警信号
def generate_alerts(data, current_inventory_value):
    """生成预警信号"""
    alerts = []
    latest_data = data.iloc[-1]
    
    # 检查是否低于安全库存线
    if current_inventory_value < latest_data['Safety_Stock_Retail']:
        alerts.append({
            'level': 'critical',
            'type': '零售渠道安全库存预警',
            'message': f'当前库存 ¥{current_inventory_value:,.0f} 低于零售渠道安全库存线 ¥{latest_data["Safety_Stock_Retail"]:,.0f}',
            'shortage': latest_data['Safety_Stock_Retail'] - current_inventory_value
        })
    
    if current_inventory_value < latest_data['Safety_Stock_Offline']:
        alerts.append({
            'level': 'warning',
            'type': '线下渠道安全库存预警',
            'message': f'当前库存 ¥{current_inventory_value:,.0f} 低于线下渠道安全库存线 ¥{latest_data["Safety_Stock_Offline"]:,.0f}',
            'shortage': latest_data['Safety_Stock_Offline'] - current_inventory_value
        })
    
    if current_inventory_value < latest_data['Safety_Stock_All']:
        alerts.append({
            'level': 'info',
            'type': '全渠道安全库存预警',
            'message': f'当前库存 ¥{current_inventory_value:,.0f} 低于全渠道安全库存线 ¥{latest_data["Safety_Stock_All"]:,.0f}',
            'shortage': latest_data['Safety_Stock_All'] - current_inventory_value
        })
    
    return alerts

# 主应用
def main():
    # 加载数据
    df = load_data()
    if df is None:
        st.stop()
    
    # 获取渠道分组
    channel_groups = define_channel_groups()
    
    # 侧边栏参数设置
    st.sidebar.header("📋 参数设置")
    
    # 清除缓存按钮
    if st.sidebar.button("🔄 刷新数据"):
        st.cache_data.clear()
        st.rerun()
    
    # OTD设置
    otd_days = st.sidebar.slider(
        "OTD (Order to Delivery) 天数", 
        min_value=1, 
        max_value=30, 
        value=7,
        help="补货周期时间（天）"
    )
    
    # 时间范围选择
    date_range = st.sidebar.date_input(
        "选择分析时间范围",
        value=[df['Date'].min().date(), df['Date'].max().date()],
        min_value=df['Date'].min().date(),
        max_value=df['Date'].max().date()
    )
    
    # 过滤数据
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = df[(df['Date'] >= pd.to_datetime(start_date)) & 
                        (df['Date'] <= pd.to_datetime(end_date))]
    else:
        filtered_df = df
    
    # 计算安全库存数据
    safety_data = calculate_safety_stock(filtered_df, channel_groups, otd_days)
    
    # 获取当前库存值
    current_inventory = safety_data['Inv.Value(RMB)'].iloc[-1]
    
    # 显示关键指标
    st.header("📊 关键指标概览")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "当前库存价值", 
            f"¥{current_inventory:,.0f}",
            delta=f"{current_inventory - safety_data['Inv.Value(RMB)'].iloc[-2]:,.0f}" if len(safety_data) > 1 else None
        )
    
    with col2:
        recent_retail_sales = safety_data['Retail_Daily_Sales'].tail(7).mean()
        if pd.isna(recent_retail_sales):
            recent_retail_sales = 0
        st.metric("零售渠道日均销量（7天）", f"¥{recent_retail_sales:,.0f}")
    
    with col3:
        recent_offline_sales = safety_data['Offline_Daily_Sales'].tail(7).mean()
        if pd.isna(recent_offline_sales):
            recent_offline_sales = 0
        st.metric("线下渠道日均销量（7天）", f"¥{recent_offline_sales:,.0f}")
    
    with col4:
        recent_all_sales = safety_data['All_Daily_Sales'].tail(7).mean()
        if pd.isna(recent_all_sales):
            recent_all_sales = 0
        st.metric("全渠道日均销量（7天）", f"¥{recent_all_sales:,.0f}")
    
    # 生成和显示预警
    alerts = generate_alerts(safety_data, current_inventory)
    
    if alerts:
        st.header("🚨 库存预警")
        for alert in alerts:
            if alert['level'] == 'critical':
                st.error(f"🔴 **{alert['type']}**: {alert['message']}")
                st.error(f"   💰 建议补货金额: ¥{alert['shortage']:,.0f}")
            elif alert['level'] == 'warning':
                st.warning(f"🟡 **{alert['type']}**: {alert['message']}")
                st.warning(f"   💰 建议补货金额: ¥{alert['shortage']:,.0f}")
            else:
                st.info(f"🔵 **{alert['type']}**: {alert['message']}")
                st.info(f"   💰 建议补货金额: ¥{alert['shortage']:,.0f}")
    else:
        st.success("✅ 当前库存充足，无需预警")
    
    # 图表1：库存与销量时间趋势
    st.header("📈 库存与销量时间趋势")
    
    fig1 = make_subplots(
        rows=2, cols=1,
        subplot_titles=('库存价值变化', '各渠道日销量变化'),
        vertical_spacing=0.1,
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # 库存变化
    fig1.add_trace(
        go.Scatter(
            x=safety_data['Date'],
            y=safety_data['Inv.Value(RMB)'],
            mode='lines',
            name='实际库存',
            line=dict(color='blue', width=3)
        ),
        row=1, col=1
    )
    
    # 销量变化
    fig1.add_trace(
        go.Scatter(
            x=safety_data['Date'],
            y=safety_data['Retail_Daily_Sales'],
            mode='lines',
            name='零售渠道日销量',
            line=dict(color='green', width=2)
        ),
        row=2, col=1
    )
    
    fig1.add_trace(
        go.Scatter(
            x=safety_data['Date'],
            y=safety_data['Offline_Daily_Sales'],
            mode='lines',
            name='线下渠道日销量',
            line=dict(color='orange', width=2)
        ),
        row=2, col=1
    )
    
    fig1.add_trace(
        go.Scatter(
            x=safety_data['Date'],
            y=safety_data['All_Daily_Sales'],
            mode='lines',
            name='全渠道日销量',
            line=dict(color='red', width=2)
        ),
        row=2, col=1
    )
    
    fig1.update_layout(
        height=600,
        showlegend=True,
        title_text="库存与销量时间趋势分析"
    )
    fig1.update_xaxes(title_text="日期", row=2, col=1)
    fig1.update_yaxes(title_text="库存价值 (¥)", row=1, col=1)
    fig1.update_yaxes(title_text="销量 (¥)", row=2, col=1)
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # 图表2：安全库存线与预警
    st.header("🛡️ 安全库存线与预警信号")
    
    fig2 = go.Figure()
    
    # 实际库存
    fig2.add_trace(go.Scatter(
        x=safety_data['Date'],
        y=safety_data['Inv.Value(RMB)'],
        mode='lines',
        name='实际库存',
        line=dict(color='blue', width=4),
        fill=None
    ))
    
    # 安全库存线
    fig2.add_trace(go.Scatter(
        x=safety_data['Date'],
        y=safety_data['Safety_Stock_Retail'],
        mode='lines',
        name=f'零售渠道安全库存线 (OTD={otd_days}天)',
        line=dict(color='red', width=2, dash='dash'),
        fill=None
    ))
    
    fig2.add_trace(go.Scatter(
        x=safety_data['Date'],
        y=safety_data['Safety_Stock_Offline'],
        mode='lines',
        name=f'线下渠道安全库存线 (OTD={otd_days}天)',
        line=dict(color='orange', width=2, dash='dash'),
        fill=None
    ))
    
    fig2.add_trace(go.Scatter(
        x=safety_data['Date'],
        y=safety_data['Safety_Stock_All'],
        mode='lines',
        name=f'全渠道安全库存线 (OTD={otd_days}天)',
        line=dict(color='green', width=2, dash='dash'),
        fill=None
    ))
    
    # 预警区域
    if alerts:
        for i, alert in enumerate(alerts):
            if alert['level'] == 'critical':
                color = 'rgba(255, 0, 0, 0.2)'
            elif alert['level'] == 'warning':
                color = 'rgba(255, 165, 0, 0.2)'
            else:
                color = 'rgba(0, 0, 255, 0.2)'
            
            fig2.add_hline(
                y=current_inventory,
                line_dash="solid",
                line_color="red" if alert['level'] == 'critical' else "orange",
                annotation_text=f"当前库存: ¥{current_inventory:,.0f}",
                annotation_position="top right"
            )
    
    fig2.update_layout(
        title="库存安全线分析与预警",
        xaxis_title="日期",
        yaxis_title="库存价值 (¥)",
        height=500,
        showlegend=True,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # 详细数据表
    st.header("📋 详细计算数据")
    
    # 显示最近7天的数据
    recent_data = safety_data.tail(7).copy()
    recent_data['Date'] = recent_data['Date'].dt.strftime('%Y-%m-%d')
    
    # 重命名列以便显示
    display_data = recent_data[[
        'Date', 'Inv.Value(RMB)', 'Retail_Daily_Sales', 'Offline_Daily_Sales', 
        'All_Daily_Sales', 'Safety_Stock_Retail', 'Safety_Stock_Offline', 'Safety_Stock_All'
    ]].copy()
    
    display_data.columns = [
        '日期', '实际库存', '零售日销量', '线下日销量', '全渠道日销量',
        '零售安全库存', '线下安全库存', '全渠道安全库存'
    ]
    
    # 格式化数值显示
    for col in display_data.columns[1:]:
        display_data[col] = display_data[col].apply(lambda x: f"¥{x:,.0f}" if pd.notna(x) else "¥0")
    
    st.dataframe(display_data, use_container_width=True)
    
    # 计算逻辑说明
    st.header("🔍 计算逻辑说明")
    
    with st.expander("展开查看详细计算方法"):
        st.markdown("""
        ### 渠道分类定义：
        - **零售渠道**: HSM, MM, ICP, Grocery & Others, CVS, DCP
        - **线下渠道**: HSM, MM, Grocery & Others, CVS, DCP, ICP, WS
        - **全渠道**: 包含所有Store Group Channel
        
        ### 安全库存计算：
        1. **日均销量计算**: 使用7天移动平均来平滑销量波动
        2. **安全库存线**: 日均销量 × OTD天数
        3. **预警机制**: 当实际库存低于安全库存线时触发预警
        
        ### 预警级别：
        - 🔴 **严重**: 低于零售渠道安全库存线
        - 🟡 **警告**: 低于线下渠道安全库存线  
        - 🔵 **提醒**: 低于全渠道安全库存线
        
        ### 建议订单量：
        - 建议补货金额 = 安全库存线 - 当前实际库存
        - 考虑OTD时间，确保补货到达前库存充足
        """)
    
    # 渠道分析
    st.header("📊 各渠道销量分析")
    
    # 按渠道聚合数据
    channel_analysis = filtered_df.groupby('Store Group Channel').agg({
        'IDS GIV': ['sum', 'mean', 'count']
    }).round(2)
    
    channel_analysis.columns = ['总销量', '日均销量', '交易天数']
    channel_analysis = channel_analysis.sort_values('总销量', ascending=False)
    
    # 添加渠道分类标识
    def get_channel_category(channel):
        if channel in channel_groups['retail']:
            return "零售渠道"
        elif channel in channel_groups['offline']:
            return "线下渠道"
        else:
            return "其他渠道"
    
    channel_analysis['渠道分类'] = channel_analysis.index.map(get_channel_category)
    
    # 重新排列列的顺序
    channel_analysis = channel_analysis[['渠道分类', '总销量', '日均销量', '交易天数']]
    
    # 格式化显示
    display_channel = channel_analysis.copy()
    display_channel['总销量'] = display_channel['总销量'].apply(lambda x: f"¥{x:,.0f}")
    display_channel['日均销量'] = display_channel['日均销量'].apply(lambda x: f"¥{x:,.0f}")
    
    st.dataframe(display_channel, use_container_width=True)
    
    # 渠道贡献饼图
    fig3 = px.pie(
        values=channel_analysis['总销量'], 
        names=channel_analysis.index,
        title="各渠道销量贡献占比",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig3.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig3, use_container_width=True)

if __name__ == "__main__":
    main() 