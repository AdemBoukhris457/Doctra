# DocRes Engine

Guide to using the DocRes image restoration engine.

## Overview

The `DocResEngine` provides direct access to document image restoration capabilities using the DocRes model. Use it for standalone image enhancement or as part of the parsing pipeline.

## Key Features

- **6 Restoration Tasks**: Comprehensive document enhancement
- **GPU Acceleration**: CUDA support for faster processing
- **Flexible Input**: Images or PDFs
- **Detailed Metadata**: Processing information returned

## Basic Usage

```python
from doctra import DocResEngine

# Initialize engine
engine = DocResEngine(device="cuda")

# Restore image
restored_img, metadata = engine.restore_image(
    image="document.jpg",
    task="appearance"
)

# Save result
restored_img.save("restored.jpg")
```

## Restoration Tasks

| Task | Description | Use Case |
|------|-------------|----------|
| `appearance` | General enhancement | Most documents |
| `dewarping` | Fix perspective | Scanned at angle |
| `deshadowing` | Remove shadows | Poor lighting |
| `deblurring` | Reduce blur | Motion/focus issues |
| `binarization` | B&W conversion | Clean text |
| `end2end` | Full pipeline | Severe degradation |

## PDF Restoration

```python
engine = DocResEngine(device="cuda")

restored_pdf = engine.restore_pdf(
    pdf_path="low_quality.pdf",
    output_path="enhanced.pdf",
    task="appearance",
    dpi=300
)
```

## See Also

- [Enhanced Parser](../parsers/enhanced-parser.md) - Integrated restoration
- [API Reference](../../api/engines.md) - Complete API documentation
- [Core Concepts](../core-concepts.md) - Understanding restoration

