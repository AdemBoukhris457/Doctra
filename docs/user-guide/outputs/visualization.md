# Visualization

Guide to visualizing Doctra's processing results.

## Overview

Doctra provides visualization tools to help you understand and verify document processing results.

## Layout Visualization

Display detected document elements with bounding boxes:

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

parser.display_pages_with_boxes(
    pdf_path="document.pdf",
    num_pages=3
)
```

## Features

- **Color-coded Elements**: Each type has a distinct color
- **Confidence Scores**: Shows detection confidence
- **Grid Layout**: Multiple pages in organized grid
- **Element Counts**: Summary statistics per page

## Color Scheme

- 🔵 **Blue**: Text regions
- 🔴 **Red**: Tables
- 🟢 **Green**: Charts
- 🟠 **Orange**: Figures

## Configuration

```python
parser.display_pages_with_boxes(
    pdf_path="document.pdf",
    num_pages=5,        # Pages to visualize
    cols=3,             # Grid columns
    page_width=700,     # Page width in pixels
    spacing=40,         # Spacing between pages
    save_path="viz.png" # Save instead of display
)
```

## Use Cases

1. **Quality Assurance**: Verify detection accuracy
2. **Debugging**: Identify layout issues
3. **Documentation**: Create visual reports
4. **Analysis**: Understand document structure

## CLI Visualization

```bash
doctra visualize document.pdf --num-pages 5 --output layout.png
```

## See Also

- [Layout Detection](../engines/layout-detection.md) - Understanding detection
- [Core Concepts](../core-concepts.md) - Processing pipeline
- [CLI Reference](../../interfaces/cli.md) - Command line tools

