# PaddleOCRVL PDF 解析器

使用 `PaddleOCRVLPDFParser` 进行端到端文档解析的指南，具有视觉语言模型功能。

## 安装要求

在使用 `PaddleOCRVLPDFParser` 之前，您需要安装所需的依赖项：

```bash
pip install -U "paddleocr[doc-parser]"
```

此外，您需要安装平台特定的 safetensors wheels：

**对于 Linux 系统：**
```bash
python -m pip install https://paddle-whl.bj.bcebos.com/nightly/cu126/safetensors/safetensors-0.6.2.dev0-cp38-abi3-linux_x86_64.whl
```

**对于 Windows 系统：**
```bash
python -m pip install https://xly-devops.cdn.bcebos.com/safetensors-nightly/safetensors-0.6.2.dev0-cp38-abi3-win_amd64.whl
```

!!! warning "使用前必需"
    这些安装步骤在使用 `PaddleOCRVLPDFParser` 之前是**必需的**。没有它们，您可能会遇到导入错误。

## 概述

`PaddleOCRVLPDFParser` 使用 PaddleOCRVL（视觉语言模型）进行全面的文档理解。它将 PaddleOCRVL 的高级文档解析功能与 DocRes 图像恢复和分割表格合并相结合，为复杂文档处理任务提供完整的解决方案。

## 主要特性

- **端到端解析**：使用 PaddleOCRVL 在单次处理中完成文档理解
- **图表识别**：自动检测图表并转换为结构化表格格式
- **文档恢复**：可选的 DocRes 集成以增强文档质量
- **分割表格合并**：自动检测并合并跨页分割的表格
- **结构化输出**：生成包含表格和图表的 Markdown、HTML 和 Excel 文件
- **多种元素类型**：处理标题、文本、表格、图表、脚注、图形标题等

## 基本用法

```python
from doctra import PaddleOCRVLPDFParser

# 使用默认设置的基本解析器
parser = PaddleOCRVLPDFParser(
    use_image_restoration=True,      # 启用 DocRes 恢复
    use_chart_recognition=True,       # 启用图表识别
    merge_split_tables=True,          # 启用分割表格合并
    device="gpu"                      # 使用 GPU 进行处理
)

# 解析 PDF 文档
parser.parse("document.pdf")
```

## 配置选项

### DocRes 图像恢复

```python
parser = PaddleOCRVLPDFParser(
    # 图像恢复设置
    use_image_restoration=True,
    restoration_task="appearance",    # 选项：appearance, dewarping, deshadowing, deblurring, binarization, end2end
    restoration_device="cuda",        # 或 "cpu" 或 None 自动检测
    restoration_dpi=300,              # 恢复处理的 DPI
)
```

### PaddleOCRVL 设置

```python
parser = PaddleOCRVLPDFParser(
    # PaddleOCRVL 配置
    use_chart_recognition=True,       # 启用图表识别和提取
    use_doc_orientation_classify=True, # 启用文档方向分类
    use_doc_unwarping=True,           # 启用文档去扭曲
    use_layout_detection=True,        # 启用布局检测
    device="gpu",                     # "gpu" 或 "cpu"
)
```

### 分割表格合并

```python
parser = PaddleOCRVLPDFParser(
    # 分割表格合并设置
    merge_split_tables=True,          # 启用分割表格检测和合并
    bottom_threshold_ratio=0.20,      # "太接近底部"检测的比率
    top_threshold_ratio=0.15,         # "太接近顶部"检测的比率
    max_gap_ratio=0.25,               # 表格之间的最大允许间隙
    column_alignment_tolerance=10.0,  # 列对齐的像素容差
    min_merge_confidence=0.65         # 合并的最小置信度分数
)
```

## 高级配置

```python
from doctra import PaddleOCRVLPDFParser

parser = PaddleOCRVLPDFParser(
    # DocRes 图像恢复设置
    use_image_restoration=True,
    restoration_task="end2end",       # 完整恢复流程
    restoration_device="cuda",        # 强制使用 GPU
    restoration_dpi=300,              # 更高的 DPI 以获得更好的质量
    
    # PaddleOCRVL 设置
    use_chart_recognition=True,
    use_doc_orientation_classify=True,  # 启用方向检测
    use_doc_unwarping=True,            # 启用去扭曲
    use_layout_detection=True,
    device="gpu",
    
    # 分割表格合并设置
    merge_split_tables=True,
    bottom_threshold_ratio=0.20,
    top_threshold_ratio=0.15,
    max_gap_ratio=0.25,
    column_alignment_tolerance=10.0,
    min_merge_confidence=0.65
)

# 使用自定义输出目录解析
parser.parse("document.pdf", output_dir="custom_output")
```

## 输出结构

解析器在 `outputs/{document_name}/paddleocr_vl_parse/` 中生成输出，包含：

