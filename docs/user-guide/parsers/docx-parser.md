# DOCX Parser

The `StructuredDOCXParser` is a comprehensive parser for Microsoft Word documents (.docx files) that extracts text, tables, images, and structured content while preserving document formatting and order.

## Overview

The DOCX parser provides:

- **Complete DOCX Support**: Extracts text, tables, images, and formatting from Word documents
- **Document Order Preservation**: Maintains the original sequence of elements (paragraphs, tables, images)
- **VLM Integration**: Optional Vision Language Model support for image analysis and table extraction
- **Multiple Output Formats**: Generates Markdown, HTML, and Excel files
- **Excel Export**: Creates structured Excel files with Table of Contents and clickable hyperlinks
- **Formatting Preservation**: Maintains text formatting (bold, italic, etc.) in output
- **Progress Tracking**: Real-time progress bars for VLM processing

## Basic Usage

```python
from doctra.parsers.structured_docx_parser import StructuredDOCXParser

# Basic DOCX parsing
parser = StructuredDOCXParser(
    extract_images=True,
    preserve_formatting=True,
    table_detection=True,
    export_excel=True
)

# Parse DOCX document
parser.parse("document.docx")
```

## Advanced Configuration

### With VLM Enhancement

```python
parser = StructuredDOCXParser(
    # VLM Settings
    use_vlm=True,
    vlm_provider="openai",  # or "gemini", "anthropic", "openrouter"
    vlm_model="gpt-4-vision",
    vlm_api_key="your_api_key",
    
    # Processing Options
    extract_images=True,
    preserve_formatting=True,
    table_detection=True,
    export_excel=True
)

# Parse with VLM enhancement
parser.parse("document.docx")
```

### Custom Processing Options

```python
parser = StructuredDOCXParser(
    # Disable image extraction for faster processing
    extract_images=False,
    
    # Disable formatting preservation for plain text
    preserve_formatting=False,
    
    # Disable table detection if not needed
    table_detection=False,
    
    # Disable Excel export
    export_excel=False
)
```

## Output Structure

When parsing a DOCX document, the parser creates:

```
outputs/document_name/
├── document.md          # Markdown version with all content
├── document.html        # HTML version with styling
├── tables.xlsx         # Excel file with extracted tables
│   ├── Table of Contents  # Summary sheet with hyperlinks
│   ├── Table 1         # Individual table sheets
│   ├── Table 2
│   └── ...
└── images/             # Extracted images
    ├── image1.png
    ├── image2.jpg
    └── ...
```

## VLM Integration Features

When VLM is enabled, the parser:

- **Analyzes Images**: Uses AI to extract structured data from images
- **Creates Tables**: Converts chart images to structured table data
- **Enhanced Excel Output**: Includes VLM-extracted tables in Excel file
- **Smart Content Display**: Shows extracted tables instead of images in Markdown/HTML
- **Progress Tracking**: Shows progress based on number of images processed

### VLM Processing Flow

1. **Image Detection**: Scans document for embedded images
2. **VLM Analysis**: Processes each image with the selected VLM model
3. **Structured Extraction**: Converts visual content to structured data
4. **Excel Integration**: Adds VLM-extracted tables to Excel output
5. **Content Replacement**: Replaces image references with extracted tables in Markdown/HTML

## Excel Output Features

The generated Excel file includes:

- **Table of Contents**: Summary sheet with all extracted tables
- **Clickable Hyperlinks**: Navigate between table sheets
- **Consistent Styling**: Professional formatting with colors and fonts
- **VLM Integration**: Includes both original and VLM-extracted tables
- **Sheet Naming**: Uses actual table titles as sheet names

## CLI Usage

```bash
# Basic DOCX parsing
doctra parse-docx document.docx

# With VLM enhancement
doctra parse-docx document.docx --use-vlm --vlm-provider openai --vlm-api-key your_key

# Custom options
doctra parse-docx document.docx \
  --extract-images \
  --preserve-formatting \
  --table-detection \
  --export-excel
```

## Web UI Usage

The DOCX parser is available in the Gradio web interface:

1. **Upload DOCX File**: Drag and drop your Word document
2. **Configure VLM**: Enable VLM and set your API key
3. **Processing Options**: Choose extraction settings
4. **Parse Document**: Click "Parse DOCX" to process
5. **View Results**: Preview content and download outputs

## Parameters Reference

### VLM Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_vlm` | bool | False | Enable VLM processing |
| `vlm_provider` | str | None | Provider: "openai", "gemini", "anthropic", "openrouter" |
| `vlm_api_key` | str | None | API key for the VLM provider |
| `vlm_model` | str | None | Specific model to use (provider-dependent) |

### Processing Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `extract_images` | bool | True | Extract embedded images from DOCX |
| `preserve_formatting` | bool | True | Preserve text formatting in output |
| `table_detection` | bool | True | Detect and extract tables |
| `export_excel` | bool | True | Export tables to Excel file |

## Error Handling

The parser handles common errors:

- **File Not Found**: Invalid DOCX file path
- **Permission Errors**: Read-only files or locked documents
- **VLM API Errors**: Invalid API keys or rate limits
- **Processing Errors**: Corrupted documents or unsupported formats

```python
try:
    parser.parse("document.docx")
except FileNotFoundError:
    print("DOCX file not found!")
except Exception as e:
    print(f"Processing error: {e}")
```

## Best Practices

### Performance Optimization

- **Disable Unused Features**: Turn off image extraction or Excel export if not needed
- **VLM Usage**: Use VLM only when structured data extraction is required
- **Large Documents**: Consider processing large documents in smaller chunks

### Output Quality

- **Formatting Preservation**: Keep enabled for better output quality
- **Table Detection**: Essential for structured data extraction
- **VLM Enhancement**: Improves table extraction from images

### Error Prevention

- **File Validation**: Ensure DOCX files are not corrupted
- **API Keys**: Set up VLM API keys before processing
- **Permissions**: Ensure write access to output directory

## Examples

### Example 1: Basic Document Processing

```python
from doctra.parsers.structured_docx_parser import StructuredDOCXParser

# Initialize parser
parser = StructuredDOCXParser()

# Process document
parser.parse("report.docx")

# Output: outputs/report/document.md, document.html, tables.xlsx
```

### Example 2: VLM-Enhanced Processing

```python
parser = StructuredDOCXParser(
    use_vlm=True,
    vlm_provider="openai",
    vlm_api_key="your_api_key"
)

# Process with AI enhancement
parser.parse("financial_report.docx")

# Output: Enhanced Excel with VLM-extracted tables
```

### Example 3: Custom Configuration

```python
parser = StructuredDOCXParser(
    extract_images=True,
    preserve_formatting=False,  # Plain text output
    table_detection=True,
    export_excel=True
)

# Process with custom settings
parser.parse("data_document.docx")
```

## Troubleshooting

### Common Issues

1. **"python-docx not installed"**
   - Solution: `pip install python-docx`

2. **"No tables extracted"**
   - Check if `table_detection=True`
   - Verify document contains tables

3. **"VLM API error"**
   - Verify API key is correct
   - Check provider and model compatibility

4. **"Images not extracted"**
   - Check if `extract_images=True`
   - Verify document contains embedded images

### Performance Tips

- Use VLM only when needed (adds processing time)
- Disable unused features for faster processing
- Process large documents in smaller batches
- Ensure sufficient disk space for outputs

## Related Documentation

- [API Reference](../../api/parsers.md#structureddocxparser)
- [VLM Integration](../engines/vlm-integration.md)
- [Export Formats](../outputs/export-formats.md)
- [Web UI Guide](../../interfaces/web-ui.md)
