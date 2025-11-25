# 基本用法示例

常见 Doctra 用例的实用示例。

## 示例 1：解析简单 PDF

```python
from doctra import StructuredPDFParser

# 初始化解析器
parser = StructuredPDFParser()

# 解析文档
parser.parse("document.pdf")

# 输出保存到：outputs/document/full_parse/
```

## 示例 2：使用自定义设置解析

```python
from doctra import StructuredPDFParser
from doctra.engines.ocr import PytesseractOCREngine

# 初始化 OCR 引擎
tesseract_ocr = PytesseractOCREngine(lang="eng", psm=4, oem=3)

parser = StructuredPDFParser(
    dpi=250,  # 更高质量
    min_score=0.7,  # 更自信的检测
    ocr_engine=tesseract_ocr
)

parser.parse("document.pdf", output_base_dir="my_results")
```

## 示例 3：扫描文档的增强解析

```python
from doctra import EnhancedPDFParser

parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="appearance",
    restoration_device="cuda"  # 使用 GPU
)

parser.parse("scanned_document.pdf")
```

## 示例 4：使用 VLM 提取结构化数据

```python
from doctra import StructuredPDFParser
from doctra.engines.vlm.service import VLMStructuredExtractor

# 初始化 VLM 引擎
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your-api-key-here"
)

parser = StructuredPDFParser(vlm=vlm_engine)
parser.parse("data_report.pdf")

# 输出包括：
# - tables.xlsx 包含提取的数据
# - tables.html 包含格式化的表格
# - vlm_items.json 包含结构化数据
```

## 示例 5：仅提取图表

```python
from doctra import ChartTablePDFParser

parser = ChartTablePDFParser(
    extract_charts=True,
    extract_tables=False
)

parser.parse("presentation.pdf")
```

## 示例 5b：PaddleOCRVL 端到端解析

```python
from doctra import PaddleOCRVLPDFParser

# 初始化启用所有功能的解析器
parser = PaddleOCRVLPDFParser(
    use_image_restoration=True,      # 启用 DocRes 恢复
    restoration_task="appearance",    # 使用外观增强
    use_chart_recognition=True,       # 启用图表识别
    merge_split_tables=True,          # 启用分割表格合并
    device="gpu"                      # 使用 GPU 进行处理
)

# 解析文档 - 自动处理所有内容类型
parser.parse("financial_report.pdf")

# 输出在：outputs/financial_report/paddleocr_vl_parse/
# - result.md：所有内容的 Markdown
# - result.html：格式化的 HTML 输出
# - tables.xlsx：Excel 格式的所有表格和图表
# - tables.html：结构化的表格和图表
```

## 示例 6：可视化布局检测

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

# 显示布局检测
parser.display_pages_with_boxes(
    pdf_path="document.pdf",
    num_pages=3,
    save_path="layout_visualization.png"
)
```

## 示例 7：独立图像恢复

```python
from doctra import DocResEngine

# 初始化恢复引擎
engine = DocResEngine(device="cuda")

# 恢复单个图像
restored_img, metadata = engine.restore_image(
    image="blurry_document.jpg",
    task="deblurring"
)

# 保存结果
restored_img.save("restored.jpg")
print(f"处理时间：{metadata['processing_time']:.2f}秒")
```

## 示例 8：批量处理

```python
import os
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

# 处理目录中的所有 PDF
pdf_directory = "documents"
for filename in os.listdir(pdf_directory):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_directory, filename)
        print(f"处理 {filename}...")
        parser.parse(pdf_path)
        print(f"完成 {filename}")
```

## 示例 9：错误处理

```python
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

try:
    parser.parse("document.pdf")
    print("处理成功！")
except FileNotFoundError:
    print("错误：未找到 PDF 文件")
except Exception as e:
    print(f"处理期间出错：{e}")
```

## 示例 10：使用 Web UI

```python
from doctra import launch_ui

# 启动 Web 界面
launch_ui()

# 在 http://127.0.0.1:7860 打开浏览器
```

## 下一步

- [高级示例](advanced-examples.md) - 复杂用例
- [集成示例](integration.md) - 与其他工具集成
- [API 参考](../api/parsers.md) - 详细的 API 文档

