# VLM Integration

Guide to using Vision Language Models with Doctra.

## Overview

Doctra integrates with Vision Language Models (VLMs) to convert visual elements (charts, tables, figures) into structured data. This enables automatic data extraction and conversion to Excel, HTML, and JSON formats.

## Supported Providers

- **OpenAI**: GPT-4 Vision, GPT-4o
- **Gemini**: Google's vision models
- **Anthropic**: Claude with vision
- **OpenRouter**: Access multiple models
- **Qianfan**: Baidu AI Cloud ERNIE models

## Basic Configuration

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser(
    use_vlm=True,
    vlm_provider="openai",
    vlm_api_key="your-api-key"
)

parser.parse("document.pdf")
```

## Provider Setup

### OpenAI

```python
parser = StructuredPDFParser(
    use_vlm=True,
    vlm_provider="openai",
    vlm_api_key="sk-xxx",
    vlm_model="gpt-4o"  # Optional
)
```

### Gemini

```python
parser = StructuredPDFParser(
    use_vlm=True,
    vlm_provider="gemini",
    vlm_api_key="your-gemini-key"
)
```

### Anthropic

```python
parser = StructuredPDFParser(
    use_vlm=True,
    vlm_provider="anthropic",
    vlm_api_key="your-anthropic-key"
)
```

### Qianfan (Baidu AI Cloud)

```python
parser = StructuredPDFParser(
    use_vlm=True,
    vlm_provider="qianfan",
    vlm_api_key="your-qianfan-key",
    vlm_model="ernie-4.5-turbo-vl-32k"  # Optional, defaults to ernie-4.5-turbo-vl-32k
)
```

**Available ERNIE Models:**
- `ernie-4.5-turbo-vl-32k` (default) - vision model with 32k context


## What Gets Processed

With VLM enabled:

- **Tables**: Converted to Excel/HTML with cell data
- **Charts**: Data points extracted + descriptions
- **Figures**: Descriptions and context generated

## Output Files

```
outputs/
└── document/
    └── full_parse/
        ├── tables.xlsx      # Extracted table data
        ├── tables.html      # HTML tables
        ├── vlm_items.json   # Structured data
        └── ...
```

## Cost Considerations

VLM processing requires API calls:

- ~1-10 calls per document
- ~$0.01-$0.10 per document
- Costs vary by provider

## See Also

- [Parsers](../parsers/structured-parser.md) - Using VLM with parsers
- [API Reference](../../api/parsers.md) - VLM configuration options
- [Examples](../../examples/basic-usage.md) - VLM usage examples

