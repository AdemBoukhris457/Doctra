# Welcome to Doctra

![Doctra Banner](https://raw.githubusercontent.com/AdemBoukhris457/Doctra/main/assets/Doctra_Banner_MultiDoc.png)

[![PyPI version](https://img.shields.io/pypi/v/doctra)](https://pypi.org/project/doctra/)
[![Python versions](https://img.shields.io/pypi/pyversions/doctra)](https://pypi.org/project/doctra/)
[![GitHub stars](https://img.shields.io/github/stars/AdemBoukhris457/Doctra)](https://github.com/AdemBoukhris457/Doctra)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1Z9UH9r1ZxGHm2cAFVKy7W9cKjcgBDOlG?usp=sharing)
[![License](https://img.shields.io/github/license/AdemBoukhris457/Doctra)](https://github.com/AdemBoukhris457/Doctra/blob/main/LICENSE)

## Overview

**Doctra** is a powerful Python library for parsing, extracting, and analyzing document content from PDFs. It combines state-of-the-art layout detection, OCR, image restoration, and Vision Language Models (VLM) to provide comprehensive document processing capabilities.

## Key Features

### :material-file-document-outline: Comprehensive PDF Parsing
- **Layout Detection**: Advanced document layout analysis using PaddleOCR
- **OCR Processing**: High-quality text extraction with Tesseract
- **Visual Elements**: Automatic extraction of figures, charts, and tables
- **Multiple Parsers**: Choose the right parser for your use case

### :material-image-auto-adjust: Image Restoration
- **6 Restoration Tasks**: Dewarping, deshadowing, appearance enhancement, deblurring, binarization, and end-to-end restoration
- **DocRes Integration**: State-of-the-art document image restoration
- **GPU Acceleration**: Automatic CUDA detection for faster processing
- **Enhanced Quality**: Improves document quality for better OCR results

### :material-robot: VLM Integration
- **Structured Data Extraction**: Convert charts and tables to structured formats
- **Multiple Providers**: OpenAI, Gemini, Anthropic, and OpenRouter support
- **Automatic Conversion**: Transform visual elements into usable data
- **Flexible Configuration**: Easy API key management and model selection

### :material-export: Rich Output Formats
- **Markdown**: Human-readable documents with embedded images
- **Excel**: Structured data in spreadsheet format
- **JSON**: Programmatically accessible data
- **HTML**: Interactive web-ready documents
- **Images**: High-quality cropped visual elements

### :material-application: User-Friendly Interfaces
- **Web UI**: Gradio-based interface with drag & drop
- **Command Line**: Powerful CLI for automation
- **Python API**: Full programmatic access
- **Real-time Progress**: Track processing status

## Quick Start

### Installation

```bash
pip install doctra
```

### Basic Usage

```python
from doctra import StructuredPDFParser

# Initialize parser
parser = StructuredPDFParser()

# Parse a document
parser.parse("document.pdf")
```

!!! tip "System Dependencies"
    Doctra requires Poppler for PDF processing. See the [Installation Guide](getting-started/installation.md) for detailed setup instructions.

## Core Components

### Parsers

| Parser | Description | Best For |
|--------|-------------|----------|
| **StructuredPDFParser** | Complete document processing | General purpose parsing |
| **EnhancedPDFParser** | Parsing with image restoration | Scanned or low-quality documents |
| **ChartTablePDFParser** | Focused extraction | Only charts and tables needed |

### Engines

| Engine | Description | Use Case |
|--------|-------------|----------|
| **DocResEngine** | Image restoration | Standalone image enhancement |
| **Layout Detection** | Document analysis | Identify document structure |
| **OCR Engine** | Text extraction | Extract text from images |
| **VLM Service** | AI processing | Convert visuals to structured data |

## Use Cases

- :material-file-chart: **Financial Reports**: Extract tables, charts, and text from financial documents
- :material-book-open-page-variant: **Research Papers**: Parse academic papers with figures and tables
- :material-file-document-multiple: **Document Archival**: Convert scanned documents to searchable formats
- :material-chart-bar: **Data Extraction**: Extract structured data from visual elements
- :material-file-restore: **Document Enhancement**: Restore and improve low-quality documents

## Getting Help

- :material-file-document: **Documentation**: You're reading it! Explore the sidebar for detailed guides
- :material-github: **GitHub Issues**: [Report bugs or request features](https://github.com/AdemBoukhris457/Doctra/issues)
- :material-package: **PyPI**: [View package details](https://pypi.org/project/doctra/)

## 📓 Interactive Notebooks

| Notebook | Colab Badge | Description |
|----------|-------------|-------------|
| **01_doctra_quick_start** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1Z9UH9r1ZxGHm2cAFVKy7W9cKjcgBDOlG?usp=sharing) | Comprehensive tutorial covering layout detection, content extraction, and multi-format outputs with visual examples |

## What's Next?

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __Quick Start__

    ---

    Get up and running with Doctra in minutes

    [:octicons-arrow-right-24: Quick Start Guide](getting-started/quick-start.md)

-   :material-book-open-variant:{ .lg .middle } __User Guide__

    ---

    Learn about parsers, engines, and advanced features

    [:octicons-arrow-right-24: Read the Guide](user-guide/core-concepts.md)

-   :material-code-tags:{ .lg .middle } __API Reference__

    ---

    Detailed API documentation for all components

    [:octicons-arrow-right-24: API Docs](api/parsers.md)

-   :material-lightbulb:{ .lg .middle } __Examples__

    ---

    Real-world examples and integration patterns

    [:octicons-arrow-right-24: View Examples](examples/basic-usage.md)

</div>

## Acknowledgments

Doctra builds upon several excellent open-source projects:

- **[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)** - Advanced document layout detection and OCR capabilities
- **[DocRes](https://github.com/ZZZHANG-jx/DocRes)** - State-of-the-art document image restoration model
- **[Outlines](https://github.com/dottxt-ai/outlines)** - Structured output generation for LLMs

We thank the developers and contributors of these projects for their valuable work.

## License

Doctra is released under the MIT License. See the [LICENSE](https://github.com/AdemBoukhris457/Doctra/blob/main/LICENSE) file for details.

