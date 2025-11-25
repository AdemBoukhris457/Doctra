# 导出器 API 参考

Doctra 导出功能的文档。

## 概述

导出器负责将解析的文档内容转换为各种输出格式。

## 可用的导出器

### MarkdownWriter

生成带嵌入图像的人类可读 Markdown 文件。

### HTMLWriter

生成用于 Web 查看的样式化 HTML 文档。

### ExcelWriter

从表格和图表创建包含结构化数据的 Excel 电子表格。

### ImageSaver

保存视觉元素（图形、图表、表格）的裁剪图像。

## 用法

导出器由解析器自动使用。输出格式由解析器配置确定。

### 输出文件

```
outputs/
└── document/
    ├── result.md          # MarkdownWriter
    ├── result.html        # HTMLWriter
    ├── tables.xlsx        # ExcelWriter（使用 VLM）
    ├── tables.html        # HTMLWriter（使用 VLM）
    └── images/            # ImageSaver
        ├── figures/
        ├── charts/
        └── tables/
```

## 另请参阅

- [解析器 API](parsers.md) - 主要解析功能
- [导出格式](../user-guide/outputs/export-formats.md) - 详细的格式文档

