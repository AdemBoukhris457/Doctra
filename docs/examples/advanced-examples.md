# Advanced Examples

Advanced usage patterns and integration examples.

## Multi-Stage Processing Pipeline

```python
from doctra import DocResEngine, StructuredPDFParser

# Stage 1: Restore document
engine = DocResEngine(device="cuda")
enhanced_pdf = engine.restore_pdf(
    pdf_path="low_quality.pdf",
    output_path="enhanced.pdf",
    task="appearance"
)

# Stage 2: Parse enhanced document
parser = StructuredPDFParser(
    use_vlm=True,
    vlm_provider="openai",
    vlm_api_key="your-key"
)
parser.parse(enhanced_pdf)
```

## Custom Processing with Different VLM Providers

```python
from doctra import ChartTablePDFParser

# Using OpenAI
parser_openai = ChartTablePDFParser(
    use_vlm=True,
    vlm_provider="openai",
    vlm_api_key="sk-xxx"
)

# Using Gemini (cost-effective)
parser_gemini = ChartTablePDFParser(
    use_vlm=True,
    vlm_provider="gemini",
    vlm_api_key="gemini-key"
)

# Parse with different providers
parser_openai.parse("important_doc.pdf")
parser_gemini.parse("regular_doc.pdf")
```

## Parallel Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor
from doctra import StructuredPDFParser

def process_pdf(pdf_path):
    parser = StructuredPDFParser()
    try:
        parser.parse(pdf_path)
        return f"Success: {pdf_path}"
    except Exception as e:
        return f"Error {pdf_path}: {e}"

# Process multiple PDFs in parallel
pdf_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(process_pdf, pdf_files)
    
for result in results:
    print(result)
```

## Dynamic DPI Selection

```python
import os
from doctra import StructuredPDFParser

def smart_parse(pdf_path):
    # Choose DPI based on file size
    file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
    
    if file_size < 5:
        dpi = 200  # Standard quality
    elif file_size < 20:
        dpi = 150  # Lower for large files
    else:
        dpi = 100  # Very low for huge files
    
    parser = StructuredPDFParser(dpi=dpi)
    print(f"Processing {pdf_path} at {dpi} DPI")
    parser.parse(pdf_path)

smart_parse("document.pdf")
```

## Integration with Data Analysis

```python
from doctra import ChartTablePDFParser
import pandas as pd

# Extract tables
parser = ChartTablePDFParser(
    extract_tables=True,
    use_vlm=True,
    vlm_provider="openai",
    vlm_api_key="your-key"
)

parser.parse("financial_report.pdf")

# Load and analyze extracted data
excel_path = "outputs/financial_report/structured_parsing/parsed_tables_charts.xlsx"
xls = pd.ExcelFile(excel_path)

for sheet_name in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet_name)
    print(f"\nTable: {sheet_name}")
    print(df.describe())
```

## See Also

- [Basic Examples](basic-usage.md) - Simpler examples
- [Integration](integration.md) - Integration patterns
- [API Reference](../api/parsers.md) - API documentation

