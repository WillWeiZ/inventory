import pandas as pd
import numpy as np

print("🔍 测试数据处理逻辑")
print("=" * 40)

# 加载数据
df = pd.read_csv('/Users/willmbp/Documents/2024/My_projects/inventory/virtual_data_new_logic.csv')

# 数据预处理
df['Date'] = pd.to_datetime(df['Date'])
df['Inv.Value(RMB)'] = pd.to_numeric(df['Inv.Value(RMB)'], errors='coerce')
df['IDS GIV'] = pd.to_numeric(df['IDS GIV'], errors='coerce').fillna(0)

print(f"数据总量: {len(df)} 条记录")

# 检查库存为0的情况
zero_inventory_days = df[df['Inv.Value(RMB)'] == 0]['Date'].unique()
print(f"库存为0的天数: {len(zero_inventory_days)} 天")
print(f"库存为0的日期样例: {zero_inventory_days[:5]}")

# 检查销量数据
total_sales = df['IDS GIV'].sum()
print(f"总销量: ¥{total_sales:,.0f}")

# 按日期聚合检查
daily_data = df.groupby('Date').agg({
    'Inv.Value(RMB)': 'first',
    'IDS GIV': 'sum'
}).reset_index()

print(f"日期范围: {daily_data['Date'].min()} 至 {daily_data['Date'].max()}")
print(f"有库存的天数: {len(daily_data[daily_data['Inv.Value(RMB)'] > 0])} 天")
print(f"无库存的天数: {len(daily_data[daily_data['Inv.Value(RMB)'] == 0])} 天")

# 检查渠道数据
channels = df['Store Group Channel'].unique()
print(f"渠道数量: {len(channels)}")
print(f"渠道列表: {list(channels)}")

# 分析有效销量数据
valid_sales_days = daily_data[daily_data['IDS GIV'] > 0]
print(f"有销量的天数: {len(valid_sales_days)} 天")

if len(valid_sales_days) > 0:
    print(f"日均销量: ¥{valid_sales_days['IDS GIV'].mean():,.0f}")
    print(f"最高日销量: ¥{valid_sales_days['IDS GIV'].max():,.0f}")
    print(f"最低日销量: ¥{valid_sales_days['IDS GIV'].min():,.0f}")

# 渠道分析
print("\n渠道销量统计:")
channel_sales = df.groupby('Store Group Channel')['IDS GIV'].sum().sort_values(ascending=False)
for channel, sales in channel_sales.head(5).items():
    print(f"  {channel}: ¥{sales:,.0f}")

print("\n✅ 数据处理测试完成") 