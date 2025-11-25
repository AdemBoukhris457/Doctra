# 图表和表格提取器

使用 `ChartTablePDFParser` 进行针对性提取的指南。

## 概述

`ChartTablePDFParser` 是一个专门用于从 PDF 文档中提取图表和表格的解析器。它针对只需要这些特定元素的场景进行了优化。

## 主要特性

- **专注提取**：仅提取图表和/或表格
- **选择性处理**：选择要提取的内容
- **VLM 集成**：将视觉元素转换为结构化数据
- **分割表格合并**：自动检测和合并跨页分割的表格
- **更快处理**：跳过不必要的元素

## 基本用法

```python
from doctra import ChartTablePDFParser

parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=True
)

parser.parse("data_report.pdf")
```

## 选择性提取

```python
# 仅提取表格
parser = ChartTablePDFParser(
    extract_charts=False,
    extract_tables=True
)

# 仅提取图表
parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=False
)
```

## 使用 VLM 获取结构化数据

```python
from doctra import ChartTablePDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

# 初始化 VLM 引擎
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-key"
)

parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=True,
    vlm=vlm_engine  # 传递 VLM 引擎实例
)

parser.parse("report.pdf")
# 输出：tables.xlsx, tables.html, vlm_items.json
```

## 分割表格合并

`ChartTablePDFParser` 包含自动检测和合并跨多个页面分割的表格。此功能对于处理财务报告、数据表格和其他大型表格跨页面边界的文档特别有用。

### 启用分割表格合并

```python
from doctra import ChartTablePDFParser

# 使用默认设置启用分割表格合并
parser = ChartTablePDFParser(
    extract_tables=True,
    merge_split_tables=True
)

parser.parse("document.pdf")
```

### 配置选项

```python
parser = ChartTablePDFParser(
    extract_tables=True,
    merge_split_tables=True,
    
    # 位置阈值
    bottom_threshold_ratio=0.20,  # 距离页面底部 20%
    top_threshold_ratio=0.15,     # 距离页面顶部 15%
    
    # 间隙容差
    max_gap_ratio=0.25,            # 页面高度的 25% 最大间隙
    
    # 结构验证
    column_alignment_tolerance=10.0,  # 列对齐的像素容差
    min_merge_confidence=0.65,       # 合并的最小置信度（0-1）
)
```

### 工作原理

分割表格检测使用两阶段方法：

1. **阶段 1：邻近检测** - 快速空间启发式方法，基于位置、重叠、间隙和宽度相似性识别候选对
2. **阶段 2：结构验证** - 使用 LSD（线段检测器）进行深度结构分析，验证列对齐和结构

有关算法的详细信息，请参阅[分割表格合并指南](../features/split-table-merging.md)。

### 输出

当检测到并合并分割表格时：

- 跳过单个表格段（不单独保存）
- 合并的表格图像保存为表格目录中的 `merged_table_<page1>_<page2>.png`
- 如果启用 VLM，合并的表格会被处理并包含在结构化输出（Excel、HTML、JSON）中
- 合并的表格包括元数据：页面范围和置信度分数

### 何时使用分割表格合并

在以下情况下启用分割表格合并：

- 处理财务报告或数据表格
- 表格跨多个页面
- 您需要完整的表格数据进行分析
- 处理包含大型数据表格的文档

## 何时使用

在以下情况下使用 `ChartTablePDFParser`：

- 您只需要图表和/或表格
- 更快的处理很重要
- 处理数据密集型文档
- 提取数据进行分析

## 另请参阅

- [VLM 集成](../engines/vlm-integration.md) - 结构化数据提取
- [结构化解析器](structured-parser.md) - 带分割表格合并详情的完整文档解析
- [分割表格合并指南](../features/split-table-merging.md) - 分割表格检测的综合指南
- [API 参考](../../api/parsers.md) - 完整 API 文档

