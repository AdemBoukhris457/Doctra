# OCR Engine

Guide to text extraction using OCR in Doctra.

## Overview

Doctra uses Tesseract OCR to extract text from document images. The OCR engine is highly configurable for different document types and languages.

## Configuration

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser(
    ocr_lang="eng",
    ocr_psm=6,
    ocr_oem=3
)
```

## Parameters

**ocr_lang**
:   Tesseract language code
    - `eng`: English
    - `fra`: French
    - `spa`: Spanish
    - `deu`: German
    - Multiple: `eng+fra`

**ocr_psm**
:   Page segmentation mode
    - `3`: Automatic
    - `6`: Uniform block (default)
    - `11`: Sparse text
    - `12`: Sparse with OSD

**ocr_oem**
:   OCR engine mode
    - `0`: Legacy
    - `1`: Neural nets LSTM
    - `3`: Default (both)

## Improving Accuracy

### 1. Increase DPI

```python
parser = StructuredPDFParser(dpi=300)
```

### 2. Use Image Restoration

```python
from doctra import EnhancedPDFParser

parser = EnhancedPDFParser(
    use_image_restoration=True
)
```

### 3. Correct Language

```python
parser = StructuredPDFParser(
    ocr_lang="fra"  # For French documents
)
```

## Multi-language Documents

```python
parser = StructuredPDFParser(
    ocr_lang="eng+fra+deu"  # Multiple languages
)
```

## See Also

- [Enhanced Parser](../parsers/enhanced-parser.md) - Improve OCR with restoration
- [Core Concepts](../core-concepts.md) - Understanding OCR in the pipeline
- [API Reference](../../api/parsers.md) - OCR configuration options

