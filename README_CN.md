# 🚀 **Doctra - 文档解析库** 📑🔎

![Doctra Logo](https://raw.githubusercontent.com/AdemBoukhris457/Doctra/main/assets/Doctra_Banner_MultiDoc.png)

<div align="center">

[English](README.md) | [中文](README_CN.md)

</div>

<div align="center">

[![stars](https://img.shields.io/github/stars/AdemBoukhris457/Doctra.svg)](https://github.com/AdemBoukhris457/Doctra)
[![forks](https://img.shields.io/github/forks/AdemBoukhris457/Doctra.svg)](https://github.com/AdemBoukhris457/Doctra)
[![PyPI version](https://img.shields.io/pypi/v/doctra)](https://pypi.org/project/doctra/)
[![Documentation](https://img.shields.io/badge/documentation-available-success)](https://ademboukhris457.github.io/Doctra/index.html)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1Z9UH9r1ZxGHm2cAFVKy7W9cKjcgBDOlG?usp=sharing)
[![Hugging Face Spaces](https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/DaVinciCode/doctra-document-parser)
</div>

## 📋 目录

- [安装](#🛠️-安装)
- [快速开始](#⚡-快速开始)
- [核心组件](#🔧-核心组件)
  - [StructuredPDFParser](#structuredpdfparser)
  - [EnhancedPDFParser](#enhancedpdfparser)
  - [ChartTablePDFParser](#charttablepdfparser)
  - [PaddleOCRVLPDFParser](#paddleocrvlpdfparser)
  - [StructuredDOCXParser](#structureddocxparser)
  - [DocResEngine](#docresengine)
- [Web UI (Gradio)](#🖥️-web-ui-gradio)
- [命令行界面](#命令行界面)
- [可视化](#🎨-可视化)
- [使用示例](#📖-使用示例)
- [功能特性](#✨-功能特性)

## 🛠️ 安装

### 从 PyPI 安装（推荐）

```bash
pip install doctra
```

### 从源码安装

```bash
git clone https://github.com/AdemBoukhris457/Doctra.git
cd Doctra
pip install .
```

### 系统依赖

Doctra 需要 **Poppler** 来处理 PDF 文件。根据您的操作系统安装：

#### Ubuntu/Debian
```bash
sudo apt install poppler-utils
```

#### macOS
```bash
brew install poppler
```

#### Windows
从 [Poppler for Windows](https://poppler.freedesktop.org/) 下载并安装，或使用 conda：
```bash
conda install -c conda-forge poppler
```

#### Google Colab
```bash
!sudo apt install poppler-utils
```

## ⚡ 快速开始

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser

# 初始化解析器
parser = StructuredPDFParser()

# 解析 PDF 文档
parser.parse("path/to/your/document.pdf")
```

## 🔧 核心组件

### StructuredPDFParser

`StructuredPDFParser` 是一个全面的 PDF 解析器，可以从 PDF 文档中提取所有类型的内容。它通过布局检测处理 PDF，使用 OCR 提取文本，保存图像以获取视觉元素，并可选择使用视觉语言模型（VLM）将图表/表格转换为结构化数据。

#### 主要特性：
- **布局检测**：使用 PaddleOCR 进行准确的文档布局分析
- **OCR 处理**：支持 PyTesseract（默认）和 PaddleOCR PP-OCRv5_server 进行文本提取
- **视觉元素提取**：将图形、图表和表格保存为图像
- **VLM 集成**：可选择将视觉元素转换为结构化数据
- **多种输出格式**：生成 Markdown、Excel 和结构化 JSON

#### 基本用法：

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser

# 不带 VLM 的基本解析器（使用默认的 PyTesseract OCR 引擎）
parser = StructuredPDFParser()

# 带 VLM 的解析器，用于结构化数据提取
from doctra.engines.vlm.service import VLMStructuredExtractor

# 初始化 VLM 引擎
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",  # 或 "gemini", "anthropic", "openrouter", "qianfan", "ollama"
    api_key="your_api_key_here"
)

# 将 VLM 引擎传递给解析器
parser = StructuredPDFParser(vlm=vlm_engine)

# 解析文档
parser.parse("document.pdf")
```

#### OCR 引擎配置：

Doctra 使用依赖注入模式来处理 OCR 引擎。您需要在外部初始化 OCR 引擎，然后将其传递给解析器：

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser
from doctra.engines.ocr import PytesseractOCREngine, PaddleOCREngine

# 选项 1：使用默认的 PyTesseract（如果 ocr_engine=None 则自动创建）
parser = StructuredPDFParser()  # 内部创建默认的 PyTesseractOCREngine

# 选项 2：显式配置 PyTesseract
tesseract_ocr = PytesseractOCREngine(
    lang="eng",      # 语言代码
    psm=4,           # 页面分割模式
    oem=3,           # OCR 引擎模式
    extra_config=""  # 额外的 Tesseract 配置
)
parser = StructuredPDFParser(ocr_engine=tesseract_ocr)

# 选项 3：使用 PaddleOCR 以获得更好的准确性
paddle_ocr = PaddleOCREngine(
    device="gpu",                          # "gpu" 或 "cpu"
    use_doc_orientation_classify=False,    # 文档方向检测
    use_doc_unwarping=False,              # 文本图像校正
    use_textline_orientation=False        # 文本行方向
)
parser = StructuredPDFParser(ocr_engine=paddle_ocr)

# 选项 4：在多个解析器之间重用 OCR 引擎
shared_ocr = PytesseractOCREngine(lang="eng", psm=6, oem=3)
parser1 = StructuredPDFParser(ocr_engine=shared_ocr)
parser2 = EnhancedPDFParser(ocr_engine=shared_ocr)  # 重用同一实例
```

#### VLM 引擎配置：

Doctra 对 VLM 引擎使用相同的依赖注入模式。您需要在外部初始化 VLM 引擎，然后将其传递给解析器：

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

# 选项 1：不使用 VLM（默认）
parser = StructuredPDFParser()  # VLM 处理已禁用

# 选项 2：初始化 VLM 引擎并传递给解析器
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",  # 或 "gemini", "anthropic", "openrouter", "qianfan", "ollama"
    vlm_model="gpt-5",      # 可选，如果为 None 则使用默认值
    api_key="your_api_key"
)
parser = StructuredPDFParser(vlm=vlm_engine)

# 选项 3：在多个解析器之间重用 VLM 引擎
shared_vlm = VLMStructuredExtractor(
    vlm_provider="gemini",
    api_key="your_api_key"
)
parser1 = StructuredPDFParser(vlm=shared_vlm)
parser2 = EnhancedPDFParser(vlm=shared_vlm)  # 重用同一实例
parser3 = ChartTablePDFParser(vlm=shared_vlm)  # 重用同一实例
```

#### 高级配置：

```python
from doctra.engines.ocr import PytesseractOCREngine, PaddleOCREngine

# 选项 1：使用 PyTesseract（默认）
ocr_engine = PytesseractOCREngine(
    lang="eng",
    psm=4,
    oem=3,
    extra_config=""
)

# 初始化 VLM 引擎
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    vlm_model="gpt-5",  # 可选，如果为 None 则使用默认值
    api_key="your_api_key"
)

parser = StructuredPDFParser(
    # VLM 引擎（传递初始化的引擎）
    vlm=vlm_engine,  # 或 None 以禁用 VLM
    
    # 布局检测设置
    layout_model_name="PP-DocLayout_plus-L",
    dpi=200,
    min_score=0.0,
    
    # OCR 引擎（传递初始化的引擎）
    ocr_engine=ocr_engine,  # 或 None 使用默认的 PyTesseract
    
    # 输出设置
    box_separator="\n"
)

# 选项 2：使用 PaddleOCR 以获得更好的准确性
paddle_ocr = PaddleOCREngine(
    device="gpu",  # 如果没有 GPU 则使用 "cpu"
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

parser = StructuredPDFParser(
    ocr_engine=paddle_ocr,
    # ... 其他设置
)
```

### EnhancedPDFParser

`EnhancedPDFParser` 扩展了 `StructuredPDFParser`，使用 DocRes 提供高级图像恢复功能。此解析器非常适合处理扫描文档、低质量 PDF 或需要在解析前进行增强的视觉失真文档。

#### 主要特性：
- **图像恢复**：在处理前使用 DocRes 进行文档增强
- **多种恢复任务**：支持去扭曲、去阴影、外观增强、去模糊、二值化和端到端恢复
- **增强质量**：提高文档质量以获得更好的 OCR 和布局检测
- **所有 StructuredPDFParser 功能**：继承基础解析器的所有功能
- **灵活配置**：广泛的恢复和处理选项

#### 基本用法：

```python
from doctra.parsers.enhanced_pdf_parser import EnhancedPDFParser

# 带图像恢复的基本增强解析器
parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="appearance"  # 默认恢复任务
)

# 使用增强功能解析文档
parser.parse("scanned_document.pdf")
```

#### 高级配置：

```python
from doctra.engines.ocr import PytesseractOCREngine, PaddleOCREngine

# 初始化 OCR 引擎（PyTesseract 或 PaddleOCR）
ocr_engine = PytesseractOCREngine(
    lang="eng",
    psm=6,
    oem=3
)

# 初始化 VLM 引擎
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    vlm_model="gpt-4-vision",  # 可选，如果为 None 则使用默认值
    api_key="your_api_key"
)

parser = EnhancedPDFParser(
    # 图像恢复设置
    use_image_restoration=True,
    restoration_task="dewarping",      # 校正透视失真
    restoration_device="cuda",         # 使用 GPU 以加快处理速度
    restoration_dpi=300,               # 更高的 DPI 以获得更好的质量
    
    # VLM 引擎（传递初始化的引擎）
    vlm=vlm_engine,  # 或 None 以禁用 VLM
    
    # 布局检测设置
    layout_model_name="PP-DocLayout_plus-L",
    dpi=200,
    min_score=0.5,
    
    # OCR 引擎（传递初始化的引擎）
    ocr_engine=ocr_engine,  # 或 None 使用默认的 PyTesseract
)
```

#### DocRes 恢复任务：

| 任务 | 描述 | 最适合 |
|------|------|--------|
| `appearance` | 一般外观增强 | 大多数文档（默认） |
| `dewarping` | 校正透视失真 | 有透视问题的扫描文档 |
| `deshadowing` | 去除阴影和光照伪影 | 有阴影问题的文档 |
| `deblurring` | 减少模糊并提高清晰度 | 模糊或低质量扫描 |
| `binarization` | 转换为黑白 | 需要干净二值化的文档 |
| `end2end` | 完整的恢复流程 | 严重退化的文档 |

### ChartTablePDFParser

`ChartTablePDFParser` 是一个专门用于从 PDF 文档中提取图表和表格的解析器。它针对只需要这些特定元素的场景进行了优化，提供更快的处理和更有针对性的输出。

#### 主要特性：
- **专注提取**：仅提取图表和/或表格
- **选择性处理**：选择提取图表、表格或两者
- **VLM 集成**：可选择转换为结构化数据
- **有序输出**：图表和表格的独立目录
- **进度跟踪**：提取的实时进度条

#### 基本用法：

```python
from doctra.parsers.table_chart_extractor import ChartTablePDFParser

# 提取图表和表格
parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=True
)

# 仅提取图表
parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=False
)

# 使用自定义输出目录解析
parser.parse("document.pdf", output_base_dir="my_outputs")
```

#### 高级配置：

```python
# 初始化 VLM 引擎
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    vlm_model="gpt-5",  # 可选，如果为 None 则使用默认值
    api_key="your_api_key"
)

parser = ChartTablePDFParser(
    # 提取设置
    extract_charts=True,
    extract_tables=True,
    
    # VLM 引擎（传递初始化的引擎）
    vlm=vlm_engine,  # 或 None 以禁用 VLM
    
    # 布局检测设置
    layout_model_name="PP-DocLayout_plus-L",
    dpi=200,
    min_score=0.0
)
```

### PaddleOCRVLPDFParser

`PaddleOCRVLPDFParser` 使用 PaddleOCRVL（视觉语言模型）进行端到端文档解析。它将 PaddleOCRVL 的高级文档理解能力与 DocRes 图像恢复和分割表格合并相结合，为复杂文档处理提供全面的解决方案。

#### 安装要求

在使用 `PaddleOCRVLPDFParser` 之前，请安装所需的依赖项：

```bash
pip install -U "paddleocr[doc-parser]"
```

**对于 Linux 系统：**
```bash
python -m pip install https://paddle-whl.bj.bcebos.com/nightly/cu126/safetensors/safetensors-0.6.2.dev0-cp38-abi3-linux_x86_64.whl
```

**对于 Windows 系统：**
```bash
python -m pip install https://xly-devops.cdn.bcebos.com/safetensors-nightly/safetensors-0.6.2.dev0-cp38-abi3-win_amd64.whl
```

#### 主要特性：
- **端到端解析**：使用 PaddleOCRVL 在单次处理中完成文档理解
- **图表识别**：自动提取图表并转换为结构化表格格式
- **文档恢复**：可选的 DocRes 集成以增强文档质量
- **分割表格合并**：自动检测并合并跨页分割的表格
- **结构化输出**：生成包含表格和图表的 Markdown、HTML 和 Excel 文件
- **多种元素类型**：处理标题、文本、表格、图表、脚注等

#### 基本用法：

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

#### 高级配置：

```python
from doctra import PaddleOCRVLPDFParser

parser = PaddleOCRVLPDFParser(
    # DocRes 图像恢复设置
    use_image_restoration=True,
    restoration_task="appearance",    # 选项：appearance, dewarping, deshadowing, deblurring, binarization, end2end
    restoration_device="cuda",        # 或 "cpu" 或 None 自动检测
    restoration_dpi=300,              # 恢复处理的 DPI
    
    # PaddleOCRVL 设置
    use_chart_recognition=True,       # 启用图表识别和提取
    use_doc_orientation_classify=True, # 启用文档方向分类
    use_doc_unwarping=True,           # 启用文档去扭曲
    use_layout_detection=True,        # 启用布局检测
    device="gpu",                     # "gpu" 或 "cpu"
    
    # 分割表格合并设置
    merge_split_tables=True,          # 启用分割表格检测和合并
    bottom_threshold_ratio=0.20,      # "太接近底部"检测的比率
    top_threshold_ratio=0.15,         # "太接近顶部"检测的比率
    max_gap_ratio=0.25,               # 表格之间的最大允许间隙
    column_alignment_tolerance=10.0,  # 列对齐的像素容差
    min_merge_confidence=0.65         # 合并的最小置信度分数
)

# 使用自定义输出目录解析
parser.parse("document.pdf", output_dir="custom_output")
```

#### 输出结构：

解析器在 `outputs/{document_name}/paddleocr_vl_parse/` 中生成输出，包含：
- **result.md**：包含所有提取内容的 Markdown 文件
- **result.html**：格式化的 HTML 文件
- **tables.xlsx**：包含所有表格和图表作为结构化数据的 Excel 文件
- **tables.html**：包含结构化表格和图表的 HTML 文件
- **enhanced_pages/**：包含 DocRes 增强页面图像的目录（如果启用了恢复）
- **tables/**：包含合并表格图像的目录（如果检测到分割表格）

#### 示例输出：

解析器提取各种文档元素：
- **标题**：文档标题和章节标题
- **文本**：段落和正文
- **表格**：提取为 HTML 并转换为 Excel 格式
- **图表**：从视觉格式转换为结构化表格数据
- **脚注**：基于视觉的脚注检测
- **图形标题**：标题和图例描述

### StructuredDOCXParser

`StructuredDOCXParser` 是一个全面的 Microsoft Word 文档（.docx 文件）解析器，可提取文本、表格、图像和结构化内容，同时保留文档格式和顺序。它支持 VLM 集成以进行增强的内容分析和结构化数据提取。

#### 主要特性：
- **完整的 DOCX 支持**：从 Word 文档中提取文本、表格、图像和格式
- **文档顺序保留**：保持元素的原始顺序（段落、表格、图像）
- **VLM 集成**：可选的视觉语言模型支持，用于图像分析和表格提取
- **多种输出格式**：生成 Markdown、HTML 和 Excel 文件
- **Excel 导出**：创建包含目录和可点击超链接的结构化 Excel 文件
- **格式保留**：在输出中保持文本格式（粗体、斜体等）
- **进度跟踪**：VLM 处理的实时进度条

#### 基本用法：

```python
from doctra.parsers.structured_docx_parser import StructuredDOCXParser

# 基本 DOCX 解析
parser = StructuredDOCXParser(
    extract_images=True,
    preserve_formatting=True,
    table_detection=True,
    export_excel=True
)

# 解析 DOCX 文档
parser.parse("document.docx")
```

#### 使用 VLM 的高级配置：

```python
# 初始化 VLM 引擎
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",  # 或 "gemini", "anthropic", "openrouter", "qianfan", "ollama"
    vlm_model="gpt-4-vision",  # 可选，如果为 None 则使用默认值
    api_key="your_api_key"
)

parser = StructuredDOCXParser(
    # VLM 引擎（传递初始化的引擎）
    vlm=vlm_engine,  # 或 None 以禁用 VLM
    
    # 处理选项
    extract_images=True,
    preserve_formatting=True,
    table_detection=True,
    export_excel=True
)

# 使用 VLM 增强解析
parser.parse("document.docx")
```

#### 输出结构：

解析 DOCX 文档时，解析器会创建：

```
outputs/document_name/
├── document.md          # 包含所有内容的 Markdown 版本
├── document.html        # 带样式的 HTML 版本
├── tables.xlsx         # 包含提取表格的 Excel 文件
│   ├── Table of Contents  # 带超链接的摘要表
│   ├── Table 1         # 单个表格工作表
│   ├── Table 2
│   └── ...
└── images/             # 提取的图像
    ├── image1.png
    ├── image2.jpg
    └── ...
```

#### VLM 集成功能：

启用 VLM 时，解析器会：
- **分析图像**：使用 AI 从图像中提取结构化数据
- **创建表格**：将图表图像转换为结构化表格数据
- **增强 Excel 输出**：在 Excel 文件中包含 VLM 提取的表格
- **智能内容显示**：在 Markdown/HTML 中显示提取的表格而不是图像
- **进度跟踪**：根据处理的图像数量显示进度

#### CLI 用法：

```bash
# 基本 DOCX 解析
doctra parse-docx document.docx

# 使用 VLM 增强
doctra parse-docx document.docx --use-vlm --vlm-provider openai --vlm-api-key your_key

# 自定义选项
doctra parse-docx document.docx \
  --extract-images \
  --preserve-formatting \
  --table-detection \
  --export-excel
```

### DocResEngine

`DocResEngine` 提供对 DocRes 图像恢复功能的直接访问。此引擎非常适合独立的图像恢复任务或当您需要对恢复过程进行细粒度控制时。

#### 主要特性：
- **直接图像恢复**：处理单个图像或整个 PDF
- **多种恢复任务**：所有 6 种 DocRes 恢复任务可用
- **GPU 加速**：自动 CUDA 检测和优化
- **灵活的输入/输出**：支持各种图像格式和 PDF
- **元数据提取**：获取恢复过程的详细信息

#### 基本用法：

```python
from doctra.engines.image_restoration import DocResEngine

# 初始化 DocRes 引擎
docres = DocResEngine(device="cuda")  # 或 "cpu" 或 None 自动检测

# 恢复单个图像
restored_img, metadata = docres.restore_image(
    image="path/to/image.jpg",
    task="appearance"
)

# 恢复整个 PDF
enhanced_pdf = docres.restore_pdf(
    pdf_path="document.pdf",
    output_path="enhanced_document.pdf",
    task="appearance"
)
```

#### 高级用法：

```python
# 使用自定义设置初始化
docres = DocResEngine(
    device="cuda",                    # 强制使用 GPU
    use_half_precision=True,         # 使用半精度以加快处理速度
    model_path="custom/model.pth",    # 自定义模型路径（可选）
    mbd_path="custom/mbd.pth"        # 自定义 MBD 模型路径（可选）
)

# 处理多个图像
images = ["doc1.jpg", "doc2.jpg", "doc3.jpg"]
for img_path in images:
    restored_img, metadata = docres.restore_image(
        image=img_path,
        task="dewarping"
    )
    print(f"已处理 {img_path}: {metadata}")

# 批量 PDF 处理
pdfs = ["report1.pdf", "report2.pdf"]
for pdf_path in pdfs:
    output_path = f"enhanced_{os.path.basename(pdf_path)}"
    docres.restore_pdf(
        pdf_path=pdf_path,
        output_path=output_path,
        task="end2end"  # 完整的恢复流程
    )
```

#### 支持的恢复任务：

| 任务 | 描述 | 用例 |
|------|------|------|
| `appearance` | 一般外观增强 | 大多数文档的默认选择 |
| `dewarping` | 校正文档透视失真 | 有透视问题的扫描文档 |
| `deshadowing` | 去除阴影和光照伪影 | 有阴影问题的文档 |
| `deblurring` | 减少模糊并提高清晰度 | 模糊或低质量扫描 |
| `binarization` | 转换为黑白 | 需要干净二值化的文档 |
| `end2end` | 完整的恢复流程 | 严重退化的文档 |

## 🖥️ Web UI (Gradio)

Doctra 提供了一个使用 Gradio 构建的全面 Web 界面，使非技术用户也能进行文档处理。

#### 功能：
- **拖放界面**：通过拖放上传 PDF
- **多种解析器**：在完整解析、增强解析和图表/表格提取之间选择
- **实时处理**：在处理文档时查看进度
- **VLM 集成**：配置 AI 功能的 API 密钥
- **输出预览**：直接在浏览器中查看结果
- **下载结果**：将处理后的文件下载为 ZIP 存档

#### 启动 Web UI：

```python
from doctra.ui.app import launch_ui

# 启动 Web 界面
launch_ui()
```

或从命令行：
```bash
python gradio_app.py
```

#### Web UI 组件：

1. **完整解析标签页**：完整的文档处理，带页面导航
2. **DOCX 解析器标签页**：带 VLM 集成的 Microsoft Word 文档解析
3. **表格和图表标签页**：带 VLM 集成的专业提取
4. **DocRes 标签页**：图像恢复，带前后对比
5. **增强解析器标签页**：带 DocRes 集成的增强解析

## 命令行界面

Doctra 包含一个强大的 CLI，用于批量处理和自动化。

#### 可用命令：

```bash
# 完整文档解析
doctra parse document.pdf

# DOCX 文档解析
doctra parse-docx document.docx

# 带图像恢复的增强解析
doctra enhance document.pdf --restoration-task appearance

# 仅提取图表和表格
doctra extract charts document.pdf
doctra extract tables document.pdf
doctra extract both document.pdf --use-vlm

# 可视化布局检测
doctra visualize document.pdf

# 快速文档分析
doctra analyze document.pdf

# 系统信息
doctra info
```

#### CLI 示例：

```bash
# 带自定义设置的增强解析
doctra enhance document.pdf \
  --restoration-task dewarping \
  --restoration-device cuda \
  --use-vlm \
  --vlm-provider openai \
  --vlm-api-key your_key

# 使用 VLM 提取图表
doctra extract charts document.pdf \
  --use-vlm \
  --vlm-provider gemini \
  --vlm-api-key your_key

# 批量处理
doctra parse *.pdf --output-dir results/
```

## 🎨 可视化

Doctra 提供强大的可视化功能，帮助您了解布局检测的工作原理并验证元素提取的准确性。

### 布局检测可视化

`StructuredPDFParser` 包含一个内置的可视化方法，显示带有在检测到的元素上叠加的边界框的 PDF 页面。这对于以下情况非常有用：

- **调试**：验证布局检测是否正常工作
- **质量保证**：检查元素识别的准确性
- **文档**：创建提取结果的可视化文档
- **分析**：了解文档结构和布局模式

#### 基本可视化：

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser

# 初始化解析器（OCR 引擎对于可视化是可选的）
parser = StructuredPDFParser()

# 显示可视化（在默认图像查看器中打开）
parser.display_pages_with_boxes("document.pdf")
```

#### 带自定义设置的高级可视化：

```python
# 自定义可视化配置
parser.display_pages_with_boxes(
    pdf_path="document.pdf",
    num_pages=5,        # 要可视化的页数
    cols=3,             # 网格中的列数
    page_width=600,     # 每页的宽度（像素）
    spacing=30,         # 页面之间的间距
    save_path="layout_visualization.png"  # 保存到文件而不是显示
)
```

#### 可视化功能：

- **颜色编码的元素**：每种元素类型（文本、表格、图表、图形）都有不同的颜色
- **置信度分数**：显示每个元素的检测置信度
- **网格布局**：在有序网格中显示多个页面
- **交互式图例**：显示所有检测到的元素类型的颜色图例
- **高质量**：适合文档的高分辨率输出
- **灵活输出**：在屏幕上显示或保存到文件

#### 示例输出：

可视化显示：
- **蓝色框**：文本元素
- **红色框**：表格
- **绿色框**：图表
- **橙色框**：图形
- **标签**：元素类型和置信度分数（例如，"table (0.95)"）
- **页面标题**：页码和元素计数
- **摘要统计**：按类型检测到的总元素

### 可视化用例：

1. **文档分析**：快速评估文档结构和复杂性
2. **质量控制**：在处理前验证提取准确性
3. **调试**：识别布局检测的问题
4. **文档**：创建提取结果的可视化报告
5. **培训**：帮助用户了解系统的工作原理

### 可视化配置选项：

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `num_pages` | 3 | 要可视化的页数 |
| `cols` | 2 | 网格布局中的列数 |
| `page_width` | 800 | 每页的宽度（像素） |
| `spacing` | 40 | 页面之间的间距（像素） |
| `save_path` | None | 保存可视化的路径（如果为 None，则在屏幕上显示） |

## 📓 交互式笔记本

| 笔记本 | Colab 徽章 | 描述 |
|--------|-----------|------|
| **01_doctra_quick_start** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1Z9UH9r1ZxGHm2cAFVKy7W9cKjcgBDOlG?usp=sharing) | 涵盖布局检测、内容提取和多格式输出的综合教程，带视觉示例 |

## 📖 使用示例

### 示例 1：基本文档处理

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser

# 初始化解析器（使用默认的 PyTesseract OCR 引擎）
parser = StructuredPDFParser()

# 处理文档
parser.parse("financial_report.pdf")

# 输出将保存到：outputs/financial_report/
# - 提取的文本内容
# - 图形、图表和表格的裁剪图像
# - 包含所有内容的 Markdown 文件
```

### 示例 2：带图像恢复的增强解析

```python
from doctra.parsers.enhanced_pdf_parser import EnhancedPDFParser
from doctra.engines.ocr import PytesseractOCREngine

# 初始化 OCR 引擎（可选 - 如果不提供则默认为 PyTesseract）
ocr_engine = PytesseractOCREngine(lang="eng", psm=4, oem=3)

# 初始化 VLM 引擎
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your_api_key"
)

# 初始化带图像恢复的增强解析器
parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="dewarping",  # 校正透视失真
    restoration_device="cuda",    # 使用 GPU 以加快处理速度
    ocr_engine=ocr_engine,        # 传递 OCR 引擎实例
    vlm=vlm_engine                # 传递 VLM 引擎实例
)

# 使用增强功能处理扫描文档
parser.parse("scanned_document.pdf")

# 输出将包括：
# - 带恢复图像的增强 PDF
# - 所有标准解析输出
# - 由于恢复而提高的 OCR 准确性
```

### 示例 2b：使用 PaddleOCR 以获得更好的准确性

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser
from doctra.engines.ocr import PaddleOCREngine

# 使用自定义设置初始化 PaddleOCR 引擎
paddle_ocr = PaddleOCREngine(
    device="gpu",  # 如果没有 GPU 则使用 "cpu"
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

# 使用 PaddleOCR 引擎创建解析器
parser = StructuredPDFParser(
    ocr_engine=paddle_ocr
)

# 使用 PaddleOCR 处理文档
parser.parse("complex_document.pdf")

# PaddleOCR 提供：
# - 对复杂文档的更高准确性
# - 在 GPU 上更好的性能
# - 自动模型管理
```

### 示例 3：直接图像恢复

```python
from doctra.engines.image_restoration import DocResEngine

# 初始化 DocRes 引擎
docres = DocResEngine(device="cuda")

# 恢复单个图像
restored_img, metadata = docres.restore_image(
    image="blurry_document.jpg",
    task="deblurring"
)

# 恢复整个 PDF
docres.restore_pdf(
    pdf_path="low_quality.pdf",
    output_path="enhanced.pdf",
    task="appearance"
)
```

### 示例 4：DOCX 文档解析

```python
from doctra.parsers.structured_docx_parser import StructuredDOCXParser

# 基本 DOCX 解析
parser = StructuredDOCXParser(
    extract_images=True,
    preserve_formatting=True,
    table_detection=True,
    export_excel=True
)

# 解析 Word 文档
parser.parse("report.docx")

# 输出将包括：
# - 包含所有内容的 Markdown 文件
# - 带样式的 HTML 文件
# - 包含提取表格的 Excel 文件
# - 在有序文件夹中提取的图像
```

### 示例 5：带 VLM 增强的 DOCX 解析

```python
from doctra.parsers.structured_docx_parser import StructuredDOCXParser

# 初始化 VLM 引擎
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    vlm_model="gpt-4-vision",  # 可选，如果为 None 则使用默认值
    api_key="your_api_key"
)

# 带 VLM 的 DOCX 解析以进行增强分析
parser = StructuredDOCXParser(
    vlm=vlm_engine,  # 传递 VLM 引擎实例
    extract_images=True,
    preserve_formatting=True,
    table_detection=True,
    export_excel=True
)

# 使用 AI 增强解析
parser.parse("financial_report.docx")

# 输出将包括：
# - 所有标准输出
# - 从图像中 VLM 提取的表格
# - 带目录的增强 Excel
# - 智能内容显示（表格而不是图像）
```

### 示例 6：PaddleOCRVL 端到端解析

```python
from doctra import PaddleOCRVLPDFParser

# 初始化启用所有功能的 PaddleOCRVL 解析器
parser = PaddleOCRVLPDFParser(
    use_image_restoration=True,      # 启用 DocRes 恢复
    restoration_task="appearance",    # 使用外观增强
    use_chart_recognition=True,       # 启用图表识别
    merge_split_tables=True,          # 启用分割表格合并
    device="gpu"                      # 使用 GPU 以加快处理速度
)

# 解析文档 - 自动处理所有内容类型
parser.parse("financial_report.pdf")

# 输出将在：outputs/financial_report/paddleocr_vl_parse/
# - result.md：所有内容的 Markdown
# - result.html：格式化的 HTML 输出
# - tables.xlsx：Excel 格式的所有表格和图表
# - tables.html：结构化表格和图表
```

### 示例 7：使用 VLM 的图表和表格提取

```python
from doctra.parsers.table_chart_extractor import ChartTablePDFParser

# 初始化 VLM 引擎
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your_api_key"
)

# 使用 VLM 初始化解析器
parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=True,
    vlm=vlm_engine  # 传递 VLM 引擎实例
)

# 处理文档
parser.parse("data_report.pdf", output_base_dir="extracted_data")

# 输出将包括：
# - 裁剪的图表和表格图像
# - Excel 格式的结构化数据
# - 带提取数据的 Markdown 表格
```

### 示例 8：Web UI 用法

```python
from doctra.ui.app import launch_ui

# 启动 Web 界面
launch_ui()

# 或以编程方式构建界面
from doctra.ui.app import build_demo
demo = build_demo()
demo.launch(share=True)  # 公开分享
```

### 示例 9：命令行用法

```bash
# 使用 VLM 的 DOCX 解析
doctra parse-docx document.docx \
  --use-vlm \
  --vlm-provider openai \
  --vlm-api-key your_key \
  --extract-images \
  --export-excel

# 带自定义设置的增强解析
doctra enhance document.pdf \
  --restoration-task dewarping \
  --restoration-device cuda \
  --use-vlm \
  --vlm-provider openai \
  --vlm-api-key your_key

# 使用 VLM 提取图表
doctra extract charts document.pdf \
  --use-vlm \
  --vlm-provider gemini \
  --vlm-api-key your_key

# 批量处理
doctra parse *.pdf --output-dir results/
```

### 示例 10：布局可视化

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser

# 初始化解析器（可视化不需要 OCR 引擎）
parser = StructuredPDFParser()

# 创建全面的可视化
parser.display_pages_with_boxes(
    pdf_path="research_paper.pdf",
    num_pages=6,        # 可视化前 6 页
    cols=2,             # 2 列布局
    page_width=700,     # 更大的页面以获得更好的细节
    spacing=50,         # 页面之间更多的间距
    save_path="research_paper_layout.png"  # 保存用于文档
)

# 快速预览（在屏幕上显示）
parser.display_pages_with_boxes("document.pdf")
```

## ✨ 功能特性

### 🔍 布局检测
- 使用 PaddleOCR 进行高级文档布局分析
- 准确识别文本、表格、图表和图形
- 可配置的置信度阈值

### 📝 OCR 处理
- **双 OCR 引擎支持**：在 PyTesseract（默认）或 PaddleOCR PP-OCRv5_server 之间选择
- **依赖注入模式**：在外部初始化 OCR 引擎并将其传递给解析器，以获得更清晰的 API
- **PaddleOCR PP-OCRv5_server**：来自 PaddleOCR 3.0 的高级模型，具有卓越的准确性
- **PyTesseract**：传统 OCR，具有广泛的语言支持和细粒度控制
- **可重用引擎**：创建一次 OCR 引擎实例并在多个解析器之间重用
- 支持多种语言（PyTesseract）
- PaddleOCR 的 GPU 加速
- 两个引擎的可配置 OCR 参数

### 🧠 PaddleOCRVL 端到端解析
- **视觉语言模型**：使用 PaddleOCRVL 进行高级文档理解
- **完整文档解析**：单次处理提取所有内容类型
- **图表识别**：自动图表检测并转换为结构化表格
- **多元素支持**：处理标题、文本、表格、图表、脚注和图形标题
- **集成恢复**：可选的 DocRes 图像恢复以增强质量
- **分割表格合并**：自动检测并合并跨页的表格
- **结构化输出**：生成包含表格和图表的 Excel 文件

### 🖼️ 视觉元素提取
- 自动裁剪并保存图形、图表和表格
- 有序的输出目录结构
- 高分辨率图像保留

### 🔧 图像恢复（DocRes）
- **6 种恢复任务**：去扭曲、去阴影、外观增强、去模糊、二值化和端到端恢复
- **GPU 加速**：自动 CUDA 检测和优化
- **增强质量**：提高文档质量以获得更好的 OCR 和布局检测
- **灵活处理**：独立图像恢复或与解析集成

### 🤖 VLM 集成
- **依赖注入模式**：在外部初始化 VLM 引擎并将其传递给解析器，以获得更清晰的 API
- **视觉语言模型支持**：从视觉元素中提取结构化数据
- **多种提供商选项**：OpenAI、Gemini、Anthropic、OpenRouter、Qianfan、Ollama
- **可重用引擎**：创建一次 VLM 引擎实例并在多个解析器之间重用
- **自动转换**：将图表和表格转换为结构化格式（Excel、HTML、JSON）

### 📊 多种输出格式
- **Markdown**：带嵌入图像和表格的人类可读文档
- **Excel**：电子表格格式的结构化数据
- **JSON**：程序可访问的结构化数据
- **HTML**：交互式 Web 就绪文档
- **图像**：高质量的裁剪视觉元素

### 🖥️ 用户界面
- **Web UI**：基于 Gradio 的界面，带拖放功能
- **命令行**：强大的 CLI，用于批量处理和自动化
- **多个标签页**：完整解析、DOCX 解析、增强解析、图表/表格提取和图像恢复

### ⚙️ 灵活配置
- 广泛的自定义选项
- 性能调整参数
- 输出格式选择
- 设备选择（CPU/GPU）

## 🙏 致谢

Doctra 建立在几个优秀的开源项目之上：

- **[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)** - 高级文档布局检测和 OCR 功能
- **[DocRes](https://github.com/ZZZHANG-jx/DocRes)** - 最先进的文档图像恢复模型
- **[Outlines](https://github.com/dottxt-ai/outlines)** - LLM 的结构化输出生成

我们感谢这些项目的开发者和贡献者，他们的宝贵工作使 Doctra 成为可能。

