# 解析器 API 参考

所有 Doctra 解析器的完整 API 文档。

## StructuredPDFParser

用于全面 PDF 文档处理的基础解析器。

::: doctra.parsers.structured_pdf_parser.StructuredPDFParser
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

---

## EnhancedPDFParser

具有图像恢复功能的增强解析器。

::: doctra.parsers.enhanced_pdf_parser.EnhancedPDFParser
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

---

## ChartTablePDFParser

用于提取图表和表格的专业解析器。

::: doctra.parsers.table_chart_extractor.ChartTablePDFParser
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

---

## PaddleOCRVLPDFParser

使用 PaddleOCRVL 视觉语言模型的端到端文档解析器。

::: doctra.parsers.paddleocr_vl_parser.PaddleOCRVLPDFParser
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

---

## StructuredDOCXParser

用于 Microsoft Word 文档（.docx 文件）的全面解析器。

::: doctra.parsers.structured_docx_parser.StructuredDOCXParser
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

---

## 快速参考

### StructuredPDFParser

```python
from doctra import StructuredPDFParser
from doctra.engines.ocr import PytesseractOCREngine, PaddleOCREngine
from doctra.engines.vlm.service import VLMStructuredExtractor

# 初始化 OCR 引擎（可选 - 如果为 None 则默认为 PyTesseract）
ocr_engine = PytesseractOCREngine(lang="eng", psm=4, oem=3)

# 初始化 VLM 引擎（可选 - None 以禁用 VLM）
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    vlm_model="gpt-4o",  # 可选
    api_key="your-api-key"
)

parser = StructuredPDFParser(
    # 布局检测
    layout_model_name: str = "PP-DocLayout_plus-L",
    dpi: int = 200,
    min_score: float = 0.0,
    
    # OCR 引擎（传递初始化的引擎实例）
    ocr_engine: Optional[Union[PytesseractOCREngine, PaddleOCREngine]] = None,
    
    # VLM 引擎（传递初始化的引擎实例）
    vlm: Optional[VLMStructuredExtractor] = None,
    
    # 分割表格合并
    merge_split_tables: bool = False,
    bottom_threshold_ratio: float = 0.20,
    top_threshold_ratio: float = 0.15,
    max_gap_ratio: float = 0.25,
    column_alignment_tolerance: float = 10.0,
    min_merge_confidence: float = 0.65,
    
    # 输出设置
    box_separator: str = "\n"
)

# 解析文档
parser.parse(
    pdf_path: str,
    output_base_dir: str = "outputs"
)

# 可视化布局
parser.display_pages_with_boxes(
    pdf_path: str,
    num_pages: int = 3,
    cols: int = 2,
    page_width: int = 800,
    spacing: int = 40,
    save_path: str = None
)
```

### EnhancedPDFParser

```python
from doctra import EnhancedPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

# 初始化 VLM 引擎（可选）
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-api-key"
)

parser = EnhancedPDFParser(
    # 图像恢复
    use_image_restoration: bool = True,
    restoration_task: str = "appearance",
    restoration_device: str = None,
    restoration_dpi: int = 200,
    
    # VLM 引擎（传递初始化的引擎实例）
    vlm: Optional[VLMStructuredExtractor] = None,
    
    # 布局检测
    layout_model_name: str = "PP-DocLayout_plus-L",
    dpi: int = 200,
    min_score: float = 0.0,
    
    # OCR 引擎（可选）
    ocr_engine: Optional[Union[PytesseractOCREngine, PaddleOCREngine]] = None,
    
    # 分割表格合并
    merge_split_tables: bool = False,
    bottom_threshold_ratio: float = 0.20,
    top_threshold_ratio: float = 0.15,
    max_gap_ratio: float = 0.25,
    column_alignment_tolerance: float = 10.0,
    min_merge_confidence: float = 0.65,
    
    # 输出设置
    box_separator: str = "\n"
)

# 使用增强功能解析
parser.parse(
    pdf_path: str,
    output_base_dir: str = "outputs"
)
```

### ChartTablePDFParser

