# DOCX 解析器

`StructuredDOCXParser` 是一个全面的 Microsoft Word 文档（.docx 文件）解析器，可提取文本、表格、图像和结构化内容，同时保留文档格式和顺序。

## 概述

DOCX 解析器提供：

- **完整的 DOCX 支持**：从 Word 文档中提取文本、表格、图像和格式
- **文档顺序保留**：保持元素的原始顺序（段落、表格、图像）
- **VLM 集成**：可选的视觉语言模型支持，用于图像分析和表格提取
- **多种输出格式**：生成 Markdown、HTML 和 Excel 文件
- **Excel 导出**：创建包含目录和可点击超链接的结构化 Excel 文件
- **格式保留**：在输出中保持文本格式（粗体、斜体等）
- **进度跟踪**：VLM 处理的实时进度条

## 基本用法

```python
from doctra.parsers.structured_docx_parser import StructuredDOCXParser

# 基本 DOCX 解析
parser = StructuredDOCXParser(
    extract_images=True,
    preserve_formatting=True,
    table_detection=True,
    export_excel=True
)

# 解析 DOCX 文档
parser.parse("document.docx")
```

## 高级配置

### 使用 VLM 增强

```python
from doctra import StructuredDOCXParser
from doctra.engines.vlm.service import VLMStructuredExtractor

# 初始化 VLM 引擎
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",  # 或 "gemini", "anthropic", "openrouter", "qianfan", "ollama"
    vlm_model="gpt-4-vision",  # 可选，如果为 None 则使用默认值
    api_key="your_api_key"
)

parser = StructuredDOCXParser(
    # VLM 引擎（传递初始化的引擎实例）
    vlm=vlm_engine,
    
    # 处理选项
    extract_images=True,
    preserve_formatting=True,
    table_detection=True,
    export_excel=True
)

# 使用 VLM 增强解析
parser.parse("document.docx")
```

### 自定义处理选项

```python
parser = StructuredDOCXParser(
    # 禁用图像提取以加快处理速度
    extract_images=False,
    
    # 禁用格式保留以获取纯文本
    preserve_formatting=False,
    
    # 如果不需要则禁用表格检测
    table_detection=False,
    
    # 禁用 Excel 导出
    export_excel=False
)
```

## 输出结构

解析 DOCX 文档时，解析器会创建：

```
outputs/document_name/
├── document.md          # 包含所有内容的 Markdown 版本
├── document.html        # 带样式的 HTML 版本
├── tables.xlsx         # 包含提取表格的 Excel 文件
│   ├── Table of Contents  # 带超链接的摘要表
│   ├── Table 1         # 单个表格工作表
│   ├── Table 2
│   └── ...
└── images/             # 提取的图像
    ├── image1.png
    ├── image2.jpg
    └── ...
```

## VLM 集成功能

启用 VLM 时，解析器会：

- **分析图像**：使用 AI 从图像中提取结构化数据
- **创建表格**：将图表图像转换为结构化表格数据
- **增强 Excel 输出**：在 Excel 文件中包含 VLM 提取的表格
- **智能内容显示**：在 Markdown/HTML 中显示提取的表格而不是图像
- **进度跟踪**：根据处理的图像数量显示进度

### VLM 处理流程

1. **图像检测**：扫描文档中的嵌入图像
2. **VLM 分析**：使用选定的 VLM 模型处理每个图像
3. **结构化提取**：将视觉内容转换为结构化数据
4. **Excel 集成**：将 VLM 提取的表格添加到 Excel 输出
5. **内容替换**：在 Markdown/HTML 中用提取的表格替换图像引用

## Excel 输出功能

生成的 Excel 文件包括：

- **目录**：包含所有提取表格的摘要表
- **可点击超链接**：在表格工作表之间导航
- **一致的样式**：专业的格式，带颜色和字体
- **VLM 集成**：包括原始和 VLM 提取的表格
- **工作表命名**：使用实际表格标题作为工作表名称

## CLI 用法

```bash
# 基本 DOCX 解析
doctra parse-docx document.docx

# 使用 VLM 增强
doctra parse-docx document.docx --use-vlm --vlm-provider openai --vlm-api-key your_key

# 自定义选项
doctra parse-docx document.docx \
  --extract-images \
  --preserve-formatting \
  --table-detection \
  --export-excel
```

