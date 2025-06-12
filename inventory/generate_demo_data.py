import pandas as pd
import numpy as np
import random
from datetime import date, timedelta

def generate_demo_data():
    """
    生成专门用于展示库存预警逻辑的演示数据
    设计理念：
    1. 库存从高到低逐渐消耗，展示预警触发过程
    2. 包含补货事件，展示库存恢复
    3. 各渠道有合理且稳定的销量分布
    4. 能够清晰展示三级预警的触发时机
    """
    
    # 基本设置
    start_date = date(2025, 1, 1)
    end_date = date(2025, 3, 30)
    
    distributor = "WuHan_Chuangjie"
    hub = "武汉创洁工贸淡化股份有限公司-武汉东西湖"
    brand = "H&S"
    
    channels = [
        'B Store', 'CB', 'CVS', 'DCP', 'DKS', 'DMW', 'DP.com', 
        'EB', 'Grocery & Others', 'HSM', 'ICP', 'MM', 'WS'
    ]
    
    # 渠道销量权重（HSM为主要渠道）
    channel_weights = {
        'HSM': 0.65,        # 主要渠道，占65%
        'MM': 0.08,         # 8%
        'ICP': 0.06,        # 6%  
        'CVS': 0.05,        # 5%
        'Grocery & Others': 0.04,  # 4%
        'DCP': 0.04,        # 4%
        'WS': 0.03,         # 3%
        'B Store': 0.02,    # 2%
        'CB': 0.015,        # 1.5%
        'DP.com': 0.01,     # 1%
        'DMW': 0.005,       # 0.5%
        'DKS': 0.003,       # 0.3%
        'EB': 0.002         # 0.2%
    }
    
    all_data = []
    
    # 设计库存和销量场景
    # 阶段1：高库存期（1月1日-15日）- 无预警
    # 阶段2：中库存期（1月16日-2月15日）- 可能触发全渠道预警
    # 阶段3：低库存期（2月16日-3月5日）- 触发线下和零售预警
    # 阶段4：补货恢复（3月6日-15日）- 库存恢复
    # 阶段5：再次下降（3月16日-30日）- 再次触发预警
    
    current_date = start_date
    current_inventory = 300000.0  # 初始库存30万
    
    while current_date <= end_date:
        # 确定当前阶段和基础日销量
        days_elapsed = (current_date - start_date).days
        
        if days_elapsed <= 15:  # 阶段1：高库存期
            base_daily_sales = random.uniform(8000, 12000)
            restocking = False
        elif days_elapsed <= 46:  # 阶段2：中库存期
            base_daily_sales = random.uniform(10000, 14000)
            restocking = False
        elif days_elapsed <= 65:  # 阶段3：低库存期
            base_daily_sales = random.uniform(12000, 16000)
            restocking = False
        elif days_elapsed <= 75:  # 阶段4：补货恢复期
            base_daily_sales = random.uniform(9000, 13000)
            # 在3月6日和3月10日进行补货
            restocking = (days_elapsed == 65 or days_elapsed == 69)
        else:  # 阶段5：再次下降期
            base_daily_sales = random.uniform(11000, 15000)
            restocking = False
        
        # 补货逻辑
        if restocking:
            restock_amount = random.uniform(80000, 120000)
            current_inventory += restock_amount
        
        # 记录当日开始库存
        daily_start_inventory = current_inventory
        
        # 为每个渠道生成销量
        daily_records = []
        total_daily_sales = 0
        
        for channel in channels:
            # 基于权重分配销量，添加随机波动
            channel_base_sales = base_daily_sales * channel_weights[channel]
            
            # 添加随机波动（±30%）
            fluctuation = random.uniform(0.7, 1.3)
            channel_sales = channel_base_sales * fluctuation
            
            # 特殊渠道逻辑
            if channel in ['ICP', 'WS']:
                # ICP和WS每2-3天才有销量
                if random.random() < 0.4:  # 40%概率有销量
                    channel_sales *= random.uniform(2, 4)  # 集中销量
                else:
                    channel_sales = 0
            
            # 确保最小销量
            if channel_sales > 0:
                channel_sales = max(channel_sales, 10)
            
            daily_records.append({
                'channel': channel,
                'sales': round(channel_sales, 2)
            })
            total_daily_sales += channel_sales
        
        # 如果库存不足，按比例缩减销量
        if total_daily_sales > current_inventory:
            scale_factor = current_inventory / total_daily_sales
            for record in daily_records:
                record['sales'] *= scale_factor
            total_daily_sales = current_inventory
        
        # 更新库存
        current_inventory = max(0, current_inventory - total_daily_sales)
        
        # 生成数据记录
        date_str = current_date.strftime('%Y-%m-%d')
        for record in daily_records:
            all_data.append({
                'Date': date_str,
                'Distributor': distributor,
                'Hub': hub,
                'Inv.Value(RMB)': round(daily_start_inventory, 2),
                'Product Hierarchy - Brand': brand,
                'Store Group Channel': record['channel'],
                'IDS GIV': record['sales']
            })
        
        current_date += timedelta(days=1)
    
    # 创建DataFrame并保存
    df = pd.DataFrame(all_data)
    output_filename = "demo_inventory_data.csv"
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    
    print("🎯 演示数据生成完成！")
    print(f"📁 文件保存为: {output_filename}")
    
    # 数据概览
    daily_summary = df.groupby('Date').agg({
        'Inv.Value(RMB)': 'first',
        'IDS GIV': 'sum'
    }).reset_index()
    
    print(f"\n📊 数据概览:")
    print(f"总记录数: {len(df)} 条")
    print(f"日期范围: {df['Date'].min()} 至 {df['Date'].max()}")
    print(f"初始库存: ¥{daily_summary['Inv.Value(RMB)'].iloc[0]:,.0f}")
    print(f"最终库存: ¥{daily_summary['Inv.Value(RMB)'].iloc[-1]:,.0f}")
    print(f"总销量: ¥{df['IDS GIV'].sum():,.0f}")
    print(f"日均销量: ¥{daily_summary['IDS GIV'].mean():,.0f}")
    
    # 渠道分析
    print(f"\n🏪 主要渠道销量:")
    channel_sales = df.groupby('Store Group Channel')['IDS GIV'].sum().sort_values(ascending=False)
    for i, (channel, sales) in enumerate(channel_sales.head(5).items(), 1):
        percentage = (sales / df['IDS GIV'].sum()) * 100
        print(f"{i}. {channel}: ¥{sales:,.0f} ({percentage:.1f}%)")
    
    # 预警阶段分析
    print(f"\n⚠️ 预警阶段预览:")
    key_dates = ['2025-01-15', '2025-02-15', '2025-03-05', '2025-03-15', '2025-03-30']
    for date_str in key_dates:
        if date_str in daily_summary['Date'].values:
            inventory = daily_summary[daily_summary['Date'] == date_str]['Inv.Value(RMB)'].iloc[0]
            print(f"{date_str}: ¥{inventory:,.0f}")
    
    print(f"\n✨ 演示亮点:")
    print("📈 库存从高到低逐渐下降，展示预警触发过程")
    print("🔄 包含补货事件，展示库存恢复逻辑") 
    print("🎯 HSM作为主渠道，占总销量65%")
    print("⚡ 能够清晰展示三级预警的实际应用")
    print("📊 数据合理且具有说服力")

if __name__ == "__main__":
    generate_demo_data() 