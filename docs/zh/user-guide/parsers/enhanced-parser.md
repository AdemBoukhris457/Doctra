# 增强 PDF 解析器

使用带图像恢复的 `EnhancedPDFParser` 的指南。

## 概述

`EnhancedPDFParser` 扩展了 `StructuredPDFParser`，具有 DocRes 图像恢复功能。它非常适合处理扫描文档、低质量 PDF 或有视觉失真的文档。

## 主要特性

- **图像恢复**：DocRes 集成用于文档增强
- **6 种恢复任务**：去扭曲、去阴影、去模糊等
- **GPU 加速**：可选的 CUDA 支持以加快处理速度
- **分割表格合并**：自动检测和合并跨页分割的表格
- **所有基础功能**：继承所有 `StructuredPDFParser` 功能

## 基本用法

```python
from doctra import EnhancedPDFParser

parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="appearance"
)

parser.parse("scanned_document.pdf")
```

## 恢复任务

| 任务 | 最适合 |
|------|--------|
| `appearance` | 一般增强（默认） |
| `dewarping` | 透视失真 |
| `deshadowing` | 去除阴影 |
| `deblurring` | 减少模糊 |
| `binarization` | 干净的黑白转换 |
| `end2end` | 严重退化 |

## 分割表格合并

`EnhancedPDFParser` 包含自动检测和合并跨多个页面分割的表格。此功能对于处理财务报告、数据表格和其他大型表格跨页面边界的文档特别有用。

### 启用分割表格合并

```python
from doctra import EnhancedPDFParser

# 使用默认设置启用分割表格合并
parser = EnhancedPDFParser(
    use_image_restoration=True,
    merge_split_tables=True
)

parser.parse("document.pdf")
```

### 配置选项

```python
parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="appearance",
    
    # 启用分割表格合并
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

1. **阶段 1：邻近检测** - 快速空间启发式方法，基于位置、水平重叠、间隙和宽度相似性识别候选对
2. **阶段 2：结构验证** - 使用 LSD（线段检测器）进行深度结构分析，验证列对齐和结构

有关算法的详细信息，请参阅[分割表格合并指南](../features/split-table-merging.md)。

### 输出

当检测到并合并分割表格时：

- **合并图像**：创建单个合成图像，组合两个表格段
- **Markdown/HTML 输出**：合并的表格出现一次，并带有指示它跨多个页面的注释（例如，"Merged Table (pages 1-2)"）
- **文件位置**：合并的表格保存为 `tables/` 目录中的 `merged_table_{page1}_{page2}.png`
- **VLM 处理**：如果启用 VLM，合并的表格作为单个完整表格进行处理，以获得更好的提取准确性

### 参数详情

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `merge_split_tables` | `False` | 启用/禁用分割表格检测 |
| `bottom_threshold_ratio` | `0.20` | 检测页面底部附近表格的比率（0-1） |
| `top_threshold_ratio` | `0.15` | 检测页面顶部附近表格的比率（0-1） |
| `max_gap_ratio` | `0.25` | 表格之间的最大允许间隙（考虑页眉/页脚） |
| `column_alignment_tolerance` | `10.0` | 列对齐验证的像素容差 |
| `min_merge_confidence` | `0.65` | 合并表格所需的最小置信度分数（0-1） |

### 何时使用分割表格合并

在以下情况下启用分割表格合并：

- 处理包含跨多个页面的大型表格的文档
- 处理财务报告、数据表格或结构化文档
- 您希望在单个视图中获得完整的表格上下文
- 使用 VLM 进行表格提取（合并的表格提供更好的上下文）

在以下情况下考虑禁用：

- 表格在页面之间是故意分开的
- 处理速度至关重要（会增加少量开销）
- 文档结构不一致

## 何时使用

在以下情况下使用 `EnhancedPDFParser`：

- 扫描文档
- 低质量 PDF
- 有视觉失真的文档
- 使用标准解析器时 OCR 准确性差

## 另请参阅

- [DocRes 引擎](../engines/docres-engine.md) - 图像恢复详情
- [结构化解析器](structured-parser.md) - 带分割表格合并详情的基础解析器
- [分割表格合并指南](../features/split-table-merging.md) - 分割表格检测的综合指南
- [API 参考](../../api/parsers.md) - 完整 API 文档

