# Parsers API Reference

Complete API documentation for all Doctra parsers.

## StructuredPDFParser

The base parser for comprehensive PDF document processing.

::: doctra.parsers.structured_pdf_parser.StructuredPDFParser
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

---

## EnhancedPDFParser

Enhanced parser with image restoration capabilities.

::: doctra.parsers.enhanced_pdf_parser.EnhancedPDFParser
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

---

## ChartTablePDFParser

Specialized parser for extracting charts and tables.

::: doctra.parsers.table_chart_extractor.ChartTablePDFParser
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

---

## StructuredDOCXParser

Comprehensive parser for Microsoft Word documents (.docx files).

::: doctra.parsers.structured_docx_parser.StructuredDOCXParser
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

---

## Quick Reference

### StructuredPDFParser

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser(
    # Layout Detection
    layout_model_name: str = "PP-DocLayout_plus-L",
    dpi: int = 200,
    min_score: float = 0.0,
    
    # OCR Settings
    ocr_lang: str = "eng",
    ocr_psm: int = 4,
    ocr_oem: int = 3,
    ocr_extra_config: str = "",
    
    # VLM Settings
    use_vlm: bool = False,
    vlm_provider: str = None,
    vlm_api_key: str = None,
    vlm_model: str = None,
    
    # Output Settings
    box_separator: str = "\n"
)

# Parse document
parser.parse(
    pdf_path: str,
    output_base_dir: str = "outputs"
)

# Visualize layout
parser.display_pages_with_boxes(
    pdf_path: str,
    num_pages: int = 3,
    cols: int = 2,
    page_width: int = 800,
    spacing: int = 40,
    save_path: str = None
)
```

### EnhancedPDFParser

```python
from doctra import EnhancedPDFParser

parser = EnhancedPDFParser(
    # Image Restoration
    use_image_restoration: bool = True,
    restoration_task: str = "appearance",
    restoration_device: str = None,
    restoration_dpi: int = 200,
    
    # All StructuredPDFParser parameters...
)

# Parse with enhancement
parser.parse(
    pdf_path: str,
    output_base_dir: str = "outputs"
)
```

### ChartTablePDFParser

```python
from doctra import ChartTablePDFParser

parser = ChartTablePDFParser(
    # Extraction Settings
    extract_charts: bool = True,
    extract_tables: bool = True,
    
    # VLM Settings
    use_vlm: bool = False,
    vlm_provider: str = None,
    vlm_api_key: str = None,
    vlm_model: str = None,
    
    # Layout Detection
    layout_model_name: str = "PP-DocLayout_plus-L",
    dpi: int = 200,
    min_score: float = 0.0
)

# Extract charts/tables
parser.parse(
    pdf_path: str,
    output_base_dir: str = "outputs"
)
```

### StructuredDOCXParser

```python
from doctra import StructuredDOCXParser

parser = StructuredDOCXParser(
    # VLM Settings
    use_vlm: bool = False,
    vlm_provider: str = None,
    vlm_api_key: str = None,
    vlm_model: str = None,
    
    # Processing Options
    extract_images: bool = True,
    preserve_formatting: bool = True,
    table_detection: bool = True,
    export_excel: bool = True
)

# Parse DOCX document
parser.parse(
    docx_path: str
)
```

## Parameter Reference

### Layout Detection Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `layout_model_name` | str | "PP-DocLayout_plus-L" | PaddleOCR layout detection model |
| `dpi` | int | 200 | Image resolution for rendering PDF pages |
| `min_score` | float | 0.0 | Minimum confidence score for detected elements |

### OCR Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ocr_lang` | str | "eng" | Tesseract language code |
| `ocr_psm` | int | 4 | Page segmentation mode |
| `ocr_oem` | int | 3 | OCR engine mode |
| `ocr_extra_config` | str | "" | Additional Tesseract configuration |

### VLM Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_vlm` | bool | False | Enable VLM processing |
| `vlm_provider` | str | None | Provider: "openai", "gemini", "anthropic", "openrouter" |
| `vlm_api_key` | str | None | API key for the VLM provider |
| `vlm_model` | str | None | Specific model to use (provider-dependent) |

### Image Restoration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_image_restoration` | bool | True | Enable image restoration |
| `restoration_task` | str | "appearance" | Restoration task type |
| `restoration_device` | str | None | Device: "cuda", "cpu", or None (auto-detect) |
| `restoration_dpi` | int | 200 | DPI for restoration processing |

### Extraction Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `extract_charts` | bool | True | Extract chart elements |
| `extract_tables` | bool | True | Extract table elements |

### DOCX Processing Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `extract_images` | bool | True | Extract embedded images from DOCX |
| `preserve_formatting` | bool | True | Preserve text formatting in output |
| `table_detection` | bool | True | Detect and extract tables |
| `export_excel` | bool | True | Export tables to Excel file |

### Output Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `box_separator` | str | "\n" | Separator between detected elements |

## Return Values

### parse() Method

Returns: `None`

Generates output files in the specified `output_base_dir`:

```
outputs/
└── <document_name>/
    ├── full_parse/  # or 'enhanced_parse/', 'structured_parsing/'
    │   ├── result.md
    │   ├── result.html
    │   ├── tables.xlsx  # If VLM enabled
    │   ├── tables.html  # If VLM enabled
    │   ├── vlm_items.json  # If VLM enabled
    │   └── images/
    │       ├── figures/
    │       ├── charts/
    │       └── tables/
```

For DOCX parsing, generates:

```
outputs/
└── <document_name>/
    ├── document.md
    ├── document.html
    ├── tables.xlsx  # With Table of Contents
    └── images/
        ├── image1.png
        ├── image2.jpg
        └── ...
```

### display_pages_with_boxes() Method

Returns: `None`

Displays or saves visualization of layout detection.

## Error Handling

All parsers may raise:

- `FileNotFoundError`: PDF file not found
- `ValueError`: Invalid parameter values
- `RuntimeError`: Processing errors (e.g., Poppler not found)
- `APIError`: VLM API errors (when VLM enabled)

Example error handling:

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

try:
    parser.parse("document.pdf")
except FileNotFoundError:
    print("PDF file not found!")
except ValueError as e:
    print(f"Invalid parameter: {e}")
except RuntimeError as e:
    print(f"Processing error: {e}")
```

## Examples

See the [Examples](../examples/basic-usage.md) section for detailed usage examples.

