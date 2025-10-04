# Engines API Reference

Complete API documentation for Doctra engines.

## DocResEngine

Image restoration engine for document enhancement.

::: doctra.engines.image_restoration.DocResEngine
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

---

## Quick Reference

### DocResEngine

```python
from doctra import DocResEngine

# Initialize engine
engine = DocResEngine(
    device: str = None,  # "cuda", "cpu", or None for auto-detect
    use_half_precision: bool = False,
    model_path: str = None,
    mbd_path: str = None
)

# Restore single image
restored_img, metadata = engine.restore_image(
    image: Union[str, np.ndarray, PIL.Image.Image],
    task: str = "appearance"
)

# Restore PDF
output_path = engine.restore_pdf(
    pdf_path: str,
    output_path: str = None,
    task: str = "appearance",
    dpi: int = 200
)
```

## Parameter Reference

### Initialization Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device` | str | None | Processing device: "cuda", "cpu", or None (auto-detect) |
| `use_half_precision` | bool | False | Use FP16 for faster GPU processing |
| `model_path` | str | None | Custom path to restoration model |
| `mbd_path` | str | None | Custom path to MBD model |

### Restoration Tasks

| Task | Description | Use Case |
|------|-------------|----------|
| `"appearance"` | General appearance enhancement | Most documents (default) |
| `"dewarping"` | Correct perspective distortion | Scanned with perspective issues |
| `"deshadowing"` | Remove shadows and lighting artifacts | Poor lighting conditions |
| `"deblurring"` | Reduce blur and improve sharpness | Motion blur, focus issues |
| `"binarization"` | Convert to black and white | Clean text extraction |
| `"end2end"` | Complete restoration pipeline | Severely degraded documents |

## Methods

### restore_image()

Restore a single image.

**Parameters**:

- `image` (str | np.ndarray | PIL.Image.Image): Input image (path, numpy array, or PIL Image)
- `task` (str): Restoration task to perform

**Returns**:

- `restored_img` (PIL.Image.Image): Restored image
- `metadata` (dict): Processing metadata including task, device, and timing

**Example**:

```python
from doctra import DocResEngine

engine = DocResEngine(device="cuda")
restored, meta = engine.restore_image("blurry.jpg", task="deblurring")

print(f"Task: {meta['task']}")
print(f"Device: {meta['device']}")
print(f"Time: {meta['processing_time']:.2f}s")

# Save restored image
restored.save("restored.jpg")
```

### restore_pdf()

Restore all pages in a PDF document.

**Parameters**:

- `pdf_path` (str): Path to input PDF
- `output_path` (str, optional): Path for output PDF (auto-generated if None)
- `task` (str): Restoration task to perform
- `dpi` (int): Resolution for processing

**Returns**:

- `output_path` (str): Path to the restored PDF

**Example**:

```python
from doctra import DocResEngine

engine = DocResEngine(device="cuda")
restored_pdf = engine.restore_pdf(
    pdf_path="low_quality.pdf",
    output_path="enhanced.pdf",
    task="appearance",
    dpi=300
)

print(f"Restored PDF saved to: {restored_pdf}")
```

## Device Selection

### Auto-Detection

```python
# Automatically uses GPU if available, otherwise CPU
engine = DocResEngine()
```

### Explicit GPU

```python
# Force GPU usage (will error if CUDA not available)
engine = DocResEngine(device="cuda")
```

### Explicit CPU

```python
# Force CPU usage (slower but always available)
engine = DocResEngine(device="cpu")
```

### Check Device

```python
import torch

print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
```

## Performance Optimization

### Half Precision

Use FP16 for ~2x speed on modern GPUs:

```python
engine = DocResEngine(
    device="cuda",
    use_half_precision=True  # Faster, minimal quality loss
)
```

**Requirements**:
- NVIDIA GPU with compute capability 7.0+ (Volta or newer)
- Examples: RTX 20xx, RTX 30xx, RTX 40xx, A100, V100

