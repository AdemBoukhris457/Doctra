# Export Formats

Guide to Doctra's output formats.

## Overview

Doctra generates multiple output formats simultaneously, each optimized for different use cases.

## Available Formats

### Markdown (.md)

Human-readable document with:

- All text content
- Embedded image references
- Table links
- Section structure

**Best for**: Documentation, version control, reading

**Example**:
```markdown
# Document Title

## Section 1

Text content...

![Figure 1](images/figures/figure_001.jpg)

See tables in [tables.xlsx](tables.xlsx)
```

### HTML (.html)

Web-ready document with:

- Styled content
- Embedded images
- Interactive tables
- Responsive layout

**Best for**: Web publishing, presentations

### Excel (.xlsx)

Spreadsheet with extracted data:

- One sheet per table
- Formatted cells
- Headers preserved
- Data structured

**Best for**: Data analysis, further processing

*Only generated when VLM is enabled*

### JSON (.json)

Structured data with:

- Element metadata
- Coordinates
- Content
- Relationships

**Best for**: Programmatic access, integration

*Only generated when VLM is enabled*

### Images

Cropped visual elements:

- `figures/`: Document images
- `charts/`: Graphs and plots
- `tables/`: Table images

**Format**: JPEG or PNG
**Best for**: Direct use, presentations

## Output Structure

```
outputs/
└── document/
    └── full_parse/
        ├── result.md          # Markdown
        ├── result.html        # HTML
        ├── tables.xlsx        # Excel (VLM)
        ├── tables.html        # HTML tables (VLM)
        ├── vlm_items.json     # JSON data (VLM)
        └── images/
            ├── figures/
            ├── charts/
            └── tables/
```

## Choosing Formats

| Use Case | Recommended Format |
|----------|-------------------|
| Reading | Markdown or HTML |
| Data analysis | Excel |
| Web publishing | HTML |
| Integration | JSON |
| Presentations | Images + HTML |
| Version control | Markdown |

## See Also

- [Visualization](visualization.md) - Visual outputs
- [Examples](../../examples/basic-usage.md) - Usage examples
- [API Reference](../../api/exporters.md) - Exporter documentation

