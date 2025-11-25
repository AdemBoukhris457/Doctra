# 引擎 API 参考

Doctra 引擎的完整 API 文档。

## DocResEngine

用于文档增强的图像恢复引擎。

::: doctra.engines.image_restoration.DocResEngine
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

---

## 快速参考

### DocResEngine

```python
from doctra import DocResEngine

# 初始化引擎
engine = DocResEngine(
    device: str = None,  # "cuda"、"cpu" 或 None 自动检测
    use_half_precision: bool = False,
    model_path: str = None,
    mbd_path: str = None
)

# 恢复单个图像
restored_img, metadata = engine.restore_image(
    image: Union[str, np.ndarray, PIL.Image.Image],
    task: str = "appearance"
)

# 恢复 PDF
output_path = engine.restore_pdf(
    pdf_path: str,
    output_path: str = None,
    task: str = "appearance",
    dpi: int = 200
)
```

## 参数参考

### 初始化参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `device` | str | None | 处理设备："cuda"、"cpu" 或 None（自动检测） |
| `use_half_precision` | bool | False | 使用 FP16 以加快 GPU 处理速度 |
| `model_path` | str | None | 恢复模型的自定义路径 |
| `mbd_path` | str | None | MBD 模型的自定义路径 |

### 恢复任务

| 任务 | 描述 | 用例 |
|------|------|------|
| `"appearance"` | 一般外观增强 | 大多数文档（默认） |
| `"dewarping"` | 校正透视失真 | 有透视问题的扫描文档 |
| `"deshadowing"` | 去除阴影和光照伪影 | 光照条件差 |
| `"deblurring"` | 减少模糊并提高清晰度 | 运动模糊、对焦问题 |
| `"binarization"` | 转换为黑白 | 干净的文本提取 |
| `"end2end"` | 完整的恢复流程 | 严重退化的文档 |

## 方法

### restore_image()

恢复单个图像。

**参数**：

- `image` (str | np.ndarray | PIL.Image.Image)：输入图像（路径、numpy 数组或 PIL 图像）
- `task` (str)：要执行的恢复任务

**返回**：

- `restored_img` (PIL.Image.Image)：恢复的图像
- `metadata` (dict)：处理元数据，包括任务、设备和时间

**示例**：

```python
from doctra import DocResEngine

engine = DocResEngine(device="cuda")
restored, meta = engine.restore_image("blurry.jpg", task="deblurring")

print(f"任务：{meta['task']}")
print(f"设备：{meta['device']}")
print(f"时间：{meta['processing_time']:.2f}秒")

# 保存恢复的图像
restored.save("restored.jpg")
```

### restore_pdf()

恢复 PDF 文档中的所有页面。

**参数**：

- `pdf_path` (str)：输入 PDF 的路径
- `output_path` (str, 可选)：输出 PDF 的路径（如果为 None 则自动生成）
- `task` (str)：要执行的恢复任务
- `dpi` (int)：处理的分辨率

**返回**：

- `output_path` (str)：恢复的 PDF 的路径

**示例**：

```python
from doctra import DocResEngine

engine = DocResEngine(device="cuda")
restored_pdf = engine.restore_pdf(
    pdf_path="low_quality.pdf",
    output_path="enhanced.pdf",
    task="appearance",
    dpi=300
)

print(f"恢复的 PDF 已保存到：{restored_pdf}")
```

## 设备选择

### 自动检测

```python
# 如果可用则自动使用 GPU，否则使用 CPU
engine = DocResEngine()
```

### 显式 GPU

```python
# 强制使用 GPU（如果 CUDA 不可用则会出错）
engine = DocResEngine(device="cuda")
```

### 显式 CPU

```python
# 强制使用 CPU（较慢但始终可用）
engine = DocResEngine(device="cpu")
```

### 检查设备

```python
import torch

print(f"CUDA 可用：{torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU：{torch.cuda.get_device_name(0)}")
```

## 性能优化

### 半精度

在现代 GPU 上使用 FP16 可获得约 2 倍速度：

```python
engine = DocResEngine(
    device="cuda",
    use_half_precision=True  # 更快，质量损失最小
)
```

