# VLM 集成

在 Doctra 中使用视觉语言模型的指南。

## 概述

Doctra 与视觉语言模型（VLM）集成，将视觉元素（图表、表格、图形）转换为结构化数据。这支持自动数据提取并转换为 Excel、HTML 和 JSON 格式。

## 支持的提供商

- **OpenAI**：GPT-4 Vision、GPT-4o
- **Gemini**：Google 的视觉模型
- **Anthropic**：带视觉功能的 Claude
- **OpenRouter**：访问多个模型
- **Qianfan**：百度智能云 ERNIE 模型
- **Ollama**：本地模型（不需要 API 密钥）

## 基本配置

Doctra 对 VLM 引擎使用**依赖注入模式**。您在外部初始化 VLM 引擎并将其传递给解析器。这提供了更清晰的 API，避免了混合配置，并允许在多个解析器之间重用 VLM 引擎。

```python
from doctra import StructuredPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

# 初始化 VLM 引擎
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-api-key"
)

# 将 VLM 引擎传递给解析器
parser = StructuredPDFParser(vlm=vlm_engine)

parser.parse("document.pdf")
```

## 提供商设置

### OpenAI

```python
from doctra import StructuredPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    vlm_model="gpt-4o",  # 可选，如果为 None 则使用默认值
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
    vlm_model="x-ai/grok-4",  # 可选，默认为 x-ai/grok-4
    api_key="your-openrouter-key"
)

parser = StructuredPDFParser(vlm=vlm_engine)
```

**可用模型：**
- `x-ai/grok-4`（默认）- Grok-4 模型
- `anthropic/claude-3.5-sonnet` - Claude 3.5 Sonnet
- `openai/gpt-4o` - 通过 OpenRouter 的 GPT-4o
- `google/gemini-pro-vision` - Gemini Pro Vision

### Qianfan（百度智能云）

```python
from doctra import StructuredPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="qianfan",
    vlm_model="ernie-4.5-turbo-vl-32k",  # 可选，默认为 ernie-4.5-turbo-vl-32k
    api_key="your-qianfan-key"
)

parser = StructuredPDFParser(vlm=vlm_engine)
```

**可用的 ERNIE 模型：**
- `ernie-4.5-turbo-vl-32k`（默认）- 具有 32k 上下文的视觉模型

### Ollama（本地模型）

```python
from doctra import StructuredPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="ollama",
    vlm_model="llava:latest",  # 可选，默认为 llava:latest
    api_key=None  # Ollama 不需要 API 密钥
)

parser = StructuredPDFParser(vlm=vlm_engine)
```

**可用模型：**
- `llava:latest`（默认）- LLaVA 视觉模型
- `llava:7b` - LLaVA 7B 模型
- `llava:13b` - LLaVA 13B 模型
- `gemma2:latest` - Gemma 2 模型
- `qwen2-vl:latest` - Qwen2-VL 模型

**先决条件：**
- Ollama 必须已安装并在本地运行
- 不需要 API 密钥
- 模型在首次使用时自动下载

## 处理内容

启用 VLM 后：

- **表格**：转换为带单元格数据的 Excel/HTML
- **图表**：提取数据点 + 描述
- **图形**：生成描述和上下文

## 输出文件

```
outputs/
└── document/
    └── full_parse/
        ├── tables.xlsx      # 提取的表格数据
        ├── tables.html      # HTML 表格
        ├── vlm_items.json   # 结构化数据
        └── ...
```

## 成本考虑

VLM 处理需要 API 调用：

- 每个文档约 1-10 次调用
- 每个文档约 $0.01-$0.10
- 成本因提供商而异

## 另请参阅

- [解析器](../parsers/structured-parser.md) - 在解析器中使用 VLM
- [API 参考](../../api/parsers.md) - VLM 配置选项
- [示例](../../examples/basic-usage.md) - VLM 使用示例

