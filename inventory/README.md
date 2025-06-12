# SKU 80814094 库存销售分析系统

这是一个基于Streamlit的可视化分析应用，用于分析SKU 80814094在武汉创洁工贸洗化股份有限公司的进销存数据。

## 功能特性

### 📈 库存销售趋势分析
- 实时库存金额趋势图
- 进货vs出货趋势对比
- 关键业务指标展示（平均库存、库存周转率等）

### 🥧 渠道分布分析  
- 不同月份各销售渠道的饼图分布
- 支持进货金额和出货金额分别分析
- 各渠道月度趋势线图

### 💧 瀑布图分析
- 月度进销存瀑布图展示
- 清晰显示每月进货、出货和库存变化
- 详细数据表格支持

### ⚠️ 安全库存分析
- 基于平均销售额和补货间隔的安全库存计算
- 可调节的OTD时间和安全系数参数
- 库存风险预警和安全区间可视化

## 安装和运行

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 确保数据文件
确保 `save.xlsx` 文件位于项目根目录

### 3. 运行应用
```bash
streamlit run streamlit_app.py
```

### 4. 访问应用
在浏览器中打开 `http://localhost:8501`

## 数据要求

应用需要包含以下字段的Excel文件：
- `FPC Code`: SKU编码
- `Distributor Hierarchy - Distributor`: 经销商
- `Distributor Hierarchy - Hub`: Hub信息
- `Report Date Hierarchy - Week Ending`: 周结束日期
- `Inv.Value(RMB)`: 库存金额
- `IDS GIV`: 出货金额
- `DS GIV`: 进货金额
- `Store Group Channel`: 销售渠道

## 使用说明

1. **侧边栏筛选**: 使用日期范围和渠道筛选器来限定分析范围
2. **Tab导航**: 在四个分析Tab之间切换查看不同维度的分析
3. **交互式图表**: 所有图表支持缩放、悬停查看详细数据
4. **参数调节**: 在安全库存分析中可以调节OTD时间和安全系数

## 技术栈

- **Streamlit**: Web应用框架
- **Pandas**: 数据处理和分析
- **Plotly**: 交互式图表库
- **OpenPyXL**: Excel文件读取 