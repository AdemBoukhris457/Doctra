# 🚀 **Doctra - Document Parser Library** 📑🔎

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

## 📋 Table of Contents

- [Installation](#🛠️-installation)
- [Quick Start](#⚡-quick-start)
- [Core Components](#🔧-core-components)
  - [StructuredPDFParser](#structuredpdfparser)
  - [EnhancedPDFParser](#enhancedpdfparser)
  - [ChartTablePDFParser](#charttablepdfparser)
  - [PaddleOCRVLPDFParser](#paddleocrvlpdfparser)
  - [StructuredDOCXParser](#structureddocxparser)
  - [DocResEngine](#docresengine)
- [Web UI (Gradio)](#🖥️-web-ui-gradio)
- [Command Line Interface](#command-line-interface)
- [Visualization](#🎨-visualization)
- [Usage Examples](#📖-usage-examples)
- [Features](#✨-features)

## 🛠️ Installation

### From PyPI (recommended)

```bash
pip install doctra
```

### From source

```bash
git clone https://github.com/AdemBoukhris457/Doctra.git
cd Doctra
pip install .
```

### System Dependencies

Doctra requires **Poppler** for PDF processing. Install it based on your operating system:

#### Ubuntu/Debian
```bash
sudo apt install poppler-utils
```

#### macOS
```bash
brew install poppler
```

#### Windows
Download and install from [Poppler for Windows](https://poppler.freedesktop.org/) or use conda:
```bash
conda install -c conda-forge poppler
```

#### Google Colab
```bash
!sudo apt install poppler-utils
```

## ⚡ Quick Start

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser

# Initialize the parser
parser = StructuredPDFParser()

# Parse a PDF document
parser.parse("path/to/your/document.pdf")
```

## 🔧 Core Components

### StructuredPDFParser

The `StructuredPDFParser` is a comprehensive PDF parser that extracts all types of content from PDF documents. It processes PDFs through layout detection, extracts text using OCR, saves images for visual elements, and optionally converts charts/tables to structured data using Vision Language Models (VLM).

#### Key Features:
- **Layout Detection**: Uses PaddleOCR for accurate document layout analysis
- **OCR Processing**: Supports both PyTesseract (default) and PaddleOCR PP-OCRv5_server for text extraction
- **Visual Element Extraction**: Saves figures, charts, and tables as images
- **VLM Integration**: Optional conversion of visual elements to structured data
- **Multiple Output Formats**: Generates Markdown, Excel, and structured JSON

#### Basic Usage:

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser

# Basic parser without VLM (uses default PyTesseract OCR engine)
parser = StructuredPDFParser()

# Parser with VLM for structured data extraction
from doctra.engines.vlm.service import VLMStructuredExtractor

# Initialize VLM engine
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",  # or "gemini", "anthropic", "openrouter", "qianfan", "ollama"
    api_key="your_api_key_here"
)

# Pass VLM engine to parser
parser = StructuredPDFParser(vlm=vlm_engine)

# Parse document
parser.parse("document.pdf")
```

#### OCR Engine Configuration:

Doctra uses a dependency injection pattern for OCR engines. You initialize the OCR engine externally and pass it to the parser:

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser
from doctra.engines.ocr import PytesseractOCREngine, PaddleOCREngine

# Option 1: Use default PyTesseract (automatic if ocr_engine=None)
parser = StructuredPDFParser()  # Creates default PyTesseractOCREngine internally

# Option 2: Explicitly configure PyTesseract
tesseract_ocr = PytesseractOCREngine(
    lang="eng",      # Language code
    psm=4,           # Page segmentation mode
    oem=3,           # OCR engine mode
    extra_config=""  # Additional Tesseract config
)
parser = StructuredPDFParser(ocr_engine=tesseract_ocr)

# Option 3: Use PaddleOCR for better accuracy
paddle_ocr = PaddleOCREngine(
    device="gpu",                          # "gpu" or "cpu"
    use_doc_orientation_classify=False,    # Document orientation detection
    use_doc_unwarping=False,              # Text image rectification
    use_textline_orientation=False        # Text line orientation
)
parser = StructuredPDFParser(ocr_engine=paddle_ocr)

# Option 4: Reuse OCR engine across multiple parsers
shared_ocr = PytesseractOCREngine(lang="eng", psm=6, oem=3)
parser1 = StructuredPDFParser(ocr_engine=shared_ocr)
parser2 = EnhancedPDFParser(ocr_engine=shared_ocr)  # Reuse same instance
```

#### VLM Engine Configuration:

Doctra uses the same dependency injection pattern for VLM engines. You initialize the VLM engine externally and pass it to the parser:

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

# Option 1: No VLM (default)
parser = StructuredPDFParser()  # VLM processing disabled

# Option 2: Initialize VLM engine and pass to parser
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",  # or "gemini", "anthropic", "openrouter", "qianfan", "ollama"
    vlm_model="gpt-5",      # Optional, uses default if None
    api_key="your_api_key"
)
parser = StructuredPDFParser(vlm=vlm_engine)

# Option 3: Reuse VLM engine across multiple parsers
shared_vlm = VLMStructuredExtractor(
    vlm_provider="gemini",
    api_key="your_api_key"
)
parser1 = StructuredPDFParser(vlm=shared_vlm)
parser2 = EnhancedPDFParser(vlm=shared_vlm)  # Reuse same instance
parser3 = ChartTablePDFParser(vlm=shared_vlm)  # Reuse same instance
```

#### Advanced Configuration:

```python
from doctra.engines.ocr import PytesseractOCREngine, PaddleOCREngine

# Option 1: Using PyTesseract (default)
ocr_engine = PytesseractOCREngine(
    lang="eng",
    psm=4,
    oem=3,
    extra_config=""
)

# Initialize VLM engine
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    vlm_model="gpt-5",  # Optional, uses default if None
    api_key="your_api_key"
)

parser = StructuredPDFParser(
    # VLM Engine (pass the initialized engine)
    vlm=vlm_engine,  # or None to disable VLM
    
    # Layout Detection Settings
    layout_model_name="PP-DocLayout_plus-L",
    dpi=200,
    min_score=0.0,
    
    # OCR Engine (pass the initialized engine)
    ocr_engine=ocr_engine,  # or None for default PyTesseract
    
    # Output Settings
    box_separator="\n"
)

# Option 2: Using PaddleOCR for better accuracy
paddle_ocr = PaddleOCREngine(
    device="gpu",  # Use "cpu" if no GPU available
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

parser = StructuredPDFParser(
    ocr_engine=paddle_ocr,
    # ... other settings
)
```

### EnhancedPDFParser

The `EnhancedPDFParser` extends the `StructuredPDFParser` with advanced image restoration capabilities using DocRes. This parser is ideal for processing scanned documents, low-quality PDFs, or documents with visual distortions that need enhancement before parsing.

#### Key Features:
- **Image Restoration**: Uses DocRes for document enhancement before processing
- **Multiple Restoration Tasks**: Supports dewarping, deshadowing, appearance enhancement, deblurring, binarization, and end-to-end restoration
- **Enhanced Quality**: Improves document quality for better OCR and layout detection
- **All StructuredPDFParser Features**: Inherits all capabilities of the base parser
- **Flexible Configuration**: Extensive options for restoration and processing

#### Basic Usage:

```python
from doctra.parsers.enhanced_pdf_parser import EnhancedPDFParser

# Basic enhanced parser with image restoration
parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="appearance"  # Default restoration task
)

# Parse document with enhancement
parser.parse("scanned_document.pdf")
```

#### Advanced Configuration:

```python
from doctra.engines.ocr import PytesseractOCREngine, PaddleOCREngine

# Initialize OCR engine (PyTesseract or PaddleOCR)
ocr_engine = PytesseractOCREngine(
    lang="eng",
    psm=6,
    oem=3
)

# Initialize VLM engine
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    vlm_model="gpt-4-vision",  # Optional, uses default if None
    api_key="your_api_key"
)

parser = EnhancedPDFParser(
    # Image Restoration Settings
    use_image_restoration=True,
    restoration_task="dewarping",      # Correct perspective distortion
    restoration_device="cuda",         # Use GPU for faster processing
    restoration_dpi=300,               # Higher DPI for better quality
    
    # VLM Engine (pass the initialized engine)
    vlm=vlm_engine,  # or None to disable VLM
    
    # Layout Detection Settings
    layout_model_name="PP-DocLayout_plus-L",
    dpi=200,
    min_score=0.5,
    
    # OCR Engine (pass the initialized engine)
    ocr_engine=ocr_engine,  # or None for default PyTesseract
)
```

#### DocRes Restoration Tasks:

| Task | Description | Best For |
|------|-------------|----------|
| `appearance` | General appearance enhancement | Most documents (default) |
| `dewarping` | Correct perspective distortion | Scanned documents with perspective issues |
| `deshadowing` | Remove shadows and lighting artifacts | Documents with shadow problems |
| `deblurring` | Reduce blur and improve sharpness | Blurry or low-quality scans |
| `binarization` | Convert to black and white | Documents needing clean binarization |
| `end2end` | Complete restoration pipeline | Severely degraded documents |

### ChartTablePDFParser

The `ChartTablePDFParser` is a specialized parser focused specifically on extracting charts and tables from PDF documents. It's optimized for scenarios where you only need these specific elements, providing faster processing and more targeted output.

#### Key Features:
- **Focused Extraction**: Extracts only charts and/or tables
- **Selective Processing**: Choose to extract charts, tables, or both
- **VLM Integration**: Optional conversion to structured data
- **Organized Output**: Separate directories for charts and tables
- **Progress Tracking**: Real-time progress bars for extraction

#### Basic Usage:

```python
from doctra.parsers.table_chart_extractor import ChartTablePDFParser

# Extract both charts and tables
parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=True
)

# Extract only charts
parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=False
)

# Parse with custom output directory
parser.parse("document.pdf", output_base_dir="my_outputs")
```

#### Advanced Configuration:

```python
# Initialize VLM engine
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    vlm_model="gpt-5",  # Optional, uses default if None
    api_key="your_api_key"
)

parser = ChartTablePDFParser(
    # Extraction Settings
    extract_charts=True,
    extract_tables=True,
    
    # VLM Engine (pass the initialized engine)
    vlm=vlm_engine,  # or None to disable VLM
    
    # Layout Detection Settings
    layout_model_name="PP-DocLayout_plus-L",
    dpi=200,
    min_score=0.0
)
```

### PaddleOCRVLPDFParser

The `PaddleOCRVLPDFParser` uses PaddleOCRVL (Vision-Language Model) for end-to-end document parsing. It combines PaddleOCRVL's advanced document understanding capabilities with DocRes image restoration and split table merging, providing a comprehensive solution for complex document processing.

#### Installation Requirements

Before using `PaddleOCRVLPDFParser`, install the required dependencies:

```bash
pip install -U "paddleocr[doc-parser]"
```

**For Linux systems:**
```bash
python -m pip install https://paddle-whl.bj.bcebos.com/nightly/cu126/safetensors/safetensors-0.6.2.dev0-cp38-abi3-linux_x86_64.whl
```

**For Windows systems:**
```bash
python -m pip install https://xly-devops.cdn.bcebos.com/safetensors-nightly/safetensors-0.6.2.dev0-cp38-abi3-win_amd64.whl
```

#### Key Features:
- **End-to-End Parsing**: Uses PaddleOCRVL for complete document understanding in a single pass
- **Chart Recognition**: Automatically extracts and converts charts to structured table format
- **Document Restoration**: Optional DocRes integration for enhanced document quality
- **Split Table Merging**: Automatically detects and merges tables split across pages
- **Structured Output**: Generates Markdown, HTML, and Excel files with tables and charts
- **Multiple Element Types**: Handles headers, text, tables, charts, footnotes, and more

#### Basic Usage:

```python
from doctra import PaddleOCRVLPDFParser

# Basic parser with default settings
parser = PaddleOCRVLPDFParser(
    use_image_restoration=True,      # Enable DocRes restoration
    use_chart_recognition=True,       # Enable chart recognition
    merge_split_tables=True,          # Enable split table merging
    device="gpu"                      # Use GPU for processing
)

# Parse a PDF document
parser.parse("document.pdf")
```

#### Advanced Configuration:

```python
from doctra import PaddleOCRVLPDFParser

parser = PaddleOCRVLPDFParser(
    # DocRes Image Restoration Settings
    use_image_restoration=True,
    restoration_task="appearance",    # Options: appearance, dewarping, deshadowing, deblurring, binarization, end2end
    restoration_device="cuda",        # or "cpu" or None for auto-detect
    restoration_dpi=300,              # DPI for restoration processing
    
    # PaddleOCRVL Settings
    use_chart_recognition=True,       # Enable chart recognition and extraction
    use_doc_orientation_classify=True, # Enable document orientation classification
    use_doc_unwarping=True,           # Enable document unwarping
    use_layout_detection=True,        # Enable layout detection
    device="gpu",                     # "gpu" or "cpu"
    
    # Split Table Merging Settings
    merge_split_tables=True,          # Enable split table detection and merging
    bottom_threshold_ratio=0.20,      # Ratio for "too close to bottom" detection
    top_threshold_ratio=0.15,         # Ratio for "too close to top" detection
    max_gap_ratio=0.25,               # Maximum allowed gap between tables
    column_alignment_tolerance=10.0,  # Pixel tolerance for column alignment
    min_merge_confidence=0.65         # Minimum confidence score for merging
)

# Parse with custom output directory
parser.parse("document.pdf", output_dir="custom_output")
```

#### Output Structure:

The parser generates output in `outputs/{document_name}/paddleocr_vl_parse/` with:
- **result.md**: Markdown file with all extracted content
- **result.html**: HTML file with formatted output
- **tables.xlsx**: Excel file containing all tables and charts as structured data
- **tables.html**: HTML file with structured tables and charts
- **enhanced_pages/**: Directory with DocRes-enhanced page images (if restoration enabled)
- **tables/**: Directory with merged table images (if split tables detected)

#### Example Output:

The parser extracts various document elements:
- **Headers**: Document titles and section headers
- **Text**: Paragraphs and body text
- **Tables**: Extracted as HTML and converted to Excel format
- **Charts**: Converted from visual format to structured table data
- **Footnotes**: Vision-based footnote detection
- **Figure Titles**: Captions and figure descriptions

### StructuredDOCXParser

The `StructuredDOCXParser` is a comprehensive parser for Microsoft Word documents (.docx files) that extracts text, tables, images, and structured content while preserving document formatting and order. It supports VLM integration for enhanced content analysis and structured data extraction.

#### Key Features:
- **Complete DOCX Support**: Extracts text, tables, images, and formatting from Word documents
- **Document Order Preservation**: Maintains the original sequence of elements (paragraphs, tables, images)
- **VLM Integration**: Optional Vision Language Model support for image analysis and table extraction
- **Multiple Output Formats**: Generates Markdown, HTML, and Excel files
- **Excel Export**: Creates structured Excel files with Table of Contents and clickable hyperlinks
- **Formatting Preservation**: Maintains text formatting (bold, italic, etc.) in output
- **Progress Tracking**: Real-time progress bars for VLM processing

#### Basic Usage:

```python
from doctra.parsers.structured_docx_parser import StructuredDOCXParser

# Basic DOCX parsing
parser = StructuredDOCXParser(
    extract_images=True,
    preserve_formatting=True,
    table_detection=True,
    export_excel=True
)

# Parse DOCX document
parser.parse("document.docx")
```

#### Advanced Configuration with VLM:

```python
# Initialize VLM engine
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",  # or "gemini", "anthropic", "openrouter", "qianfan", "ollama"
    vlm_model="gpt-4-vision",  # Optional, uses default if None
    api_key="your_api_key"
)

parser = StructuredDOCXParser(
    # VLM Engine (pass the initialized engine)
    vlm=vlm_engine,  # or None to disable VLM
    
    # Processing Options
    extract_images=True,
    preserve_formatting=True,
    table_detection=True,
    export_excel=True
)

# Parse with VLM enhancement
parser.parse("document.docx")
```

#### Output Structure:

When parsing a DOCX document, the parser creates:

```
outputs/document_name/
├── document.md          # Markdown version with all content
├── document.html        # HTML version with styling
├── tables.xlsx         # Excel file with extracted tables
│   ├── Table of Contents  # Summary sheet with hyperlinks
│   ├── Table 1         # Individual table sheets
│   ├── Table 2
│   └── ...
└── images/             # Extracted images
    ├── image1.png
    ├── image2.jpg
    └── ...
```

#### VLM Integration Features:

When VLM is enabled, the parser:
- **Analyzes Images**: Uses AI to extract structured data from images
- **Creates Tables**: Converts chart images to structured table data
- **Enhanced Excel Output**: Includes VLM-extracted tables in Excel file
- **Smart Content Display**: Shows extracted tables instead of images in Markdown/HTML
- **Progress Tracking**: Shows progress based on number of images processed

#### CLI Usage:

```bash
# Basic DOCX parsing
doctra parse-docx document.docx

# With VLM enhancement
doctra parse-docx document.docx --use-vlm --vlm-provider openai --vlm-api-key your_key

# Custom options
doctra parse-docx document.docx \
  --extract-images \
  --preserve-formatting \
  --table-detection \
  --export-excel
```

### DocResEngine

The `DocResEngine` provides direct access to DocRes image restoration capabilities. This engine is perfect for standalone image restoration tasks or when you need fine-grained control over the restoration process.

#### Key Features:
- **Direct Image Restoration**: Process individual images or entire PDFs
- **Multiple Restoration Tasks**: All 6 DocRes restoration tasks available
- **GPU Acceleration**: Automatic CUDA detection and optimization
- **Flexible Input/Output**: Support for various image formats and PDFs
- **Metadata Extraction**: Get detailed information about restoration process

#### Basic Usage:

```python
from doctra.engines.image_restoration import DocResEngine

# Initialize DocRes engine
docres = DocResEngine(device="cuda")  # or "cpu" or None for auto-detect

# Restore a single image
restored_img, metadata = docres.restore_image(
    image="path/to/image.jpg",
    task="appearance"
)

# Restore entire PDF
enhanced_pdf = docres.restore_pdf(
    pdf_path="document.pdf",
    output_path="enhanced_document.pdf",
    task="appearance"
)
```

#### Advanced Usage:

```python
# Initialize with custom settings
docres = DocResEngine(
    device="cuda",                    # Force GPU usage
    use_half_precision=True,         # Use half precision for faster processing
    model_path="custom/model.pth",    # Custom model path (optional)
    mbd_path="custom/mbd.pth"        # Custom MBD model path (optional)
)

# Process multiple images
images = ["doc1.jpg", "doc2.jpg", "doc3.jpg"]
for img_path in images:
    restored_img, metadata = docres.restore_image(
        image=img_path,
        task="dewarping"
    )
    print(f"Processed {img_path}: {metadata}")

# Batch PDF processing
pdfs = ["report1.pdf", "report2.pdf"]
for pdf_path in pdfs:
    output_path = f"enhanced_{os.path.basename(pdf_path)}"
    docres.restore_pdf(
        pdf_path=pdf_path,
        output_path=output_path,
        task="end2end"  # Complete restoration pipeline
    )
```

#### Supported Restoration Tasks:

| Task | Description | Use Case |
|------|-------------|----------|
| `appearance` | General appearance enhancement | Default choice for most documents |
| `dewarping` | Correct document perspective distortion | Scanned documents with perspective issues |
| `deshadowing` | Remove shadows and lighting artifacts | Documents with shadow problems |
| `deblurring` | Reduce blur and improve sharpness | Blurry or low-quality scans |
| `binarization` | Convert to black and white | Documents needing clean binarization |
| `end2end` | Complete restoration pipeline | Severely degraded documents |

## 🖥️ Web UI (Gradio)

Doctra provides a comprehensive web interface built with Gradio that makes document processing accessible to non-technical users.

#### Features:
- **Drag & Drop Interface**: Upload PDFs by dragging and dropping
- **Multiple Parsers**: Choose between full parsing, enhanced parsing, and chart/table extraction
- **Real-time Processing**: See progress as documents are processed
- **VLM Integration**: Configure API keys for AI features
- **Output Preview**: View results directly in the browser
- **Download Results**: Download processed files as ZIP archives

#### Launch the Web UI:

```python
from doctra.ui.app import launch_ui

# Launch the web interface
launch_ui()
```

Or from command line:
```bash
python gradio_app.py
```

#### Web UI Components:

1. **Full Parse Tab**: Complete document processing with page navigation
2. **DOCX Parser Tab**: Microsoft Word document parsing with VLM integration
3. **Tables & Charts Tab**: Specialized extraction with VLM integration
4. **DocRes Tab**: Image restoration with before/after comparison
5. **Enhanced Parser Tab**: Enhanced parsing with DocRes integration

## Command Line Interface

Doctra includes a powerful CLI for batch processing and automation.

#### Available Commands:

```bash
# Full document parsing
doctra parse document.pdf

# DOCX document parsing
doctra parse-docx document.docx

# Enhanced parsing with image restoration
doctra enhance document.pdf --restoration-task appearance

# Extract only charts and tables
doctra extract charts document.pdf
doctra extract tables document.pdf
doctra extract both document.pdf --use-vlm

# Visualize layout detection
doctra visualize document.pdf

# Quick document analysis
doctra analyze document.pdf

# System information
doctra info
```

#### CLI Examples:

```bash
# Enhanced parsing with custom settings
doctra enhance document.pdf \
  --restoration-task dewarping \
  --restoration-device cuda \
  --use-vlm \
  --vlm-provider openai \
  --vlm-api-key your_key

# Extract charts with VLM
doctra extract charts document.pdf \
  --use-vlm \
  --vlm-provider gemini \
  --vlm-api-key your_key

# Batch processing
doctra parse *.pdf --output-dir results/
```

## 🎨 Visualization

Doctra provides powerful visualization capabilities to help you understand how the layout detection works and verify the accuracy of element extraction.

### Layout Detection Visualization

The `StructuredPDFParser` includes a built-in visualization method that displays PDF pages with bounding boxes overlaid on detected elements. This is perfect for:

- **Debugging**: Verify that layout detection is working correctly
- **Quality Assurance**: Check the accuracy of element identification
- **Documentation**: Create visual documentation of extraction results
- **Analysis**: Understand document structure and layout patterns

#### Basic Visualization:

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser

# Initialize parser (OCR engine is optional for visualization)
parser = StructuredPDFParser()

# Display visualization (opens in default image viewer)
parser.display_pages_with_boxes("document.pdf")
```

#### Advanced Visualization with Custom Settings:

```python
# Custom visualization configuration
parser.display_pages_with_boxes(
    pdf_path="document.pdf",
    num_pages=5,        # Number of pages to visualize
    cols=3,             # Number of columns in grid
    page_width=600,     # Width of each page in pixels
    spacing=30,         # Spacing between pages
    save_path="layout_visualization.png"  # Save to file instead of displaying
)
```

#### Visualization Features:

- **Color-coded Elements**: Each element type (text, table, chart, figure) has a distinct color
- **Confidence Scores**: Shows detection confidence for each element
- **Grid Layout**: Multiple pages displayed in an organized grid
- **Interactive Legend**: Color legend showing all detected element types
- **High Quality**: High-resolution output suitable for documentation
- **Flexible Output**: Display on screen or save to file

#### Example Output:

The visualization shows:
- **Blue boxes**: Text elements
- **Red boxes**: Tables
- **Green boxes**: Charts
- **Orange boxes**: Figures
- **Labels**: Element type and confidence score (e.g., "table (0.95)")
- **Page titles**: Page number and element count
- **Summary statistics**: Total elements detected by type

### Use Cases for Visualization:

1. **Document Analysis**: Quickly assess document structure and complexity
2. **Quality Control**: Verify extraction accuracy before processing
3. **Debugging**: Identify issues with layout detection
4. **Documentation**: Create visual reports of extraction results
5. **Training**: Help users understand how the system works

### Visualization Configuration Options:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `num_pages` | 3 | Number of pages to visualize |
| `cols` | 2 | Number of columns in grid layout |
| `page_width` | 800 | Width of each page in pixels |
| `spacing` | 40 | Spacing between pages in pixels |
| `save_path` | None | Path to save visualization (if None, displays on screen) |

## 📓 Interactive Notebooks

| Notebook | Colab Badge | Description |
|----------|-------------|-------------|
| **01_doctra_quick_start** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1Z9UH9r1ZxGHm2cAFVKy7W9cKjcgBDOlG?usp=sharing) | Comprehensive tutorial covering layout detection, content extraction, and multi-format outputs with visual examples |
| **case_study_01_financial_report_analysis** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AdemBoukhris457/Doctra/blob/main/notebooks/case_study_01_financial_report_analysis.ipynb) | Financial report analysis: Extract tables and charts from PDF reports, convert visual elements to structured data using VLM, and analyze financial data with pandas |
| **case_study_02_scanned_document_restoration** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AdemBoukhris457/Doctra/blob/main/notebooks/case_study_02_scanned_document_restoration.ipynb) | Scanned document restoration: Apply DocRes engine for image restoration (appearance, dewarping, deshadowing, deblurring, binarization, end2end), restore PDFs, and compare parsing results before and after restoration |

## 📖 Usage Examples

### Example 1: Basic Document Processing

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser

# Initialize parser (uses default PyTesseract OCR engine)
parser = StructuredPDFParser()

# Process document
parser.parse("financial_report.pdf")

# Output will be saved to: outputs/financial_report/
# - Extracted text content
# - Cropped images of figures, charts, and tables
# - Markdown file with all content
```

### Example 2: Enhanced Parsing with Image Restoration

```python
from doctra.parsers.enhanced_pdf_parser import EnhancedPDFParser
from doctra.engines.ocr import PytesseractOCREngine

# Initialize OCR engine (optional - defaults to PyTesseract if not provided)
ocr_engine = PytesseractOCREngine(lang="eng", psm=4, oem=3)

# Initialize VLM engine
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your_api_key"
)

# Initialize enhanced parser with image restoration
parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="dewarping",  # Correct perspective distortion
    restoration_device="cuda",    # Use GPU for faster processing
    ocr_engine=ocr_engine,        # Pass OCR engine instance
    vlm=vlm_engine                # Pass VLM engine instance
)

# Process scanned document with enhancement
parser.parse("scanned_document.pdf")

# Output will include:
# - Enhanced PDF with restored images
# - All standard parsing outputs
# - Improved OCR accuracy due to restoration
```

### Example 2b: Using PaddleOCR for Better Accuracy

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser
from doctra.engines.ocr import PaddleOCREngine

# Initialize PaddleOCR engine with custom settings
paddle_ocr = PaddleOCREngine(
    device="gpu",  # Use "cpu" if no GPU available
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

# Create parser with PaddleOCR engine
parser = StructuredPDFParser(
    ocr_engine=paddle_ocr
)

# Process document with PaddleOCR
parser.parse("complex_document.pdf")

# PaddleOCR provides:
# - Higher accuracy for complex documents
# - Better performance on GPU
# - Automatic model management
```

### Example 3: Direct Image Restoration

```python
from doctra.engines.image_restoration import DocResEngine

# Initialize DocRes engine
docres = DocResEngine(device="cuda")

# Restore individual images
restored_img, metadata = docres.restore_image(
    image="blurry_document.jpg",
    task="deblurring"
)

# Restore entire PDF
docres.restore_pdf(
    pdf_path="low_quality.pdf",
    output_path="enhanced.pdf",
    task="appearance"
)
```

### Example 4: DOCX Document Parsing

```python
from doctra.parsers.structured_docx_parser import StructuredDOCXParser

# Basic DOCX parsing
parser = StructuredDOCXParser(
    extract_images=True,
    preserve_formatting=True,
    table_detection=True,
    export_excel=True
)

# Parse Word document
parser.parse("report.docx")

# Output will include:
# - Markdown file with all content
# - HTML file with styling
# - Excel file with extracted tables
# - Extracted images in organized folders
```

### Example 5: DOCX Parsing with VLM Enhancement

```python
from doctra.parsers.structured_docx_parser import StructuredDOCXParser

# Initialize VLM engine
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    vlm_model="gpt-4-vision",  # Optional, uses default if None
    api_key="your_api_key"
)

# DOCX parsing with VLM for enhanced analysis
parser = StructuredDOCXParser(
    vlm=vlm_engine,  # Pass VLM engine instance
    extract_images=True,
    preserve_formatting=True,
    table_detection=True,
    export_excel=True
)

# Parse with AI enhancement
parser.parse("financial_report.docx")

# Output will include:
# - All standard outputs
# - VLM-extracted tables from images
# - Enhanced Excel with Table of Contents
# - Smart content display (tables instead of images)
```

### Example 6: PaddleOCRVL End-to-End Parsing

```python
from doctra import PaddleOCRVLPDFParser

# Initialize PaddleOCRVL parser with all features enabled
parser = PaddleOCRVLPDFParser(
    use_image_restoration=True,      # Enable DocRes restoration
    restoration_task="appearance",    # Use appearance enhancement
    use_chart_recognition=True,       # Enable chart recognition
    merge_split_tables=True,          # Enable split table merging
    device="gpu"                      # Use GPU for faster processing
)

# Parse document - automatically handles all content types
parser.parse("financial_report.pdf")

# Output will be in: outputs/financial_report/paddleocr_vl_parse/
# - result.md: All content in Markdown
# - result.html: Formatted HTML output
# - tables.xlsx: All tables and charts in Excel format
# - tables.html: Structured tables and charts
```

### Example 7: Chart and Table Extraction with VLM

```python
from doctra.parsers.table_chart_extractor import ChartTablePDFParser

# Initialize VLM engine
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your_api_key"
)

# Initialize parser with VLM
parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=True,
    vlm=vlm_engine  # Pass VLM engine instance
)

# Process document
parser.parse("data_report.pdf", output_base_dir="extracted_data")

# Output will include:
# - Cropped chart and table images
# - Structured data in Excel format
# - Markdown tables with extracted data
```

### Example 8: Web UI Usage

```python
from doctra.ui.app import launch_ui

# Launch the web interface
launch_ui()

# Or build the interface programmatically
from doctra.ui.app import build_demo
demo = build_demo()
demo.launch(share=True)  # Share publicly
```

### Example 9: Command Line Usage

```bash
# DOCX parsing with VLM
doctra parse-docx document.docx \
  --use-vlm \
  --vlm-provider openai \
  --vlm-api-key your_key \
  --extract-images \
  --export-excel

# Enhanced parsing with custom settings
doctra enhance document.pdf \
  --restoration-task dewarping \
  --restoration-device cuda \
  --use-vlm \
  --vlm-provider openai \
  --vlm-api-key your_key

# Extract charts with VLM
doctra extract charts document.pdf \
  --use-vlm \
  --vlm-provider gemini \
  --vlm-api-key your_key

# Batch processing
doctra parse *.pdf --output-dir results/
```

### Example 10: Layout Visualization

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser

# Initialize parser (OCR engine not needed for visualization)
parser = StructuredPDFParser()

# Create a comprehensive visualization
parser.display_pages_with_boxes(
    pdf_path="research_paper.pdf",
    num_pages=6,        # Visualize first 6 pages
    cols=2,             # 2 columns layout
    page_width=700,     # Larger pages for better detail
    spacing=50,         # More spacing between pages
    save_path="research_paper_layout.png"  # Save for documentation
)

# For quick preview (displays on screen)
parser.display_pages_with_boxes("document.pdf")
```

## ✨ Features

### 🔍 Layout Detection
- Advanced document layout analysis using PaddleOCR
- Accurate identification of text, tables, charts, and figures
- Configurable confidence thresholds

### 📝 OCR Processing
- **Dual OCR Engine Support**: Choose between PyTesseract (default) or PaddleOCR PP-OCRv5_server
- **Dependency Injection Pattern**: Initialize OCR engines externally and pass them to parsers for clearer API
- **PaddleOCR PP-OCRv5_server**: Advanced model from PaddleOCR 3.0 with superior accuracy
- **PyTesseract**: Traditional OCR with extensive language support and fine-grained control
- **Reusable Engines**: Create OCR engine instances once and reuse across multiple parsers
- Support for multiple languages (PyTesseract)
- GPU acceleration for PaddleOCR
- Configurable OCR parameters for both engines

### 🧠 PaddleOCRVL End-to-End Parsing
- **Vision-Language Model**: Advanced document understanding using PaddleOCRVL
- **Complete Document Parsing**: Single-pass extraction of all content types
- **Chart Recognition**: Automatic chart detection and conversion to structured tables
- **Multi-Element Support**: Handles headers, text, tables, charts, footnotes, and figure titles
- **Integrated Restoration**: Optional DocRes image restoration for enhanced quality
- **Split Table Merging**: Automatic detection and merging of tables across pages
- **Structured Output**: Generates Excel files with both tables and charts

### 🖼️ Visual Element Extraction
- Automatic cropping and saving of figures, charts, and tables
- Organized output directory structure
- High-resolution image preservation

### 🔧 Image Restoration (DocRes)
- **6 Restoration Tasks**: Dewarping, deshadowing, appearance enhancement, deblurring, binarization, and end-to-end restoration
- **GPU Acceleration**: Automatic CUDA detection and optimization
- **Enhanced Quality**: Improves document quality for better OCR and layout detection
- **Flexible Processing**: Standalone image restoration or integrated with parsing

### 🤖 VLM Integration
- **Dependency Injection Pattern**: Initialize VLM engines externally and pass them to parsers for clearer API
- **Vision Language Model Support**: Structured data extraction from visual elements
- **Multiple Provider Options**: OpenAI, Gemini, Anthropic, OpenRouter, Qianfan, Ollama
- **Reusable Engines**: Create VLM engine instances once and reuse across multiple parsers
- **Automatic Conversion**: Charts and tables converted to structured formats (Excel, HTML, JSON)

### 📊 Multiple Output Formats
- **Markdown**: Human-readable document with embedded images and tables
- **Excel**: Structured data in spreadsheet format
- **JSON**: Programmatically accessible structured data
- **HTML**: Interactive web-ready documents
- **Images**: High-quality cropped visual elements

### 🖥️ User Interfaces
- **Web UI**: Gradio-based interface with drag & drop functionality
- **Command Line**: Powerful CLI for batch processing and automation
- **Multiple Tabs**: Full parsing, DOCX parsing, enhanced parsing, chart/table extraction, and image restoration

### ⚙️ Flexible Configuration
- Extensive customization options
- Performance tuning parameters
- Output format selection
- Device selection (CPU/GPU)

## 🙏 Acknowledgments

Doctra builds upon several excellent open-source projects:

- **[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)** - Advanced document layout detection and OCR capabilities
- **[DocRes](https://github.com/ZZZHANG-jx/DocRes)** - State-of-the-art document image restoration model
- **[Outlines](https://github.com/dottxt-ai/outlines)** - Structured output generation for LLMs

We thank the developers and contributors of these projects for their valuable work that makes Doctra possible.