```python
from doctra import ChartTablePDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

# 初始化 VLM 引擎（可选）
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-api-key"
)

parser = ChartTablePDFParser(
    # 提取设置
    extract_charts: bool = True,
    extract_tables: bool = True,
    
    # VLM 引擎（传递初始化的引擎实例）
    vlm: Optional[VLMStructuredExtractor] = None,
    
    # 布局检测
    layout_model_name: str = "PP-DocLayout_plus-L",
    dpi: int = 200,
    min_score: float = 0.0,
    
    # 分割表格合并
    merge_split_tables: bool = False,
    bottom_threshold_ratio: float = 0.20,
    top_threshold_ratio: float = 0.15,
    max_gap_ratio: float = 0.25,
    column_alignment_tolerance: float = 10.0,
    min_merge_confidence: float = 0.65,
)

# 提取图表/表格
parser.parse(
    pdf_path: str,
    output_base_dir: str = "outputs"
)
```

### StructuredDOCXParser

```python
from doctra import StructuredDOCXParser
from doctra.engines.vlm.service import VLMStructuredExtractor

# 初始化 VLM 引擎（可选）
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-api-key"
)

parser = StructuredDOCXParser(
    # VLM 引擎（传递初始化的引擎实例）
    vlm: Optional[VLMStructuredExtractor] = None,
    
    # 处理选项
    extract_images: bool = True,
    preserve_formatting: bool = True,
    table_detection: bool = True,
    export_excel: bool = True
)

# 解析 DOCX 文档
parser.parse(
    docx_path: str
)
```

## 参数参考

### 布局检测参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `layout_model_name` | str | "PP-DocLayout_plus-L" | PaddleOCR 布局检测模型 |
| `dpi` | int | 200 | 渲染 PDF 页面的图像分辨率 |
| `min_score` | float | 0.0 | 检测元素的最小置信度分数 |

### OCR 参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `ocr_engine` | `Optional[Union[PytesseractOCREngine, PaddleOCREngine]]` | `None` | OCR 引擎实例。如果为 `None`，则创建默认的 `PytesseractOCREngine`，使用 lang="eng", psm=4, oem=3 |

**OCR 引擎配置：**

OCR 引擎必须在外部初始化并传递给解析器。这使用依赖注入模式以实现更清晰的 API 设计。

**PytesseractOCREngine 参数：**
- `lang` (str, 默认: "eng")：Tesseract 语言代码（例如 "eng"、"fra"、"spa"、"deu"，或多个："eng+fra"）
- `psm` (int, 默认: 4)：页面分割模式（3=自动，4=单列，6=统一块，11=稀疏文本，12=带 OSD 的稀疏）
- `oem` (int, 默认: 3)：OCR 引擎模式（0=传统，1=神经网络 LSTM，3=默认两者）
- `extra_config` (str, 默认: "")：额外的 Tesseract 配置字符串

**PaddleOCREngine 参数：**
- `device` (str, 默认: "gpu")：OCR 处理设备（"cpu" 或 "gpu"）
- `use_doc_orientation_classify` (bool, 默认: False)：启用文档方向分类
- `use_doc_unwarping` (bool, 默认: False)：启用文本图像校正
- `use_textline_orientation` (bool, 默认: False)：启用文本行方向分类

**示例：**
```python
from doctra.engines.ocr import PytesseractOCREngine, PaddleOCREngine

# PyTesseract
tesseract_ocr = PytesseractOCREngine(lang="eng", psm=4, oem=3)
parser = StructuredPDFParser(ocr_engine=tesseract_ocr)

# PaddleOCR
paddle_ocr = PaddleOCREngine(device="gpu")
parser = StructuredPDFParser(ocr_engine=paddle_ocr)
```

**注意**：使用 PaddleOCR 时，默认使用 PaddleOCR 3.0 的 PP-OCRv5_server 模型。模型在首次使用时自动下载。

### VLM 参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `vlm` | `Optional[VLMStructuredExtractor]` | `None` | VLM 引擎实例。如果为 `None`，则禁用 VLM 处理。 |

**VLM 引擎配置：**

VLM 引擎必须在外部初始化并传递给解析器。这使用依赖注入模式以实现更清晰的 API 设计。

