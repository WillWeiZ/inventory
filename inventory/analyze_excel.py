import pandas as pd
import numpy as np

# 读取Excel文件
df = pd.read_excel('save.xlsx')

print("=== Excel文件数据分析 ===")
print(f"数据形状: {df.shape}")
print(f"列数: {len(df.columns)}")
print(f"行数: {len(df)}")

print("\n=== 列名信息 ===")
for i, col in enumerate(df.columns):
    print(f"{i+1}. {col}")

print("\n=== 前5行数据预览 ===")
print(df.head())

print("\n=== 关键字段值分析 ===")

# 检查SKU信息
if 'SKU' in df.columns:
    unique_skus = df['SKU'].unique()
    print(f"SKU数量: {len(unique_skus)}")
    print(f"SKU值: {unique_skus}")
elif any('sku' in col.lower() for col in df.columns):
    sku_cols = [col for col in df.columns if 'sku' in col.lower()]
    print(f"包含SKU的列: {sku_cols}")
    for col in sku_cols:
        print(f"{col}的唯一值: {df[col].unique()}")

# 检查Distributor信息
distributor_cols = [col for col in df.columns if 'distributor' in col.lower()]
if distributor_cols:
    print(f"\nDistributor相关列: {distributor_cols}")
    for col in distributor_cols:
        unique_vals = df[col].unique()
        print(f"{col}的唯一值: {unique_vals}")

# 检查Hub信息
hub_cols = [col for col in df.columns if 'hub' in col.lower()]
if hub_cols:
    print(f"\nHub相关列: {hub_cols}")
    for col in hub_cols:
        unique_vals = df[col].unique()
        print(f"{col}的唯一值: {unique_vals}")

# 检查时间相关信息
date_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['date', 'week', 'time'])]
if date_cols:
    print(f"\n时间相关列: {date_cols}")
    for col in date_cols:
        unique_vals = df[col].unique()
        print(f"{col}的唯一值数量: {len(unique_vals)}")
        if len(unique_vals) <= 10:
            print(f"{col}的值: {unique_vals}")
        else:
            print(f"{col}的前10个值: {unique_vals[:10]}")

# 检查金额相关信息
value_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['value', 'giv', 'inv', 'rmb', '金额'])]
if value_cols:
    print(f"\n金额相关列: {value_cols}")
    for col in value_cols:
        non_null_count = df[col].count()
        total_count = len(df)
        print(f"{col}: 非空值数量 {non_null_count}/{total_count}")
        if non_null_count > 0:
            print(f"  最小值: {df[col].min()}")
            print(f"  最大值: {df[col].max()}")

# 检查Store Group Channel相关信息
channel_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['channel', 'store', 'group'])]
if channel_cols:
    print(f"\nChannel/Store相关列: {channel_cols}")
    for col in channel_cols:
        unique_vals = df[col].unique()
        print(f"{col}的唯一值: {unique_vals}")

print("\n=== 数据缺失情况 ===")
print(df.isnull().sum())

print("\n=== 验证用户描述 ===")
print("根据用户描述验证以下内容:")
print("1. SKU 80814094")
print("2. WuHan_ChuangJie distributor")
print("3. Week Ending 时间维度")
print("4. 不同Hub的库存金额Inv.Value(RMB)")
print("5. 不同Store Group Channel的出货金额IDS GIV和进货金额DS GIV")
print("6. 进销存数据按周，库存数据只在最后一周") 