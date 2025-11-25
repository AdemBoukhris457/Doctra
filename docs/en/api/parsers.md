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

## PaddleOCRVLPDFParser

End-to-end document parser using PaddleOCRVL Vision-Language Model.

::: doctra.parsers.paddleocr_vl_parser.PaddleOCRVLPDFParser
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
from doctra.engines.ocr import PytesseractOCREngine, PaddleOCREngine
from doctra.engines.vlm.service import VLMStructuredExtractor

# Initialize OCR engine (optional - defaults to PyTesseract if None)
ocr_engine = PytesseractOCREngine(lang="eng", psm=4, oem=3)

# Initialize VLM engine (optional - None to disable VLM)
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    vlm_model="gpt-4o",  # Optional
    api_key="your-api-key"
)

parser = StructuredPDFParser(
    # Layout Detection
    layout_model_name: str = "PP-DocLayout_plus-L",
    dpi: int = 200,
    min_score: float = 0.0,
    
    # OCR Engine (pass initialized engine instance)
    ocr_engine: Optional[Union[PytesseractOCREngine, PaddleOCREngine]] = None,
    
    # VLM Engine (pass initialized engine instance)
    vlm: Optional[VLMStructuredExtractor] = None,
    
    # Split Table Merging
    merge_split_tables: bool = False,
    bottom_threshold_ratio: float = 0.20,
    top_threshold_ratio: float = 0.15,
    max_gap_ratio: float = 0.25,
    column_alignment_tolerance: float = 10.0,
    min_merge_confidence: float = 0.65,
    
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
from doctra.engines.vlm.service import VLMStructuredExtractor

# Initialize VLM engine (optional)
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-api-key"
)

parser = EnhancedPDFParser(
    # Image Restoration
    use_image_restoration: bool = True,
    restoration_task: str = "appearance",
    restoration_device: str = None,
    restoration_dpi: int = 200,
    
    # VLM Engine (pass initialized engine instance)
    vlm: Optional[VLMStructuredExtractor] = None,
    
    # Layout Detection
    layout_model_name: str = "PP-DocLayout_plus-L",
    dpi: int = 200,
    min_score: float = 0.0,
    
    # OCR Engine (optional)
    ocr_engine: Optional[Union[PytesseractOCREngine, PaddleOCREngine]] = None,
    
    # Split Table Merging
    merge_split_tables: bool = False,
    bottom_threshold_ratio: float = 0.20,
    top_threshold_ratio: float = 0.15,
    max_gap_ratio: float = 0.25,
    column_alignment_tolerance: float = 10.0,
    min_merge_confidence: float = 0.65,
    
    # Output Settings
    box_separator: str = "\n"
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
from doctra.engines.vlm.service import VLMStructuredExtractor

# Initialize VLM engine (optional)
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-api-key"
)

parser = ChartTablePDFParser(
    # Extraction Settings
    extract_charts: bool = True,
    extract_tables: bool = True,
    
    # VLM Engine (pass initialized engine instance)
    vlm: Optional[VLMStructuredExtractor] = None,
    
    # Layout Detection
    layout_model_name: str = "PP-DocLayout_plus-L",
    dpi: int = 200,
    min_score: float = 0.0,
    
    # Split Table Merging
    merge_split_tables: bool = False,
    bottom_threshold_ratio: float = 0.20,
    top_threshold_ratio: float = 0.15,
    max_gap_ratio: float = 0.25,
    column_alignment_tolerance: float = 10.0,
    min_merge_confidence: float = 0.65,
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
from doctra.engines.vlm.service import VLMStructuredExtractor

# Initialize VLM engine (optional)
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-api-key"
)

