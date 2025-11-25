# Development Guide

Thank you for your interest in contributing to Doctra! This guide will help you get started.

## Getting Started

### Development Setup

1. **Fork and Clone**

```bash
git clone https://github.com/YOUR_USERNAME/Doctra.git
cd Doctra
```

2. **Create Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. **Install Development Dependencies**

```bash
pip install -e ".[dev]"
```

This installs Doctra in editable mode with development tools.

4. **Install System Dependencies**

Follow the [Installation Guide](../getting-started/installation.md#system-dependencies) for Poppler.

## Project Structure

```
Doctra/
├── doctra/              # Main package
│   ├── parsers/         # PDF parsers
│   ├── engines/         # Processing engines
│   ├── exporters/       # Output formatters
│   ├── ui/              # Web interface
│   ├── cli/             # Command line interface
│   └── utils/           # Utilities
├── tests/               # Test suite
├── docs/                # Documentation
├── examples/            # Example scripts
├── notebooks/           # Jupyter notebooks
└── setup.py             # Package configuration
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/updates

### 2. Make Changes

Write clean, well-documented code following our [Code Style](#code-style).

### 3. Run Tests

```bash
pytest tests/
```

Run specific test:

```bash
pytest tests/test_structured_pdf_parser.py
```

With coverage:

```bash
pytest --cov=doctra tests/
```

### 4. Format Code

```bash
# Format with Black
black doctra tests

# Sort imports
isort doctra tests

# Lint with Flake8
flake8 doctra tests
```

### 5. Type Checking

```bash
mypy doctra
```

### 6. Commit Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

Commit message format:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting
- `refactor:` - Code restructuring
- `test:` - Tests
- `chore:` - Maintenance

### 7. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with these configurations:

```python
# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,docs,build,dist
```

### Code Formatting

```python
# Black configuration in pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311', 'py312']
```

### Import Sorting

```python
# isort configuration in pyproject.toml
[tool.isort]
profile = "black"
multi_line_output = 3
```

### Example Code

```python
"""Module docstring explaining purpose."""

from typing import Optional, Union

import numpy as np
from PIL import Image

from doctra.utils import helper_function


class MyParser:
    """Class docstring explaining purpose.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Attributes:
        attribute1: Description
    """
    
    def __init__(self, param1: str, param2: int = 10):
        """Initialize the parser."""
        self.param1 = param1
        self.param2 = param2
    
    def process(self, input_data: Union[str, np.ndarray]) -> Optional[Image.Image]:
        """Process input data.
        
        Args:
            input_data: Input to process
        
        Returns:
            Processed image or None
        
        Raises:
            ValueError: If input is invalid
        """
        if not self._validate(input_data):
            raise ValueError("Invalid input")
        
        return self._do_process(input_data)
    
    def _validate(self, data) -> bool:
        """Private helper method."""
        return data is not None
```

## Testing

### Writing Tests

Create tests in `tests/` directory:

```python
import pytest
from doctra.parsers import StructuredPDFParser


def test_parser_initialization():
    """Test parser can be initialized."""
    parser = StructuredPDFParser()
    assert parser is not None


def test_parse_basic_pdf():
    """Test parsing a basic PDF."""
    parser = StructuredPDFParser()
    result = parser.parse("test_data/sample.pdf")
    assert result is not None


@pytest.mark.parametrize("dpi", [100, 200, 300])
def test_different_dpi_settings(dpi):
    """Test parser with different DPI settings."""
    parser = StructuredPDFParser(dpi=dpi)
    assert parser.dpi == dpi
```

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_parsers.py

# Specific test
pytest tests/test_parsers.py::test_parser_initialization

# With verbose output
pytest -v

# With coverage
pytest --cov=doctra --cov-report=html

# Stop on first failure
pytest -x
```

### Test Coverage

Aim for >80% code coverage:

```bash
pytest --cov=doctra --cov-report=term-missing
```

## Documentation

### Building Documentation

```bash
# Install documentation dependencies
pip install -r docs/requirements.txt

# Build and serve locally
mkdocs serve

# Build static site
mkdocs build
```

View at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Writing Documentation

- Use Markdown for all documentation
- Add docstrings to all public APIs
- Include code examples
- Update relevant docs when adding features

### Docstring Format

We use Google-style docstrings:

```python
def function(param1: str, param2: int) -> bool:
    """Short description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is invalid
        
    Examples:
        >>> function("test", 5)
        True
    """
    pass
```

## Pull Request Guidelines

### Before Submitting

- [ ] Tests pass: `pytest`
- [ ] Code formatted: `black doctra tests`
- [ ] Imports sorted: `isort doctra tests`
- [ ] Linting clean: `flake8 doctra tests`
- [ ] Type checking: `mypy doctra`
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing done

## Checklist
- [ ] Tests pass
- [ ] Code formatted
- [ ] Documentation updated
- [ ] CHANGELOG updated
```

### Review Process

1. Automated checks run (tests, linting)
2. Code review by maintainers
3. Requested changes addressed
4. Approved and merged

## Common Tasks

### Adding a New Parser

1. Create parser file: `doctra/parsers/new_parser.py`
2. Implement parser class
3. Add tests: `tests/test_new_parser.py`
4. Update `doctra/__init__.py`
5. Add documentation: `docs/user-guide/parsers/new-parser.md`
6. Add API reference: `docs/api/parsers.md`

### Adding a New Feature

1. Create feature branch
2. Implement feature with tests
3. Update documentation
4. Submit PR with description

### Fixing a Bug

1. Create test that reproduces bug
2. Fix bug
3. Verify test passes
4. Submit PR referencing issue

## Development Tools

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pre-commit install
```

This runs checks before each commit:

- Black formatting
- isort import sorting
- Flake8 linting
- Trailing whitespace removal

### IDE Setup

#### VS Code

Recommended `settings.json`:

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

- Enable Black formatter
- Enable Flake8 linter
- Enable mypy type checker

## Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/AdemBoukhris457/Doctra/discussions)
- **Bugs**: Report in [GitHub Issues](https://github.com/AdemBoukhris457/Doctra/issues)
- **Chat**: Join our community (link in README)

## Code of Conduct

Please read and follow our [Code of Conduct](code-of-conduct.md).

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

