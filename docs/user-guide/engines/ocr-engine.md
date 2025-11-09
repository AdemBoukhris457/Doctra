# OCR Engine

Guide to text extraction using OCR in Doctra.

## Overview

Doctra supports two OCR engines for text extraction:

1. **PyTesseract** (default) - Traditional Tesseract OCR engine with extensive language support
2. **PaddleOCR** - Advanced PP-OCRv5_server model released in PaddleOCR 3.0, offering superior accuracy and performance

You can choose between these engines based on your needs. PyTesseract is the default and works well for most use cases, while PaddleOCR provides enhanced accuracy for complex documents.

## Choosing an OCR Engine

Doctra uses a **dependency injection pattern** for OCR engines. You initialize the OCR engine externally and pass it to the parser. This provides a clearer API, avoids mixed configurations, and allows reusing OCR engines across multiple parsers.

### PyTesseract (Default)

PyTesseract is the default OCR engine and works well for most documents. It offers extensive language support and fine-grained control.

```python
from doctra import StructuredPDFParser
from doctra.engines.ocr import PytesseractOCREngine

# Option 1: Use default PyTesseract (automatic if ocr_engine=None)
parser = StructuredPDFParser()  # Creates default PytesseractOCREngine internally

# Option 2: Explicitly configure PyTesseract
tesseract_ocr = PytesseractOCREngine(
    lang="eng",
    psm=6,
    oem=3
)
parser = StructuredPDFParser(ocr_engine=tesseract_ocr)
```

### PaddleOCR with PP-OCRv5_server

PaddleOCR provides the advanced **PP-OCRv5_server** model (default in PaddleOCR 3.0), which offers:

- **Higher accuracy** for complex documents
- **Better performance** on GPU
- **Advanced text detection** and recognition
- **Automatic model management** (models downloaded automatically)

```python
from doctra import StructuredPDFParser
from doctra.engines.ocr import PaddleOCREngine

# Initialize PaddleOCR engine
paddle_ocr = PaddleOCREngine(
    device="gpu",  # Use "cpu" if no GPU available
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

# Pass to parser
parser = StructuredPDFParser(ocr_engine=paddle_ocr)
```

### Reusing OCR Engines

One of the benefits of the dependency injection pattern is that you can create an OCR engine once and reuse it across multiple parsers:

```python
from doctra.engines.ocr import PytesseractOCREngine
from doctra import StructuredPDFParser, EnhancedPDFParser

# Create OCR engine once
shared_ocr = PytesseractOCREngine(lang="eng", psm=6, oem=3)

# Reuse across multiple parsers
parser1 = StructuredPDFParser(ocr_engine=shared_ocr)
parser2 = EnhancedPDFParser(ocr_engine=shared_ocr)
parser3 = StructuredPDFParser(ocr_engine=shared_ocr)
```

## PyTesseract Parameters

These parameters are configured when initializing `PytesseractOCREngine`:

**lang**
:   Tesseract language code
    - `eng`: English
    - `fra`: French
    - `spa`: Spanish
    - `deu`: German
    - Multiple: `eng+fra`

**psm**
:   Page segmentation mode
    - `3`: Automatic
    - `4`: Assume a single column of text (default)
    - `6`: Uniform block of text
    - `11`: Sparse text
    - `12`: Sparse text with OSD

**oem**
:   OCR engine mode
    - `0`: Legacy
    - `1`: Neural nets LSTM
    - `3`: Default (both)

**extra_config**
:   Additional Tesseract configuration string

**Example:**
```python
from doctra.engines.ocr import PytesseractOCREngine

ocr = PytesseractOCREngine(
    lang="eng",
    psm=6,
    oem=3,
    extra_config=""
)
```

## PaddleOCR Parameters

These parameters are configured when initializing `PaddleOCREngine`:

**device**
:   Device to use for OCR processing
    - `"gpu"`: Use GPU acceleration (default, recommended if available)
    - `"cpu"`: Use CPU processing

**use_doc_orientation_classify**
:   Enable document orientation classification model (default: `False`)
    - Automatically detects and corrects document orientation

**use_doc_unwarping**
:   Enable text image rectification model (default: `False`)
    - Corrects perspective distortion in scanned documents

**use_textline_orientation**
:   Enable text line orientation classification model (default: `False`)
    - Handles rotated text lines

**Example:**
```python
from doctra.engines.ocr import PaddleOCREngine

ocr = PaddleOCREngine(
    device="gpu",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)
```

**Note**: The PP-OCRv5_server model is automatically used by default in PaddleOCR 3.0. Models are automatically downloaded on first use and cached for future use.

## Improving Accuracy

### 1. Choose the Right OCR Engine

For complex documents or when accuracy is critical, consider using PaddleOCR:

```python
from doctra import StructuredPDFParser
from doctra.engines.ocr import PaddleOCREngine

paddle_ocr = PaddleOCREngine(device="gpu")
parser = StructuredPDFParser(ocr_engine=paddle_ocr)
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
from doctra.engines.ocr import PaddleOCREngine

paddle_ocr = PaddleOCREngine(device="gpu")
parser = EnhancedPDFParser(
    use_image_restoration=True,
    ocr_engine=paddle_ocr  # Combine with PaddleOCR for best results
)
```

### 4. Correct Language (PyTesseract)

For PyTesseract, specify the document language when initializing the engine:

```python
from doctra import StructuredPDFParser
from doctra.engines.ocr import PytesseractOCREngine

tesseract_ocr = PytesseractOCREngine(lang="fra")  # For French documents
parser = StructuredPDFParser(ocr_engine=tesseract_ocr)
```

## Multi-language Documents (PyTesseract)

PyTesseract supports multiple languages. Configure this when initializing the engine:

```python
from doctra import StructuredPDFParser
from doctra.engines.ocr import PytesseractOCREngine

tesseract_ocr = PytesseractOCREngine(lang="eng+fra+deu")  # Multiple languages
parser = StructuredPDFParser(ocr_engine=tesseract_ocr)
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

