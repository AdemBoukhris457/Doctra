# Enhanced PDF Parser

Guide to using the `EnhancedPDFParser` with image restoration.

## Overview

The `EnhancedPDFParser` extends `StructuredPDFParser` with DocRes image restoration capabilities. It's ideal for processing scanned documents, low-quality PDFs, or documents with visual distortions.

## Key Features

- **Image Restoration**: DocRes integration for document enhancement
- **6 Restoration Tasks**: Dewarping, deshadowing, deblurring, and more
- **GPU Acceleration**: Optional CUDA support for faster processing
- **Split Table Merging**: Automatic detection and merging of tables split across pages
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

## Split Table Merging

The `EnhancedPDFParser` includes automatic detection and merging of tables that are split across multiple pages. This feature is especially useful for processing financial reports, data tables, and other documents where large tables span page boundaries.

### Enabling Split Table Merging

```python
from doctra import EnhancedPDFParser

# Enable split table merging with default settings
parser = EnhancedPDFParser(
    use_image_restoration=True,
    merge_split_tables=True
)

parser.parse("document.pdf")
```

### Configuration Options

```python
parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="appearance",
    
    # Enable split table merging
    merge_split_tables=True,
    
    # Position thresholds
    bottom_threshold_ratio=0.20,  # 20% from bottom of page
    top_threshold_ratio=0.15,     # 15% from top of page
    
    # Gap tolerance
    max_gap_ratio=0.25,            # 25% of page height max gap
    
    # Structural validation
    column_alignment_tolerance=10.0,  # Pixel tolerance for column alignment
    min_merge_confidence=0.65,       # Minimum confidence to merge (0-1)
)
```

### How It Works

The split table detection uses a two-phase approach:

1. **Phase 1: Proximity Detection** - Fast spatial heuristics to identify candidate pairs based on position, horizontal overlap, gap analysis, and width similarity
2. **Phase 2: Structural Validation** - Deep structural analysis using LSD (Line Segment Detector) to validate column alignment and structure

For detailed information about the algorithm, see the [Split Table Merging Guide](../features/split-table-merging.md).

### Output

When split tables are detected and merged:

- **Merged Image**: A single composite image is created combining both table segments
- **Markdown/HTML Output**: The merged table appears once with a note indicating it spans multiple pages (e.g., "Merged Table (pages 1-2)")
- **File Location**: Merged tables are saved as `merged_table_{page1}_{page2}.png` in the `tables/` directory
- **VLM Processing**: If VLM is enabled, the merged table is processed as a single complete table for better extraction accuracy

### Parameter Details

| Parameter | Default | Description |
|-----------|---------|-------------|
| `merge_split_tables` | `False` | Enable/disable split table detection |
| `bottom_threshold_ratio` | `0.20` | Ratio for detecting tables near bottom of page (0-1) |
| `top_threshold_ratio` | `0.15` | Ratio for detecting tables near top of page (0-1) |
| `max_gap_ratio` | `0.25` | Maximum allowed gap between tables (accounts for headers/footers) |
| `column_alignment_tolerance` | `10.0` | Pixel tolerance for column alignment validation |
| `min_merge_confidence` | `0.65` | Minimum confidence score (0-1) required to merge tables |

### When to Use Split Table Merging

Enable split table merging when:

- Processing documents with large tables spanning multiple pages
- Working with financial reports, data tables, or structured documents
- You want complete table context in a single view
- Using VLM for table extraction (merged tables provide better context)

Consider disabling when:

- Tables are intentionally separate across pages
- Processing speed is critical (adds minor overhead)
- Document structure is inconsistent

## When to Use

Use `EnhancedPDFParser` for:

- Scanned documents
- Low-quality PDFs
- Documents with visual distortions
- When OCR accuracy is poor with standard parser

## See Also

- [DocRes Engine](../engines/docres-engine.md) - Image restoration details
- [Structured Parser](structured-parser.md) - Base parser with split table merging details
- [Split Table Merging Guide](../features/split-table-merging.md) - Comprehensive guide to split table detection
- [API Reference](../../api/parsers.md) - Complete API documentation