parser = StructuredDOCXParser(
    # VLM Engine (pass initialized engine instance)
    vlm: Optional[VLMStructuredExtractor] = None,
    
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
| `ocr_engine` | `Optional[Union[PytesseractOCREngine, PaddleOCREngine]]` | `None` | OCR engine instance. If `None`, creates a default `PytesseractOCREngine` with lang="eng", psm=4, oem=3 |

**OCR Engine Configuration:**

OCR engines must be initialized externally and passed to the parser. This uses a dependency injection pattern for clearer API design.

**PytesseractOCREngine Parameters:**
- `lang` (str, default: "eng"): Tesseract language code (e.g., "eng", "fra", "spa", "deu", or multiple: "eng+fra")
- `psm` (int, default: 4): Page segmentation mode (3=Automatic, 4=Single column, 6=Uniform block, 11=Sparse text, 12=Sparse with OSD)
- `oem` (int, default: 3): OCR engine mode (0=Legacy, 1=Neural nets LSTM, 3=Default both)
- `extra_config` (str, default: ""): Additional Tesseract configuration string

**PaddleOCREngine Parameters:**
- `device` (str, default: "gpu"): Device for OCR processing ("cpu" or "gpu")
- `use_doc_orientation_classify` (bool, default: False): Enable document orientation classification
- `use_doc_unwarping` (bool, default: False): Enable text image rectification
- `use_textline_orientation` (bool, default: False): Enable text line orientation classification

**Example:**
```python
from doctra.engines.ocr import PytesseractOCREngine, PaddleOCREngine

# PyTesseract
tesseract_ocr = PytesseractOCREngine(lang="eng", psm=4, oem=3)
parser = StructuredPDFParser(ocr_engine=tesseract_ocr)

# PaddleOCR
paddle_ocr = PaddleOCREngine(device="gpu")
parser = StructuredPDFParser(ocr_engine=paddle_ocr)
```

**Note**: When using PaddleOCR, PaddleOCR 3.0's PP-OCRv5_server model is used by default. Models are automatically downloaded on first use.

### VLM Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `vlm` | `Optional[VLMStructuredExtractor]` | `None` | VLM engine instance. If `None`, VLM processing is disabled. |

**VLM Engine Configuration:**

VLM engines must be initialized externally and passed to the parser. This uses a dependency injection pattern for clearer API design.

**VLMStructuredExtractor Parameters:**
- `vlm_provider` (str, required): VLM provider to use ("openai", "gemini", "anthropic", "openrouter", "qianfan", "ollama")
- `vlm_model` (str, optional): Model name to use (defaults to provider-specific defaults)
- `api_key` (str, optional): API key for the VLM provider (required for all providers except Ollama)

**Example:**
```python
from doctra.engines.vlm.service import VLMStructuredExtractor

# Initialize VLM engine
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    vlm_model="gpt-4o",  # Optional
    api_key="your-api-key"
)

# Pass to parser
parser = StructuredPDFParser(vlm=vlm_engine)
```

### Image Restoration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_image_restoration` | bool | True | Enable image restoration |
| `restoration_task` | str | "appearance" | Restoration task type |
| `restoration_device` | str | None | Device: "cuda", "cpu", or None (auto-detect) |
| `restoration_dpi` | int | 200 | DPI for restoration processing |

### Split Table Merging Parameters

Available for both `StructuredPDFParser` and `EnhancedPDFParser`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `merge_split_tables` | bool | False | Enable automatic detection and merging of tables split across pages |
| `bottom_threshold_ratio` | float | 0.20 | Ratio (0-1) for detecting tables near bottom of page. Tables within this ratio from the bottom are considered candidates. |
| `top_threshold_ratio` | float | 0.15 | Ratio (0-1) for detecting tables near top of page. Tables within this ratio from the top are considered candidates. |
| `max_gap_ratio` | float | 0.25 | Maximum allowed gap between table segments as ratio of page height. Accounts for headers, footers, and page margins. |
| `column_alignment_tolerance` | float | 10.0 | Pixel tolerance for column alignment validation when comparing table structures. |
| `min_merge_confidence` | float | 0.65 | Minimum confidence score (0-1) required to merge two table segments. Higher values are more conservative. |

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

