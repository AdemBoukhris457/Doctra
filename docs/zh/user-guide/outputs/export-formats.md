# 导出格式

Doctra 输出格式指南。

## 概述

Doctra 同时生成多种输出格式，每种格式针对不同的用例进行了优化。

## 可用格式

### Markdown (.md)

人类可读的文档，包含：

- 所有文本内容
- 嵌入的图像引用
- 表格链接
- 章节结构

**最适合**：文档、版本控制、阅读

**示例**：
```markdown
# 文档标题

## 第 1 节

文本内容...

![图 1](images/figures/figure_001.jpg)

请参阅 [tables.xlsx](tables.xlsx) 中的表格
```

### HTML (.html)

Web 就绪的文档，包含：

- 样式化内容
- 嵌入的图像
- 交互式表格
- 响应式布局

**最适合**：Web 发布、演示

### Excel (.xlsx)

包含提取数据的电子表格：

- 每个表格一个工作表
- 格式化的单元格
- 保留的标题
- 结构化数据

**最适合**：数据分析、进一步处理

*仅在启用 VLM 时生成*

### JSON (.json)

结构化数据，包含：

- 元素元数据
- 坐标
- 内容
- 关系

**最适合**：程序化访问、集成

*仅在启用 VLM 时生成*

### 图像

裁剪的视觉元素：

- `figures/`：文档图像
- `charts/`：图形和图表
- `tables/`：表格图像

**格式**：JPEG 或 PNG
**最适合**：直接使用、演示

## 输出结构

```
outputs/
└── document/
    └── full_parse/
        ├── result.md          # Markdown
        ├── result.html        # HTML
        ├── tables.xlsx        # Excel (VLM)
        ├── tables.html        # HTML 表格 (VLM)
        ├── vlm_items.json     # JSON 数据 (VLM)
        └── images/
            ├── figures/
            ├── charts/
            └── tables/
```

## 选择格式

| 用例 | 推荐格式 |
|------|----------|
| 阅读 | Markdown 或 HTML |
| 数据分析 | Excel |
| Web 发布 | HTML |
| 集成 | JSON |
| 演示 | 图像 + HTML |
| 版本控制 | Markdown |

## 另请参阅

- [可视化](visualization.md) - 视觉输出
- [示例](../../examples/basic-usage.md) - 使用示例
- [API 参考](../../api/exporters.md) - 导出器文档