- **result.md**：包含所有提取内容的 Markdown 文件
- **result.html**：格式化的 HTML 文件
- **tables.xlsx**：包含所有表格和图表作为结构化数据的 Excel 文件
- **tables.html**：包含结构化表格和图表的 HTML 文件
- **enhanced_pages/**：包含 DocRes 增强页面图像的目录（如果启用了恢复）
- **tables/**：包含合并表格图像的目录（如果检测到分割表格）

## 提取的内容类型

解析器提取各种文档元素：

- **标题**：文档标题和章节标题
- **文本**：段落和正文
- **表格**：提取为 HTML 并转换为 Excel 格式
- **图表**：从视觉格式转换为结构化表格数据（管道分隔格式）
- **脚注**：基于视觉的脚注检测（`vision_footnote`）
- **图形标题**：标题和图例描述
- **数字**：独立数字（如页码）

## 图表识别

PaddleOCRVL 自动识别图表并将其转换为结构化表格格式。图表以管道分隔格式提取，然后转换为 Excel 兼容的表格。

示例图表输出：
```
Category | Percentage
PCT system fees | 358.6%
Madrid system fees | 76.2%
```

这会自动转换为带标题和行的结构化表格，以便包含在 Excel 输出中。

## 分割表格合并

解析器包含自动检测和合并跨多个页面分割的表格。此功能使用与其他解析器相同的两阶段方法：

1. **阶段 1：邻近检测** - 快速空间启发式方法
2. **阶段 2：结构验证** - 使用 LSD 进行深度结构分析

详细信息，请参阅[分割表格合并指南](../features/split-table-merging.md)。

## DocRes 恢复任务

| 任务 | 描述 | 最适合 |
|------|------|--------|
| `appearance` | 一般外观增强 | 大多数文档（默认） |
| `dewarping` | 校正透视失真 | 有透视问题的扫描文档 |
| `deshadowing` | 去除阴影和光照伪影 | 有阴影问题的文档 |
| `deblurring` | 减少模糊并提高清晰度 | 模糊或低质量扫描 |
| `binarization` | 转换为黑白 | 需要干净二值化的文档 |
| `end2end` | 完整的恢复流程 | 严重退化的文档 |

## 参数参考

### DocRes 参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `use_image_restoration` | bool | `True` | 启用/禁用 DocRes 图像恢复 |
| `restoration_task` | str | `"appearance"` | 要使用的 DocRes 恢复任务 |
| `restoration_device` | str | `None` | DocRes 的设备（"cuda"、"cpu" 或 None 自动检测） |
| `restoration_dpi` | int | `200` | 恢复处理的 DPI |

### PaddleOCRVL 参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `use_chart_recognition` | bool | `True` | 启用图表识别和提取 |
| `use_doc_orientation_classify` | bool | `False` | 启用文档方向分类 |
| `use_doc_unwarping` | bool | `False` | 启用文档去扭曲 |
| `use_layout_detection` | bool | `True` | 启用布局检测 |
| `device` | str | `"gpu"` | PaddleOCRVL 处理的设备（"gpu" 或 "cpu"） |

### 分割表格合并参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `merge_split_tables` | bool | `True` | 启用/禁用分割表格检测 |
| `bottom_threshold_ratio` | float | `0.20` | 检测页面底部附近表格的比率（0-1） |
| `top_threshold_ratio` | float | `0.15` | 检测页面顶部附近表格的比率（0-1） |
| `max_gap_ratio` | float | `0.25` | 表格之间的最大允许间隙 |
| `column_alignment_tolerance` | float | `10.0` | 列对齐验证的像素容差 |
| `min_merge_confidence` | float | `0.65` | 合并表格所需的最小置信度分数（0-1） |

## 何时使用

在以下情况下使用 `PaddleOCRVLPDFParser`：

- **复杂文档**：包含多种内容类型的文档（文本、表格、图表、图形）
- **图表提取**：当您需要将图表转换为结构化数据时
- **端到端处理**：当您想要单次处理的文档理解解决方案时
- **质量增强**：当文档在处理前需要恢复时
- **分割表格**：包含跨多个页面的表格的文档
- **全面输出**：当您需要所有内容类型的结构化格式时

在以下情况下考虑其他解析器：

- **简单文本提取**：使用 `StructuredPDFParser` 进行基本文本提取
- **仅视觉元素**：使用 `ChartTablePDFParser` 仅提取图表/表格
- **不需要恢复**：如果文档质量良好，使用 `StructuredPDFParser`

## 示例：财务报告处理

```python
from doctra import PaddleOCRVLPDFParser

# 为财务报告初始化解析器
parser = PaddleOCRVLPDFParser(
    use_image_restoration=True,
    restoration_task="appearance",
    use_chart_recognition=True,      # 对财务图表很重要
    merge_split_tables=True,         # 财务表格经常跨页
    device="gpu"
)

# 处理财务报告
parser.parse("annual_report.pdf")

# 输出包括：
# - 所有文本内容
# - 财务表格（包括合并的分割表格）
# - 转换为 Excel 格式的图表
# - 全部在结构化 Excel 文件中（tables.xlsx）
```

## 另请参阅

- [DocRes 引擎](../engines/docres-engine.md) - 图像恢复详情
- [分割表格合并指南](../features/split-table-merging.md) - 分割表格检测的综合指南
- [结构化解析器](structured-parser.md) - 用于比较的基础解析器
- [API 参考](../../api/parsers.md) - 完整 API 文档

