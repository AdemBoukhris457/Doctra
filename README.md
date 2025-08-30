# 🚀 **Doctra - Document Parser Library** 📑🔎

![Doctra Logo](https://raw.githubusercontent.com/AdemBoukhris457/Doctra/main/assets/Doctra_Logo.png)

<div align="center">

[![stars](https://img.shields.io/github/stars/AdemBoukhris457/Doctra.svg)](https://github.com/AdemBoukhris457/Doctra)
[![forks](https://img.shields.io/github/forks/AdemBoukhris457/Doctra.svg)](https://github.com/AdemBoukhris457/Doctra)
[![PyPI version](https://img.shields.io/pypi/v/doctra)](https://pypi.org/project/doctra/)
</div>

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Components](#core-components)
  - [StructuredPDFParser](#structuredpdfparser)
  - [ChartTablePDFParser](#charttablepdfparser)
- [Visualization](#visualization)
- [Usage Examples](#usage-examples)
- [Features](#features)
- [Requirements](#requirements)

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

### Example 2: Chart and Table Extraction with VLM

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

### Example 3: Custom Configuration

```python
from doctra.parsers.structured_pdf_parser import StructuredPDFParser

# Custom configuration for high-quality processing
parser = StructuredPDFParser(
    use_vlm=True,
    vlm_provider="openai",
    vlm_api_key="your_openai_api_key",
    vlm__model="gpt-5",
    layout_model_name="PP-DocLayout_plus-L",
    dpi=300,  # Higher DPI for better quality
    min_score=0.5,  # Higher confidence threshold
    ocr_lang="eng",
    ocr_psm=6,  # Uniform block of text
    box_separator="\n\n"  # Double line breaks between elements
)

parser.parse("complex_document.pdf")
```

### Example 4: Layout Visualization

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

### 🤖 VLM Integration
- Vision Language Model support for structured data extraction
- Multiple provider options (Gemini, OpenAI)
- Automatic conversion of charts and tables to structured formats

### 📊 Multiple Output Formats
- **Markdown**: Human-readable document with embedded images and tables
- **Excel**: Structured data in spreadsheet format
- **JSON**: Programmatically accessible structured data
- **Images**: High-quality cropped visual elements

### ⚙️ Flexible Configuration
- Extensive customization options
- Performance tuning parameters
- Output format selection

## 📋 Requirements

### Core Dependencies
- **PaddleOCR**: Document layout detection
- **Outlines**: Structured output generation
- **Tesseract**: OCR text extraction
- **Pillow**: Image processing
- **OpenCV**: Computer vision operations
- **Pandas**: Data manipulation
- **OpenPyXL**: Excel file generation
- **Google Generative AI**: For Gemini VLM integration
- **OpenAI**: For GPT-5 VLM integration