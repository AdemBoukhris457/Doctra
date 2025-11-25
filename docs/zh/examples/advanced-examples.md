# 高级示例

高级用法模式和集成示例。

## 多阶段处理管道

```python
from doctra import DocResEngine, StructuredPDFParser

# 阶段 1：恢复文档
engine = DocResEngine(device="cuda")
enhanced_pdf = engine.restore_pdf(
    pdf_path="low_quality.pdf",
    output_path="enhanced.pdf",
    task="appearance"
)

# 阶段 2：解析增强的文档
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-key"
)

parser = StructuredPDFParser(vlm=vlm_engine)
parser.parse(enhanced_pdf)
```

## 使用不同 VLM 提供商的自定义处理

```python
from doctra import ChartTablePDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

# 使用 OpenAI
vlm_openai = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="sk-xxx"
)
parser_openai = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=True,
    vlm=vlm_openai
)

# 使用 Gemini（成本效益高）
vlm_gemini = VLMStructuredExtractor(
    vlm_provider="gemini",
    api_key="gemini-key"
)
parser_gemini = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=True,
    vlm=vlm_gemini
)

# 使用 Qianfan ERNIE（百度智能云）
vlm_qianfan = VLMStructuredExtractor(
    vlm_provider="qianfan",
    vlm_model="ernie-4.5-turbo-vl-32k",
    api_key="qianfan-key"
)
parser_qianfan = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=True,
    vlm=vlm_qianfan
)

# 使用不同的提供商解析
parser_openai.parse("doc.pdf")
parser_gemini.parse("doc.pdf")
parser_qianfan.parse("doc.pdf")
```

## 并行批量处理

```python
from concurrent.futures import ThreadPoolExecutor
from doctra import StructuredPDFParser

def process_pdf(pdf_path):
    parser = StructuredPDFParser()
    try:
        parser.parse(pdf_path)
        return f"成功：{pdf_path}"
    except Exception as e:
        return f"错误 {pdf_path}：{e}"

# 并行处理多个 PDF
pdf_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(process_pdf, pdf_files)
    
for result in results:
    print(result)
```

## 动态 DPI 选择

```python
import os
from doctra import StructuredPDFParser

def smart_parse(pdf_path):
    # 根据文件大小选择 DPI
    file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
    
    if file_size < 5:
        dpi = 200  # 标准质量
    elif file_size < 20:
        dpi = 150  # 大文件使用较低 DPI
    else:
        dpi = 100  # 超大文件使用非常低的 DPI
    
    parser = StructuredPDFParser(dpi=dpi)
    print(f"以 {dpi} DPI 处理 {pdf_path}")
    parser.parse(pdf_path)

smart_parse("document.pdf")
```

## 与数据分析集成

```python
from doctra import ChartTablePDFParser
import pandas as pd

# 提取表格
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-key"
)

parser = ChartTablePDFParser(
    extract_tables=True,
    vlm=vlm_engine
)

parser.parse("financial_report.pdf")

# 加载并分析提取的数据
excel_path = "outputs/financial_report/structured_parsing/parsed_tables_charts.xlsx"
xls = pd.ExcelFile(excel_path)

for sheet_name in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet_name)
    print(f"\n表格：{sheet_name}")
    print(df.describe())
```

## 另请参阅

- [基本示例](basic-usage.md) - 更简单的示例
- [集成](integration.md) - 集成模式
- [API 参考](../api/parsers.md) - API 文档

