import pandas as pd
import numpy as np
from datetime import datetime

print('📊 库存预警与订单建议系统 - 演示分析')
print('=' * 50)

# 加载数据
print('📂 正在加载数据...')
df = pd.read_csv('/Users/willmbp/Documents/2024/My_projects/inventory/virtual_data_new_logic.csv')

# 数据预处理
df['Date'] = pd.to_datetime(df['Date'])
df['Inv.Value(RMB)'] = pd.to_numeric(df['Inv.Value(RMB)'], errors='coerce')
df['IDS GIV'] = pd.to_numeric(df['IDS GIV'], errors='coerce').fillna(0)

print(f'✅ 数据加载完成，共 {len(df)} 条记录')
print(f'📅 时间范围: {df["Date"].min().strftime("%Y-%m-%d")} 至 {df["Date"].max().strftime("%Y-%m-%d")}')

# 定义渠道分组
retail_channels = ['HSM', 'MM', 'ICP', 'Grocery & Others', 'CVS', 'DCP']
offline_channels = ['HSM', 'MM', 'Grocery & Others', 'CVS', 'DCP', 'ICP', 'WS']

print('\n🏪 渠道分类:')
print(f'零售渠道: {retail_channels}')
print(f'线下渠道: {offline_channels}')

# 计算各渠道日销量
retail_daily = df[df['Store Group Channel'].isin(retail_channels)].groupby('Date')['IDS GIV'].sum()
offline_daily = df[df['Store Group Channel'].isin(offline_channels)].groupby('Date')['IDS GIV'].sum()
all_daily = df.groupby('Date')['IDS GIV'].sum()

print('\n📈 销量统计:')
print(f'零售渠道总销量: ¥{retail_daily.sum():,.0f}')
print(f'线下渠道总销量: ¥{offline_daily.sum():,.0f}')
print(f'全渠道总销量: ¥{all_daily.sum():,.0f}')

# 计算移动平均（7天）
retail_ma = retail_daily.rolling(window=7, min_periods=1).mean()
offline_ma = offline_daily.rolling(window=7, min_periods=1).mean()
all_ma = all_daily.rolling(window=7, min_periods=1).mean()

print('\n📊 近期日均销量（7天移动平均）:')
print(f'零售渠道: ¥{retail_ma.iloc[-1]:,.0f}')
print(f'线下渠道: ¥{offline_ma.iloc[-1]:,.0f}')
print(f'全渠道: ¥{all_ma.iloc[-1]:,.0f}')

# 设置OTD参数
otd_days = 7
print(f'\n⏱️ OTD (Order to Delivery) 设置: {otd_days} 天')

# 计算安全库存线
safety_stock_retail = retail_ma.iloc[-1] * otd_days
safety_stock_offline = offline_ma.iloc[-1] * otd_days
safety_stock_all = all_ma.iloc[-1] * otd_days

# 获取当前库存
daily_data = df.groupby('Date')['Inv.Value(RMB)'].first()
current_inventory = daily_data.iloc[-1]
current_date = daily_data.index[-1]

print(f'\n💰 当前库存状态 ({current_date.strftime("%Y-%m-%d")}):')
print(f'实际库存: ¥{current_inventory:,.0f}')
print(f'零售渠道安全库存线: ¥{safety_stock_retail:,.0f}')
print(f'线下渠道安全库存线: ¥{safety_stock_offline:,.0f}')
print(f'全渠道安全库存线: ¥{safety_stock_all:,.0f}')

# 生成预警
print('\n🚨 库存预警分析:')
alerts = []

if current_inventory < safety_stock_retail:
    shortage = safety_stock_retail - current_inventory
    alerts.append(('严重', '零售渠道', shortage))
    print(f'🔴 严重预警: 当前库存低于零售渠道安全库存线')
    print(f'   缺口: ¥{shortage:,.0f}')
    print(f'   建议立即补货: ¥{shortage:,.0f}')

if current_inventory < safety_stock_offline:
    shortage = safety_stock_offline - current_inventory
    alerts.append(('警告', '线下渠道', shortage))
    print(f'🟡 警告: 当前库存低于线下渠道安全库存线')
    print(f'   缺口: ¥{shortage:,.0f}')
    print(f'   建议补货: ¥{shortage:,.0f}')

if current_inventory < safety_stock_all:
    shortage = safety_stock_all - current_inventory
    alerts.append(('提醒', '全渠道', shortage))
    print(f'🔵 提醒: 当前库存低于全渠道安全库存线')
    print(f'   缺口: ¥{shortage:,.0f}')
    print(f'   建议补货: ¥{shortage:,.0f}')

if not alerts:
    print('✅ 库存充足，无需预警')

# 渠道分析
print('\n📊 各渠道销量分析:')
channel_analysis = df.groupby('Store Group Channel').agg({
    'IDS GIV': ['sum', 'mean', 'count']
}).round(0)

channel_analysis.columns = ['总销量', '日均销量', '交易天数']
channel_analysis = channel_analysis.sort_values('总销量', ascending=False)

print('\n渠道排名（按总销量）:')
for i, (channel, data) in enumerate(channel_analysis.head(5).iterrows(), 1):
    print(f'{i}. {channel}: ¥{data["总销量"]:,.0f} (日均: ¥{data["日均销量"]:,.0f})')

# 总结报告
print('\n📋 总结报告:')
print('=' * 50)
print(f'分析日期: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'当前库存: ¥{current_inventory:,.0f}')
print(f'预警数量: {len(alerts)} 个')

if alerts:
    print('预警详情:')
    for level, channel_type, shortage in alerts:
        print(f'  - {level}预警 ({channel_type}): 建议补货 ¥{shortage:,.0f}')
else:
    print('库存状态: 正常')

print('\n💡 建议:')
if alerts:
    max_shortage = max(alert[2] for alert in alerts)
    print(f'1. 立即安排补货，建议补货金额: ¥{max_shortage:,.0f}')
    print(f'2. 考虑缩短补货周期，当前OTD为{otd_days}天')
    print(f'3. 加强销量预测，优化库存管理')
else:
    print(f'1. 继续监控库存水平变化')
    print(f'2. 保持当前补货策略')
    print(f'3. 可考虑适当减少库存以优化资金周转')

print('\n🔧 系统功能:')
print('- 实时库存监控')
print('- 多级预警机制')
print('- 动态安全库存计算')
print('- 补货建议')
print('- 渠道分析')

print('\n' + '=' * 50)
print('演示完成！要运行完整的交互式应用，请执行: streamlit run inventory_alert_system.py') 