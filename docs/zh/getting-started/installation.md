# 安装

本指南将帮助您在系统上安装 Doctra 及其依赖项。

## 要求

- Python 3.8 或更高版本
- pip 包管理器
- Poppler（用于 PDF 处理）
- Tesseract OCR（由依赖项自动处理）

## 安装 Doctra

### 从 PyPI 安装（推荐）

使用 pip 从 PyPI 安装 Doctra 是最简单的方法：

```bash
pip install doctra
```

这将自动安装 Doctra 和所有 Python 依赖项。

### 从源码安装

要从源码安装最新的开发版本：

```bash
git clone https://github.com/AdemBoukhris457/Doctra.git
cd Doctra
pip install -e .
```

`-e` 标志以可编辑模式安装，这对开发很有用。

## 系统依赖 {#system-dependencies}

Doctra 需要 **Poppler** 来处理 PDF。请根据您的操作系统按照以下说明操作：

### :simple-ubuntu: Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install poppler-utils
```

### :simple-apple: macOS

使用 Homebrew：

```bash
brew install poppler
```

如果您没有 Homebrew，请从 [brew.sh](https://brew.sh) 安装。

### :simple-windows: Windows

#### 选项 1：使用 Conda

```bash
conda install -c conda-forge poppler
```

#### 选项 2：手动安装

1. 从[此链接](https://poppler.freedesktop.org/)下载 Windows 版 Poppler
2. 解压归档文件
3. 将 `bin` 目录添加到系统 PATH

### :simple-googlecolab: Google Colab

```bash
!apt-get install poppler-utils
```

## 可选依赖

### VLM 提供商

要使用视觉语言模型进行结构化数据提取，请安装相应的提供商：

#### OpenAI

```bash
pip install doctra[openai]
```

#### Google Gemini

```bash
pip install doctra[gemini]
```

#### 所有 VLM 提供商

```bash
pip install doctra[openai,gemini]
```

### 开发依赖

要参与 Doctra 的开发：

```bash
pip install doctra[dev]
```

这将安装测试、代码检查和格式化工具。

## 验证安装

安装后，验证 Doctra 是否正确安装：

```python
import doctra
print(doctra.__version__)
```

您应该看到版本号（例如 `0.4.3`）。

### 检查系统依赖

要检查 Poppler 是否正确安装：

```bash
pdftoppm -v
```

您应该看到 Poppler 版本信息。

## GPU 支持

### CUDA 加速处理

Doctra 可以利用 GPU 加速进行图像恢复任务。要启用 GPU 支持：

1. 安装支持 CUDA 的 PyTorch：

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

2. 验证 CUDA 是否可用：

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
```

### PaddlePaddle GPU 支持

用于 GPU 加速的布局检测和 PaddleOCRVL：

```bash
# 安装 PaddlePaddle GPU (CUDA 12.6)
pip install paddlepaddle-gpu==3.2.1 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/

# 安装支持 doc-parser 的 PaddleOCR
pip install -U "paddleocr[doc-parser]"

# 安装平台特定的 safetensors（PaddleOCRVL 必需）
# 对于 Linux：
pip install https://paddle-whl.bj.bcebos.com/nightly/cu126/safetensors/safetensors-0.6.2.dev0-cp38-abi3-linux_x86_64.whl

# 对于 Windows：
pip install https://xly-devops.cdn.bcebos.com/safetensors-nightly/safetensors-0.6.2.dev0-cp38-abi3-win_amd64.whl
```

!!! note "GPU 要求"
    GPU 支持需要：
    
    - 具有 CUDA 计算能力 3.5+ 的 NVIDIA GPU
    - CUDA 12.6（适用于 PaddlePaddle 3.2.1）或查看 [PaddlePaddle 安装指南](https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/zh/develop/install/pip/linux-pip.html) 了解其他 CUDA 版本
    - cuDNN 8.6 或更高版本

!!! tip "自动安装"
    从 PyPI 或源码安装 Doctra 时，PaddleOCR 依赖项会自动安装，并针对 safetensors 进行平台特定处理。安装将自动为您的平台（Linux 或 Windows）选择正确的 safetensors wheel。

## 故障排除

### ImportError: No module named 'doctra'

**解决方案**：确保 Doctra 已安装在您的活动 Python 环境中：

```bash
pip list | grep doctra
```

如果未列出，请使用 `pip install doctra` 重新安装。

### 找不到 Poppler

**症状**：错误消息提到 "pdftoppm" 或 "Poppler"

**解决方案**：

1. 验证 Poppler 安装：`pdftoppm -v`
2. 如果未安装，请按照[系统依赖](#system-dependencies)部分操作
3. 在 Windows 上，确保 Poppler 的 `bin` 目录在您的 PATH 中

### CUDA 内存不足

**解决方案**：使用 CPU 处理或降低 DPI 设置：

```python
parser = StructuredPDFParser(
    dpi=150,  # 从默认的 200 降低
    restoration_device="cpu"  # 强制使用 CPU
)
```

### PaddleOCR 模型下载失败

**解决方案**：手动下载模型或检查网络连接：

```python
from doctra.parsers import StructuredPDFParser

# 这将触发模型下载
parser = StructuredPDFParser()
```

模型在首次使用时下载到 `~/.paddleocr/`。

## 下一步

现在您已经安装了 Doctra，请查看：

- [快速开始](quick-start.md) - 您的第一个 Doctra 程序
- [系统要求](system-requirements.md) - 详细的硬件要求
- [用户指南](../user-guide/core-concepts.md) - 了解核心概念

## 获取帮助

如果您在安装过程中遇到问题：

1. 查看 [GitHub Issues](https://github.com/AdemBoukhris457/Doctra/issues) 查找类似问题
2. 创建新问题，包含：
    - 您的操作系统和版本
    - Python 版本（`python --version`）
    - 完整错误消息
    - 使用的安装方法

