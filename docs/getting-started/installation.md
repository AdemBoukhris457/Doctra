# Installation

This guide will help you install Doctra and its dependencies on your system.

## Requirements

- Python 3.8 or higher
- pip package manager
- Poppler (for PDF processing)
- Tesseract OCR (automatically handled by dependencies)

## Installing Doctra

### From PyPI (Recommended)

The easiest way to install Doctra is from PyPI using pip:

```bash
pip install doctra
```

This will install Doctra and all Python dependencies automatically.

### From Source

To install the latest development version from source:

```bash
git clone https://github.com/AdemBoukhris457/Doctra.git
cd Doctra
pip install -e .
```

The `-e` flag installs in editable mode, which is useful for development.

## System Dependencies

Doctra requires **Poppler** for PDF processing. Follow the instructions for your operating system:

### :simple-ubuntu: Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install poppler-utils
```

### :simple-apple: macOS

Using Homebrew:

```bash
brew install poppler
```

If you don't have Homebrew, install it from [brew.sh](https://brew.sh).

### :simple-windows: Windows

#### Option 1: Using Conda

```bash
conda install -c conda-forge poppler
```

#### Option 2: Manual Installation

1. Download Poppler for Windows from [this link](https://poppler.freedesktop.org/)
2. Extract the archive
3. Add the `bin` directory to your system PATH

### :simple-googlecolab: Google Colab

```bash
!apt-get install poppler-utils
```

## Optional Dependencies

### VLM Providers

To use Vision Language Models for structured data extraction, install the appropriate provider:

#### OpenAI

```bash
pip install doctra[openai]
```

#### Google Gemini

```bash
pip install doctra[gemini]
```

#### All VLM Providers

```bash
pip install doctra[openai,gemini]
```

### Development Dependencies

For contributing to Doctra:

```bash
pip install doctra[dev]
```

This installs testing, linting, and formatting tools.

## Verifying Installation

After installation, verify that Doctra is installed correctly:

```python
import doctra
print(doctra.__version__)
```

You should see the version number printed (e.g., `0.4.3`).

### Check System Dependencies

To check if Poppler is installed correctly:

```bash
pdftoppm -v
```

You should see the Poppler version information.

## GPU Support

### CUDA for Faster Processing

Doctra can leverage GPU acceleration for image restoration tasks. To enable GPU support:

1. Install CUDA-compatible PyTorch:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

2. Verify CUDA is available:

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
```

### PaddlePaddle GPU Support

For GPU-accelerated layout detection:

```bash
pip uninstall paddlepaddle
pip install paddlepaddle-gpu
```

!!! note "GPU Requirements"
    GPU support requires:
    
    - NVIDIA GPU with CUDA Compute Capability 3.5+
    - CUDA 11.8 or higher
    - cuDNN 8.6 or higher

## Troubleshooting

### ImportError: No module named 'doctra'

**Solution**: Ensure Doctra is installed in your active Python environment:

```bash
pip list | grep doctra
```

If not listed, reinstall with `pip install doctra`.

### Poppler not found

**Symptoms**: Error message mentioning "pdftoppm" or "Poppler"

**Solution**: 

1. Verify Poppler installation: `pdftoppm -v`
2. If not installed, follow the [System Dependencies](#system-dependencies) section
3. On Windows, ensure Poppler's `bin` directory is in your PATH

### CUDA out of memory

**Solution**: Use CPU processing or reduce DPI settings:

```python
parser = StructuredPDFParser(
    dpi=150,  # Reduce from default 200
    restoration_device="cpu"  # Force CPU usage
)
```

### PaddleOCR model download fails

**Solution**: Manually download models or check your network connection:

```python
from doctra.parsers import StructuredPDFParser

# This will trigger model download
parser = StructuredPDFParser()
```

Models are downloaded to `~/.paddleocr/` on first use.

## Next Steps

Now that you have Doctra installed, check out:

- [Quick Start](quick-start.md) - Your first Doctra program
- [System Requirements](system-requirements.md) - Detailed hardware requirements
- [User Guide](../user-guide/core-concepts.md) - Learn about core concepts

## Getting Help

If you encounter issues during installation:

1. Check the [GitHub Issues](https://github.com/AdemBoukhris457/Doctra/issues) for similar problems
2. Create a new issue with:
    - Your operating system and version
    - Python version (`python --version`)
    - Full error message
    - Installation method used

