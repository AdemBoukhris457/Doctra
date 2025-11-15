# Chart & Table Extractor

Guide to using the `ChartTablePDFParser` for targeted extraction.

## Overview

The `ChartTablePDFParser` is a specialized parser focused exclusively on extracting charts and tables from PDF documents. It's optimized for scenarios where you only need these specific elements.

## Key Features

- **Focused Extraction**: Extract only charts and/or tables
- **Selective Processing**: Choose what to extract
- **VLM Integration**: Convert visuals to structured data
- **Split Table Merging**: Automatic detection and merging of tables split across pages
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

## Split Table Merging

The `ChartTablePDFParser` includes automatic detection and merging of tables that are split across multiple pages. This feature is especially useful for processing financial reports, data tables, and other documents where large tables span page boundaries.

### Enabling Split Table Merging

```python
from doctra import ChartTablePDFParser

# Enable split table merging with default settings
parser = ChartTablePDFParser(
    extract_tables=True,
    merge_split_tables=True
)

parser.parse("document.pdf")
```

### Configuration Options

```python
parser = ChartTablePDFParser(
    extract_tables=True,
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

1. **Phase 1: Proximity Detection** - Fast spatial heuristics to identify candidate pairs based on position, overlap, gap, and width similarity
2. **Phase 2: Structural Validation** - Deep structural analysis using LSD (Line Segment Detector) to validate column alignment and structure

For detailed information about the algorithm, see the [Split Table Merging Guide](../features/split-table-merging.md).

### Output

When split tables are detected and merged:

- Individual table segments are skipped (not saved separately)
- Merged table images are saved as `merged_table_<page1>_<page2>.png` in the tables directory
- If VLM is enabled, merged tables are processed and included in the structured output (Excel, HTML, JSON)
- Merged tables include metadata: page range and confidence score

### When to Use Split Table Merging

Enable split table merging when:

- Processing financial reports or data tables
- Tables span multiple pages
- You need complete table data for analysis
- Working with documents that have large data tables

## When to Use

Use `ChartTablePDFParser` when:

- You only need charts and/or tables
- Faster processing is important
- Working with data-heavy documents
- Extracting data for analysis

## See Also

- [VLM Integration](../engines/vlm-integration.md) - Structured data extraction
- [Structured Parser](structured-parser.md) - Full document parsing with split table merging details
- [Split Table Merging Guide](../features/split-table-merging.md) - Comprehensive guide to split table detection
- [API Reference](../../api/parsers.md) - Complete API documentation