## Web UI 用法

DOCX 解析器在 Gradio Web 界面中可用：

1. **上传 DOCX 文件**：拖放您的 Word 文档
2. **配置 VLM**：启用 VLM 并设置您的 API 密钥
3. **处理选项**：选择提取设置
4. **解析文档**：点击 "Parse DOCX" 进行处理
5. **查看结果**：预览内容并下载输出

## 参数参考

### VLM 设置

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

vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    vlm_model="gpt-4-vision",  # 可选
    api_key="your-api-key"
)

parser = StructuredDOCXParser(vlm=vlm_engine)
```

### 处理选项

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `extract_images` | bool | True | 从 DOCX 中提取嵌入的图像 |
| `preserve_formatting` | bool | True | 在输出中保留文本格式 |
| `table_detection` | bool | True | 检测并提取表格 |
| `export_excel` | bool | True | 将表格导出到 Excel 文件 |

## 错误处理

解析器处理常见错误：

- **文件未找到**：无效的 DOCX 文件路径
- **权限错误**：只读文件或锁定的文档
- **VLM API 错误**：无效的 API 密钥或速率限制
- **处理错误**：损坏的文档或不支持的格式

```python
try:
    parser.parse("document.docx")
except FileNotFoundError:
    print("未找到 DOCX 文件！")
except Exception as e:
    print(f"处理错误：{e}")
```

## 最佳实践

### 性能优化

- **禁用未使用的功能**：如果不需要，关闭图像提取或 Excel 导出
- **VLM 使用**：仅在需要结构化数据提取时使用 VLM
- **大型文档**：考虑将大型文档分成较小的块进行处理

### 输出质量

- **格式保留**：保持启用以获得更好的输出质量
- **表格检测**：对结构化数据提取至关重要
- **VLM 增强**：改善从图像中提取表格

### 错误预防

- **文件验证**：确保 DOCX 文件未损坏
- **API 密钥**：在处理前设置 VLM API 密钥
- **权限**：确保对输出目录的写入访问权限

## 示例

### 示例 1：基本文档处理

```python
from doctra.parsers.structured_docx_parser import StructuredDOCXParser

# 初始化解析器
parser = StructuredDOCXParser()

# 处理文档
parser.parse("report.docx")

# 输出：outputs/report/document.md, document.html, tables.xlsx
```

### 示例 2：VLM 增强处理

```python
from doctra import StructuredDOCXParser
from doctra.engines.vlm.service import VLMStructuredExtractor

# 初始化 VLM 引擎
vlm_engine = VLMStructuredExtractor(
    vlm_provider="openai",
    api_key="your_api_key"
)

parser = StructuredDOCXParser(vlm=vlm_engine)

# 使用 AI 增强处理
parser.parse("financial_report.docx")

# 输出：带 VLM 提取表格的增强 Excel
```

### 示例 3：自定义配置

```python
parser = StructuredDOCXParser(
    extract_images=True,
    preserve_formatting=False,  # 纯文本输出
    table_detection=True,
    export_excel=True
)

# 使用自定义设置处理
parser.parse("data_document.docx")
```

## 故障排除

### 常见问题

1. **"python-docx not installed"**
   - 解决方案：`pip install python-docx`

2. **"No tables extracted"**
   - 检查 `table_detection=True`
   - 验证文档包含表格

3. **"VLM API error"**
   - 验证 API 密钥是否正确
   - 检查提供商和模型兼容性

4. **"Images not extracted"**
   - 检查 `extract_images=True`
   - 验证文档包含嵌入图像

### 性能提示

- 仅在需要时使用 VLM（会增加处理时间）
- 禁用未使用的功能以加快处理速度
- 将大型文档分成较小的批次处理
- 确保有足够的磁盘空间用于输出

## 相关文档

- [API 参考](../../api/parsers.md#structureddocxparser)
- [VLM 集成](../engines/vlm-integration.md)
- [导出格式](../outputs/export-formats.md)
- [Web UI 指南](../../interfaces/web-ui.md)

