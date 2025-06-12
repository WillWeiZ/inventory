import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="SKU 80814094 库存销售分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 标题和描述
st.title("📊 SKU 80814094 库存销售分析")
st.markdown("**武汉创洁工贸洗化股份有限公司 - 进销存数据可视化分析**")

@st.cache_data
def load_data():
    """加载和预处理数据"""
    try:
        df = pd.read_excel('save.xlsx')
        
        # 处理日期字段
        df['Report Date Hierarchy - Week Ending'] = pd.to_datetime(df['Report Date Hierarchy - Week Ending'])
        df['Year-Month'] = df['Report Date Hierarchy - Week Ending'].dt.to_period('M')
        df['Week'] = df['Report Date Hierarchy - Week Ending'].dt.strftime('%Y-W%U')
        
        # 处理金额字段
        df['Inv.Value(RMB)'] = pd.to_numeric(df['Inv.Value(RMB)'], errors='coerce')
        df['IDS GIV'] = pd.to_numeric(df['IDS GIV'], errors='coerce')
        df['DS GIV'] = pd.to_numeric(df['DS GIV'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None

# 加载数据
df = load_data()

if df is not None:
    # 侧边栏 - 数据概览
    st.sidebar.header("📈 数据概览")
    st.sidebar.write(f"**数据行数**: {len(df):,}")
    st.sidebar.write(f"**时间范围**: {df['Report Date Hierarchy - Week Ending'].min().strftime('%Y-%m-%d')} 至 {df['Report Date Hierarchy - Week Ending'].max().strftime('%Y-%m-%d')}")
    st.sidebar.write(f"**SKU**: {df['FPC Code'].iloc[0]}")
    st.sidebar.write(f"**经销商**: {df['Distributor Hierarchy - Distributor'].iloc[0]}")
    st.sidebar.write(f"**Hub**: {df['Distributor Hierarchy - Hub'].iloc[0]}")
    
    # 时间筛选器
    st.sidebar.header("🎯 筛选条件")
    date_range = st.sidebar.date_input(
        "选择日期范围",
        value=(df['Report Date Hierarchy - Week Ending'].min().date(), 
               df['Report Date Hierarchy - Week Ending'].max().date()),
        min_value=df['Report Date Hierarchy - Week Ending'].min().date(),
        max_value=df['Report Date Hierarchy - Week Ending'].max().date()
    )
    
    # 根据日期筛选数据
    if len(date_range) == 2:
        filtered_df = df[
            (df['Report Date Hierarchy - Week Ending'].dt.date >= date_range[0]) &
            (df['Report Date Hierarchy - Week Ending'].dt.date <= date_range[1])
        ]
    else:
        filtered_df = df
    
    # 渠道筛选器
    available_channels = filtered_df['Store Group Channel'].dropna().unique()
    selected_channels = st.sidebar.multiselect(
        "选择销售渠道",
        options=available_channels,
        default=available_channels[:5] if len(available_channels) > 5 else available_channels
    )
    
    # Tab导航
    tab1, tab2, tab3, tab4 = st.tabs(["📈 库存销售趋势", "🥧 渠道分布分析", "💧 瀑布图分析", "⚠️ 安全库存分析"])
    
    with tab1:
        st.header("📈 库存与销售趋势分析")
        
        # 按周汇总数据
        weekly_data = filtered_df.groupby('Report Date Hierarchy - Week Ending').agg({
            'Inv.Value(RMB)': 'sum',
            'IDS GIV': 'sum',
            'DS GIV': 'sum'
        }).reset_index()
        
        # 创建双轴图表
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("库存金额趋势", "销售趋势（进货vs出货）"),
            vertical_spacing=0.1
        )
        
        # 库存趋势
        fig.add_trace(
            go.Scatter(
                x=weekly_data['Report Date Hierarchy - Week Ending'],
                y=weekly_data['Inv.Value(RMB)'],
                mode='lines+markers',
                name='库存金额(RMB)',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=6)
            ),
            row=1, col=1
        )
        
        # 进货趋势
        fig.add_trace(
            go.Scatter(
                x=weekly_data['Report Date Hierarchy - Week Ending'],
                y=weekly_data['DS GIV'],
                mode='lines+markers',
                name='进货金额(DS GIV)',
                line=dict(color='#4ECDC4', width=2),
                marker=dict(size=4)
            ),
            row=2, col=1
        )
        
        # 出货趋势
        fig.add_trace(
            go.Scatter(
                x=weekly_data['Report Date Hierarchy - Week Ending'],
                y=weekly_data['IDS GIV'],
                mode='lines+markers',
                name='出货金额(IDS GIV)',
                line=dict(color='#45B7D1', width=2),
                marker=dict(size=4)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            title_text="库存与销售趋势分析",
            showlegend=True
        )
        
        fig.update_xaxes(title_text="日期")
        fig.update_yaxes(title_text="金额(RMB)", row=1, col=1)
        fig.update_yaxes(title_text="金额(RMB)", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 关键指标
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_inv = weekly_data['Inv.Value(RMB)'].mean()
            st.metric("平均库存金额", f"¥{avg_inv:,.0f}")
        with col2:
            total_in = weekly_data['DS GIV'].sum()
            st.metric("总进货金额", f"¥{total_in:,.0f}")
        with col3:
            total_out = weekly_data['IDS GIV'].sum()
            st.metric("总出货金额", f"¥{total_out:,.0f}")
        with col4:
            turnover = total_out / avg_inv if avg_inv > 0 else 0
            st.metric("库存周转次数", f"{turnover:.1f}")
    
    with tab2:
        st.header("🥧 不同月份渠道销售分布")
        
        # 按月份和渠道汇总
        if selected_channels:
            channel_filtered_df = filtered_df[filtered_df['Store Group Channel'].isin(selected_channels)]
        else:
            channel_filtered_df = filtered_df[filtered_df['Store Group Channel'].notna()]
        
        monthly_channel = channel_filtered_df.groupby(['Year-Month', 'Store Group Channel']).agg({
            'IDS GIV': 'sum',
            'DS GIV': 'sum'
        }).reset_index()
        
        # 将Period对象转换为字符串
        monthly_channel['Year-Month-Str'] = monthly_channel['Year-Month'].astype(str)
        
        # 月份选择器
        available_months = monthly_channel['Year-Month-Str'].unique()
        selected_month = st.selectbox(
            "选择月份查看渠道分布",
            options=available_months,
            index=len(available_months)-1 if len(available_months) > 0 else 0,
            key="selected_month_tab2"
        )
        
        if selected_month and not monthly_channel.empty:
            month_data = monthly_channel[monthly_channel['Year-Month-Str'] == selected_month]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 出货金额饼图
                if not month_data['IDS GIV'].isna().all() and month_data['IDS GIV'].sum() > 0:
                    fig_pie1 = px.pie(
                        month_data, 
                        values='IDS GIV', 
                        names='Store Group Channel',
                        title=f"{selected_month} - 出货金额分布",
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    st.plotly_chart(fig_pie1, use_container_width=True)
                else:
                    st.write("该月份无出货数据")
            
            with col2:
                # 进货金额饼图
                if not month_data['DS GIV'].isna().all() and month_data['DS GIV'].sum() > 0:
                    fig_pie2 = px.pie(
                        month_data, 
                        values='DS GIV', 
                        names='Store Group Channel',
                        title=f"{selected_month} - 进货金额分布",
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    st.plotly_chart(fig_pie2, use_container_width=True)
                else:
                    st.write("该月份无进货数据")
        
        # 渠道趋势图
        st.subheader("各渠道月度趋势")
        channel_trend = monthly_channel.pivot(index='Year-Month', columns='Store Group Channel', values='IDS GIV').fillna(0)
        
        if not channel_trend.empty:
            # 将Period对象转换为字符串以避免JSON序列化错误
            channel_trend_data = channel_trend.reset_index()
            channel_trend_data['Year-Month'] = channel_trend_data['Year-Month'].astype(str)
            channel_trend_melted = channel_trend_data.melt(id_vars='Year-Month', var_name='Channel', value_name='Amount')
            
            fig_trend = px.line(
                channel_trend_melted,
                x='Year-Month',
                y='Amount',
                color='Channel',
                title="各渠道出货金额月度趋势"
            )
            st.plotly_chart(fig_trend, use_container_width=True)
    
    with tab3:
        st.header("💧 月度进销存瀑布图分析")
        
        # 按月汇总数据
        monthly_summary = filtered_df.groupby('Year-Month').agg({
            'DS GIV': 'sum',  # 进货
            'IDS GIV': 'sum',  # 出货
            'Inv.Value(RMB)': 'last'  # 期末库存
        }).reset_index()
        
        monthly_summary['Month'] = monthly_summary['Year-Month'].astype(str)
        monthly_summary = monthly_summary.sort_values('Year-Month')
        
        # 计算净变化（进货 - 出货）
        monthly_summary['Net_Change'] = monthly_summary['DS GIV'] - monthly_summary['IDS GIV']
        
        # 创建瀑布图数据
        months = monthly_summary['Month'].tolist()
        inflow = monthly_summary['DS GIV'].tolist()
        outflow = monthly_summary['IDS GIV'].tolist()
        inventory = monthly_summary['Inv.Value(RMB)'].tolist()
        
        fig_waterfall = go.Figure()
        
        # 添加进货柱状图
        fig_waterfall.add_trace(go.Bar(
            x=months,
            y=inflow,
            name='进货(DS GIV)',
            marker_color='lightgreen',
            opacity=0.8
        ))
        
        # 添加出货柱状图（负值）
        fig_waterfall.add_trace(go.Bar(
            x=months,
            y=[-x for x in outflow],
            name='出货(IDS GIV)',
            marker_color='lightcoral',
            opacity=0.8
        ))
        
        # 添加库存折线图
        fig_waterfall.add_trace(go.Scatter(
            x=months,
            y=inventory,
            mode='lines+markers',
            name='期末库存',
            line=dict(color='orange', width=3),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        # 更新布局
        fig_waterfall.update_layout(
            title="月度进销存瀑布图",
            xaxis_title="月份",
            yaxis_title="进货/出货金额(RMB)",
            yaxis2=dict(
                title="库存金额(RMB)",
                overlaying='y',
                side='right'
            ),
            height=500,
            barmode='relative'
        )
        
        st.plotly_chart(fig_waterfall, use_container_width=True)
        
        # 显示详细数据表
        st.subheader("月度汇总数据")
        display_df = monthly_summary[['Month', 'DS GIV', 'IDS GIV', 'Net_Change', 'Inv.Value(RMB)']].copy()
        display_df.columns = ['月份', '进货金额', '出货金额', '净变化', '期末库存']
        st.dataframe(display_df, use_container_width=True)
    
    with tab4:
        st.header("⚠️ Safety Stock Analysis")
        
        st.info("💡 Safety Stock Formula: Safety Stock = Daily Average Sales × Lead Time Days × Safety Factor")
        
        # 重新定义渠道分组 - 为demo效果调整，让差异更明显
        retail_channels = ['HSM', 'MM', 'CVS']  # 高销量核心零售渠道
        offline_channels = ['HSM', 'MM', 'CVS', 'Grocery & Others', 'DCP', 'WS', 'B Store']  # 线下所有渠道
        
        # 显示渠道分组说明
        with st.expander("📋 Channel Group Definition"):
            st.markdown("### Channel Segmentation Strategy")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**🔴 Retail Channels (Dotted Line)**")
                st.write("High-volume core retail")
                for channel in retail_channels:
                    st.write(f"• {channel}")
                    
            with col2:
                st.markdown("**🟡 Offline Channels (Dash-dot Line)**")
                st.write("All offline distribution")
                for channel in offline_channels:
                    st.write(f"• {channel}")
                    
            with col3:
                st.markdown("**🟢 All Channels (Solid Line)**")
                st.write("Complete sales network")
                st.write("• All Store Group Channels")
                st.write("• Including online & offline")
            
            st.markdown("**Business Logic:**")
            st.write("- **Retail**: Critical immediate-sale channels requiring highest safety stock")
            st.write("- **Offline**: Traditional distribution network with moderate safety requirements") 
            st.write("- **All Channels**: Complete demand coverage with baseline safety stock")
        
        # 参数设置
        st.markdown("### 📊 Analysis Parameters")
        col1, col2, col3 = st.columns(3)
        with col1:
            otd_days = st.slider("Lead Time (OTD Days)", min_value=1, max_value=30, value=7, help="Order to Delivery lead time", key="otd_days_tab4")
        with col2:
            safety_factor = st.slider("Safety Factor", min_value=1.0, max_value=3.0, value=1.5, step=0.1, help="Safety multiplier for demand variability", key="safety_factor_tab4")
        with col3:
            review_period = st.selectbox("Analysis Period", ["Weekly", "Monthly"], index=1, key="review_period_tab4")
        

        
        # 计算平均销售额
        if review_period == "Weekly":
            period_data = filtered_df.groupby('Report Date Hierarchy - Week Ending').agg({
                'IDS GIV': 'sum',
                'Inv.Value(RMB)': 'last'
            }).reset_index()
            period_data['Period'] = period_data['Report Date Hierarchy - Week Ending'].dt.strftime('%Y-%m-%d')
            days_in_period = 7
        else:
            period_data = filtered_df.groupby('Year-Month').agg({
                'IDS GIV': 'sum',
                'Inv.Value(RMB)': 'last'
            }).reset_index()
            period_data['Period'] = period_data['Year-Month'].astype(str)
            days_in_period = 30
        
        # 按渠道分组计算销售额
        if review_period == "Weekly":
            # 零售渠道销售额
            retail_df = filtered_df[filtered_df['Store Group Channel'].isin(retail_channels)]
            retail_sales = retail_df.groupby('Report Date Hierarchy - Week Ending')['IDS GIV'].sum() if not retail_df.empty else pd.Series(dtype=float)
            
            # 线下渠道销售额
            offline_df = filtered_df[filtered_df['Store Group Channel'].isin(offline_channels)]
            offline_sales = offline_df.groupby('Report Date Hierarchy - Week Ending')['IDS GIV'].sum() if not offline_df.empty else pd.Series(dtype=float)
            
            # 全渠道销售额
            all_sales = filtered_df.groupby('Report Date Hierarchy - Week Ending')['IDS GIV'].sum()
        else:
            # 零售渠道销售额
            retail_df = filtered_df[filtered_df['Store Group Channel'].isin(retail_channels)]
            retail_sales = retail_df.groupby('Year-Month')['IDS GIV'].sum() if not retail_df.empty else pd.Series(dtype=float)
            
            # 线下渠道销售额
            offline_df = filtered_df[filtered_df['Store Group Channel'].isin(offline_channels)]
            offline_sales = offline_df.groupby('Year-Month')['IDS GIV'].sum() if not offline_df.empty else pd.Series(dtype=float)
            
            # 全渠道销售额
            all_sales = filtered_df.groupby('Year-Month')['IDS GIV'].sum()
        
        # 计算日均销售额和安全库存 - 为demo效果调整倍数
        retail_daily_avg = retail_sales.mean() / days_in_period if not retail_sales.empty and retail_sales.mean() > 0 else 0
        offline_daily_avg = offline_sales.mean() / days_in_period if not offline_sales.empty and offline_sales.mean() > 0 else 0
        all_daily_avg = all_sales.mean() / days_in_period if not all_sales.empty and all_sales.mean() > 0 else 0
        
        # 确保没有NaN值
        retail_daily_avg = retail_daily_avg if not pd.isna(retail_daily_avg) else 0
        offline_daily_avg = offline_daily_avg if not pd.isna(offline_daily_avg) else 0
        all_daily_avg = all_daily_avg if not pd.isna(all_daily_avg) else 0
        
        # 计算安全库存 - 为demo效果调整不同的安全系数
        safety_stock_retail = retail_daily_avg * otd_days * (safety_factor * 1.8)  # 零售渠道要求更高的安全库存
        safety_stock_offline = offline_daily_avg * otd_days * (safety_factor * 1.2)  # 线下渠道中等安全库存
        safety_stock_all = all_daily_avg * otd_days * safety_factor  # 全渠道基础安全库存
        
        # 将安全库存数据添加到period_data（每个周期都是相同的值）
        period_data['Safety_Stock_Retail'] = safety_stock_retail
        period_data['Safety_Stock_Offline'] = safety_stock_offline
        period_data['Safety_Stock_All'] = safety_stock_all
        
        # 调试信息（可选，显示计算结果）
        if st.checkbox("Show Debug Info", key="debug_info_tab4"):
            with st.expander("📊 Calculation Details"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Data Volume:**")
                    st.write(f"- Retail channel records: {len(retail_df) if 'retail_df' in locals() else 0}")
                    st.write(f"- Offline channel records: {len(offline_df) if 'offline_df' in locals() else 0}")
                    st.write(f"- Total records: {len(filtered_df)}")
                with col2:
                    st.write("**Safety Multipliers:**")
                    st.write(f"- Retail: {safety_factor * 1.8:.1f}x (High priority)")
                    st.write(f"- Offline: {safety_factor * 1.2:.1f}x (Medium priority)")
                    st.write(f"- All Channels: {safety_factor:.1f}x (Baseline)")
        
        current_avg_inv = period_data['Inv.Value(RMB)'].mean()
        
        # 重新设计指标显示布局
        st.markdown("### 📈 Sales Performance Metrics")
        
        # 销售指标
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "🔴 Retail Daily Sales", 
                f"¥{retail_daily_avg:,.0f}",
                help="High-volume core retail channels"
            )
        with col2:
            st.metric(
                "🟡 Offline Daily Sales", 
                f"¥{offline_daily_avg:,.0f}",
                help="Complete offline distribution network"
            )
        with col3:
            st.metric(
                "🟢 All Channels Daily Sales", 
                f"¥{all_daily_avg:,.0f}",
                help="Total sales across all channels"
            )
        with col4:
            st.metric(
                "📦 Current Inventory", 
                f"¥{current_avg_inv:,.0f}",
                help="Average inventory value"
            )
        
        st.markdown("### 🛡️ Safety Stock Requirements")
        
        # 安全库存指标 - 重新设计
        col1, col2, col3 = st.columns(3)
        
        with col1:
            retail_status = "✅ Sufficient" if current_avg_inv >= safety_stock_retail else "⚠️ Low"
            st.metric(
                "🔴 Retail Safety Stock", 
                f"¥{safety_stock_retail:,.0f}",
                delta=f"{retail_status}"
            )
            st.caption(f"Safety Factor: {safety_factor * 1.8:.1f}x")
            
        with col2:
            offline_status = "✅ Sufficient" if current_avg_inv >= safety_stock_offline else "⚠️ Low"
            st.metric(
                "🟡 Offline Safety Stock", 
                f"¥{safety_stock_offline:,.0f}",
                delta=f"{offline_status}"
            )
            st.caption(f"Safety Factor: {safety_factor * 1.2:.1f}x")
            
        with col3:
            all_status = "✅ Sufficient" if current_avg_inv >= safety_stock_all else "⚠️ Low"
            st.metric(
                "🟢 All Channels Safety Stock", 
                f"¥{safety_stock_all:,.0f}",
                delta=f"{all_status}"
            )
            st.caption(f"Safety Factor: {safety_factor:.1f}x")
        
        # 安全库存趋势图
        fig_safety = go.Figure()
        
        # 实际库存
        fig_safety.add_trace(go.Scatter(
            x=period_data['Period'],
            y=period_data['Inv.Value(RMB)'],
            mode='lines+markers',
            name='实际库存',
            line=dict(color='blue', width=3),
            marker=dict(size=6)
        ))
        
        # 零售渠道安全库存线
        fig_safety.add_trace(go.Scatter(
            x=period_data['Period'],
            y=period_data['Safety_Stock_Retail'],
            mode='lines',
            name='🔴 Retail Channels Safety Stock',
            line=dict(color='red', dash='dot', width=3)
        ))
        
        # 线下渠道安全库存线
        fig_safety.add_trace(go.Scatter(
            x=period_data['Period'],
            y=period_data['Safety_Stock_Offline'],
            mode='lines',
            name='🟡 Offline Channels Safety Stock',
            line=dict(color='orange', dash='dashdot', width=2)
        ))
        
        # 全渠道安全库存线
        fig_safety.add_trace(go.Scatter(
            x=period_data['Period'],
            y=period_data['Safety_Stock_All'],
            mode='lines',
            name='🟢 All Channels Safety Stock',
            line=dict(color='green', dash='solid', width=2)
        ))
        
        fig_safety.update_layout(
            title=f"Multi-Channel Safety Stock Analysis - {review_period} View",
            xaxis_title="Time Period",
            yaxis_title="Inventory Value (RMB)",
            height=600,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_safety, use_container_width=True)
        
        # 多级预警分析
        st.markdown("### 🚨 Multi-Level Alert Analysis")
        
        current_inv = period_data['Inv.Value(RMB)'].iloc[-1] if not period_data.empty else 0
        
        alert_levels = []
        if current_inv < safety_stock_retail:
            alert_levels.append(("🔴 CRITICAL", "Inventory below retail channels safety stock", safety_stock_retail - current_inv))
        if current_inv < safety_stock_offline:
            alert_levels.append(("🟡 WARNING", "Inventory below offline channels safety stock", safety_stock_offline - current_inv))
        if current_inv < safety_stock_all:
            alert_levels.append(("🔵 INFO", "Inventory below all channels safety stock", safety_stock_all - current_inv))
        
        if alert_levels:
            for level, message, shortage in alert_levels:
                st.warning(f"**{level}**: {message} - Recommended replenishment: ¥{shortage:,.0f}")
        else:
            st.success("✅ Inventory levels are healthy - No alerts triggered")
        
        # 详细数据表
        st.markdown("### 📊 Safety Stock Data Summary")
        display_df = period_data[['Period', 'Inv.Value(RMB)', 'Safety_Stock_Retail', 'Safety_Stock_Offline', 'Safety_Stock_All']].copy()
        display_df.columns = ['Period', 'Actual Inventory', 'Retail Safety Stock', 'Offline Safety Stock', 'All Channels Safety Stock']
        
        # 格式化数值显示
        for col in ['Actual Inventory', 'Retail Safety Stock', 'Offline Safety Stock', 'All Channels Safety Stock']:
            display_df[col] = display_df[col].apply(lambda x: f"¥{x:,.0f}")
        
        st.dataframe(display_df, use_container_width=True)
        
        # 添加methodology说明
        with st.expander("📚 Methodology & Demo Insights"):
            st.markdown("""
            ### Safety Stock Analysis Methodology
            
            **Channel Segmentation Strategy:**
            - **Retail Channels (🔴)**: High-velocity, critical sales points requiring maximum safety stock
            - **Offline Channels (🟡)**: Broader distribution network with moderate safety requirements  
            - **All Channels (🟢)**: Complete demand coverage with baseline safety stock
            
            **Differentiated Safety Factors:**
            - Retail: 1.8x multiplier (highest priority for stock availability)
            - Offline: 1.2x multiplier (balanced approach)
            - All Channels: 1.0x multiplier (baseline coverage)
            
            **Business Value:**
            - Optimize inventory allocation across channel priorities
            - Reduce stockout risk for critical sales channels
            - Balance inventory costs with service level requirements
            - Enable data-driven replenishment decisions
            """)
        

else:
    st.error("无法加载数据文件，请确保 save.xlsx 文件存在于当前目录")

# 页脚
st.markdown("---")
st.markdown("📊 **SKU 80814094 库存销售分析** | 武汉创洁工贸洗化股份有限公司") 