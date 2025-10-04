# Web UI

Guide to using Doctra's Gradio-based web interface.

## Overview

Doctra provides a user-friendly web interface for document processing without writing code.

## Launching the UI

### Python

```python
from doctra import launch_ui

# Launch web interface
launch_ui()
```

### Command Line

```bash
python -m doctra.ui.app
```

### Module Script

```bash
python gradio_app.py
```

The UI opens at: `http://127.0.0.1:7860`

## Interface Tabs

### 1. Full Parse

Complete document processing:

- Upload PDF
- Configure settings
- View results
- Download outputs

### 2. Tables & Charts

Specialized extraction:

- Extract charts and/or tables
- Enable VLM processing
- Configure API keys
- Download structured data

### 3. DocRes

Image restoration:

- Upload images or PDFs
- Select restoration task
- Compare before/after
- Download enhanced files

### 4. Enhanced Parser

Combined restoration and parsing:

- Upload PDF
- Configure restoration
- Enable VLM
- Get comprehensive results

## Features

- **Drag & Drop**: Easy file upload
- **Real-time Progress**: See processing status
- **Preview Results**: View output in browser
- **Download ZIP**: Get all results packaged
- **Configuration**: Adjust all settings
- **API Key Management**: Secure key input

## Configuration Options

Each tab provides settings for:

- DPI resolution
- Language selection
- VLM provider and API key
- Restoration tasks
- Output preferences

## Sharing the UI

Launch with public URL:

```python
from doctra import build_demo

demo = build_demo()
demo.launch(share=True)
```

This generates a temporary public URL for sharing.

## Use Cases

- **Non-technical Users**: No coding required
- **Quick Processing**: Fast one-off document processing
- **Experimentation**: Try different settings
- **Demonstrations**: Show Doctra capabilities
- **Prototyping**: Test before integrating

## See Also

- [CLI Reference](cli.md) - Command line interface
- [API Reference](../api/parsers.md) - Python API
- [Examples](../examples/basic-usage.md) - Usage examples

