# Split Table Merging

A comprehensive guide to Doctra's automatic detection and merging of tables split across page boundaries.

## Overview

Many documents contain large tables that span multiple pages. When processing such documents, each page may contain only a portion of a table, making it difficult to extract complete data. Doctra's split table merging feature automatically detects these split tables and combines them into single, complete table images.

## Table of Contents

- [How It Works](#how-it-works)
- [Detection Algorithm](#detection-algorithm)
- [Visual Schema](#visual-schema)
- [Phase-by-Phase Breakdown](#phase-by-phase-breakdown)
- [Configuration Parameters](#configuration-parameters)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## How It Works

The split table detection uses a sophisticated two-phase approach:

1. **Phase 1: Proximity Detection** - Fast spatial heuristics to identify candidate pairs
2. **Phase 2: Structural Validation** - Deep structural analysis using computer vision

This design balances speed (avoiding expensive operations on all pairs) with accuracy (validating only promising candidates).

## Detection Algorithm

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Start: Parse PDF Document                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Extract Tables │
                    │ from All Pages │
                    └────────┬───────┘
                             │
                             ▼
        ┌──────────────────────────────────────────┐
        │     Phase 1: Proximity Detection         │
        │  ────────────────────────────────────   │
        │  1. Check position (bottom/top)          │
        │  2. Check horizontal overlap             │
        │  3. Check gap between tables             │
        │  4. Check width similarity               │
        └────────────┬─────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼ YES                   ▼ NO
┌─────────────────┐      ┌──────────────┐
│ Candidate Match │      │ Skip Pair    │
│  Found → Phase 2│      │ Try Next     │
└────────┬────────┘      └──────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│     Phase 2: Structural Validation      │
│  ────────────────────────────────────    │
│  1. Detect columns (LSD)                 │
│  2. Compare column counts                │
│  3. Check column alignment               │
│  4. Calculate confidence score           │
└────────────┬─────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼ YES             ▼ NO
┌────────────┐    ┌──────────┐
│   Merge    │    │  Reject  │
│  Tables    │    │  Match   │
└────────────┘    └──────────┘
```

## Visual Schema

### Document Layout Representation

```
Page 1                              Page 2
┌─────────────────────────┐        ┌─────────────────────────┐
│                         │        │                         │
│                         │        │  Table Segment 2        │
│                         │        │  ┌─────────────────┐   │
│                         │        │  │  Row 6          │   │
│  Table Segment 1         │        │  │  Row 7          │   │
│  ┌─────────────────┐    │        │  │  Row 8          │   │
│  │  Row 1          │    │        │  │  ...            │   │
│  │  Row 2          │    │        │  └─────────────────┘   │
│  │  Row 3          │    │        │                         │
│  │  Row 4          │    │        │                         │
│  │  Row 5          │    │        │                         │
│  └─────────────────┘    │        │                         │
│         ▼               │        │         ▲               │
│   (close to bottom)     │        │   (close to top)        │
│                         │        │                         │
└─────────────────────────┘        └─────────────────────────┘
       │                                        │
       └──────────── Gap: 18.8% ────────────────┘
        (page break + headers/footers)
```

### Phase 1: Proximity Detection Schema

```
┌─────────────────────────────────────────────────────────────┐
│              Proximity Detection Checks                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Check 1: Position                                          │
│  ┌──────────────┐                    ┌──────────────┐      │
│  │   Page 1     │                    │   Page 2     │      │
│  │              │                    │              │      │
│  │              │                    │  ┌────────┐  │      │
│  │              │                    │  │  Seg2  │  │      │
│  │              │                    │  │        │  │      │
│  │  ┌────────┐  │                    │  └────────┘  │      │
│  │  │  Seg1  │  │                    │     ▲        │      │
│  │  │        │  │                    │   y1 ≤ 15%   │      │
│  │  └────────┘  │                    │              │      │
│  │     ▼        │                    │              │      │
│  │  y2 ≥ 80%    │                    │              │      │
│  │              │                    │              │      │
│  └──────────────┘                    └──────────────┘      │
│                                                             │
│  Check 2: Horizontal Overlap                                │
│  ┌──────────────────────────────────────────────┐          │
│  │  Seg1:  x1=100  ──────────  x2=900          │          │
│  │         └─────────────────────────────────┐ │          │
│  │                                            │ │          │
│  │  Seg2:      x1=120  ──────────  x2=920     │ │          │
│  │             └───────────────────────────┐  │ │          │
│  │                                         │  │ │          │
│  │  Overlap: 780px / 800px = 97.5% ✅      │  │ │          │
│  └────────────────────────────────────────┴──┴─┘          │
│                                                             │
│  Check 3: Gap Analysis                                      │
│  ┌──────────────────────────────────────────────┐          │
│  │  Gap = (Page1_height - Seg1_y2) + Seg2_y1  │          │
│  │      = (1000px - 850px) + 150px            │          │
│  │      = 300px (30% of page height)          │          │
│  │                                             │          │
│  │  Threshold: 25% → 300px > 250px ❌          │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  Check 4: Width Similarity                                  │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │  Seg1 Width  │         │  Seg2 Width  │                 │
│  │   800px      │  vs     │   820px      │                 │
│  │              │         │              │                 │
│  │  Difference: 20px (2.5%) ✅                              │
│  └──────────────┘         └──────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### Phase 2: Structural Validation Schema

```
┌─────────────────────────────────────────────────────────────┐
│           Structural Validation Process                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: Image Preprocessing                                │
│  ┌─────────────────────────────────────────┐               │
│  │  Original Image                         │               │
│  │  → Grayscale Conversion                 │               │
│  │  → CLAHE Contrast Enhancement           │               │
│  │  → OTSU Binary Thresholding             │               │
│  │  → Morphological Operations             │               │
│  │  Result: Enhanced binary image ready    │               │
│  │         for line detection              │               │
│  └─────────────────────────────────────────┘               │
│                                                             │
│  Step 2: LSD Column Detection                               │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │  Segment 1       │        │  Segment 2       │          │
│  │                 │        │                 │          │
│  │  │  │  │  │  │  │        │  │  │  │  │  │  │          │
│  │  └──┴──┴──┴──┘        │  └──┴──┴──┘          │          │
│  │                 │        │                 │          │
│  │  Detected:      │        │  Detected:      │          │
│  │  5 columns      │        │  5 columns      │          │
│  │  Positions:     │        │  Positions:     │          │
│  │  [100, 250,     │        │  [100, 250,     │          │
│  │   400, 550,     │        │   400, 550,     │          │
│  │   700]         │        │   700]         │          │
│  └──────────────────┘        └──────────────────┘          │
│                                                             │
│  Step 3: Column Alignment Check                             │
│  ┌─────────────────────────────────────────┐               │
│  │  Seg1 Cols:  [100, 250, 400, 550, 700]  │               │
│  │  Seg2 Cols:  [102, 248, 402, 552, 698]  │               │
│  │                                         │               │
│  │  Differences: [2, 2, 2, 2, 2] pixels    │               │
│  │  All < 10px tolerance ✅                 │               │
│  │                                         │               │
│  │  Alignment Score: 100%                  │               │
│  └─────────────────────────────────────────┘               │
│                                                             │
│  Step 4: Confidence Calculation                             │
│  ┌─────────────────────────────────────────┐               │
│  │  Factors:                               │               │
│  │  - Column count match:  +0.3            │               │
│  │  - Column alignment:    +0.4            │               │
│  │  - Width similarity:    +0.1            │               │
│  │  - Overlap ratio:        +0.2            │               │
│  │                                         │               │
│  │  Total Confidence: 1.0 (100%) ✅        │               │
│  └─────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## Phase-by-Phase Breakdown

### Phase 1: Proximity Detection

#### 1.1 Position Check

**Purpose**: Identify tables that are positioned at page boundaries, which is a strong indicator of page breaks.

**Algorithm**:
```
For table segment 1 on page N:
  bottom_ratio = segment_y2 / page_height
  If bottom_ratio >= (1.0 - bottom_threshold_ratio):
    ✅ Candidate for first segment

For table segment 2 on page N+1:
  top_ratio = segment_y1 / page_height
  If top_ratio <= top_threshold_ratio:
    ✅ Candidate for second segment
```

**Example**:
```
Page Height: 1000px
Segment 1 y2: 850px
  → bottom_ratio = 850/1000 = 0.85
  → Threshold: 1.0 - 0.20 = 0.80
  → 0.85 >= 0.80 ✅ PASS

Segment 2 y1: 150px
  → top_ratio = 150/1000 = 0.15
  → Threshold: 0.15
  → 0.15 <= 0.15 ✅ PASS
```

#### 1.2 Horizontal Overlap Check

**Purpose**: Ensure tables are aligned horizontally, indicating they're the same table.

**Algorithm**:
```
overlap = calculate_overlap(seg1_x1, seg1_x2, seg2_x1, seg2_x2)
  = max(0, min(seg1_x2, seg2_x2) - max(seg1_x1, seg2_x1))

overlap_ratio = overlap / max(seg1_width, seg2_width)

If overlap_ratio >= 0.5:
  ✅ PASS (at least 50% overlap)
```

**Visual Representation**:
```
Seg1:  |───────────|
Seg2:     |───────────|
       └─┘─────────┘
       Overlap = 7 units / 11 units = 63.6% ✅
```

#### 1.3 Gap Analysis

**Purpose**: Measure the space between tables accounting for page breaks, headers, and footers.

**Algorithm**:
```
gap_pixels = (page1_height - seg1_y2) + seg2_y1
gap_ratio = gap_pixels / page1_height

If gap_ratio <= max_gap_ratio:
  ✅ PASS (gap is reasonable)
```

**Considerations**:
- Headers/footers take up space
- Page margins create natural gaps
- Default 25% accommodates typical document layouts

#### 1.4 Width Similarity Check

**Purpose**: Verify both segments have similar widths, confirming they share the same structure.

**Algorithm**:
```
width1 = seg1_x2 - seg1_x1
width2 = seg2_x2 - seg2_x1
width_diff = abs(width1 - width2)
width_ratio = width_diff / max(width1, width2)

If width_ratio <= width_similarity_threshold (0.20):
  ✅ PASS (widths are similar)
```

### Phase 2: Structural Validation

#### 2.1 Image Preprocessing

**Purpose**: Enhance images for optimal line detection.

**Steps**:

1. **Grayscale Conversion**
   ```
   Original RGB → Grayscale
   ```

2. **Contrast Enhancement (CLAHE)**
   ```
   Apply Contrast Limited Adaptive Histogram Equalization
   → Improves line visibility in low-contrast areas
   ```

3. **Binary Thresholding (OTSU)**
   ```
   Grayscale → Binary (black/white)
   → OTSU automatically determines optimal threshold
   ```

4. **Morphological Operations**
   ```
   Apply MORPH_CLOSE with vertical kernel (1x5)
   → Connects broken or dashed lines
   → Enhances vertical line detection
   ```

**Visual Flow**:
```
RGB Image → Grayscale → Enhanced → Binary → Morphology → Ready for LSD
```

#### 2.2 LSD Column Detection

**Purpose**: Detect vertical lines representing column boundaries using OpenCV's Line Segment Detector.

**LSD Algorithm Overview**:
```
1. Gradient Computation
   → Calculate image gradients
   → Identify edge regions

2. Line Region Growing
   → Grow line segments from seed points
   → Connect adjacent pixels with similar orientation

3. Region Validation
   → Verify regions meet line criteria
   → Filter by length and support

4. Refinement
   → Refine line endpoints
   → Adjust for sub-pixel accuracy
```

**Column Extraction Process**:
```
┌─────────────────────────────────────┐
│ 1. Detect all line segments (LSD) │
│    → Returns: List of (x1,y1,x2,y2)│
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. Filter by angle                  │
│    → Keep: 75° ≤ angle ≤ 105°       │
│    → Remove: horizontal/diagonal    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 3. Extract x-coordinates            │
│    → Collect: x1, x2 for each line  │
│    → Result: [x1, x2, x3, ..., xn]  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. Cluster nearby coordinates       │
│    → Threshold: 1% of image width    │
│    → Merge: |x_i - x_j| < threshold│
│    → Result: [col1, col2, col3,...]│
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 5. Filter edge columns              │
│    → Remove: within 2% of edges     │
│    → Result: Valid column positions │
└─────────────────────────────────────┘
```

**Clustering Example**:
```
Detected x-coordinates:
[98, 100, 102, 248, 250, 252, 398, 400, 402]

After clustering (threshold=5px):
[100, 250, 400]  ← 3 columns detected
```

#### 2.3 Column Count Matching

**Purpose**: Compare the number of columns in both segments with adaptive tolerance.

**Algorithm**:
```
col_count1 = len(columns_detected_in_seg1)
col_count2 = len(columns_detected_in_seg2)
diff = abs(col_count1 - col_count2)

# Adaptive threshold based on table size
max_cols = max(col_count1, col_count2)

If max_cols <= 5:
    max_allowed_diff = 1
Else if max_cols <= 10:
    max_allowed_diff = 2
Else if max_cols <= 20:
    max_allowed_diff = max(3, int(max_cols * 0.15))
Else:
    max_allowed_diff = max(5, int(max_cols * 0.20))

If diff <= max_allowed_diff:
    ✅ PASS
```

**Examples**:
```
Small table: 4 vs 5 columns → diff=1 → ✅ (threshold=1)
Medium: 8 vs 10 → diff=2 → ✅ (threshold=2)
Large: 15 vs 18 → diff=3 → ✅ (threshold=3, 15*0.15=2.25→3)
```

#### 2.4 Column Alignment Validation

**Purpose**: Verify columns align between segments, ensuring structural continuity.

**Algorithm**:
```
For each column in segment1:
    Find closest column in segment2
    Calculate distance = |col1_pos - col2_pos|
    If distance <= tolerance:
        ✅ Aligned column
    Else:
        ❌ Misaligned column

alignment_score = aligned_columns / total_columns

If alignment_score >= 0.6:
    ✅ PASS (at least 60% alignment)
```

**Visual Example**:
```
Segment 1 columns:     Segment 2 columns:
   100px ────────         102px ────────  (diff: 2px ✅)
   250px ────────         248px ────────  (diff: 2px ✅)
   400px ────────         402px ────────  (diff: 2px ✅)
   550px ────────         552px ────────  (diff: 2px ✅)
   700px ────────         698px ────────  (diff: 2px ✅)

All columns aligned → Score: 5/5 = 100% ✅
```

#### 2.5 Confidence Calculation

**Purpose**: Compute overall confidence score for the merge decision.

**Scoring Formula**:
```
confidence = 0.0

# Column count match (max 0.3)
if column_count_match:
    confidence += 0.3
elif column_diff <= 1:
    confidence += 0.2
elif column_diff <= 2:
    confidence += 0.1

# Column alignment (max 0.4)
alignment_weight = alignment_score * 0.4
confidence += alignment_weight

# Width similarity (max 0.1)
width_score = 1.0 - min(1.0, width_ratio / 0.2)
confidence += width_score * 0.1

# Overlap ratio (max 0.2)
overlap_score = min(1.0, (overlap_ratio - 0.5) / 0.5)  # 0.5-1.0 → 0.0-1.0
confidence += overlap_score * 0.2

Final: confidence (0.0 - 1.0)
```

**Example Calculation**:
```
Perfect match:
  - Column count: 5 vs 5 → +0.3
  - Alignment: 100% → +0.4
  - Width: 800px vs 802px (0.25%) → +0.1
  - Overlap: 98% → +0.2
  Total: 1.0 (100% confidence) ✅
```

### Fallback Mechanisms

#### Too Many Columns Detected

**Problem**: LSD may detect noise (horizontal lines, text boundaries) as columns.

**Solution**:
```
If detected_columns > 20:
    → Likely noise, not real columns
    → Skip structural validation
    → Use proximity-based fallback
    → Confidence: 0.70 (lower than validated)
```

#### No Columns Detected

**Problem**: Borderless tables or poor image quality prevent column detection.

**Solution**:
```
If columns_detected == 0 in both segments:
    → Tables lack visible borders
    → Fall back to proximity matching
    → Confidence: 0.65
    → Reason: "Proximity match (no columns detected by LSD)"
```

## Configuration Parameters

### Detailed Parameter Reference

| Parameter | Type | Default | Range | Impact |
|-----------|------|---------|-------|--------|
| `merge_split_tables` | bool | `False` | True/False | Master switch for feature |
| `bottom_threshold_ratio` | float | `0.20` | 0.0-1.0 | How close to bottom triggers detection |
| `top_threshold_ratio` | float | `0.15` | 0.0-1.0 | How close to top triggers detection |
| `max_gap_ratio` | float | `0.25` | 0.0-1.0 | Maximum gap between segments |
| `column_alignment_tolerance` | float | `10.0` | 1.0-50.0 | Pixel tolerance for alignment |
| `min_merge_confidence` | float | `0.65` | 0.0-1.0 | Minimum confidence to merge |

### Tuning Guidelines

#### For Documents with Large Headers/Footers

```python
parser = StructuredPDFParser(
    merge_split_tables=True,
    max_gap_ratio=0.30,  # Increase to 30% for larger headers
)
```

#### For Stricter Merging (Fewer False Positives)

```python
parser = StructuredPDFParser(
    merge_split_tables=True,
    min_merge_confidence=0.80,  # Higher threshold
    column_alignment_tolerance=5.0,  # Tighter alignment
)
```

#### For More Aggressive Merging (Catch More Cases)

```python
parser = StructuredPDFParser(
    merge_split_tables=True,
    min_merge_confidence=0.55,  # Lower threshold
    max_gap_ratio=0.35,  # Allow larger gaps
    bottom_threshold_ratio=0.25,  # More lenient position check
    top_threshold_ratio=0.20,
)
```

## Examples

### Example 1: Financial Report Table

```
Document: Quarterly Financial Report
Pages: 2 pages, table spans both

Detection Result:
✅ Match found: Page 1→2
   Confidence: 0.92
   Reason: LSD validation: 6 vs 6 columns, alignment=0.95
   Gap: 18.8% of page height
   
Output:
- Merged image: merged_table_1_2.png
- Markdown: Single table entry with note "pages 1-2"
```

### Example 2: Borderless Table

```
Document: Research Data Table
Pages: 2 pages, no visible borders

Detection Result:
✅ Match found: Page 3→4
   Confidence: 0.70
   Reason: Proximity match (too many columns detected, likely noise)
   Note: Using fallback validation (no clear column boundaries)
   
Output:
- Merged image created
- Lower confidence due to lack of structural validation
```

### Example 3: Rejected Match

```
Document: Separate Tables
Pages: 2 pages with different tables

Detection Result:
❌ No match
   Reason: Column count mismatch (4 vs 7 columns)
   Confidence: 0.45 (below threshold of 0.65)
   
Output:
- Tables processed separately
- No merge attempted
```

## Troubleshooting

### Tables Not Being Merged

**Problem**: Split tables are not being detected.

**Solutions**:

1. **Check Position Thresholds**
   ```python
   # Verify tables are actually near page boundaries
   bottom_threshold_ratio=0.25  # Try increasing
   top_threshold_ratio=0.20
   ```

2. **Check Gap Tolerance**
   ```python
   # Large headers/footers may require:
   max_gap_ratio=0.30  # Increase from 0.25
   ```

3. **Lower Confidence Threshold**
   ```python
   min_merge_confidence=0.60  # Try lowering from 0.65
   ```

4. **Enable Debug Mode**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### False Positives (Incorrect Merges)

**Problem**: Separate tables are being incorrectly merged.

**Solutions**:

1. **Increase Confidence Threshold**
   ```python
   min_merge_confidence=0.75  # More conservative
   ```

2. **Tighten Alignment Tolerance**
   ```python
   column_alignment_tolerance=5.0  # Stricter alignment
   ```

3. **Adjust Position Thresholds**
   ```python
   bottom_threshold_ratio=0.15  # More restrictive
   top_threshold_ratio=0.10
   ```

### Performance Issues

**Problem**: Processing is too slow with split table detection.

**Solutions**:

1. **Disable if not needed**
   ```python
   merge_split_tables=False  # Skip detection entirely
   ```

2. **The feature is already optimized** - Phase 1 filters out most pairs before expensive Phase 2 operations

### Column Detection Failures

**Problem**: LSD not detecting columns correctly.

**Causes & Solutions**:

1. **Low image quality**
   - Solution: Increase DPI
   ```python
   dpi=300  # Instead of 200
   ```

2. **Dashed/broken lines**
   - Solution: Already handled by morphological operations
   - May need to check preprocessing parameters

3. **Borderless tables**
   - Solution: System automatically falls back to proximity matching

## Technical Implementation Details

### Data Structures

```python
@dataclass
class TableSegment:
    """Represents a table segment with bounding box and page info."""
    page_index: int
    box_index: int
    x1: float
    y1: float
    x2: float
    y2: float
    page_width: int
    page_height: int
    image: Image.Image  # Cropped table image
    confidence: float

@dataclass
class SplitTableMatch:
    """Represents a validated split table match."""
    segment1: TableSegment
    segment2: TableSegment
    confidence: float
    merge_reason: str
    column_count1: int
    column_count2: int
```

### Performance Characteristics

- **Time Complexity**: O(n²) for table pairs, but Phase 1 filters dramatically reduce n
- **Space Complexity**: O(n) for storing segments and matches
- **Typical Performance**: 
  - 10 pages with 20 tables → ~10ms for Phase 1, ~50ms for Phase 2
  - Most time spent in image processing (LSD detection)

### Dependencies

- **OpenCV**: For LSD (Line Segment Detector) and image processing
- **NumPy**: For numerical operations
- **PIL**: For image manipulation

## Best Practices

1. **Enable for financial/structured documents**: Most likely to have split tables
2. **Disable for narrative documents**: Tables are usually separate
3. **Adjust thresholds based on document type**: Financial reports may need different settings than academic papers
4. **Review merged results**: Especially when using lower confidence thresholds
5. **Use appropriate DPI**: Higher DPI improves column detection accuracy

## Related Documentation

- [Structured Parser Guide](../parsers/structured-parser.md) - Main parser documentation
- [API Reference](../../api/parsers.md) - Complete parameter reference
- [Examples](../../../examples/basic-usage.md) - Code examples and use cases
