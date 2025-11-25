# 布局检测

Doctra 中文档布局检测的指南。

## 概述

布局检测是 Doctra 处理管道的基础。它分析 PDF 页面以识别和分类不同的文档元素（文本、表格、图表、图形）。

## 工作原理

1. **渲染**：PDF 页面在指定 DPI 下转换为图像
2. **检测**：PaddleOCR 模型识别元素区域
3. **分类**：按类型标记元素
4. **过滤**：移除低置信度检测

## 配置

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser(
    layout_model_name="PP-DocLayout_plus-L",
    dpi=200,
    min_score=0.5
)
```

## 参数

**layout_model_name**
:   要使用的 PaddleOCR 模型
    - `PP-DocLayout_plus-L`：最佳准确性（较慢）
    - `PP-DocLayout_plus-M`：更快，良好的准确性

**dpi**
:   图像分辨率
    - 100-150：快速，质量较低
    - 200：平衡（默认）
    - 250-300：高质量，较慢

**min_score**
:   置信度阈值（0-1）
    - 0.0：包含所有检测
    - 0.5：中等过滤
    - 0.7+：保守，仅高置信度

## 可视化

验证检测质量：

```python
parser.display_pages_with_boxes(
    pdf_path="document.pdf",
    num_pages=3
)
```

## 元素类型

- **文本**：常规内容（蓝色框）
- **表格**：表格数据（红色框）
- **图表**：图形和图表（绿色框）
- **图形**：图像和图表（橙色框）

## 另请参阅

- [核心概念](../core-concepts.md) - 了解管道
- [可视化](../outputs/visualization.md) - 布局可视化
- [API 参考](../../api/parsers.md) - 配置选项