**要求**：
- 计算能力 7.0+ 的 NVIDIA GPU（Volta 或更新版本）
- 示例：RTX 20xx、RTX 30xx、RTX 40xx、A100、V100

### 批量处理

高效处理多个图像：

```python
from doctra import DocResEngine

engine = DocResEngine(device="cuda")

# 处理图像列表
images = ["doc1.jpg", "doc2.jpg", "doc3.jpg"]
restored_images = []

for img_path in images:
    restored, _ = engine.restore_image(img_path, task="appearance")
    restored_images.append(restored)
    restored.save(f"restored_{img_path}")
```

### DPI 考虑

| DPI | 质量 | 速度 | 内存 | 最适合 |
|-----|------|------|------|--------|
| 100 | 低 | 快 | 低 | 快速预览 |
| 150 | 中 | 中 | 中 | 一般用途 |
| 200 | 好 | 慢 | 中 | 默认设置 |
| 300 | 高 | 非常慢 | 高 | 高质量扫描 |

## 元数据

`restore_image()` 方法返回元数据：

```python
restored, metadata = engine.restore_image("doc.jpg", "appearance")

print(metadata)
# {
#     'task': 'appearance',
#     'device': 'cuda',
#     'processing_time': 1.23,
#     'input_size': (1920, 1080),
#     'output_size': (1920, 1080)
# }
```

## 错误处理

```python
from doctra import DocResEngine

engine = DocResEngine(device="cuda")

try:
    restored, meta = engine.restore_image("document.jpg", "appearance")
except FileNotFoundError:
    print("未找到图像")
except RuntimeError as e:
    print(f"CUDA 错误：{e}")
    # 回退到 CPU
    engine = DocResEngine(device="cpu")
    restored, meta = engine.restore_image("document.jpg", "appearance")
except Exception as e:
    print(f"意外错误：{e}")
```

## 与解析器集成

DocResEngine 已集成到 EnhancedPDFParser 中：

```python
from doctra import EnhancedPDFParser

# 这内部使用 DocResEngine
parser = EnhancedPDFParser(
    use_image_restoration=True,
    restoration_task="appearance",
    restoration_device="cuda"
)

parser.parse("document.pdf")
```

对于独立恢复：

```python
from doctra import DocResEngine

# 步骤 1：恢复 PDF
engine = DocResEngine(device="cuda")
enhanced_pdf = engine.restore_pdf(
    pdf_path="low_quality.pdf",
    output_path="enhanced.pdf",
    task="appearance"
)

# 步骤 2：解析增强的 PDF
from doctra import StructuredPDFParser

parser = StructuredPDFParser()
parser.parse(enhanced_pdf)
```

## 示例

### 示例 1：去扭曲扫描文档

```python
from doctra import DocResEngine

engine = DocResEngine(device="cuda")

# 修复透视失真
restored, meta = engine.restore_image(
    "scanned_with_distortion.jpg",
    task="dewarping"
)

restored.save("dewarped.jpg")
print(f"处理时间：{meta['processing_time']:.2f}秒")
```

### 示例 2：去除阴影

```python
from doctra import DocResEngine

engine = DocResEngine(device="cuda")

# 去除阴影伪影
restored, meta = engine.restore_image(
    "document_with_shadows.jpg",
    task="deshadowing"
)

restored.save("no_shadows.jpg")
```

### 示例 3：批量 PDF 恢复

```python
import os
from doctra import DocResEngine

engine = DocResEngine(device="cuda", use_half_precision=True)

pdf_dir = "input_pdfs"
output_dir = "restored_pdfs"
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(pdf_dir):
    if filename.endswith(".pdf"):
        input_path = os.path.join(pdf_dir, filename)
        output_path = os.path.join(output_dir, f"restored_{filename}")
        
        print(f"处理 {filename}...")
        engine.restore_pdf(
            pdf_path=input_path,
            output_path=output_path,
            task="appearance",
            dpi=200
        )
```

## 另请参阅

- [增强解析器](../user-guide/parsers/enhanced-parser.md) - 将恢复与解析结合使用
- [核心概念](../user-guide/core-concepts.md) - 了解图像恢复
- [示例](../examples/advanced-examples.md) - 高级用法模式

