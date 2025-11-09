# Chart & Table Extractor

Guide to using the `ChartTablePDFParser` for targeted extraction.

## Overview

The `ChartTablePDFParser` is a specialized parser focused exclusively on extracting charts and tables from PDF documents. It's optimized for scenarios where you only need these specific elements.

## Key Features

- **Focused Extraction**: Extract only charts and/or tables
- **Selective Processing**: Choose what to extract
- **VLM Integration**: Convert visuals to structured data
- **Faster Processing**: Skips unnecessary elements

## Basic Usage

```python
from doctra import ChartTablePDFParser

parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=True
)

parser.parse("data_report.pdf")
```

## Selective Extraction

```python
# Extract only tables
parser = ChartTablePDFParser(
    extract_charts=False,
    extract_tables=True
)

# Extract only charts
parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=False
)
```

## With VLM for Structured Data

```python
from doctra import ChartTablePDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

# Initialize VLM engine
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-key"
)

parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=True,
    vlm=vlm_engine  # Pass VLM engine instance
)

parser.parse("report.pdf")
# Outputs: tables.xlsx, tables.html, vlm_items.json
```

## When to Use

Use `ChartTablePDFParser` when:

- You only need charts and/or tables
- Faster processing is important
- Working with data-heavy documents
- Extracting data for analysis

## See Also

- [VLM Integration](../engines/vlm-integration.md) - Structured data extraction
- [Structured Parser](structured-parser.md) - Full document parsing
- [API Reference](../../api/parsers.md) - Complete API documentation

