# 更新日志

Doctra 的所有重要更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
本项目遵循 [语义化版本](https://semver.org/spec/v2.0.0.html)。

## [0.4.3] - 2024-XX-XX

### 当前版本

这是 Doctra 的当前稳定版本。

### 功能

- **多种 PDF 解析器**
    - `StructuredPDFParser`：完整的文档处理
    - `EnhancedPDFParser`：带图像恢复的解析
    - `ChartTablePDFParser`：专门的图表/表格提取

- **图像恢复**
    - DocRes 集成用于文档增强
    - 6 种恢复任务：appearance、dewarping、deshadowing、deblurring、binarization、end2end
    - GPU 加速支持

- **VLM 集成**
    - 支持 OpenAI、Gemini、Anthropic、OpenRouter、Qianfan 和 Ollama
    - 从图表和表格中提取结构化数据
    - 自动转换为 Excel/HTML/JSON

- **输出格式**
    - 带嵌入图像的 Markdown
    - 用于 Web 查看的 HTML
    - 用于数据分析的 Excel
    - 用于程序化访问的 JSON
    - 高质量图像提取

- **用户界面**
    - 基于 Gradio 的 Web UI
    - 全面的 CLI
    - 完整的 Python API

- **可视化**
    - 布局检测可视化
    - 边界框叠加
    - 置信度分数
    - 多页面网格显示

### 依赖项

- Python 3.8+
- PaddlePaddle >= 2.4.0
- PaddleOCR >= 2.6.0
- Pillow >= 8.0.0
- OpenCV >= 4.5.0
- Pandas >= 1.3.0
- Tesseract >= 0.1.3
- PyTesseract >= 0.3.10
- pdf2image >= 1.16.0
- Anthropic >= 0.40.0
- Outlines >= 0.0.34

## [未发布]

### 计划功能

- [ ] 支持其他文档格式（DOCX、PPTX）
- [ ] 改进表格结构识别
- [ ] 批量处理 API
- [ ] Docker 容器
- [ ] 云部署指南
- [ ] 其他 VLM 提供商
- [ ] 性能优化
- [ ] 多语言文档

## 版本历史

### [0.4.3] - 当前

具有完整功能集的当前稳定版本。

### [0.4.0] - 之前

具有核心功能的初始公开版本。

## 升级指南

### 从 0.4.0 升级到 0.4.3

没有破坏性更改。只需升级：

```bash
pip install --upgrade doctra
```

## 贡献

有关以下信息，请参阅我们的[贡献指南](contributing/development.md)：

- 报告错误
- 请求功能
- 提交拉取请求
- 开发设置

## 支持

- **文档**：[https://ademboukhris457.github.io/Doctra/](https://ademboukhris457.github.io/Doctra/)
- **GitHub Issues**：[https://github.com/AdemBoukhris457/Doctra/issues](https://github.com/AdemBoukhris457/Doctra/issues)
- **PyPI**：[https://pypi.org/project/doctra/](https://pypi.org/project/doctra/)

