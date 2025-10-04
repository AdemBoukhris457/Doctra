# 🚀 **Doctra - Document Parser Library** 📑🔎

![Doctra Logo](https://raw.githubusercontent.com/AdemBoukhris457/Doctra/main/assets/Doctra_Banner.png)

<div align="center">

[![stars](https://img.shields.io/github/stars/AdemBoukhris457/Doctra.svg)](https://github.com/AdemBoukhris457/Doctra)
[![forks](https://img.shields.io/github/forks/AdemBoukhris457/Doctra.svg)](https://github.com/AdemBoukhris457/Doctra)
[![PyPI version](https://img.shields.io/pypi/v/doctra)](https://pypi.org/project/doctra/)
[![Doc Status](https://github.com/AdemBoukhris457/Doctra/actions/workflows/build-docs.yml/badge.svg)](https://ademboukhris457.github.io/Doctra/)
</div>

## 📋 Table of Contents

- [Installation](#🛠️-installation)
- [Quick Start](#⚡-quick-start)
- [Core Components](#🔧-core-components)
  - [StructuredPDFParser](#structuredpdfparser)
  - [EnhancedPDFParser](#enhancedpdfparser)
  - [ChartTablePDFParser](#charttablepdfparser)
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
Download and install from [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/) or use conda:
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
- **OCR Processing**: Extracts text from all document elements
- **Visual Element Extraction**: Saves figures, charts, and tables as images
- **VLM Integration**: Optional conversion of visual elements to structured data
- **Multiple Output Formats**: Generates Markdown, Excel, and structured JSON

#### Basic Usage:

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser

# Basic parser without VLM
parser = StructuredPDFParser()

# Parser with VLM for structured data extraction
parser = StructuredPDFParser(
    use_vlm=True,
    vlm_provider="openai",  # or "gemini" or "anthropic" or "openrouter"
    vlm_api_key="your_api_key_here"
)

# Parse document
parser.parse("document.pdf")
```

#### Advanced Configuration:

```python
parser = StructuredPDFParser(
    # VLM Settings
    use_vlm=True,
    vlm_provider="openai",
    vlm_model="gpt-5",
    vlm_api_key="your_api_key",
    
    # Layout Detection Settings
    layout_model_name="PP-DocLayout_plus-L",
    dpi=200,
    min_score=0.0,
    
    # OCR Settings
    ocr_lang="eng",
    ocr_psm=4,
    ocr_oem=3,
    ocr_extra_config="",
    
    # Output Settings
    box_separator="\n"
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
parser = EnhancedPDFParser(
    # Image Restoration Settings
    use_image_restoration=True,
    restoration_task="dewarping",      # Correct perspective distortion
    restoration_device="cuda",         # Use GPU for faster processing
    restoration_dpi=300,               # Higher DPI for better quality
    
    # VLM Settings
    use_vlm=True,
    vlm_provider="openai",
    vlm_model="gpt-4-vision",
    vlm_api_key="your_api_key",
    
    # Layout Detection Settings
    layout_model_name="PP-DocLayout_plus-L",
    dpi=200,
    min_score=0.5,
    
    # OCR Settings
    ocr_lang="eng",
    ocr_psm=6
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
parser = ChartTablePDFParser(
    # Extraction Settings
    extract_charts=True,
    extract_tables=True,
    
    # VLM Settings
    use_vlm=True,
    vlm_provider="openai",
    vlm_model="gpt-5",
    vlm_api_key="your_api_key",
    
    # Layout Detection Settings
    layout_model_name="PP-DocLayout_plus-L",
    dpi=200,
    min_score=0.0
)
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
2. **Tables & Charts Tab**: Specialized extraction with VLM integration
3. **DocRes Tab**: Image restoration with before/after comparison
4. **Enhanced Parser Tab**: Enhanced parsing with DocRes integration

## Command Line Interface

Doctra includes a powerful CLI for batch processing and automation.

#### Available Commands:

```bash
# Full document parsing
doctra parse document.pdf

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

# Initialize parser
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

## 📖 Usage Examples

### Example 1: Basic Document Processing

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser

# Initialize parser
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

# Initialize enhanced parser with image restoration
parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="dewarping",  # Correct perspective distortion
    restoration_device="cuda",    # Use GPU for faster processing
    use_vlm=True,
    vlm_provider="openai",
    vlm_api_key="your_api_key"
)

# Process scanned document with enhancement
parser.parse("scanned_document.pdf")

# Output will include:
# - Enhanced PDF with restored images
# - All standard parsing outputs
# - Improved OCR accuracy due to restoration
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

### Example 4: Chart and Table Extraction with VLM

```python
from doctra.parsers.table_chart_extractor import ChartTablePDFParser

# Initialize parser with VLM
parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=True,
    use_vlm=True,
    vlm_provider="openai",
    vlm_api_key="your_gemini_api_key"
)

# Process document
parser.parse("data_report.pdf", output_base_dir="extracted_data")

# Output will include:
# - Cropped chart and table images
# - Structured data in Excel format
# - Markdown tables with extracted data
```

### Example 5: Web UI Usage

```python
from doctra.ui.app import launch_ui

# Launch the web interface
launch_ui()

# Or build the interface programmatically
from doctra.ui.app import build_demo
demo = build_demo()
demo.launch(share=True)  # Share publicly
```

### Example 6: Command Line Usage

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

### Example 7: Layout Visualization

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser

# Initialize parser
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
- High-quality text extraction using Tesseract
- Support for multiple languages
- Configurable OCR parameters

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
- Vision Language Model support for structured data extraction
- Multiple provider options (OpenAI, Gemini, Anthropic, OpenRouter)
- Automatic conversion of charts and tables to structured formats

### 📊 Multiple Output Formats
- **Markdown**: Human-readable document with embedded images and tables
- **Excel**: Structured data in spreadsheet format
- **JSON**: Programmatically accessible structured data
- **HTML**: Interactive web-ready documents
- **Images**: High-quality cropped visual elements

### 🖥️ User Interfaces
- **Web UI**: Gradio-based interface with drag & drop functionality
- **Command Line**: Powerful CLI for batch processing and automation
- **Multiple Tabs**: Full parsing, enhanced parsing, chart/table extraction, and image restoration

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
