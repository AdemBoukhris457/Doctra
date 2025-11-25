# 命令行界面

Doctra 提供了一个强大的 CLI，用于文档处理自动化。

## 安装

CLI 随 Doctra 自动安装：

```bash
pip install doctra
```

验证安装：

```bash
doctra --version
```

## 基本用法

```bash
doctra [COMMAND] [OPTIONS] [ARGUMENTS]
```

## 命令

### parse

使用完整处理解析 PDF 文档。

```bash
doctra parse <pdf_file> [OPTIONS]
```

**选项**：

- `--output-dir PATH`：输出目录（默认：`outputs`）
- `--dpi INTEGER`：图像分辨率（默认：200）
- `--min-score FLOAT`：最小置信度分数（默认：0.0）
- `--ocr-lang TEXT`：OCR 语言代码（默认：`eng`）
- `--use-vlm`：启用 VLM 处理
- `--vlm-provider TEXT`：VLM 提供商（`openai`、`gemini`、`anthropic`、`openrouter`）
- `--vlm-api-key TEXT`：VLM API 密钥
- `--vlm-model TEXT`：特定的 VLM 模型

**示例**：

```bash
# 基本解析
doctra parse document.pdf

# 使用自定义设置
doctra parse document.pdf --dpi 300 --output-dir my_outputs

# 使用 VLM
doctra parse document.pdf --use-vlm --vlm-provider openai --vlm-api-key sk-xxx
```

### parse-docx

解析 Microsoft Word 文档（.docx 文件）。

```bash
doctra parse-docx <docx_file> [OPTIONS]
```

**选项**：

- `--output-dir PATH`：输出目录（默认：`outputs`）
- `--use-vlm`：启用 VLM 处理
- `--vlm-provider TEXT`：VLM 提供商（`openai`、`gemini`、`anthropic`、`openrouter`）
- `--vlm-api-key TEXT`：VLM API 密钥
- `--vlm-model TEXT`：特定的 VLM 模型
- `--extract-images`：提取嵌入的图像（默认：True）
- `--preserve-formatting`：保留文本格式（默认：True）
- `--table-detection`：检测并提取表格（默认：True）
- `--export-excel`：将表格导出到 Excel 文件（默认：True）
- `--verbose`：启用详细输出

**示例**：

```bash
# 基本 DOCX 解析
doctra parse-docx document.docx

# 使用 VLM 增强
doctra parse-docx document.docx --use-vlm --vlm-provider openai --vlm-api-key sk-xxx

# 自定义选项
doctra parse-docx document.docx \
  --extract-images \
  --preserve-formatting \
  --table-detection \
  --export-excel \
  --output-dir my_outputs
```

### enhance

对低质量文档进行图像恢复解析。

```bash
doctra enhance <pdf_file> [OPTIONS]
```

**选项**：

- 所有 `parse` 选项，加上：
- `--restoration-task TEXT`：恢复任务（默认：`appearance`）
    - 选择：`appearance`、`dewarping`、`deshadowing`、`deblurring`、`binarization`、`end2end`
- `--restoration-device TEXT`：设备（`cuda`、`cpu` 或 auto）
- `--restoration-dpi INTEGER`：恢复的 DPI（默认：200）

**示例**：

```bash
# 基本增强
doctra enhance scanned.pdf

# 使用 GPU 去扭曲
doctra enhance scanned.pdf --restoration-task dewarping --restoration-device cuda

# 使用 VLM 的完整增强
doctra enhance scanned.pdf \
  --restoration-task appearance \
  --restoration-device cuda \
  --use-vlm \
  --vlm-provider openai \
  --vlm-api-key sk-xxx
```

### extract

仅从文档中提取图表和/或表格。

```bash
doctra extract <type> <pdf_file> [OPTIONS]
```

**类型**：

- `charts`：仅提取图表
- `tables`：仅提取表格
- `both`：提取图表和表格

**选项**：

