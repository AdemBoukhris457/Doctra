# Command Line Interface

Doctra provides a powerful CLI for document processing automation.

## Installation

The CLI is automatically installed with Doctra:

```bash
pip install doctra
```

Verify installation:

```bash
doctra --version
```

## Basic Usage

```bash
doctra [COMMAND] [OPTIONS] [ARGUMENTS]
```

## Commands

### parse

Parse a PDF document with full processing.

```bash
doctra parse <pdf_file> [OPTIONS]
```

**Options**:

- `--output-dir PATH`: Output directory (default: `outputs`)
- `--dpi INTEGER`: Image resolution (default: 200)
- `--min-score FLOAT`: Minimum confidence score (default: 0.0)
- `--ocr-lang TEXT`: OCR language code (default: `eng`)
- `--use-vlm`: Enable VLM processing
- `--vlm-provider TEXT`: VLM provider (`openai`, `gemini`, `anthropic`, `openrouter`)
- `--vlm-api-key TEXT`: VLM API key
- `--vlm-model TEXT`: Specific VLM model

**Example**:

```bash
# Basic parsing
doctra parse document.pdf

# With custom settings
doctra parse document.pdf --dpi 300 --output-dir my_outputs

# With VLM
doctra parse document.pdf --use-vlm --vlm-provider openai --vlm-api-key sk-xxx
```

### parse-docx

Parse a Microsoft Word document (.docx file).

```bash
doctra parse-docx <docx_file> [OPTIONS]
```

**Options**:

- `--output-dir PATH`: Output directory (default: `outputs`)
- `--use-vlm`: Enable VLM processing
- `--vlm-provider TEXT`: VLM provider (`openai`, `gemini`, `anthropic`, `openrouter`)
- `--vlm-api-key TEXT`: VLM API key
- `--vlm-model TEXT`: Specific VLM model
- `--extract-images`: Extract embedded images (default: True)
- `--preserve-formatting`: Preserve text formatting (default: True)
- `--table-detection`: Detect and extract tables (default: True)
- `--export-excel`: Export tables to Excel file (default: True)
- `--verbose`: Enable verbose output

**Examples**:

```bash
# Basic DOCX parsing
doctra parse-docx document.docx

# With VLM enhancement
doctra parse-docx document.docx --use-vlm --vlm-provider openai --vlm-api-key sk-xxx

# Custom options
doctra parse-docx document.docx \
  --extract-images \
  --preserve-formatting \
  --table-detection \
  --export-excel \
  --output-dir my_outputs
```

### enhance

Parse with image restoration for low-quality documents.

```bash
doctra enhance <pdf_file> [OPTIONS]
```

**Options**:

- All `parse` options, plus:
- `--restoration-task TEXT`: Restoration task (default: `appearance`)
    - Choices: `appearance`, `dewarping`, `deshadowing`, `deblurring`, `binarization`, `end2end`
- `--restoration-device TEXT`: Device (`cuda`, `cpu`, or auto)
- `--restoration-dpi INTEGER`: DPI for restoration (default: 200)

**Example**:

```bash
# Basic enhancement
doctra enhance scanned.pdf

# Dewarp with GPU
doctra enhance scanned.pdf --restoration-task dewarping --restoration-device cuda

# Full enhancement with VLM
doctra enhance scanned.pdf \
  --restoration-task appearance \
  --restoration-device cuda \
  --use-vlm \
  --vlm-provider openai \
  --vlm-api-key sk-xxx
```

### extract

Extract only charts and/or tables from a document.

```bash
doctra extract <type> <pdf_file> [OPTIONS]
```

**Type**:

- `charts`: Extract only charts
- `tables`: Extract only tables
- `both`: Extract both charts and tables

**Options**:

- `--output-dir PATH`: Output directory (default: `outputs`)
- `--dpi INTEGER`: Image resolution (default: 200)
- `--use-vlm`: Enable VLM for structured data
- `--vlm-provider TEXT`: VLM provider
- `--vlm-api-key TEXT`: VLM API key
- `--vlm-model TEXT`: Specific VLM model

**Examples**:

