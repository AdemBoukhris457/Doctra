# Contributing to Doctra

Thank you for your interest in contributing to Doctra! This document provides guidelines for contributors.

## Code of Conduct

This project is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior to boukhrisadam98@gmail.com.

## Getting Started

### How to Contribute

- 🐛 **Bug Reports**: Report issues you encounter
- 💡 **Feature Requests**: Suggest new features or improvements  
- 📝 **Documentation**: Improve or add documentation
- 🧪 **Testing**: Add or improve tests
- 🔧 **Code**: Fix bugs or implement new features

### Before You Start

1. Check existing [Issues](https://github.com/AdemBoukhris457/Doctra/issues) and [Pull Requests](https://github.com/AdemBoukhris457/Doctra/pulls)
2. For major changes, open an issue first to discuss the approach
3. Fork the repository and create a feature branch

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Poppler (for PDF processing)

### Setup Steps

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/Doctra.git
cd Doctra

# 2. Create virtual environment
python -m venv venv
# Windows: .\venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Install system dependencies
# Ubuntu/Debian: sudo apt install poppler-utils
# macOS: brew install poppler
# Windows: Download from http://blog.alivate.com.au/poppler-windows/

# 5. Install pre-commit hooks
pre-commit install
```

## Development Workflow

### 1. Create Branch

```bash
git checkout -b feature/your-feature-name
```

**Branch naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/updates

### 2. Make Changes

Follow the [Code Style](#code-style) guidelines.

### 3. Test and Format

```bash
# Run tests
pytest

# Format code
black doctra tests
isort doctra tests

# Lint
flake8 doctra tests
mypy doctra
```

### 4. Commit and Push

```bash
git add .
git commit -m "feat: add new feature description"
git push origin feature/your-feature-name
```

**Commit format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting
- `refactor:` - Code restructuring
- `test:` - Tests
- `chore:` - Maintenance

## Code Style

### Python Guidelines

- **Line length**: 88 characters (Black default)
- **Type hints**: Required for all public APIs
- **Docstrings**: Follow the library's docstring format (see examples below)

### Docstring Format

Follow the library's existing docstring pattern:

```python
def function_name(param1: str, param2: int = 10) -> bool:
    """
    Brief description of what the function does.
    
    Longer description if needed, explaining the purpose
    and any important details about the function.

    :param param1: Description of param1
    :param param2: Description of param2 (default: 10)
    :return: Description of return value
    :raises ValueError: When param1 is invalid
    """
    pass
```

### Class Docstrings

```python
class MyParser:
    """
    Brief description of the class.
    
    Longer description explaining the class purpose
    and main functionality.

    :param param1: Description of param1
    :param param2: Description of param2
    """
    
    def __init__(self, param1: str, param2: int = 10):
        """Initialize the parser."""
        self.param1 = param1
        self.param2 = param2
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

# With coverage
pytest --cov=doctra --cov-report=html

# Specific test
pytest tests/test_parsers.py::test_parser_initialization
```

## Pull Request Guidelines

### Before Submitting

- [ ] Tests pass: `pytest`
- [ ] Code formatted: `black doctra tests`
- [ ] Imports sorted: `isort doctra tests`
- [ ] Linting clean: `flake8 doctra tests`
- [ ] Type checking: `mypy doctra`
- [ ] Documentation updated

### PR Template

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
```

## Common Tasks

### Adding a New Parser

1. Create `doctra/parsers/new_parser.py`
2. Implement class with proper docstrings
3. Add tests in `tests/test_new_parser.py`
4. Update `doctra/__init__.py`
5. Add documentation

### Adding a New Feature

1. Create feature branch
2. Implement with tests
3. Update documentation
4. Submit PR

### Fixing a Bug

1. Create test that reproduces bug
2. Fix the bug
3. Verify test passes
4. Submit PR referencing issue

## Getting Help

- **Questions**: [GitHub Discussions](https://github.com/AdemBoukhris457/Doctra/discussions)
- **Bugs**: [GitHub Issues](https://github.com/AdemBoukhris457/Doctra/issues)
- **Documentation**: [Documentation Site](https://ademboukhris457.github.io/Doctra/)

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
