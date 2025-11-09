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
- **Ollama**: Local models (no API key required)

## Basic Configuration

Doctra uses a **dependency injection pattern** for VLM engines. You initialize the VLM engine externally and pass it to the parser. This provides a clearer API, avoids mixed configurations, and allows reusing VLM engines across multiple parsers.

```python
from doctra import StructuredPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

# Initialize VLM engine
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-api-key"
)

# Pass VLM engine to parser
parser = StructuredPDFParser(vlm=vlm_engine)

parser.parse("document.pdf")
```

## Provider Setup

### OpenAI

```python
from doctra import StructuredPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    vlm_model="gpt-4o",  # Optional, uses default if None
    api_key="sk-xxx"
)

parser = StructuredPDFParser(vlm=vlm_engine)
```

### Gemini

```python
from doctra import StructuredPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="gemini",
    api_key="your-gemini-key"
)

parser = StructuredPDFParser(vlm=vlm_engine)
```

### Anthropic

```python
from doctra import StructuredPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="anthropic",
    api_key="your-anthropic-key"
)

parser = StructuredPDFParser(vlm=vlm_engine)
```

### OpenRouter

```python
from doctra import StructuredPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openrouter",
    vlm_model="x-ai/grok-4",  # Optional, defaults to x-ai/grok-4
    api_key="your-openrouter-key"
)

parser = StructuredPDFParser(vlm=vlm_engine)
```

**Available Models:**
- `x-ai/grok-4` (default) - Grok-4 model
- `anthropic/claude-3.5-sonnet` - Claude 3.5 Sonnet
- `openai/gpt-4o` - GPT-4o via OpenRouter
- `google/gemini-pro-vision` - Gemini Pro Vision

### Qianfan (Baidu AI Cloud)

```python
from doctra import StructuredPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="qianfan",
    vlm_model="ernie-4.5-turbo-vl-32k",  # Optional, defaults to ernie-4.5-turbo-vl-32k
    api_key="your-qianfan-key"
)

parser = StructuredPDFParser(vlm=vlm_engine)
```

**Available ERNIE Models:**
- `ernie-4.5-turbo-vl-32k` (default) - vision model with 32k context

### Ollama (Local Models)

```python
from doctra import StructuredPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="ollama",
    vlm_model="llava:latest",  # Optional, defaults to llava:latest
    api_key=None  # No API key required for Ollama
)

parser = StructuredPDFParser(vlm=vlm_engine)
```

**Available Models:**
- `llava:latest` (default) - LLaVA vision model
- `llava:7b` - LLaVA 7B model
- `llava:13b` - LLaVA 13B model
- `gemma2:latest` - Gemma 2 model
- `qwen2-vl:latest` - Qwen2-VL model

**Prerequisites:**
- Ollama must be installed and running locally
- No API key required
- Models are downloaded automatically on first use

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

