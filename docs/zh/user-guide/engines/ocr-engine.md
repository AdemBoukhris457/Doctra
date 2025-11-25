# OCR 引擎

在 Doctra 中使用 OCR 进行文本提取的指南。

## 概述

Doctra 支持两种 OCR 引擎进行文本提取：

1. **PyTesseract**（默认）- 传统的 Tesseract OCR 引擎，具有广泛的语言支持
2. **PaddleOCR** - PaddleOCR 3.0 发布的高级 PP-OCRv5_server 模型，提供卓越的准确性和性能

您可以根据需要选择这些引擎。PyTesseract 是默认引擎，适用于大多数用例，而 PaddleOCR 为复杂文档提供更高的准确性。

## 选择 OCR 引擎

Doctra 对 OCR 引擎使用**依赖注入模式**。您在外部初始化 OCR 引擎并将其传递给解析器。这提供了更清晰的 API，避免了混合配置，并允许在多个解析器之间重用 OCR 引擎。

### PyTesseract（默认）

PyTesseract 是默认的 OCR 引擎，适用于大多数文档。它提供广泛的语言支持和细粒度控制。

```python
from doctra import StructuredPDFParser
from doctra.engines.ocr import PytesseractOCREngine

# 选项 1：使用默认的 PyTesseract（如果 ocr_engine=None 则自动创建）
parser = StructuredPDFParser()  # 内部创建默认的 PytesseractOCREngine

# 选项 2：显式配置 PyTesseract
tesseract_ocr = PytesseractOCREngine(
    lang="eng",
    psm=6,
    oem=3
)
parser = StructuredPDFParser(ocr_engine=tesseract_ocr)
```

### PaddleOCR with PP-OCRv5_server

PaddleOCR 提供高级的 **PP-OCRv5_server** 模型（PaddleOCR 3.0 中的默认模型），提供：

- **更高的准确性**用于复杂文档
- **更好的性能**在 GPU 上
- **高级文本检测**和识别
- **自动模型管理**（模型自动下载）

```python
from doctra import StructuredPDFParser
from doctra.engines.ocr import PaddleOCREngine

# 初始化 PaddleOCR 引擎
paddle_ocr = PaddleOCREngine(
    device="gpu",  # 如果没有 GPU 则使用 "cpu"
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

# 传递给解析器
parser = StructuredPDFParser(ocr_engine=paddle_ocr)
```

### 重用 OCR 引擎

依赖注入模式的一个好处是您可以创建一次 OCR 引擎并在多个解析器之间重用：

```python
from doctra.engines.ocr import PytesseractOCREngine
from doctra import StructuredPDFParser, EnhancedPDFParser

# 创建一次 OCR 引擎
shared_ocr = PytesseractOCREngine(lang="eng", psm=6, oem=3)

# 在多个解析器之间重用
parser1 = StructuredPDFParser(ocr_engine=shared_ocr)
parser2 = EnhancedPDFParser(ocr_engine=shared_ocr)
parser3 = StructuredPDFParser(ocr_engine=shared_ocr)
```

## PyTesseract 参数

这些参数在初始化 `PytesseractOCREngine` 时配置：

**lang**
:   Tesseract 语言代码
    - `eng`：英语
    - `fra`：法语
    - `spa`：西班牙语
    - `deu`：德语
    - 多个：`eng+fra`

**psm**
:   页面分割模式
    - `3`：自动
    - `4`：假设单列文本（默认）
    - `6`：统一文本块
    - `11`：稀疏文本
    - `12`：带 OSD 的稀疏文本

**oem**
:   OCR 引擎模式
    - `0`：传统
    - `1`：神经网络 LSTM
    - `3`：默认（两者）

**extra_config**
:   额外的 Tesseract 配置字符串

**示例：**
```python
from doctra.engines.ocr import PytesseractOCREngine

ocr = PytesseractOCREngine(
    lang="eng",
    psm=6,
    oem=3,
    extra_config=""
)
```

## PaddleOCR 参数

这些参数在初始化 `PaddleOCREngine` 时配置：

**device**
:   用于 OCR 处理的设备
    - `"gpu"`：使用 GPU 加速（默认，如果可用则推荐）
    - `"cpu"`：使用 CPU 处理

**use_doc_orientation_classify**
:   启用文档方向分类模型（默认：`False`）
    - 自动检测和校正文档方向

**use_doc_unwarping**
:   启用文本图像校正模型（默认：`False`）
    - 校正扫描文档中的透视失真

**use_textline_orientation**
:   启用文本行方向分类模型（默认：`False`）
    - 处理旋转的文本行

**示例：**
```python
from doctra.engines.ocr import PaddleOCREngine

ocr = PaddleOCREngine(
    device="gpu",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)
```

**注意**：PP-OCRv5_server 模型在 PaddleOCR 3.0 中默认自动使用。模型在首次使用时自动下载并缓存以供将来使用。

## 提高准确性

### 1. 选择正确的 OCR 引擎

对于复杂文档或准确性至关重要时，考虑使用 PaddleOCR：

```python
from doctra import StructuredPDFParser
from doctra.engines.ocr import PaddleOCREngine

paddle_ocr = PaddleOCREngine(device="gpu")
parser = StructuredPDFParser(ocr_engine=paddle_ocr)
```

### 2. 增加 DPI

更高的分辨率可提高两个引擎的文本识别：

```python
parser = StructuredPDFParser(dpi=300)
```

### 3. 使用图像恢复

在 OCR 之前增强文档质量：

```python
from doctra import EnhancedPDFParser
from doctra.engines.ocr import PaddleOCREngine

paddle_ocr = PaddleOCREngine(device="gpu")
parser = EnhancedPDFParser(
    use_image_restoration=True,
    ocr_engine=paddle_ocr  # 与 PaddleOCR 结合以获得最佳结果
)
```

### 4. 正确语言（PyTesseract）

对于 PyTesseract，在初始化引擎时指定文档语言：

```python
from doctra import StructuredPDFParser
from doctra.engines.ocr import PytesseractOCREngine

tesseract_ocr = PytesseractOCREngine(lang="fra")  # 用于法语文档
parser = StructuredPDFParser(ocr_engine=tesseract_ocr)
```

## 多语言文档（PyTesseract）

PyTesseract 支持多种语言。在初始化引擎时配置：

```python
from doctra import StructuredPDFParser
from doctra.engines.ocr import PytesseractOCREngine

tesseract_ocr = PytesseractOCREngine(lang="eng+fra+deu")  # 多种语言
parser = StructuredPDFParser(ocr_engine=tesseract_ocr)
```

## 何时使用每个引擎

### 使用 PyTesseract 当：
- 处理标准文档
- 需要多语言支持
- 想要对 OCR 参数进行细粒度控制
- 仅 CPU 环境

### 使用 PaddleOCR 当：
- 处理复杂或退化的文档
- 需要最大准确性
- 有 GPU 可用于更快处理
- 处理亚洲语言（更好的支持）
- 处理大批量文档

## 另请参阅

- [增强解析器](../parsers/enhanced-parser.md) - 使用恢复改进 OCR
- [核心概念](../core-concepts.md) - 了解管道中的 OCR
- [API 参考](../../api/parsers.md) - OCR 配置选项

