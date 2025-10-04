# Layout Detection

Guide to document layout detection in Doctra.

## Overview

Layout detection is the foundation of Doctra's processing pipeline. It analyzes PDF pages to identify and classify different document elements (text, tables, charts, figures).

## How It Works

1. **Render**: PDF pages converted to images at specified DPI
2. **Detection**: PaddleOCR model identifies element regions
3. **Classification**: Elements labeled by type
4. **Filtering**: Low-confidence detections removed

## Configuration

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser(
    layout_model_name="PP-DocLayout_plus-L",
    dpi=200,
    min_score=0.5
)
```

## Parameters

**layout_model_name**
:   PaddleOCR model to use
    - `PP-DocLayout_plus-L`: Best accuracy (slower)
    - `PP-DocLayout_plus-M`: Faster, good accuracy

**dpi**
:   Image resolution
    - 100-150: Fast, lower quality
    - 200: Balanced (default)
    - 250-300: High quality, slower

**min_score**
:   Confidence threshold (0-1)
    - 0.0: Include all detections
    - 0.5: Moderate filtering
    - 0.7+: Conservative, high confidence only

## Visualization

Verify detection quality:

```python
parser.display_pages_with_boxes(
    pdf_path="document.pdf",
    num_pages=3
)
```

## Element Types

- **Text**: Regular content (blue boxes)
- **Tables**: Tabular data (red boxes)
- **Charts**: Graphs and plots (green boxes)
- **Figures**: Images and diagrams (orange boxes)

## See Also

- [Core Concepts](../core-concepts.md) - Understanding the pipeline
- [Visualization](../outputs/visualization.md) - Layout visualization
- [API Reference](../../api/parsers.md) - Configuration options

