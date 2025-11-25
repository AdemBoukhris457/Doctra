# Changelog

All notable changes to Doctra will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.3] - 2024-XX-XX

### Current Release

This is the current stable release of Doctra.

### Features

- **Multiple PDF Parsers**
    - `StructuredPDFParser`: Complete document processing
    - `EnhancedPDFParser`: Parsing with image restoration
    - `ChartTablePDFParser`: Specialized chart/table extraction

- **Image Restoration**
    - DocRes integration for document enhancement
    - 6 restoration tasks: appearance, dewarping, deshadowing, deblurring, binarization, end2end
    - GPU acceleration support

- **VLM Integration**
    - Support for OpenAI, Gemini, Anthropic, OpenRouter, Qianfan, and Ollama
    - Structured data extraction from charts and tables
    - Automatic conversion to Excel/HTML/JSON

- **Output Formats**
    - Markdown with embedded images
    - HTML for web viewing
    - Excel for data analysis
    - JSON for programmatic access
    - High-quality image extraction

- **User Interfaces**
    - Gradio-based web UI
    - Comprehensive CLI
    - Full Python API

- **Visualization**
    - Layout detection visualization
    - Bounding box overlays
    - Confidence scores
    - Multi-page grid display

### Dependencies

- Python 3.8+
- PaddlePaddle >= 2.4.0
- PaddleOCR >= 2.6.0
- Pillow >= 8.0.0
- OpenCV >= 4.5.0
- Pandas >= 1.3.0
- Tesseract >= 0.1.3
- PyTesseract >= 0.3.10
- pdf2image >= 1.16.0
- Anthropic >= 0.40.0
- Outlines >= 0.0.34

## [Unreleased]

### Planned Features

- [ ] Support for additional document formats (DOCX, PPTX)
- [ ] Improved table structure recognition
- [ ] Batch processing API
- [ ] Docker container
- [ ] Cloud deployment guides
- [ ] Additional VLM providers
- [ ] Performance optimizations
- [ ] Multilingual documentation

## Version History

### [0.4.3] - Current

Current stable release with full feature set.

### [0.4.0] - Previous

Initial public release with core features.

## Upgrade Guide

### From 0.4.0 to 0.4.3

No breaking changes. Simply upgrade:

```bash
pip install --upgrade doctra
```

## Contributing

See our [Contributing Guide](contributing/development.md) for information on:

- Reporting bugs
- Requesting features
- Submitting pull requests
- Development setup

## Support

- **Documentation**: [https://ademboukhris457.github.io/Doctra/](https://ademboukhris457.github.io/Doctra/)
- **GitHub Issues**: [https://github.com/AdemBoukhris457/Doctra/issues](https://github.com/AdemBoukhris457/Doctra/issues)
- **PyPI**: [https://pypi.org/project/doctra/](https://pypi.org/project/doctra/)

