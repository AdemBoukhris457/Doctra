# Basic Usage Examples

Practical examples for common Doctra use cases.

## Example 1: Parse a Simple PDF

```python
from doctra import StructuredPDFParser

# Initialize parser
parser = StructuredPDFParser()

# Parse document
parser.parse("document.pdf")

# Output saved to: outputs/document/full_parse/
```

## Example 2: Parse with Custom Settings

```python
from doctra import StructuredPDFParser
from doctra.engines.ocr import PytesseractOCREngine

# Initialize OCR engine
tesseract_ocr = PytesseractOCREngine(lang="eng", psm=4, oem=3)

parser = StructuredPDFParser(
    dpi=250,  # Higher quality
    min_score=0.7,  # More confident detections
    ocr_engine=tesseract_ocr
)

parser.parse("document.pdf", output_base_dir="my_results")
```

## Example 3: Enhanced Parsing for Scanned Documents

```python
from doctra import EnhancedPDFParser

parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="appearance",
    restoration_device="cuda"  # Use GPU
)

parser.parse("scanned_document.pdf")
```

## Example 4: Extract Structured Data with VLM

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser(
    use_vlm=True,
    vlm_provider="openai",
    vlm_api_key="your-api-key-here"
)

parser.parse("data_report.pdf")

# Output includes:
# - tables.xlsx with extracted data
# - tables.html with formatted tables
# - vlm_items.json with structured data
```

## Example 5: Extract Only Charts

```python
from doctra import ChartTablePDFParser

parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=False
)

parser.parse("presentation.pdf")
```

## Example 6: Visualize Layout Detection

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

# Display layout detection
parser.display_pages_with_boxes(
    pdf_path="document.pdf",
    num_pages=3,
    save_path="layout_visualization.png"
)
```

## Example 7: Standalone Image Restoration

```python
from doctra import DocResEngine

# Initialize restoration engine
engine = DocResEngine(device="cuda")

# Restore a single image
restored_img, metadata = engine.restore_image(
    image="blurry_document.jpg",
    task="deblurring"
)

# Save result
restored_img.save("restored.jpg")
print(f"Processed in {metadata['processing_time']:.2f}s")
```

## Example 8: Batch Processing

```python
import os
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

# Process all PDFs in directory
pdf_directory = "documents"
for filename in os.listdir(pdf_directory):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_directory, filename)
        print(f"Processing {filename}...")
        parser.parse(pdf_path)
        print(f"Completed {filename}")
```

## Example 9: Error Handling

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

try:
    parser.parse("document.pdf")
    print("Processing successful!")
except FileNotFoundError:
    print("Error: PDF file not found")
except Exception as e:
    print(f"Error during processing: {e}")
```

## Example 10: Using the Web UI

```python
from doctra import launch_ui

# Launch web interface
launch_ui()

# Opens browser at http://127.0.0.1:7860
```

## Next Steps

- [Advanced Examples](advanced-examples.md) - Complex use cases
- [Integration Examples](integration.md) - Integrate with other tools
- [API Reference](../api/parsers.md) - Detailed API documentation

