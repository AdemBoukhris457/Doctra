# Structured PDF Parser

Comprehensive guide to using the `StructuredPDFParser`.

## Overview

The `StructuredPDFParser` is the foundational parser in Doctra, designed for general-purpose PDF document processing. It combines layout detection, OCR, and optional VLM integration to extract all content from PDF documents.

## Key Features

- **Layout Detection**: PaddleOCR-based document structure analysis
- **OCR Processing**: Text extraction from all document elements
- **Visual Element Extraction**: Automatic cropping of figures, charts, and tables
- **VLM Integration**: Optional structured data extraction
- **Multiple Output Formats**: Markdown, HTML, Excel, JSON

## Basic Usage

```python
from doctra import StructuredPDFParser

# Initialize parser with defaults
parser = StructuredPDFParser()

# Parse document
parser.parse("document.pdf")
```

## Configuration

See [API Reference](../../api/parsers.md#structuredpdfparser) for detailed parameter documentation.

## Output Structure

```
outputs/
└── document/
    └── full_parse/
        ├── result.md
        ├── result.html
        └── images/
```

## When to Use

Use `StructuredPDFParser` for:

- General PDF processing
- Good quality documents
- When image restoration is not needed
- Extracting all content types

## See Also

- [Split Table Merging](../features/split-table-merging.md) - Detailed guide to automatic table merging
- [Enhanced Parser](enhanced-parser.md) - With image restoration
- [Chart & Table Extractor](chart-table-extractor.md) - Focused extraction
- [API Reference](../../api/parsers.md) - Complete API documentation

