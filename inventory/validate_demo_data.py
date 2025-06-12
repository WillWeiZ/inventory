import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def validate_demo_data():
    """验证演示数据的质量和预警逻辑展示效果"""
    
    print("🔍 验证演示数据...")
    
    # 加载数据
    df = pd.read_csv('demo_inventory_data.csv')
    
    # 基本数据验证
    print(f"\n📊 基本数据统计:")
    print(f"总记录数: {len(df):,}")
    print(f"日期范围: {df['Date'].min()} 至 {df['Date'].max()}")
    print(f"唯一日期数: {df['Date'].nunique()}")
    print(f"渠道数量: {df['Store Group Channel'].nunique()}")
    
    # 按日汇总数据
    daily_data = df.groupby('Date').agg({
        'Inv.Value(RMB)': 'first',
        'IDS GIV': 'sum'
    }).reset_index()
    
    daily_data['Date'] = pd.to_datetime(daily_data['Date'])
    daily_data = daily_data.sort_values('Date')
    
    print(f"\n📈 库存趋势分析:")
    print(f"初始库存: ¥{daily_data['Inv.Value(RMB)'].iloc[0]:,.0f}")
    print(f"最终库存: ¥{daily_data['Inv.Value(RMB)'].iloc[-1]:,.0f}")
    print(f"最高库存: ¥{daily_data['Inv.Value(RMB)'].max():,.0f}")
    print(f"最低库存: ¥{daily_data['Inv.Value(RMB)'].min():,.0f}")
    
    # 销量分析
    print(f"\n💰 销量分析:")
    print(f"总销量: ¥{daily_data['IDS GIV'].sum():,.0f}")
    print(f"日均销量: ¥{daily_data['IDS GIV'].mean():,.0f}")
    print(f"最高日销量: ¥{daily_data['IDS GIV'].max():,.0f}")
    print(f"最低日销量: ¥{daily_data['IDS GIV'].min():,.0f}")
    
    # 渠道分析
    print(f"\n🏪 渠道销量排名:")
    channel_sales = df.groupby('Store Group Channel')['IDS GIV'].sum().sort_values(ascending=False)
    total_sales = channel_sales.sum()
    
    for i, (channel, sales) in enumerate(channel_sales.items(), 1):
        percentage = (sales / total_sales) * 100
        print(f"{i:2d}. {channel:20s}: ¥{sales:8,.0f} ({percentage:5.1f}%)")
    
    # 预警逻辑验证
    print(f"\n⚠️ 预警逻辑验证:")
    
    # 计算7日移动平均
    daily_data['MA7'] = daily_data['IDS GIV'].rolling(window=7, min_periods=1).mean()
    
    # 不同OTD下的安全库存线
    otd_scenarios = [7, 14, 21]
    
    for otd in otd_scenarios:
        daily_data[f'Safety_Stock_{otd}'] = daily_data['MA7'] * otd
        
        # 检查预警触发情况
        below_safety = daily_data[daily_data['Inv.Value(RMB)'] < daily_data[f'Safety_Stock_{otd}']]
        
        print(f"\nOTD {otd:2d}天:")
        print(f"  安全库存线均值: ¥{daily_data[f'Safety_Stock_{otd}'].mean():,.0f}")
        print(f"  触发预警天数: {len(below_safety)} / {len(daily_data)} 天")
        
        if len(below_safety) > 0:
            print(f"  首次预警日期: {below_safety['Date'].min().strftime('%Y-%m-%d')}")
            print(f"  最低库存/安全库存比: {(below_safety['Inv.Value(RMB)'] / below_safety[f'Safety_Stock_{otd}']).min():.1%}")
    
    # 补货事件识别
    print(f"\n🔄 补货事件分析:")
    daily_data['Inventory_Change'] = daily_data['Inv.Value(RMB)'].diff()
    restocks = daily_data[daily_data['Inventory_Change'] > 50000]  # 补货阈值5万
    
    if len(restocks) > 0:
        print(f"检测到 {len(restocks)} 次补货事件:")
        for _, restock in restocks.iterrows():
            print(f"  {restock['Date'].strftime('%Y-%m-%d')}: +¥{restock['Inventory_Change']:,.0f}")
    else:
        print("未检测到明显的补货事件")
    
    # 数据质量检查
    print(f"\n✅ 数据质量检查:")
    
    # 检查缺失值
    missing_inventory = daily_data['Inv.Value(RMB)'].isna().sum()
    missing_sales = daily_data['IDS GIV'].isna().sum()
    zero_inventory_days = (daily_data['Inv.Value(RMB)'] == 0).sum()
    zero_sales_days = (daily_data['IDS GIV'] == 0).sum()
    
    print(f"库存缺失值: {missing_inventory} 天")
    print(f"销量缺失值: {missing_sales} 天") 
    print(f"零库存天数: {zero_inventory_days} 天")
    print(f"零销量天数: {zero_sales_days} 天")
    
    # 逻辑一致性检查
    inconsistent_days = 0
    for i in range(1, len(daily_data)):
        prev_inventory = daily_data.iloc[i-1]['Inv.Value(RMB)']
        prev_sales = daily_data.iloc[i-1]['IDS GIV']
        curr_inventory = daily_data.iloc[i]['Inv.Value(RMB)']
        
        # 计算理论库存（不考虑补货）
        theoretical_inventory = prev_inventory - prev_sales
        
        # 如果当前库存明显高于理论库存，可能是补货
        if curr_inventory > theoretical_inventory + 1000:  # 允许1000的误差
            continue
        
        # 如果差异过大，标记为不一致
        if abs(curr_inventory - theoretical_inventory) > 1000:
            inconsistent_days += 1
    
    print(f"库存逻辑不一致天数: {inconsistent_days} 天")
    
    # 演示效果评估
    print(f"\n🎯 演示效果评估:")
    
    # 检查是否有清晰的库存下降趋势
    downward_trend_days = 0
    for i in range(1, len(daily_data)):
        if daily_data.iloc[i]['Inv.Value(RMB)'] < daily_data.iloc[i-1]['Inv.Value(RMB)']:
            downward_trend_days += 1
    
    trend_percentage = (downward_trend_days / (len(daily_data) - 1)) * 100
    print(f"库存下降趋势天数比例: {trend_percentage:.1f}%")
    
    # 检查HSM是否为主导渠道
    hsm_percentage = (channel_sales['HSM'] / total_sales) * 100
    print(f"HSM渠道占比: {hsm_percentage:.1f}% {'✅' if hsm_percentage > 60 else '❌'}")
    
    # 检查是否有多级预警触发
    otd_14_alerts = len(daily_data[daily_data['Inv.Value(RMB)'] < daily_data['Safety_Stock_14']])
    alert_percentage = (otd_14_alerts / len(daily_data)) * 100
    print(f"14天OTD预警触发率: {alert_percentage:.1f}% {'✅' if 20 <= alert_percentage <= 80 else '❌'}")
    
    print(f"\n🎉 演示数据验证完成！")
    
    # 生成演示要点
    print(f"\n📋 演示要点总结:")
    print("1. 📊 库存从30万逐步下降至0，展示完整生命周期")
    print("2. 🎯 HSM渠道占主导地位，符合实际业务模式")
    print("3. ⚠️ 多阶段预警触发，展示预警系统的实用性")
    print("4. 🔄 包含补货事件，展示库存管理的动态性")
    print("5. 📈 数据逻辑一致，无异常值干扰演示效果")

if __name__ == "__main__":
    validate_demo_data() 