```bash
# Extract charts only
doctra extract charts report.pdf

# Extract tables with VLM
doctra extract tables report.pdf --use-vlm --vlm-provider gemini --vlm-api-key xxx

# Extract both
doctra extract both report.pdf --output-dir data_extracts
```

### visualize

Visualize layout detection results.

```bash
doctra visualize <pdf_file> [OPTIONS]
```

**Options**:

- `--num-pages INTEGER`: Number of pages to visualize (default: 3)
- `--cols INTEGER`: Number of columns in grid (default: 2)
- `--page-width INTEGER`: Width of each page (default: 800)
- `--spacing INTEGER`: Spacing between pages (default: 40)
- `--output PATH`: Save to file instead of displaying
- `--dpi INTEGER`: Image resolution (default: 200)

**Examples**:

```bash
# Display first 3 pages
doctra visualize document.pdf

# Save visualization of 6 pages
doctra visualize document.pdf --num-pages 6 --output layout.png

# Custom grid layout
doctra visualize document.pdf --num-pages 9 --cols 3 --page-width 600
```

### analyze

Quick document analysis showing structure.

```bash
doctra analyze <pdf_file> [OPTIONS]
```

**Options**:

- `--dpi INTEGER`: Image resolution (default: 200)

**Example**:

```bash
doctra analyze document.pdf
```

Output shows:

```
Document Analysis: document.pdf
=====================================
Total pages: 10

Page 1:
  - Text regions: 5
  - Tables: 1
  - Charts: 0
  - Figures: 2

Page 2:
  ...
```

### info

Display system and configuration information.

```bash
doctra info
```

Shows:

- Doctra version
- Python version
- Installed dependencies
- GPU availability
- System information

**Example output**:

```
Doctra Information
==================
Version: 0.4.3
Python: 3.10.11

Dependencies:
  - PaddlePaddle: 2.5.0
  - PaddleOCR: 2.7.0
  - PyTesseract: 0.3.10
  - Pillow: 10.0.0

System:
  - OS: Windows 10
  - CUDA Available: Yes
  - GPU: NVIDIA GeForce RTX 3080
```

## Batch Processing

### Process Multiple Files

```bash
# Using shell globbing
doctra parse *.pdf --output-dir batch_results

# Using find (Linux/Mac)
find ./documents -name "*.pdf" -exec doctra parse {} \;

# Using PowerShell (Windows)
Get-ChildItem *.pdf | ForEach-Object { doctra parse $_.FullName }
```

### Process Directory

```bash
# Parse all PDFs in directory
for pdf in directory/*.pdf; do
    doctra parse "$pdf" --output-dir results/
done
```

## Environment Variables

Set default values using environment variables:

```bash
# VLM Configuration
export DOCTRA_VLM_PROVIDER=openai
export DOCTRA_VLM_API_KEY=sk-xxx
export DOCTRA_VLM_MODEL=gpt-4o

# Processing Settings
export DOCTRA_DPI=200
export DOCTRA_OCR_LANG=eng
export DOCTRA_DEVICE=cuda

# Then use without flags
doctra parse document.pdf --use-vlm
```

## Configuration File

Create `.doctra.yml` in your project directory:

```yaml
# .doctra.yml
vlm:
  provider: openai
  api_key: sk-xxx
  model: gpt-4o

processing:
  dpi: 200
  ocr_lang: eng
  device: cuda

output:
  base_dir: outputs
```

Then run commands without options:

```bash
doctra parse document.pdf
```

## Output Structure

### Standard Parse

```
outputs/
└── document/
    └── full_parse/
        ├── result.md
        ├── result.html
        └── images/
            ├── figures/
            ├── charts/
            └── tables/
```

### Enhanced Parse

```
outputs/
└── document/
    └── enhanced_parse/
        ├── result.md
        ├── result.html
        ├── document_enhanced.pdf  # Restored PDF
        ├── enhanced_pages/  # Restored page images
        └── images/
```

### Extract

```
outputs/
└── document/
    └── structured_parsing/
        ├── charts/  # Chart images
        ├── tables/  # Table images
        ├── parsed_tables_charts.xlsx  # If VLM enabled
        ├── parsed_tables_charts.html  # If VLM enabled
        └── vlm_items.json  # If VLM enabled
```

### DOCX Parse

