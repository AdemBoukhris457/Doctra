# 开发指南

感谢您对为 Doctra 做出贡献感兴趣！本指南将帮助您入门。

## 入门

### 开发设置

1. **Fork 和克隆**

```bash
git clone https://github.com/YOUR_USERNAME/Doctra.git
cd Doctra
```

2. **创建虚拟环境**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. **安装开发依赖**

```bash
pip install -e ".[dev]"
```

这将以可编辑模式安装 Doctra 和开发工具。

4. **安装系统依赖**

按照[安装指南](../getting-started/installation.md#system-dependencies)安装 Poppler。

## 项目结构

```
Doctra/
├── doctra/              # 主包
│   ├── parsers/         # PDF 解析器
│   ├── engines/         # 处理引擎
│   ├── exporters/       # 输出格式化器
│   ├── ui/              # Web 界面
│   ├── cli/             # 命令行界面
│   └── utils/           # 工具
├── tests/               # 测试套件
├── docs/                # 文档
├── examples/            # 示例脚本
├── notebooks/           # Jupyter 笔记本
└── setup.py             # 包配置
```

## 开发工作流

### 1. 创建分支

```bash
git checkout -b feature/your-feature-name
```

分支命名约定：

- `feature/` - 新功能
- `fix/` - 错误修复
- `docs/` - 文档更新
- `refactor/` - 代码重构
- `test/` - 测试添加/更新

### 2. 进行更改

编写清晰、文档完善的代码，遵循我们的[代码风格](#code-style)。

### 3. 运行测试

```bash
pytest tests/
```

运行特定测试：

```bash
pytest tests/test_structured_pdf_parser.py
```

带覆盖率：

```bash
pytest --cov=doctra tests/
```

### 4. 格式化代码

```bash
# 使用 Black 格式化
black doctra tests

# 排序导入
isort doctra tests

# 使用 Flake8 检查
flake8 doctra tests
```

### 5. 类型检查

```bash
mypy doctra
```

### 6. 提交更改

```bash
git add .
git commit -m "feat: add new feature description"
```

提交消息格式：

- `feat:` - 新功能
- `fix:` - 错误修复
- `docs:` - 文档
- `style:` - 格式化
- `refactor:` - 代码重构
- `test:` - 测试
- `chore:` - 维护

### 7. 推送并创建 PR

```bash
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request。

## 代码风格 {#code-style}

### Python 风格指南

我们遵循 [PEP 8](https://pep8.org/)，配置如下：

```python
# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,docs,build,dist
```

### 代码格式化

```python
# pyproject.toml 中的 Black 配置
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311', 'py312']
```

### 导入排序

```python
# pyproject.toml 中的 isort 配置
[tool.isort]
profile = "black"
multi_line_output = 3
```

### 示例代码

```python
"""模块文档字符串，说明用途。"""

from typing import Optional, Union

import numpy as np
from PIL import Image

from doctra.utils import helper_function


class MyParser:
    """类文档字符串，说明用途。
    
    Args:
        param1: param1 的描述
        param2: param2 的描述
    
    Attributes:
        attribute1: 描述
    """
    
    def __init__(self, param1: str, param2: int = 10):
        """初始化解析器。"""
        self.param1 = param1
        self.param2 = param2
    
    def process(self, input_data: Union[str, np.ndarray]) -> Optional[Image.Image]:
        """处理输入数据。
        
        Args:
            input_data: 要处理的输入
        
        Returns:
            处理后的图像或 None
        
        Raises:
            ValueError: 如果输入无效
        """
        if not self._validate(input_data):
            raise ValueError("Invalid input")
        
        return self._do_process(input_data)
    
    def _validate(self, data) -> bool:
        """私有辅助方法。"""
        return data is not None
```

## 测试

### 编写测试

在 `tests/` 目录中创建测试：

```python
import pytest
from doctra.parsers import StructuredPDFParser


def test_parser_initialization():
    """测试解析器可以初始化。"""
    parser = StructuredPDFParser()
    assert parser is not None


def test_parse_basic_pdf():
    """测试解析基本 PDF。"""
    parser = StructuredPDFParser()
    result = parser.parse("test_data/sample.pdf")
    assert result is not None


@pytest.mark.parametrize("dpi", [100, 200, 300])
def test_different_dpi_settings(dpi):
    """测试不同 DPI 设置的解析器。"""
    parser = StructuredPDFParser(dpi=dpi)
    assert parser.dpi == dpi
```

### 运行测试

```bash
# 所有测试
pytest

# 特定文件
pytest tests/test_parsers.py

# 特定测试
pytest tests/test_parsers.py::test_parser_initialization

# 详细输出
pytest -v

# 带覆盖率
pytest --cov=doctra --cov-report=html

# 在第一次失败时停止
pytest -x
```

### 测试覆盖率

目标是 >80% 的代码覆盖率：

```bash
pytest --cov=doctra --cov-report=term-missing
```

## 文档

### 构建文档

```bash
# 安装文档依赖
pip install -r docs/requirements.txt

# 构建并在本地提供
mkdocs serve

# 构建静态站点
mkdocs build
```

查看地址：[http://127.0.0.1:8000](http://127.0.0.1:8000)

### 编写文档

- 对所有文档使用 Markdown
- 为所有公共 API 添加文档字符串
- 包含代码示例
- 添加功能时更新相关文档

### 文档字符串格式

我们使用 Google 风格的文档字符串：

```python
def function(param1: str, param2: int) -> bool:
    """简短描述。
    
    如果需要，可以添加更长的描述。
    
    Args:
        param1: param1 的描述
        param2: param2 的描述
    
    Returns:
        返回值的描述
    
    Raises:
        ValueError: 当 param1 无效时
        
    Examples:
        >>> function("test", 5)
        True
    """
    pass
```

## Pull Request 指南

### 提交前

- [ ] 测试通过：`pytest`
- [ ] 代码已格式化：`black doctra tests`
- [ ] 导入已排序：`isort doctra tests`
- [ ] 代码检查通过：`flake8 doctra tests`
- [ ] 类型检查：`mypy doctra`
- [ ] 文档已更新
- [ ] CHANGELOG.md 已更新

### PR 描述模板

```markdown
## Description
更改的简要描述

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
描述已完成的测试

## Checklist
- [ ] Tests pass
- [ ] Code formatted
- [ ] Documentation updated
- [ ] CHANGELOG updated
```

### 审查流程

1. 运行自动化检查（测试、代码检查）
2. 维护者进行代码审查
3. 解决请求的更改
4. 批准并合并

## 常见任务

### 添加新解析器

1. 创建解析器文件：`doctra/parsers/new_parser.py`
2. 实现解析器类
3. 添加测试：`tests/test_new_parser.py`
4. 更新 `doctra/__init__.py`
5. 添加文档：`docs/user-guide/parsers/new-parser.md`
6. 添加 API 参考：`docs/api/parsers.md`

### 添加新功能

1. 创建功能分支
2. 实现功能并编写测试
3. 更新文档
4. 提交带描述的 PR

### 修复错误

1. 创建重现错误的测试
2. 修复错误
3. 验证测试通过
4. 提交引用问题的 PR

## 开发工具

### Pre-commit 钩子

安装 pre-commit 钩子：

```bash
pre-commit install
```

这会在每次提交前运行检查：

- Black 格式化
- isort 导入排序
- Flake8 代码检查
- 删除尾随空格

### IDE 设置

#### VS Code

推荐的 `settings.json`：

```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "[python]": {
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

#### PyCharm

- 启用 Black 格式化器
- 启用 Flake8 检查器
- 启用 mypy 类型检查器

## 获取帮助

- **问题**：打开 [GitHub Discussion](https://github.com/AdemBoukhris457/Doctra/discussions)
- **错误**：在 [GitHub Issues](https://github.com/AdemBoukhris457/Doctra/issues) 中报告
- **聊天**：加入我们的社区（README 中的链接）

## 行为准则

请阅读并遵循我们的[行为准则](code-of-conduct.md)。

## 许可证

通过贡献，您同意您的贡献将在 MIT 许可证下授权。

