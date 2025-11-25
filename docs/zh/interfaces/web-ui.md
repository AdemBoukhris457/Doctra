# Web UI

使用 Doctra 基于 Gradio 的 Web 界面指南。

## 概述

Doctra 提供了一个用户友好的 Web 界面，无需编写代码即可处理文档。

## 启动 UI

### Python

```python
from doctra import launch_ui

# 启动 Web 界面
launch_ui()
```

### 命令行

```bash
python -m doctra.ui.app
```

### 模块脚本

```bash
python gradio_app.py
```

UI 在以下地址打开：`http://127.0.0.1:7860`

## 界面标签页

### 1. 完整解析

完整的文档处理：

- 上传 PDF
- 配置设置
- 查看结果
- 下载输出

### 2. DOCX 解析器

Microsoft Word 文档处理：

- 上传 DOCX 文件
- 配置 VLM 设置
- 选择处理选项
- 查看提取的内容
- 下载结构化输出

### 3. 表格和图表

专业提取：

- 提取图表和/或表格
- 启用 VLM 处理
- 配置 API 密钥
- 下载结构化数据

### 4. DocRes

图像恢复：

- 上传图像或 PDF
- 选择恢复任务
- 比较前后效果
- 下载增强的文件

### 5. 增强解析器

结合恢复和解析：

- 上传 PDF
- 配置恢复
- 启用 VLM
- 获得全面的结果

## 功能

- **拖放**：轻松上传文件
- **实时进度**：查看处理状态
- **预览结果**：在浏览器中查看输出
- **下载 ZIP**：获取打包的所有结果
- **配置**：调整所有设置
- **API 密钥管理**：安全的密钥输入

## 配置选项

每个标签页提供以下设置：

- DPI 分辨率
- 语言选择
- VLM 提供商和 API 密钥
- 恢复任务
- 输出首选项

## 分享 UI

使用公共 URL 启动：

```python
from doctra import build_demo

demo = build_demo()
demo.launch(share=True)
```

这将生成一个临时的公共 URL 用于分享。

## 用例

- **非技术用户**：无需编码
- **快速处理**：快速的一次性文档处理
- **实验**：尝试不同的设置
- **演示**：展示 Doctra 功能
- **原型设计**：在集成前进行测试

## 另请参阅

- [CLI 参考](cli.md) - 命令行界面
- [API 参考](../api/parsers.md) - Python API
- [示例](../examples/basic-usage.md) - 使用示例

