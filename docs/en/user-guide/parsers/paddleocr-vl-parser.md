# PaddleOCRVL PDF Parser

Guide to using the `PaddleOCRVLPDFParser` for end-to-end document parsing with Vision-Language Model capabilities.

## Installation Requirements

Before using the `PaddleOCRVLPDFParser`, you need to install the required dependencies:

```bash
pip install -U "paddleocr[doc-parser]"
```

Additionally, you need to install platform-specific safetensors wheels:

**For Linux systems:**
```bash
python -m pip install https://paddle-whl.bj.bcebos.com/nightly/cu126/safetensors/safetensors-0.6.2.dev0-cp38-abi3-linux_x86_64.whl
```

**For Windows systems:**
```bash
python -m pip install https://xly-devops.cdn.bcebos.com/safetensors-nightly/safetensors-0.6.2.dev0-cp38-abi3-win_amd64.whl
```

!!! warning "Required Before Use"
    These installation steps are **required** before using `PaddleOCRVLPDFParser`. Without them, you may encounter import errors.

## Overview

The `PaddleOCRVLPDFParser` uses PaddleOCRVL (Vision-Language Model) for comprehensive document understanding. It combines PaddleOCRVL's advanced document parsing capabilities with DocRes image restoration and split table merging, providing a complete solution for complex document processing tasks.

## Key Features

- **End-to-End Parsing**: Uses PaddleOCRVL for complete document understanding in a single pass
- **Chart Recognition**: Automatically detects and converts charts to structured table format
- **Document Restoration**: Optional DocRes integration for enhanced document quality
- **Split Table Merging**: Automatically detects and merges tables split across pages
- **Structured Output**: Generates Markdown, HTML, and Excel files with tables and charts
- **Multiple Element Types**: Handles headers, text, tables, charts, footnotes, figure titles, and more

## Basic Usage

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

## Configuration Options

### DocRes Image Restoration

```python
parser = PaddleOCRVLPDFParser(
    # Image Restoration Settings
    use_image_restoration=True,
    restoration_task="appearance",    # Options: appearance, dewarping, deshadowing, deblurring, binarization, end2end
    restoration_device="cuda",        # or "cpu" or None for auto-detect
    restoration_dpi=300,              # DPI for restoration processing
)
```

### PaddleOCRVL Settings

```python
parser = PaddleOCRVLPDFParser(
    # PaddleOCRVL Configuration
    use_chart_recognition=True,       # Enable chart recognition and extraction
    use_doc_orientation_classify=True, # Enable document orientation classification
    use_doc_unwarping=True,           # Enable document unwarping
    use_layout_detection=True,        # Enable layout detection
    device="gpu",                     # "gpu" or "cpu"
)
```

### Split Table Merging

```python
parser = PaddleOCRVLPDFParser(
    # Split Table Merging Settings
    merge_split_tables=True,          # Enable split table detection and merging
    bottom_threshold_ratio=0.20,      # Ratio for "too close to bottom" detection
    top_threshold_ratio=0.15,         # Ratio for "too close to top" detection
    max_gap_ratio=0.25,               # Maximum allowed gap between tables
    column_alignment_tolerance=10.0,  # Pixel tolerance for column alignment
    min_merge_confidence=0.65         # Minimum confidence score for merging
)
```

## Advanced Configuration

```python
from doctra import PaddleOCRVLPDFParser

parser = PaddleOCRVLPDFParser(
    # DocRes Image Restoration Settings
    use_image_restoration=True,
    restoration_task="end2end",       # Full restoration pipeline
    restoration_device="cuda",        # Force GPU usage
    restoration_dpi=300,              # Higher DPI for better quality
    
    # PaddleOCRVL Settings
    use_chart_recognition=True,
    use_doc_orientation_classify=True,  # Enable orientation detection
    use_doc_unwarping=True,            # Enable unwarping
    use_layout_detection=True,
    device="gpu",
    
    # Split Table Merging Settings
    merge_split_tables=True,
    bottom_threshold_ratio=0.20,
    top_threshold_ratio=0.15,
    max_gap_ratio=0.25,
    column_alignment_tolerance=10.0,
    min_merge_confidence=0.65
)

# Parse with custom output directory
parser.parse("document.pdf", output_dir="custom_output")
```

## Output Structure

The parser generates output in `outputs/{document_name}/paddleocr_vl_parse/` with:

- **result.md**: Markdown file with all extracted content
- **result.html**: HTML file with formatted output
- **tables.xlsx**: Excel file containing all tables and charts as structured data
- **tables.html**: HTML file with structured tables and charts
- **enhanced_pages/**: Directory with DocRes-enhanced page images (if restoration enabled)
- **tables/**: Directory with merged table images (if split tables detected)

## Extracted Content Types

The parser extracts various document elements:

- **Headers**: Document titles and section headers
- **Text**: Paragraphs and body text
- **Tables**: Extracted as HTML and converted to Excel format
- **Charts**: Converted from visual format to structured table data (pipe-delimited format)
- **Footnotes**: Vision-based footnote detection (`vision_footnote`)
- **Figure Titles**: Captions and figure descriptions
- **Numbers**: Standalone numbers (like page numbers)

## Chart Recognition

PaddleOCRVL automatically recognizes charts and converts them to structured table format. Charts are extracted in a pipe-delimited format and then converted to Excel-compatible tables.

Example chart output:
```
Category | Percentage
PCT system fees | 358.6%
Madrid system fees | 76.2%
```

This is automatically converted to a structured table with headers and rows for inclusion in the Excel output.

## Split Table Merging

The parser includes automatic detection and merging of tables that are split across multiple pages. This feature uses the same two-phase approach as other parsers:

1. **Phase 1: Proximity Detection** - Fast spatial heuristics
2. **Phase 2: Structural Validation** - Deep structural analysis using LSD

For detailed information, see the [Split Table Merging Guide](../features/split-table-merging.md).

## DocRes Restoration Tasks

| Task | Description | Best For |
|------|-------------|----------|
| `appearance` | General appearance enhancement | Most documents (default) |
| `dewarping` | Correct perspective distortion | Scanned documents with perspective issues |
| `deshadowing` | Remove shadows and lighting artifacts | Documents with shadow problems |
| `deblurring` | Reduce blur and improve sharpness | Blurry or low-quality scans |
| `binarization` | Convert to black and white | Documents needing clean binarization |
| `end2end` | Complete restoration pipeline | Severely degraded documents |

## Parameter Reference

### DocRes Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_image_restoration` | bool | `True` | Enable/disable DocRes image restoration |
| `restoration_task` | str | `"appearance"` | DocRes restoration task to use |
| `restoration_device` | str | `None` | Device for DocRes ("cuda", "cpu", or None for auto-detect) |
| `restoration_dpi` | int | `200` | DPI for restoration processing |

### PaddleOCRVL Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_chart_recognition` | bool | `True` | Enable chart recognition and extraction |
| `use_doc_orientation_classify` | bool | `False` | Enable document orientation classification |
| `use_doc_unwarping` | bool | `False` | Enable document unwarping |
| `use_layout_detection` | bool | `True` | Enable layout detection |
| `device` | str | `"gpu"` | Device for PaddleOCRVL processing ("gpu" or "cpu") |

### Split Table Merging Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `merge_split_tables` | bool | `True` | Enable/disable split table detection |
| `bottom_threshold_ratio` | float | `0.20` | Ratio for detecting tables near bottom of page (0-1) |
| `top_threshold_ratio` | float | `0.15` | Ratio for detecting tables near top of page (0-1) |
| `max_gap_ratio` | float | `0.25` | Maximum allowed gap between tables |
| `column_alignment_tolerance` | float | `10.0` | Pixel tolerance for column alignment validation |
| `min_merge_confidence` | float | `0.65` | Minimum confidence score (0-1) required to merge tables |

## When to Use

Use `PaddleOCRVLPDFParser` for:

- **Complex Documents**: Documents with multiple content types (text, tables, charts, figures)
- **Chart Extraction**: When you need charts converted to structured data
- **End-to-End Processing**: When you want a single-pass solution for document understanding
- **Quality Enhancement**: When documents need restoration before processing
- **Split Tables**: Documents with tables spanning multiple pages
- **Comprehensive Output**: When you need all content types in structured formats

Consider other parsers when:

- **Simple Text Extraction**: Use `StructuredPDFParser` for basic text extraction
- **Only Visual Elements**: Use `ChartTablePDFParser` for charts/tables only
- **No Restoration Needed**: Use `StructuredPDFParser` if document quality is good

## Example: Financial Report Processing

```python
from doctra import PaddleOCRVLPDFParser

# Initialize parser for financial reports
parser = PaddleOCRVLPDFParser(
    use_image_restoration=True,
    restoration_task="appearance",
    use_chart_recognition=True,      # Important for financial charts
    merge_split_tables=True,         # Financial tables often span pages
    device="gpu"
)

# Process financial report
parser.parse("annual_report.pdf")

# Output includes:
# - All text content
# - Financial tables (including merged split tables)
# - Charts converted to Excel format
# - All in structured Excel file (tables.xlsx)
```

## See Also

- [DocRes Engine](../engines/docres-engine.md) - Image restoration details
- [Split Table Merging Guide](../features/split-table-merging.md) - Comprehensive guide to split table detection
- [Structured Parser](structured-parser.md) - Base parser for comparison
- [API Reference](../../api/parsers.md) - Complete API documentation

