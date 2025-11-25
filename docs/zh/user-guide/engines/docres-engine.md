# DocRes 引擎

使用 DocRes 图像恢复引擎的指南。

## 概述

`DocResEngine` 提供对使用 DocRes 模型的文档图像恢复功能的直接访问。将其用于独立图像增强或作为解析管道的一部分。

## 主要特性

- **6 种恢复任务**：全面的文档增强
- **GPU 加速**：支持 CUDA 以加快处理速度
- **灵活输入**：图像或 PDF
- **详细元数据**：返回处理信息

## 基本用法

```python
from doctra import DocResEngine

# 初始化引擎
engine = DocResEngine(device="cuda")

# 恢复图像
restored_img, metadata = engine.restore_image(
    image="document.jpg",
    task="appearance"
)

# 保存结果
restored_img.save("restored.jpg")
```

## 恢复任务

| 任务 | 描述 | 用例 |
|------|------|------|
| `appearance` | 一般增强 | 大多数文档 |
| `dewarping` | 修复透视 | 倾斜扫描 |
| `deshadowing` | 去除阴影 | 光照条件差 |
| `deblurring` | 减少模糊 | 运动/对焦问题 |
| `binarization` | 黑白转换 | 干净文本 |
| `end2end` | 完整流程 | 严重退化 |

## PDF 恢复

```python
engine = DocResEngine(device="cuda")

restored_pdf = engine.restore_pdf(
    pdf_path="low_quality.pdf",
    output_path="enhanced.pdf",
    task="appearance",
    dpi=300
)
```

## 另请参阅

- [增强解析器](../parsers/enhanced-parser.md) - 集成恢复
- [API 参考](../../api/engines.md) - 完整 API 文档
- [核心概念](../core-concepts.md) - 了解恢复

