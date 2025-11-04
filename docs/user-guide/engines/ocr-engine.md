# OCR Engine

Guide to text extraction using OCR in Doctra.

## Overview

Doctra supports two OCR engines for text extraction:

1. **PyTesseract** (default) - Traditional Tesseract OCR engine with extensive language support
2. **PaddleOCR** - Advanced PP-OCRv5_server model released in PaddleOCR 3.0, offering superior accuracy and performance

You can choose between these engines based on your needs. PyTesseract is the default and works well for most use cases, while PaddleOCR provides enhanced accuracy for complex documents.

## Choosing an OCR Engine

### PyTesseract (Default)

PyTesseract is the default OCR engine and works well for most documents. It offers extensive language support and fine-grained control.

```python
from doctra import StructuredPDFParser

# PyTesseract is the default - no need to specify
parser = StructuredPDFParser(
    ocr_lang="eng",
    ocr_psm=6,
    ocr_oem=3
)

# Or explicitly specify it
parser = StructuredPDFParser(
    ocr_engine="pytesseract",
    ocr_lang="eng",
    ocr_psm=6,
    ocr_oem=3
)
```

### PaddleOCR with PP-OCRv5_server

PaddleOCR provides the advanced **PP-OCRv5_server** model (default in PaddleOCR 3.0), which offers:

- **Higher accuracy** for complex documents
- **Better performance** on GPU
- **Advanced text detection** and recognition
- **Automatic model management** (models downloaded automatically)

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser(
    ocr_engine="paddleocr",
    paddleocr_device="gpu",  # Use "cpu" if no GPU available
    paddleocr_use_doc_orientation_classify=False,
    paddleocr_use_doc_unwarping=False,
    paddleocr_use_textline_orientation=False
)
```

## PyTesseract Parameters

These parameters are only used when `ocr_engine="pytesseract"` (or when using the default):

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

**ocr_extra_config**
:   Additional Tesseract configuration string

## PaddleOCR Parameters

These parameters are only used when `ocr_engine="paddleocr"`:

**paddleocr_device**
:   Device to use for OCR processing
    - `"gpu"`: Use GPU acceleration (default, recommended if available)
    - `"cpu"`: Use CPU processing

**paddleocr_use_doc_orientation_classify**
:   Enable document orientation classification model (default: `False`)
    - Automatically detects and corrects document orientation

**paddleocr_use_doc_unwarping**
:   Enable text image rectification model (default: `False`)
    - Corrects perspective distortion in scanned documents

**paddleocr_use_textline_orientation**
:   Enable text line orientation classification model (default: `False`)
    - Handles rotated text lines

**Note**: The PP-OCRv5_server model is automatically used by default in PaddleOCR 3.0. Models are automatically downloaded on first use and cached for future use.

## Improving Accuracy

### 1. Choose the Right OCR Engine

For complex documents or when accuracy is critical, consider using PaddleOCR:

```python
parser = StructuredPDFParser(
    ocr_engine="paddleocr",
    paddleocr_device="gpu"  # Use GPU for better performance
)
```

### 2. Increase DPI

Higher resolution improves text recognition for both engines:

```python
parser = StructuredPDFParser(dpi=300)
```

### 3. Use Image Restoration

Enhance document quality before OCR:

```python
from doctra import EnhancedPDFParser

parser = EnhancedPDFParser(
    use_image_restoration=True,
    ocr_engine="paddleocr"  # Combine with PaddleOCR for best results
)
```

### 4. Correct Language (PyTesseract)

For PyTesseract, specify the document language:

```python
parser = StructuredPDFParser(
    ocr_engine="pytesseract",
    ocr_lang="fra"  # For French documents
)
```

## Multi-language Documents (PyTesseract)

PyTesseract supports multiple languages:

```python
parser = StructuredPDFParser(
    ocr_engine="pytesseract",
    ocr_lang="eng+fra+deu"  # Multiple languages
)
```

## When to Use Each Engine

### Use PyTesseract when:
- Working with standard documents
- Need multi-language support
- Want fine-grained control over OCR parameters
- CPU-only environment

### Use PaddleOCR when:
- Dealing with complex or degraded documents
- Need maximum accuracy
- Have GPU available for faster processing
- Working with Asian languages (better support)
- Processing large batches of documents

## See Also

- [Enhanced Parser](../parsers/enhanced-parser.md) - Improve OCR with restoration
- [Core Concepts](../core-concepts.md) - Understanding OCR in the pipeline
- [API Reference](../../api/parsers.md) - OCR configuration options

