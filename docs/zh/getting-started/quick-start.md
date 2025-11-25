# 快速开始

本指南将帮助您在几分钟内开始使用 Doctra。

## 您的第一个文档解析

让我们解析一个 PDF 文档并提取其内容：

```python
from doctra import StructuredPDFParser

# 初始化解析器
parser = StructuredPDFParser()

# 解析文档
parser.parse("document.pdf")
```

就是这样！Doctra 将：

1. 检测文档布局
2. 使用 OCR 提取文本
3. 保存图形、图表和表格的图像
4. 生成包含所有内容的 Markdown 文件

## 了解输出

解析后，您将找到以下结构：

```
outputs/
└── document/
    ├── full_parse/
    │   ├── result.md          # 包含所有内容的 Markdown
    │   ├── result.html        # HTML 版本
    │   └── images/            # 提取的视觉元素
    │       ├── figures/       # 文档图形
    │       ├── charts/        # 图表和图形
    │       └── tables/        # 表格图像
```

## 基本示例

### 使用自定义输出目录解析

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser()
parser.parse("document.pdf", output_base_dir="my_outputs")
```

### 解析扫描文档

对于扫描或低质量文档，请使用增强解析器：

```python
from doctra import EnhancedPDFParser

parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="appearance"  # 改善整体外观
)

parser.parse("scanned_document.pdf")
```

### 仅提取图表和表格

如果您只需要图表和表格：

```python
from doctra import ChartTablePDFParser

parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=True
)

parser.parse("data_report.pdf")
```

## 使用视觉语言模型

要将图表和表格转换为结构化数据，请添加 VLM 支持：

```python
from doctra import StructuredPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

# 初始化 VLM 引擎
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-api-key-here"
)

# 将 VLM 引擎传递给解析器
parser = StructuredPDFParser(vlm=vlm_engine)

parser.parse("document.pdf")
```

这将生成：

- `tables.xlsx` - 包含提取表格数据的 Excel 文件
- `tables.html` - 用于 Web 查看的 HTML 表格
- `vlm_items.json` - 包含结构化数据的 JSON

!!! tip "VLM 提供商"
    Doctra 支持多个 VLM 提供商：
    
    - `"openai"` - GPT-4 Vision 和 GPT-4o
    - `"gemini"` - Google 的 Gemini 模型
    - `"anthropic"` - 带视觉功能的 Claude
    - `"openrouter"` - 访问多个模型
    - `"qianfan"` - 百度智能云 ERNIE 模型
    - `"ollama"` - 本地模型（不需要 API 密钥）

## 文档恢复

在解析前增强文档质量：

```python
from doctra import DocResEngine

# 初始化恢复引擎
docres = DocResEngine(device="cuda")  # 使用 GPU 以加快速度

# 恢复单个图像
restored_img, metadata = docres.restore_image(
    image="blurry_doc.jpg",
    task="deblurring"
)

# 或增强整个 PDF
docres.restore_pdf(
    pdf_path="low_quality.pdf",
    output_path="enhanced.pdf",
    task="appearance"
)
```

可用的恢复任务：

| 任务 | 描述 |
|------|------|
| `appearance` | 一般外观增强 |
| `dewarping` | 校正透视失真 |
| `deshadowing` | 去除阴影 |
| `deblurring` | 减少模糊 |
| `binarization` | 转换为黑白 |
| `end2end` | 完整的恢复流程 |

## 使用 Web UI

启动图形界面以便轻松处理文档：

```python
from doctra import launch_ui

# 启动 Web 界面
launch_ui()
```

或从命令行：

```bash
python -m doctra.ui.app
```

然后在浏览器中打开显示的 URL（通常是 `http://127.0.0.1:7860`）。

## 命令行界面

Doctra 提供了一个强大的 CLI：

```bash
# 解析文档
doctra parse document.pdf

# 增强解析
doctra enhance document.pdf --restoration-task appearance

# 提取图表和表格
doctra extract both document.pdf --use-vlm

# 可视化布局
doctra visualize document.pdf
```

有关所有可用命令，请参阅 [CLI 参考](../interfaces/cli.md)。

## 布局可视化

可视化 Doctra 如何检测文档元素：

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

# 显示布局检测结果
parser.display_pages_with_boxes(
    pdf_path="document.pdf",
    num_pages=3,  # 前 3 页
    save_path="layout_viz.png"
)
```

这将创建一个可视化表示，显示：

- 检测到的文本区域（蓝色框）
- 表格（红色框）
- 图表（绿色框）
- 图形（橙色框）
- 每个元素的置信度分数

## 配置选项

### 解析器配置

```python
from doctra import StructuredPDFParser
from doctra.engines.ocr import PytesseractOCREngine

# 初始化 OCR 引擎
tesseract_ocr = PytesseractOCREngine(lang="eng", psm=6, oem=3)

parser = StructuredPDFParser(
    # 布局检测
    layout_model_name="PP-DocLayout_plus-L",  # 模型选择
    dpi=200,  # 图像分辨率
    min_score=0.5,  # 置信度阈值
    
    # OCR 引擎
    ocr_engine=tesseract_ocr,
    
    # 输出
    box_separator="\n"  # 元素之间的分隔符
)
```

### 增强解析器配置

```python
from doctra import EnhancedPDFParser

# 初始化 VLM 引擎（可选）
from doctra.engines.vlm.service import VLMStructuredExtractor

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-key"
)

parser = EnhancedPDFParser(
    # 图像恢复
    use_image_restoration=True,
    restoration_task="dewarping",
    restoration_device="cuda",  # 或 "cpu"
    restoration_dpi=300,
    
    # VLM 引擎（传递初始化的引擎实例）
    vlm=vlm_engine,
    
    # 所有 StructuredPDFParser 选项也可用
)
```

## 常见模式

### 批量处理

```python
import os
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

# 处理目录中的所有 PDF
pdf_dir = "documents"
for filename in os.listdir(pdf_dir):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_dir, filename)
        print(f"处理 {filename}...")
        parser.parse(pdf_path)
```

### 错误处理

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

try:
    parser.parse("document.pdf")
except FileNotFoundError:
    print("未找到文档！")
except Exception as e:
    print(f"解析文档时出错：{e}")
```

### 进度跟踪

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

# 进度条会自动显示
parser.parse("large_document.pdf")
```

## 下一步

现在您已经学习了基础知识：

1. **深入了解**：阅读[用户指南](../user-guide/core-concepts.md)了解详细说明
2. **探索解析器**：了解每个解析器的功能
3. **高级示例**：查看[高级示例](../examples/advanced-examples.md)
4. **API 参考**：浏览 [API 文档](../api/parsers.md)

## 获取帮助

- :material-book-open: 阅读完整的[文档](../index.md)
- :material-github: 查看 [GitHub issues](https://github.com/AdemBoukhris457/Doctra/issues)
- :material-message-question: 在讨论中提问

## 常见问题

### "找不到 Poppler" 错误

安装 Poppler（请参阅[安装](installation.md#system-dependencies)）。

### OCR 准确性低

尝试使用带图像恢复的增强解析器：

```python
from doctra import EnhancedPDFParser

parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="appearance"
)
```

### 处理速度慢

使用 GPU 加速：

```python
parser = EnhancedPDFParser(
    restoration_device="cuda"  # 使用 GPU
)
```

或降低 DPI：

```python
parser = StructuredPDFParser(
    dpi=150  # 较低分辨率
)
```

