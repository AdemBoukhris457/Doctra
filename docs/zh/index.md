# 欢迎使用 Doctra

![Doctra Banner](https://raw.githubusercontent.com/AdemBoukhris457/Doctra/main/assets/Doctra_Banner_MultiDoc.png)

[![PyPI version](https://img.shields.io/pypi/v/doctra)](https://pypi.org/project/doctra/)
[![Python versions](https://img.shields.io/pypi/pyversions/doctra)](https://pypi.org/project/doctra/)
[![GitHub stars](https://img.shields.io/github/stars/AdemBoukhris457/Doctra)](https://github.com/AdemBoukhris457/Doctra)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1Z9UH9r1ZxGHm2cAFVKy7W9cKjcgBDOlG?usp=sharing)
[![License](https://img.shields.io/github/license/AdemBoukhris457/Doctra)](https://github.com/AdemBoukhris457/Doctra/blob/main/LICENSE)

## 概述

**Doctra** 是一个强大的 Python 库，用于解析、提取和分析 PDF 文档内容。它结合了最先进的布局检测、OCR、图像恢复和视觉语言模型（VLM），提供全面的文档处理功能。

## 主要特性

### :material-file-document-outline: 全面的 PDF 解析
- **布局检测**：使用 PaddleOCR 进行高级文档布局分析
- **OCR 处理**：使用 Tesseract 进行高质量文本提取
- **视觉元素**：自动提取图形、图表和表格
- **多种解析器**：为您的用例选择合适的解析器

### :material-image-auto-adjust: 图像恢复
- **6 种恢复任务**：去扭曲、去阴影、外观增强、去模糊、二值化和端到端恢复
- **DocRes 集成**：最先进的文档图像恢复
- **GPU 加速**：自动 CUDA 检测以加快处理速度
- **增强质量**：提高文档质量以获得更好的 OCR 结果

### :material-robot: VLM 集成
- **结构化数据提取**：将图表和表格转换为结构化格式
- **多种提供商**：支持 OpenAI、Gemini、Anthropic 和 OpenRouter
- **自动转换**：将视觉元素转换为可用数据
- **灵活配置**：简单的 API 密钥管理和模型选择

### :material-export: 丰富的输出格式
- **Markdown**：带嵌入图像的人类可读文档
- **Excel**：电子表格格式的结构化数据
- **JSON**：程序可访问的数据
- **HTML**：交互式 Web 就绪文档
- **图像**：高质量的裁剪视觉元素

### :material-application: 用户友好的界面
- **Web UI**：基于 Gradio 的界面，支持拖放
- **命令行**：强大的 CLI 用于自动化
- **Python API**：完整的程序访问
- **实时进度**：跟踪处理状态

## 快速开始

### 安装

```bash
pip install doctra
```

### 基本用法

```python
from doctra import StructuredPDFParser

# 初始化解析器
parser = StructuredPDFParser()

# 解析文档
parser.parse("document.pdf")
```

!!! tip "系统依赖"
    Doctra 需要 Poppler 来处理 PDF。有关详细设置说明，请参阅[安装指南](getting-started/installation.md)。

## 核心组件

### 解析器

| 解析器 | 描述 | 最适合 |
|--------|------|--------|
| **StructuredPDFParser** | 完整的文档处理 | 通用解析 |
| **EnhancedPDFParser** | 带图像恢复的解析 | 扫描或低质量文档 |
| **ChartTablePDFParser** | 专注提取 | 仅需要图表和表格 |
| **PaddleOCRVLPDFParser** | 端到端 VLM 解析 | 包含图表和表格的复杂文档 |

### 引擎

| 引擎 | 描述 | 用例 |
|------|------|------|
| **DocResEngine** | 图像恢复 | 独立图像增强 |
| **Layout Detection** | 文档分析 | 识别文档结构 |
| **OCR Engine** | 文本提取 | 从图像中提取文本 |
| **VLM Service** | AI 处理 | 将视觉元素转换为结构化数据 |

## 用例

- :material-file-chart: **财务报告**：从财务文档中提取表格、图表和文本
- :material-book-open-page-variant: **研究论文**：解析带图形和表格的学术论文
- :material-file-document-multiple: **文档归档**：将扫描文档转换为可搜索格式
- :material-chart-bar: **数据提取**：从视觉元素中提取结构化数据
- :material-file-restore: **文档增强**：恢复和改进低质量文档

## 获取帮助

- :material-file-document: **文档**：您正在阅读它！浏览侧边栏以获取详细指南
- :material-github: **GitHub Issues**：[报告错误或请求功能](https://github.com/AdemBoukhris457/Doctra/issues)
- :material-package: **PyPI**：[查看包详细信息](https://pypi.org/project/doctra/)

## 📓 交互式笔记本

| 笔记本 | Colab 徽章 | 描述 |
|--------|-----------|------|
| **01_doctra_quick_start** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1Z9UH9r1ZxGHm2cAFVKy7W9cKjcgBDOlG?usp=sharing) | 涵盖布局检测、内容提取和多格式输出的综合教程，带视觉示例 |
| **case_study_01_financial_report_analysis** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AdemBoukhris457/Doctra/blob/main/notebooks/case_study_01_financial_report_analysis.ipynb) | 财务报告分析：从 PDF 报告中提取表格和图表，使用 VLM 将视觉元素转换为结构化数据，并使用 pandas 分析财务数据 |
| **case_study_02_scanned_document_restoration** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AdemBoukhris457/Doctra/blob/main/notebooks/case_study_02_scanned_document_restoration.ipynb) | 扫描文档恢复：应用 DocRes 引擎进行图像恢复（外观、去扭曲、去阴影、去模糊、二值化、端到端），恢复 PDF，并比较恢复前后的解析结果 |

## 下一步？

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __快速开始__

    ---

    在几分钟内开始使用 Doctra

    [:octicons-arrow-right-24: 快速开始指南](getting-started/quick-start.md)

-   :material-book-open-variant:{ .lg .middle } __用户指南__

    ---

    了解解析器、引擎和高级功能

    [:octicons-arrow-right-24: 阅读指南](user-guide/core-concepts.md)

-   :material-code-tags:{ .lg .middle } __API 参考__

    ---

    所有组件的详细 API 文档

    [:octicons-arrow-right-24: API 文档](api/parsers.md)

-   :material-lightbulb:{ .lg .middle } __示例__

    ---

    真实世界的示例和集成模式

    [:octicons-arrow-right-24: 查看示例](examples/basic-usage.md)

</div>

## 致谢

Doctra 建立在几个优秀的开源项目之上：

- **[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)** - 高级文档布局检测和 OCR 功能
- **[DocRes](https://github.com/ZZZHANG-jx/DocRes)** - 最先进的文档图像恢复模型
- **[Outlines](https://github.com/dottxt-ai/outlines)** - LLM 的结构化输出生成

我们感谢这些项目的开发者和贡献者的宝贵工作。

## 许可证

Doctra 在 MIT 许可证下发布。有关详细信息，请参阅 [LICENSE](https://github.com/AdemBoukhris457/Doctra/blob/main/LICENSE) 文件。