**VLMStructuredExtractor 参数：**
- `vlm_provider` (str, 必需)：要使用的 VLM 提供商（"openai"、"gemini"、"anthropic"、"openrouter"、"qianfan"、"ollama"）
- `vlm_model` (str, 可选)：要使用的模型名称（默认为提供商特定的默认值）
- `api_key` (str, 可选)：VLM 提供商的 API 密钥（除 Ollama 外的所有提供商都需要）

**示例：**
```python
from doctra.engines.vlm.service import VLMStructuredExtractor

# 初始化 VLM 引擎
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    vlm_model="gpt-4o",  # 可选
    api_key="your-api-key"
)

# 传递给解析器
parser = StructuredPDFParser(vlm=vlm_engine)
```

### 图像恢复参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `use_image_restoration` | bool | True | 启用图像恢复 |
| `restoration_task` | str | "appearance" | 恢复任务类型 |
| `restoration_device` | str | None | 设备："cuda"、"cpu" 或 None（自动检测） |
| `restoration_dpi` | int | 200 | 恢复处理的 DPI |

### 分割表格合并参数

适用于 `StructuredPDFParser` 和 `EnhancedPDFParser`。

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `merge_split_tables` | bool | False | 启用自动检测和合并跨页分割的表格 |
| `bottom_threshold_ratio` | float | 0.20 | 检测页面底部附近表格的比率（0-1）。在此比率内距离底部的表格被视为候选。 |
| `top_threshold_ratio` | float | 0.15 | 检测页面顶部附近表格的比率（0-1）。在此比率内距离顶部的表格被视为候选。 |
| `max_gap_ratio` | float | 0.25 | 表格段之间的最大允许间隙，作为页面高度的比率。考虑页眉、页脚和页边距。 |
| `column_alignment_tolerance` | float | 10.0 | 比较表格结构时列对齐验证的像素容差。 |
| `min_merge_confidence` | float | 0.65 | 合并两个表格段所需的最小置信度分数（0-1）。值越高越保守。 |

### 提取参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `extract_charts` | bool | True | 提取图表元素 |
| `extract_tables` | bool | True | 提取表格元素 |

### DOCX 处理参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `extract_images` | bool | True | 从 DOCX 中提取嵌入的图像 |
| `preserve_formatting` | bool | True | 在输出中保留文本格式 |
| `table_detection` | bool | True | 检测并提取表格 |
| `export_excel` | bool | True | 将表格导出到 Excel 文件 |

### 输出参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `box_separator` | str | "\n" | 检测元素之间的分隔符 |

## 返回值

### parse() 方法

返回：`None`

在指定的 `output_base_dir` 中生成输出文件：

```
outputs/
└── <document_name>/
    ├── full_parse/  # 或 'enhanced_parse/'、'structured_parsing/'
    │   ├── result.md
    │   ├── result.html
    │   ├── tables.xlsx  # 如果启用 VLM
    │   ├── tables.html  # 如果启用 VLM
    │   ├── vlm_items.json  # 如果启用 VLM
    │   └── images/
    │       ├── figures/
    │       ├── charts/
    │       └── tables/
```

对于 DOCX 解析，生成：

```
outputs/
└── <document_name>/
    ├── document.md
    ├── document.html
    ├── tables.xlsx  # 带目录
    └── images/
        ├── image1.png
        ├── image2.jpg
        └── ...
```

### display_pages_with_boxes() 方法

返回：`None`

显示或保存布局检测的可视化。

## 错误处理

所有解析器可能引发：

- `FileNotFoundError`：未找到 PDF 文件
- `ValueError`：无效的参数值
- `RuntimeError`：处理错误（例如，未找到 Poppler）
- `APIError`：VLM API 错误（启用 VLM 时）

错误处理示例：

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

try:
    parser.parse("document.pdf")
except FileNotFoundError:
    print("未找到 PDF 文件！")
except ValueError as e:
    print(f"无效参数：{e}")
except RuntimeError as e:
    print(f"处理错误：{e}")
```

## 示例

有关详细使用示例，请参阅[示例](../examples/basic-usage.md)部分。

