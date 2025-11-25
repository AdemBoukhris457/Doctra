# System Requirements

This page outlines the hardware and software requirements for running Doctra effectively.

## Python Requirements

- **Python Version**: 3.8 or higher
- **Operating Systems**: 
    - Linux (Ubuntu, Debian, CentOS, etc.)
    - macOS (10.13 or higher)
    - Windows (10 or higher)

## Hardware Requirements

### Minimum Requirements

| Component | Specification |
|-----------|---------------|
| CPU | Dual-core processor, 2.0 GHz |
| RAM | 4 GB |
| Disk Space | 2 GB for installation + space for outputs |
| GPU | Not required (CPU processing available) |

### Recommended Requirements

| Component | Specification |
|-----------|---------------|
| CPU | Quad-core processor, 3.0 GHz or higher |
| RAM | 8 GB or more |
| Disk Space | 10 GB for installation + models + outputs |
| GPU | NVIDIA GPU with 4+ GB VRAM (for acceleration) |

### Performance Considerations

#### Processing Speed

Typical processing times for a 10-page PDF:

| Configuration | Time |
|---------------|------|
| CPU only (4 cores) | ~2-3 minutes |
| GPU (NVIDIA GTX 1060) | ~1-2 minutes |
| GPU (NVIDIA RTX 3080) | ~30-60 seconds |

!!! note "Factors Affecting Performance"
    - Document complexity (number of images, tables, charts)
    - Image resolution (DPI setting)
    - Image restoration enabled/disabled
    - VLM processing (requires network calls)

#### Memory Usage

Expected RAM usage:

- **Basic parsing**: 500 MB - 2 GB
- **Enhanced parsing**: 1 GB - 4 GB
- **VLM processing**: Additional 500 MB - 1 GB
- **High DPI (300+)**: Additional 2-4 GB

## Software Dependencies

### Required

1. **Poppler** - PDF rendering and processing
    - Version: Latest stable release
    - Installation: See [Installation Guide](installation.md#system-dependencies)

2. **Tesseract OCR** - Text extraction
    - Automatically installed via Python dependencies
    - No manual installation required

### Optional

1. **CUDA Toolkit** - For GPU acceleration
    - Version: 11.8 or higher
    - Required only for GPU processing
    - Download: [NVIDIA CUDA Downloads](https://developer.nvidia.com/cuda-downloads)

2. **cuDNN** - Deep learning GPU acceleration
    - Version: 8.6 or higher
    - Required only for GPU processing
    - Download: [NVIDIA cuDNN Downloads](https://developer.nvidia.com/cudnn)

## GPU Support

### CUDA Requirements

For GPU-accelerated processing:

- **GPU**: NVIDIA GPU with Compute Capability 3.5 or higher
- **CUDA**: Version 11.8 or higher
- **cuDNN**: Version 8.6 or higher
- **Driver**: Compatible NVIDIA driver

### Supported GPUs

Doctra's image restoration works with CUDA-capable NVIDIA GPUs:

| GPU Series | Support Level |
|------------|---------------|
| GeForce GTX 10xx and newer | ✅ Full support |
| GeForce RTX series | ✅ Full support |
| Tesla series | ✅ Full support |
| Quadro series | ✅ Full support |
| AMD GPUs | ❌ Not supported |
| Intel GPUs | ❌ Not supported |

### Checking GPU Compatibility

Verify CUDA availability:

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
```

## Network Requirements

### Model Downloads

On first use, Doctra downloads AI models:

- **PaddleOCR models**: ~300 MB
- **DocRes models**: ~200 MB
- **Total**: ~500 MB initial download

Models are cached locally after first download.

### VLM API Access

If using Vision Language Models:

- Stable internet connection required
- API rate limits apply (provider-dependent)
- Bandwidth: Minimal (images are compressed before sending)

## Storage Requirements

### Installation

| Component | Size |
|-----------|------|
| Doctra package | ~50 MB |
| Python dependencies | ~500 MB |
| AI models (downloaded on first use) | ~500 MB |
| **Total** | **~1 GB** |

### Processing Outputs

Expected output sizes per document:

| Document Size | Output Size (approx.) |
|---------------|----------------------|
| 10-page report | 5-20 MB |
| 50-page document | 25-100 MB |
| 100-page book | 50-200 MB |

!!! tip "Storage Planning"
    Plan for 2-10x the original PDF size for outputs, depending on:
    
    - Number of images in the document
    - DPI settings used
    - Whether image restoration is enabled

## Browser Requirements (Web UI)

For the Gradio-based web interface:

- **Modern Browser**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **JavaScript**: Must be enabled
- **Local Network**: Access to localhost required

## Cloud Deployment

Doctra can run on cloud platforms:

### Recommended Cloud Specs

| Provider | Instance Type | vCPUs | RAM | GPU |
|----------|--------------|-------|-----|-----|
| AWS | t3.xlarge | 4 | 16 GB | Optional |
| GCP | n1-standard-4 | 4 | 15 GB | Optional |
| Azure | Standard_D4s_v3 | 4 | 16 GB | Optional |

For GPU processing:

| Provider | Instance Type | GPU | VRAM |
|----------|--------------|-----|------|
| AWS | g4dn.xlarge | T4 | 16 GB |
| GCP | n1-standard-4 + T4 | T4 | 16 GB |
| Azure | NC6 | K80 | 12 GB |

### Google Colab

Doctra works perfectly in Google Colab:

- **Free Tier**: Sufficient for most use cases
- **GPU**: Available in free tier
- **RAM**: 12-13 GB in free tier
- **Disk**: 100+ GB temporary storage

## Operating System Specific Notes

### Linux

- **Best Performance**: Generally fastest due to better CUDA support
- **Easy Setup**: Package managers make dependency installation simple
- **Docker**: Easy containerization for deployment

### macOS

- **No GPU Support**: CUDA not available on macOS
- **Good CPU Performance**: Efficient on Apple Silicon (M1/M2)
- **Poppler**: Easy installation via Homebrew

### Windows

- **GPU Support**: Full CUDA support available
- **Poppler Setup**: Requires manual installation or conda
- **Path Configuration**: May need to add Poppler to PATH

## Performance Optimization

### For CPU-Only Systems

```python
parser = StructuredPDFParser(
    dpi=150,  # Lower resolution
    min_score=0.7  # Higher threshold = fewer elements
)
```

### For GPU Systems

```python
from doctra import EnhancedPDFParser

parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_device="cuda",  # Use GPU
    restoration_dpi=300  # Higher quality
)
```

### Memory Optimization

```python
# Process documents in batches
import os
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

# Process one at a time to manage memory
for pdf_file in pdf_files:
    parser.parse(pdf_file)
    # Parser is reused, memory is cleaned between documents
```

## Troubleshooting

### Out of Memory Errors

**Solutions**:

1. Reduce DPI: `dpi=100`
2. Disable image restoration
3. Close other applications
4. Process fewer pages at once

### Slow Processing

**Solutions**:

1. Enable GPU: `restoration_device="cuda"`
2. Reduce DPI: `dpi=150`
3. Upgrade hardware
4. Process during off-peak hours

### Model Download Failures

**Solutions**:

1. Check internet connection
2. Verify firewall settings
3. Use VPN if behind restrictive network
4. Manual model download (see troubleshooting guide)

## Next Steps

- [Installation Guide](installation.md) - Install Doctra
- [Quick Start](quick-start.md) - Start using Doctra
- [Performance Tips](../user-guide/core-concepts.md) - Optimize your setup