### Batch Processing

Process multiple images efficiently:

```python
from doctra import DocResEngine

engine = DocResEngine(device="cuda")

# Process image list
images = ["doc1.jpg", "doc2.jpg", "doc3.jpg"]
restored_images = []

for img_path in images:
    restored, _ = engine.restore_image(img_path, task="appearance")
    restored_images.append(restored)
    restored.save(f"restored_{img_path}")
```

### DPI Considerations

| DPI | Quality | Speed | Memory | Best For |
|-----|---------|-------|--------|----------|
| 100 | Low | Fast | Low | Quick previews |
| 150 | Medium | Medium | Medium | General use |
| 200 | Good | Slow | Medium | Default setting |
| 300 | High | Very Slow | High | High-quality scans |

## Metadata

The `restore_image()` method returns metadata:

```python
restored, metadata = engine.restore_image("doc.jpg", "appearance")

print(metadata)
# {
#     'task': 'appearance',
#     'device': 'cuda',
#     'processing_time': 1.23,
#     'input_size': (1920, 1080),
#     'output_size': (1920, 1080)
# }
```

## Error Handling

```python
from doctra import DocResEngine

engine = DocResEngine(device="cuda")

try:
    restored, meta = engine.restore_image("document.jpg", "appearance")
except FileNotFoundError:
    print("Image not found")
except RuntimeError as e:
    print(f"CUDA error: {e}")
    # Fall back to CPU
    engine = DocResEngine(device="cpu")
    restored, meta = engine.restore_image("document.jpg", "appearance")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Integration with Parsers

DocResEngine is integrated into EnhancedPDFParser:

```python
from doctra import EnhancedPDFParser

# This internally uses DocResEngine
parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="appearance",
    restoration_device="cuda"
)

parser.parse("document.pdf")
```

For standalone restoration:

```python
from doctra import DocResEngine

# Step 1: Restore PDF
engine = DocResEngine(device="cuda")
enhanced_pdf = engine.restore_pdf(
    pdf_path="low_quality.pdf",
    output_path="enhanced.pdf",
    task="appearance"
)

# Step 2: Parse enhanced PDF
from doctra import StructuredPDFParser

parser = StructuredPDFParser()
parser.parse(enhanced_pdf)
```

## Examples

### Example 1: Dewarp Scanned Document

```python
from doctra import DocResEngine

engine = DocResEngine(device="cuda")

# Fix perspective distortion
restored, meta = engine.restore_image(
    "scanned_with_distortion.jpg",
    task="dewarping"
)

restored.save("dewarped.jpg")
print(f"Processed in {meta['processing_time']:.2f}s")
```

### Example 2: Remove Shadows

```python
from doctra import DocResEngine

engine = DocResEngine(device="cuda")

# Remove shadow artifacts
restored, meta = engine.restore_image(
    "document_with_shadows.jpg",
    task="deshadowing"
)

restored.save("no_shadows.jpg")
```

### Example 3: Batch PDF Restoration

```python
import os
from doctra import DocResEngine

engine = DocResEngine(device="cuda", use_half_precision=True)

pdf_dir = "input_pdfs"
output_dir = "restored_pdfs"
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(pdf_dir):
    if filename.endswith(".pdf"):
        input_path = os.path.join(pdf_dir, filename)
        output_path = os.path.join(output_dir, f"restored_{filename}")
        
        print(f"Processing {filename}...")
        engine.restore_pdf(
            pdf_path=input_path,
            output_path=output_path,
            task="appearance",
            dpi=200
        )
```

## See Also

- [Enhanced Parser](../user-guide/parsers/enhanced-parser.md) - Using restoration with parsing
- [Core Concepts](../user-guide/core-concepts.md) - Understanding image restoration
- [Examples](../examples/advanced-examples.md) - Advanced usage patterns