- `--output-dir PATH`：输出目录（默认：`outputs`）
- `--dpi INTEGER`：图像分辨率（默认：200）
- `--use-vlm`：启用 VLM 以获取结构化数据
- `--vlm-provider TEXT`：VLM 提供商
- `--vlm-api-key TEXT`：VLM API 密钥
- `--vlm-model TEXT`：特定的 VLM 模型

**示例**：

```bash
# 仅提取图表
doctra extract charts report.pdf

# 使用 VLM 提取表格
doctra extract tables report.pdf --use-vlm --vlm-provider gemini --vlm-api-key xxx

# 提取两者
doctra extract both report.pdf --output-dir data_extracts
```

### visualize

可视化布局检测结果。

```bash
doctra visualize <pdf_file> [OPTIONS]
```

**选项**：

- `--num-pages INTEGER`：要可视化的页数（默认：3）
- `--cols INTEGER`：网格中的列数（默认：2）
- `--page-width INTEGER`：每页的宽度（默认：800）
- `--spacing INTEGER`：页面之间的间距（默认：40）
- `--output PATH`：保存到文件而不是显示
- `--dpi INTEGER`：图像分辨率（默认：200）

**示例**：

```bash
# 显示前 3 页
doctra visualize document.pdf

# 保存 6 页的可视化
doctra visualize document.pdf --num-pages 6 --output layout.png

# 自定义网格布局
doctra visualize document.pdf --num-pages 9 --cols 3 --page-width 600
```

### analyze

快速文档分析，显示结构。

```bash
doctra analyze <pdf_file> [OPTIONS]
```

**选项**：

- `--dpi INTEGER`：图像分辨率（默认：200）

**示例**：

```bash
doctra analyze document.pdf
```

输出显示：

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

显示系统和配置信息。

```bash
doctra info
```

显示：

- Doctra 版本
- Python 版本
- 已安装的依赖项
- GPU 可用性
- 系统信息

**示例输出**：

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

## 批量处理

### 处理多个文件

```bash
# 使用 shell 通配符
doctra parse *.pdf --output-dir batch_results

# 使用 find (Linux/Mac)
find ./documents -name "*.pdf" -exec doctra parse {} \;

# 使用 PowerShell (Windows)
Get-ChildItem *.pdf | ForEach-Object { doctra parse $_.FullName }
```

### 处理目录

```bash
# 解析目录中的所有 PDF
for pdf in directory/*.pdf; do
    doctra parse "$pdf" --output-dir results/
done
```

## 环境变量

使用环境变量设置默认值：

```bash
# VLM 配置
export DOCTRA_VLM_PROVIDER=openai
export DOCTRA_VLM_API_KEY=sk-xxx
export DOCTRA_VLM_MODEL=gpt-4o

# 处理设置
export DOCTRA_DPI=200
export DOCTRA_OCR_LANG=eng
export DOCTRA_DEVICE=cuda

# 然后无需标志即可使用
doctra parse document.pdf --use-vlm
```

## 配置文件

在项目目录中创建 `.doctra.yml`：

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

然后无需选项即可运行命令：

```bash
doctra parse document.pdf
```

## 输出结构

### 标准解析

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

### 增强解析

```
outputs/
└── document/
    └── enhanced_parse/
        ├── result.md
        ├── result.html
        ├── document_enhanced.pdf  # 恢复的 PDF
        ├── enhanced_pages/  # 恢复的页面图像
        └── images/
```

### 提取

```
outputs/
└── document/
    └── structured_parsing/
        ├── charts/  # 图表图像
        ├── tables/  # 表格图像
        ├── parsed_tables_charts.xlsx  # 如果启用 VLM
        ├── parsed_tables_charts.html  # 如果启用 VLM
        └── vlm_items.json  # 如果启用 VLM
```

### DOCX 解析

```
outputs/
└── document/
    ├── document.md
    ├── document.html
    ├── tables.xlsx  # 带目录
    └── images/
        ├── image1.png
        ├── image2.jpg
        └── ...
```

## 示例

### 示例 1：基本文档处理

