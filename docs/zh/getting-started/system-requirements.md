# 系统要求

本页概述了有效运行 Doctra 所需的硬件和软件要求。

## Python 要求

- **Python 版本**：3.8 或更高版本
- **操作系统**：
    - Linux（Ubuntu、Debian、CentOS 等）
    - macOS（10.13 或更高版本）
    - Windows（10 或更高版本）

## 硬件要求

### 最低要求

| 组件 | 规格 |
|------|------|
| CPU | 双核处理器，2.0 GHz |
| RAM | 4 GB |
| 磁盘空间 | 2 GB 用于安装 + 输出空间 |
| GPU | 不需要（可使用 CPU 处理） |

### 推荐要求

| 组件 | 规格 |
|------|------|
| CPU | 四核处理器，3.0 GHz 或更高 |
| RAM | 8 GB 或更多 |
| 磁盘空间 | 10 GB 用于安装 + 模型 + 输出 |
| GPU | 具有 4+ GB VRAM 的 NVIDIA GPU（用于加速） |

### 性能考虑

#### 处理速度

处理 10 页 PDF 的典型时间：

| 配置 | 时间 |
|------|------|
| 仅 CPU（4 核） | ~2-3 分钟 |
| GPU（NVIDIA GTX 1060） | ~1-2 分钟 |
| GPU（NVIDIA RTX 3080） | ~30-60 秒 |

!!! note "影响性能的因素"
    - 文档复杂性（图像、表格、图表的数量）
    - 图像分辨率（DPI 设置）
    - 是否启用图像恢复
    - VLM 处理（需要网络调用）

#### 内存使用

预期的 RAM 使用：

- **基本解析**：500 MB - 2 GB
- **增强解析**：1 GB - 4 GB
- **VLM 处理**：额外 500 MB - 1 GB
- **高 DPI (300+)**：额外 2-4 GB

## 软件依赖

### 必需