```
outputs/
└── document/
    ├── document.md
    ├── document.html
    ├── tables.xlsx  # With Table of Contents
    └── images/
        ├── image1.png
        ├── image2.jpg
        └── ...
```

## Examples

### Example 1: Basic Document Processing

```bash
# Parse a financial report
doctra parse financial_report.pdf

# Output: outputs/financial_report/full_parse/
```

### Example 2: Enhanced Processing with VLM

```bash
# Process scanned document with enhancement and VLM
doctra enhance scanned_document.pdf \
  --restoration-task appearance \
  --restoration-device cuda \
  --use-vlm \
  --vlm-provider openai \
  --vlm-api-key $OPENAI_API_KEY \
  --output-dir enhanced_results
```

### Example 3: DOCX Document Processing

```bash
# Basic DOCX parsing
doctra parse-docx report.docx

# With VLM enhancement for structured data
doctra parse-docx financial_report.docx \
  --use-vlm \
  --vlm-provider openai \
  --vlm-api-key $OPENAI_API_KEY \
  --export-excel

# Result: outputs/financial_report/document.md, document.html, tables.xlsx
```

### Example 4: Extract Data for Analysis

```bash
# Extract all tables with VLM to get structured data
doctra extract tables data_report.pdf \
  --use-vlm \
  --vlm-provider gemini \
  --vlm-api-key $GEMINI_API_KEY

# Result: outputs/data_report/structured_parsing/parsed_tables_charts.xlsx
```

### Example 5: Batch Processing Pipeline

```bash
#!/bin/bash
# process_documents.sh

INPUT_DIR="./input_pdfs"
OUTPUT_DIR="./processed"

for pdf in "$INPUT_DIR"/*.pdf; do
    echo "Processing: $pdf"
    
    # First enhance the document
    doctra enhance "$pdf" \
      --restoration-task appearance \
      --restoration-device cuda \
      --output-dir "$OUTPUT_DIR"
    
    echo "Completed: $pdf"
done

echo "All documents processed!"
```

### Example 6: Quality Check with Visualization

```bash
# Visualize layout detection before full processing
doctra visualize document.pdf --num-pages 5 --output viz_check.png

# Review viz_check.png to ensure good detection

# Then proceed with full processing
doctra parse document.pdf --use-vlm
```

## Troubleshooting

### Command Not Found

**Problem**: `doctra: command not found`

**Solution**:

```bash
# Ensure Doctra is installed
pip install doctra

# Or use module syntax
python -m doctra.cli.main parse document.pdf
```

### API Key Errors

**Problem**: VLM API key not recognized

**Solution**:

```bash
# Set environment variable
export OPENAI_API_KEY=sk-xxx

# Or pass directly
doctra parse document.pdf --use-vlm --vlm-api-key sk-xxx
```

### Poppler Errors

**Problem**: `pdftoppm not found`

**Solution**: Install Poppler (see [Installation Guide](../getting-started/installation.md#system-dependencies))

### Memory Errors

**Problem**: Out of memory during processing

**Solution**:

```bash
# Reduce DPI
doctra parse large.pdf --dpi 150

# Or process pages individually
doctra parse large.pdf --max-pages 10
```

## Advanced Usage

### Custom Scripts

Combine CLI with shell scripts:

```bash
#!/bin/bash
# Smart processing script

PDF=$1

# Check file size
SIZE=$(du -k "$PDF" | cut -f1)

if [ $SIZE -gt 10000 ]; then
    echo "Large file, using lower DPI..."
    doctra parse "$PDF" --dpi 150
else
    echo "Standard processing..."
    doctra parse "$PDF" --dpi 200 --use-vlm
fi
```

### Integration with Other Tools

```bash
# OCR + Search Pipeline
doctra parse document.pdf
grep "keyword" outputs/document/full_parse/result.md

# Extract data and analyze
doctra extract tables report.pdf --use-vlm
python analyze_tables.py outputs/report/structured_parsing/parsed_tables_charts.xlsx
```

## See Also

- [Python API](../api/parsers.md) - Programmatic usage
- [Web UI](web-ui.md) - Graphical interface
- [Examples](../examples/basic-usage.md) - Usage examples