```bash
# 解析财务报告
doctra parse financial_report.pdf

# 输出：outputs/financial_report/full_parse/
```

### 示例 2：使用 VLM 的增强处理

```bash
# 使用增强和 VLM 处理扫描文档
doctra enhance scanned_document.pdf \
  --restoration-task appearance \
  --restoration-device cuda \
  --use-vlm \
  --vlm-provider openai \
  --vlm-api-key $OPENAI_API_KEY \
  --output-dir enhanced_results
```

### 示例 3：DOCX 文档处理

```bash
# 基本 DOCX 解析
doctra parse-docx report.docx

# 使用 VLM 增强以获取结构化数据
doctra parse-docx financial_report.docx \
  --use-vlm \
  --vlm-provider openai \
  --vlm-api-key $OPENAI_API_KEY \
  --export-excel

# 结果：outputs/financial_report/document.md, document.html, tables.xlsx
```

### 示例 4：提取数据进行分析

```bash
# 使用 VLM 提取所有表格以获取结构化数据
doctra extract tables data_report.pdf \
  --use-vlm \
  --vlm-provider gemini \
  --vlm-api-key $GEMINI_API_KEY

# 结果：outputs/data_report/structured_parsing/parsed_tables_charts.xlsx
```

### 示例 5：批量处理管道

```bash
#!/bin/bash
# process_documents.sh

INPUT_DIR="./input_pdfs"
OUTPUT_DIR="./processed"

for pdf in "$INPUT_DIR"/*.pdf; do
    echo "Processing: $pdf"
    
    # 首先增强文档
    doctra enhance "$pdf" \
      --restoration-task appearance \
      --restoration-device cuda \
      --output-dir "$OUTPUT_DIR"
    
    echo "Completed: $pdf"
done

echo "All documents processed!"
```

### 示例 6：使用可视化的质量检查

```bash
# 在完整处理前可视化布局检测
doctra visualize document.pdf --num-pages 5 --output viz_check.png

# 查看 viz_check.png 以确保良好的检测

# 然后继续完整处理
doctra parse document.pdf --use-vlm
```

## 故障排除

### 命令未找到

**问题**：`doctra: command not found`

**解决方案**：

```bash
# 确保已安装 Doctra
pip install doctra

# 或使用模块语法
python -m doctra.cli.main parse document.pdf
```

### API 密钥错误

**问题**：VLM API 密钥未被识别

**解决方案**：

```bash
# 设置环境变量
export OPENAI_API_KEY=sk-xxx

# 或直接传递
doctra parse document.pdf --use-vlm --vlm-api-key sk-xxx
```

### Poppler 错误

**问题**：`pdftoppm not found`

**解决方案**：安装 Poppler（请参阅[安装指南](../getting-started/installation.md#system-dependencies)）

### 内存错误

**问题**：处理期间内存不足

**解决方案**：

```bash
# 降低 DPI
doctra parse large.pdf --dpi 150

# 或单独处理页面
doctra parse large.pdf --max-pages 10
```

## 高级用法

### 自定义脚本

将 CLI 与 shell 脚本结合：

```bash
#!/bin/bash
# 智能处理脚本

PDF=$1

# 检查文件大小
SIZE=$(du -k "$PDF" | cut -f1)

if [ $SIZE -gt 10000 ]; then
    echo "Large file, using lower DPI..."
    doctra parse "$PDF" --dpi 150
else
    echo "Standard processing..."
    doctra parse "$PDF" --dpi 200 --use-vlm
fi
```

### 与其他工具集成

```bash
# OCR + 搜索管道
doctra parse document.pdf
grep "keyword" outputs/document/full_parse/result.md

# 提取数据并分析
doctra extract tables report.pdf --use-vlm
python analyze_tables.py outputs/report/structured_parsing/parsed_tables_charts.xlsx
```

## 另请参阅

- [Python API](../api/parsers.md) - 程序化用法
- [Web UI](web-ui.md) - 图形界面
- [示例](../examples/basic-usage.md) - 使用示例

