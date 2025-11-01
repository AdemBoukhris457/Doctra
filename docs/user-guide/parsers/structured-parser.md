# Structured PDF Parser

Comprehensive guide to using the `StructuredPDFParser`.

## Overview

The `StructuredPDFParser` is the foundational parser in Doctra, designed for general-purpose PDF document processing. It combines layout detection, OCR, and optional VLM integration to extract all content from PDF documents.

## Key Features

- **Layout Detection**: PaddleOCR-based document structure analysis
- **OCR Processing**: Text extraction from all document elements
- **Visual Element Extraction**: Automatic cropping of figures, charts, and tables
- **VLM Integration**: Optional structured data extraction
- **Split Table Merging**: Automatic detection and merging of tables split across pages
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

## Split Table Merging

The `StructuredPDFParser` includes an advanced feature to automatically detect and merge tables that are split across multiple pages. This is especially useful for processing financial reports, data tables, and other documents where large tables span page boundaries.

### How It Works

The split table detection uses a two-phase approach combining spatial heuristics with structural analysis:

#### Phase 1: Proximity Detection

The system first identifies candidate table pairs using position-based heuristics:

1. **Position Check**: 
   - The first table segment must be close to the bottom of its page (within 20% by default)
   - The second table segment must be close to the top of the next page (within 15% by default)

2. **Horizontal Alignment**:
   - The tables must have significant horizontal overlap (at least 50%)
   - This ensures they're aligned vertically on the page

3. **Gap Analysis**:
   - The gap between the end of the first table and start of the second table is measured
   - The gap accounts for page breaks, headers, and footers
   - Maximum allowed gap is 25% of page height by default

4. **Width Similarity**:
   - Both table segments must have similar widths (within 20% difference)
   - This ensures they belong to the same table structure

#### Phase 2: Structural Validation

Once proximity checks pass, the system performs deeper structural analysis using **LSD (Line Segment Detector)** from OpenCV:

1. **Column Detection**:
   - LSD detects vertical lines in both table segments
   - These lines represent column boundaries
   - The algorithm is adaptive and works across different table structures without parameter tuning

2. **Column Count Matching**:
   - The system compares the number of columns detected in both segments
   - Tolerance is adaptive based on table size:
     - Small tables (≤5 columns): Allows 1 column difference
     - Medium tables (6-10 columns): Allows 2 column differences
     - Large tables (11-20 columns): Allows 15% difference or minimum 3
   
3. **Column Alignment**:
   - The relative positions of columns are compared between segments
   - At least 60% of columns must align within a tolerance (10 pixels by default)
   - This ensures structural continuity

4. **Confidence Scoring**:
   - A confidence score (0-1) is calculated based on:
     - Column count match
     - Column alignment quality
     - Width similarity
     - Overlap ratio
   - Only matches with confidence ≥ 0.65 (default) are merged

#### Fallback Mechanisms

The system includes intelligent fallbacks for edge cases:

- **Too Many Columns Detected**: If LSD detects >20 columns, it likely indicates noise (horizontal lines, text boundaries). The system falls back to proximity-based matching with lower confidence.

- **No Columns Detected**: For borderless tables or poor image quality, if no columns are detected in either segment, the system uses proximity-based matching.

- **Noise Filtering**: The system filters out edge columns that are too close to image boundaries (likely artifacts).

### Enabling Split Table Merging

```python
from doctra import StructuredPDFParser

# Enable split table merging with default settings
parser = StructuredPDFParser(
    merge_split_tables=True
)

# Parse document - split tables will be automatically merged
parser.parse("document.pdf")
```

### Configuration Options

```python
parser = StructuredPDFParser(
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

### Parameter Details

| Parameter | Default | Description |
|-----------|---------|-------------|
| `merge_split_tables` | `False` | Enable/disable split table detection |
| `bottom_threshold_ratio` | `0.20` | Ratio for detecting tables near bottom of page (0-1) |
| `top_threshold_ratio` | `0.15` | Ratio for detecting tables near top of page (0-1) |
| `max_gap_ratio` | `0.25` | Maximum allowed gap between tables (accounts for headers/footers) |
| `column_alignment_tolerance` | `10.0` | Pixel tolerance for column alignment validation |
| `min_merge_confidence` | `0.65` | Minimum confidence score (0-1) required to merge tables |

### Output

When split tables are detected and merged:

- **Merged Image**: A single composite image is created combining both table segments
- **Markdown Output**: The merged table appears once in the markdown with a note indicating it spans multiple pages
- **HTML Output**: Similar to markdown, the merged table appears as a single element
- **File Location**: Merged tables are saved as `merged_table_{page1}_{page2}.png` in the `tables/` directory

Example output note:
```
📊 Table (merged from pages 1-2, confidence: 0.75)
```

### When to Use

Enable split table merging when:

- Processing documents with large tables spanning multiple pages
- Working with financial reports, data tables, or structured documents
- You want complete table context in a single view
- Tables frequently break across page boundaries

Consider disabling when:

- Tables are intentionally separate across pages
- Processing speed is critical (adds minor overhead)
- Document structure is inconsistent

### Technical Details

**Algorithm**: The detection uses OpenCV's LSD (Line Segment Detector), which is:
- **Adaptive**: Works across different table structures without parameter tuning
- **Robust**: Handles various line styles (solid, dashed, partially broken)
- **Efficient**: Fast processing suitable for batch operations

**Preprocessing**: Before column detection, images undergo:
- Grayscale conversion
- Contrast enhancement (CLAHE)
- Binary thresholding (OTSU)
- Morphological operations to connect broken lines

**Clustering**: Detected line segments are clustered using adaptive thresholds based on image width, ensuring that multiple detections of the same column boundary are merged into a single column marker.

For a complete, detailed explanation with visual schemas and examples, see the [Split Table Merging Guide](../../features/split-table-merging.md).

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

