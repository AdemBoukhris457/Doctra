# Exporters API Reference

Documentation for Doctra's export functionality.

## Overview

Exporters handle converting parsed document content into various output formats.

## Available Exporters

### MarkdownWriter

Generates human-readable Markdown files with embedded images.

### HTMLWriter

Produces styled HTML documents for web viewing.

### ExcelWriter

Creates Excel spreadsheets with structured data from tables and charts.

### ImageSaver

Saves cropped images of visual elements (figures, charts, tables).

## Usage

Exporters are used automatically by parsers. Output format is determined by parser configuration.

### Output Files

```
outputs/
└── document/
    ├── result.md          # MarkdownWriter
    ├── result.html        # HTMLWriter
    ├── tables.xlsx        # ExcelWriter (with VLM)
    ├── tables.html        # HTMLWriter (with VLM)
    └── images/            # ImageSaver
        ├── figures/
        ├── charts/
        └── tables/
```

## See Also

- [Parsers API](parsers.md) - Main parsing functionality
- [Export Formats](../user-guide/outputs/export-formats.md) - Detailed format documentation