1. **Poppler** - PDF 渲染和处理
    - 版本：最新稳定版本
    - 安装：请参阅[安装指南](installation.md#system-dependencies)

2. **Tesseract OCR** - 文本提取
    - 通过 Python 依赖项自动安装
    - 无需手动安装

### 可选

1. **CUDA Toolkit** - 用于 GPU 加速
    - 版本：11.8 或更高版本
    - 仅 GPU 处理需要
    - 下载：[NVIDIA CUDA 下载](https://developer.nvidia.com/cuda-downloads)

2. **cuDNN** - 深度学习 GPU 加速
    - 版本：8.6 或更高版本
    - 仅 GPU 处理需要
    - 下载：[NVIDIA cuDNN 下载](https://developer.nvidia.com/cudnn)

## GPU 支持

### CUDA 要求

用于 GPU 加速处理：

- **GPU**：具有计算能力 3.5 或更高的 NVIDIA GPU
- **CUDA**：版本 11.8 或更高版本
- **cuDNN**：版本 8.6 或更高版本
- **驱动程序**：兼容的 NVIDIA 驱动程序

### 支持的 GPU

Doctra 的图像恢复功能适用于支持 CUDA 的 NVIDIA GPU：

| GPU 系列 | 支持级别 |
|----------|----------|
| GeForce GTX 10xx 及更新版本 | ✅ 完全支持 |
| GeForce RTX 系列 | ✅ 完全支持 |
| Tesla 系列 | ✅ 完全支持 |
| Quadro 系列 | ✅ 完全支持 |
| AMD GPU | ❌ 不支持 |
| Intel GPU | ❌ 不支持 |

### 检查 GPU 兼容性

验证 CUDA 是否可用：

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
```

## 网络要求

### 模型下载

首次使用时，Doctra 会下载 AI 模型：

- **PaddleOCR 模型**：~300 MB
- **DocRes 模型**：~200 MB
- **总计**：~500 MB 初始下载

模型在首次下载后会在本地缓存。

### VLM API 访问

如果使用视觉语言模型：

- 需要稳定的互联网连接
- 适用 API 速率限制（取决于提供商）
- 带宽：最小（图像在发送前会被压缩）

## 存储要求

### 安装

| 组件 | 大小 |
|------|------|
| Doctra 包 | ~50 MB |
| Python 依赖项 | ~500 MB |
| AI 模型（首次使用时下载） | ~500 MB |
| **总计** | **~1 GB** |

### 处理输出

每个文档的预期输出大小：

| 文档大小 | 输出大小（约） |
|----------|---------------|
| 10 页报告 | 5-20 MB |
| 50 页文档 | 25-100 MB |
| 100 页书籍 | 50-200 MB |

!!! tip "存储规划"
    根据以下因素，为输出预留原始 PDF 大小的 2-10 倍空间：
    
    - 文档中的图像数量
    - 使用的 DPI 设置
    - 是否启用图像恢复

## 浏览器要求（Web UI）

对于基于 Gradio 的 Web 界面：

- **现代浏览器**：Chrome 90+、Firefox 88+、Safari 14+、Edge 90+
- **JavaScript**：必须启用
- **本地网络**：需要访问 localhost

## 云部署

Doctra 可以在云平台上运行：

### 推荐的云规格

| 提供商 | 实例类型 | vCPU | RAM | GPU |
|--------|----------|------|-----|-----|
| AWS | t3.xlarge | 4 | 16 GB | 可选 |
| GCP | n1-standard-4 | 4 | 15 GB | 可选 |
| Azure | Standard_D4s_v3 | 4 | 16 GB | 可选 |

对于 GPU 处理：

| 提供商 | 实例类型 | GPU | VRAM |
|--------|----------|-----|------|
| AWS | g4dn.xlarge | T4 | 16 GB |
| GCP | n1-standard-4 + T4 | T4 | 16 GB |
| Azure | NC6 | K80 | 12 GB |

### Google Colab

Doctra 在 Google Colab 中运行良好：

- **免费层**：足以满足大多数用例
- **GPU**：免费层可用
- **RAM**：免费层 12-13 GB
- **磁盘**：100+ GB 临时存储

## 操作系统特定说明

### Linux

- **最佳性能**：通常最快，因为 CUDA 支持更好
- **易于设置**：包管理器使依赖项安装变得简单
- **Docker**：易于容器化部署

### macOS

- **无 GPU 支持**：macOS 上不可用 CUDA
- **良好的 CPU 性能**：在 Apple Silicon (M1/M2) 上高效
- **Poppler**：通过 Homebrew 轻松安装

### Windows

- **GPU 支持**：完全支持 CUDA
- **Poppler 设置**：需要手动安装或使用 conda
- **路径配置**：可能需要将 Poppler 添加到 PATH

## 性能优化

### 对于仅 CPU 系统

```python
parser = StructuredPDFParser(
    dpi=150,  # 较低分辨率
    min_score=0.7  # 更高阈值 = 更少元素
)
```

### 对于 GPU 系统

```python
from doctra import EnhancedPDFParser

parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_device="cuda",  # 使用 GPU
    restoration_dpi=300  # 更高质量
)
```

### 内存优化

```python
# 批量处理文档
import os
from doctra import StructuredPDFParser

parser = StructuredPDFParser()

# 一次处理一个以管理内存
for pdf_file in pdf_files:
    parser.parse(pdf_file)
    # 解析器被重用，文档之间的内存被清理
```

## 故障排除

### 内存不足错误

**解决方案**：

1. 降低 DPI：`dpi=100`
2. 禁用图像恢复
3. 关闭其他应用程序
4. 一次处理更少的页面

### 处理速度慢

**解决方案**：

1. 启用 GPU：`restoration_device="cuda"`
2. 降低 DPI：`dpi=150`
3. 升级硬件
4. 在非高峰时段处理

### 模型下载失败

**解决方案**：

1. 检查互联网连接
2. 验证防火墙设置
3. 如果在限制性网络后，使用 VPN
4. 手动下载模型（请参阅故障排除指南）

## 下一步

- [安装指南](installation.md) - 安装 Doctra
- [快速开始](quick-start.md) - 开始使用 Doctra
- [性能提示](../user-guide/core-concepts.md) - 优化您的设置

