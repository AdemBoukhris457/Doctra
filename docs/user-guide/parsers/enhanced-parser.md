# Enhanced PDF Parser

Guide to using the `EnhancedPDFParser` with image restoration.

## Overview

The `EnhancedPDFParser` extends `StructuredPDFParser` with DocRes image restoration capabilities. It's ideal for processing scanned documents, low-quality PDFs, or documents with visual distortions.

## Key Features

- **Image Restoration**: DocRes integration for document enhancement
- **6 Restoration Tasks**: Dewarping, deshadowing, deblurring, and more
- **GPU Acceleration**: Optional CUDA support for faster processing
- **All Base Features**: Inherits all `StructuredPDFParser` capabilities

## Basic Usage

```python
from doctra import EnhancedPDFParser

parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="appearance"
)

parser.parse("scanned_document.pdf")
```

## Restoration Tasks

| Task | Best For |
|------|----------|
| `appearance` | General enhancement (default) |
| `dewarping` | Perspective distortion |
| `deshadowing` | Shadow removal |
| `deblurring` | Blur reduction |
| `binarization` | Clean B&W conversion |
| `end2end` | Severe degradation |

## When to Use

Use `EnhancedPDFParser` for:

- Scanned documents
- Low-quality PDFs
- Documents with visual distortions
- When OCR accuracy is poor with standard parser

## See Also

- [DocRes Engine](../engines/docres-engine.md) - Image restoration details
- [Structured Parser](structured-parser.md) - Base parser
- [API Reference](../../api/parsers.md) - Complete API documentation

