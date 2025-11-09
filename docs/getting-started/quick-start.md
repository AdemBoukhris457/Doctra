# Quick Start

This guide will get you started with Doctra in just a few minutes.

## Your First Document Parse

Let's parse a PDF document and extract its content:

```python
from doctra import StructuredPDFParser

# Initialize the parser
parser = StructuredPDFParser()

# Parse a document
parser.parse("document.pdf")
```

That's it! Doctra will:

1. Detect the document layout
2. Extract text using OCR
3. Save images of figures, charts, and tables
4. Generate a Markdown file with all content

## Understanding the Output

After parsing, you'll find the following structure:

```
outputs/
└── document/
    ├── full_parse/
    │   ├── result.md          # Markdown with all content
    │   ├── result.html        # HTML version
    │   └── images/            # Extracted visual elements
    │       ├── figures/       # Document figures
    │       ├── charts/        # Charts and graphs
    │       └── tables/        # Table images
```

## Basic Examples

### Parse with Custom Output Directory

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser()
parser.parse("document.pdf", output_base_dir="my_outputs")
```

### Parse Scanned Documents

For scanned or low-quality documents, use the enhanced parser:

```python
from doctra import EnhancedPDFParser

parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="appearance"  # Improve overall appearance
)

parser.parse("scanned_document.pdf")
```

### Extract Only Charts and Tables

If you only need charts and tables:

```python
from doctra import ChartTablePDFParser

parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=True
)

parser.parse("data_report.pdf")
```

## Using Vision Language Models

To convert charts and tables to structured data, add VLM support:

```python
from doctra import StructuredPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

# Initialize VLM engine
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-api-key-here"
)

# Pass VLM engine to parser
parser = StructuredPDFParser(vlm=vlm_engine)

parser.parse("document.pdf")
```

This will generate:

- `tables.xlsx` - Excel file with extracted table data
- `tables.html` - HTML tables for web viewing
- `vlm_items.json` - JSON with structured data

!!! tip "VLM Providers"
    Doctra supports multiple VLM providers:
    
    - `"openai"` - GPT-4 Vision and GPT-4o
    - `"gemini"` - Google's Gemini models
    - `"anthropic"` - Claude with vision
    - `"openrouter"` - Access multiple models
    - `"qianfan"` - Baidu AI Cloud ERNIE models
    - `"ollama"` - Local models (no API key required)

## Document Restoration

Enhance document quality before parsing:

```python
from doctra import DocResEngine

# Initialize restoration engine
docres = DocResEngine(device="cuda")  # Use GPU for speed

# Restore a single image
restored_img, metadata = docres.restore_image(
    image="blurry_doc.jpg",
    task="deblurring"
)

# Or enhance an entire PDF
docres.restore_pdf(
    pdf_path="low_quality.pdf",
    output_path="enhanced.pdf",
    task="appearance"
)
```

Available restoration tasks:

| Task | Description |
|------|-------------|
| `appearance` | General appearance enhancement |
| `dewarping` | Correct perspective distortion |
| `deshadowing` | Remove shadows |
| `deblurring` | Reduce blur |
| `binarization` | Convert to black and white |
| `end2end` | Complete restoration pipeline |

## Using the Web UI

Launch the graphical interface for easy document processing:

```python
from doctra import launch_ui

# Launch web interface
launch_ui()
```

Or from the command line:

```bash
python -m doctra.ui.app
```

Then open your browser to the displayed URL (typically `http://127.0.0.1:7860`).

## Command Line Interface

Doctra provides a powerful CLI:

```bash
# Parse a document
doctra parse document.pdf

# Enhanced parsing
doctra enhance document.pdf --restoration-task appearance

# Extract charts and tables
doctra extract both document.pdf --use-vlm

# Visualize layout
doctra visualize document.pdf
```

See the [CLI Reference](../interfaces/cli.md) for all available commands.

## Layout Visualization

Visualize how Doctra detects document elements:

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

# Display layout detection results
parser.display_pages_with_boxes(
    pdf_path="document.pdf",
    num_pages=3,  # First 3 pages
    save_path="layout_viz.png"
)
```

This creates a visual representation showing:

- Detected text regions (blue boxes)
- Tables (red boxes)
- Charts (green boxes)
- Figures (orange boxes)
- Confidence scores for each element

## Configuration Options

### Parser Configuration

```python
from doctra import StructuredPDFParser
from doctra.engines.ocr import PytesseractOCREngine

# Initialize OCR engine
tesseract_ocr = PytesseractOCREngine(lang="eng", psm=6, oem=3)

parser = StructuredPDFParser(
    # Layout Detection
    layout_model_name="PP-DocLayout_plus-L",  # Model choice
    dpi=200,  # Image resolution
    min_score=0.5,  # Confidence threshold
    
    # OCR Engine
    ocr_engine=tesseract_ocr,
    
    # Output
    box_separator="\n"  # Separator between elements
)
```

### Enhanced Parser Configuration

```python
from doctra import EnhancedPDFParser

# Initialize VLM engine (optional)
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-key"
)

parser = EnhancedPDFParser(
    # Image Restoration
    use_image_restoration=True,
    restoration_task="dewarping",
    restoration_device="cuda",  # or "cpu"
    restoration_dpi=300,
    
    # VLM Engine (pass initialized engine instance)
    vlm=vlm_engine,
    
    # All StructuredPDFParser options also available
)
```

## Common Patterns

### Batch Processing

```python
import os
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

# Process all PDFs in a directory
pdf_dir = "documents"
for filename in os.listdir(pdf_dir):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_dir, filename)
        print(f"Processing {filename}...")
        parser.parse(pdf_path)
```

### Error Handling

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

try:
    parser.parse("document.pdf")
except FileNotFoundError:
    print("Document not found!")
except Exception as e:
    print(f"Error parsing document: {e}")
```

### Progress Tracking

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

# Progress bars are shown automatically
parser.parse("large_document.pdf")
```

## Next Steps

Now that you've learned the basics:

1. **Dive Deeper**: Read the [User Guide](../user-guide/core-concepts.md) for detailed explanations
2. **Explore Parsers**: Learn about each parser's capabilities
3. **Advanced Examples**: Check out [Advanced Examples](../examples/advanced-examples.md)
4. **API Reference**: Browse the [API Documentation](../api/parsers.md)

## Getting Help

- :material-book-open: Read the full [documentation](../index.md)
- :material-github: Check [GitHub issues](https://github.com/AdemBoukhris457/Doctra/issues)
- :material-message-question: Ask questions in discussions

## Common Issues

### "Poppler not found" Error

Install Poppler (see [Installation](installation.md#system-dependencies)).

### Low OCR Accuracy

Try the enhanced parser with image restoration:

```python
from doctra import EnhancedPDFParser

parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="appearance"
)
```

### Slow Processing

Use GPU acceleration:

```python
parser = EnhancedPDFParser(
    restoration_device="cuda"  # Use GPU
)
```

Or reduce DPI:

```python
parser = StructuredPDFParser(
    dpi=150  # Lower resolution
)
```

