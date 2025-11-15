"""Setup script for Doctra."""
from setuptools import setup, find_packages
import os
import sys

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get version from version.py
version = {}
with open(os.path.join('doctra', 'version.py')) as f:
    exec(f.read(), version)

# Platform-specific safetensors dependencies
safetensors_deps = []
if sys.platform == 'linux':
    safetensors_deps.append(
        "safetensors @ https://paddle-whl.bj.bcebos.com/nightly/cu126/safetensors/safetensors-0.6.2.dev0-cp38-abi3-linux_x86_64.whl"
    )
elif sys.platform == 'win32':
    safetensors_deps.append(
        "safetensors @ https://xly-devops.cdn.bcebos.com/safetensors-nightly/safetensors-0.6.2.dev0-cp38-abi3-win_amd64.whl"
    )

setup(
    name="doctra",
    version=version['__version__'],
    description="Parse, extract, and analyze documents with ease",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Adem Boukhris",
    author_email="boukhrisadam98@gmail.com",
    url="https://github.com/AdemBoukhris457/Doctra",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "doctra=doctra.cli.main:cli",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "paddlepaddle-gpu>=2.6.0",
        "paddleocr[doc-parser]>=3.2.0",
        "pillow>=8.0.0",
        "opencv-python>=4.5.0",
        "pandas>=1.3.0",
        "openpyxl>=3.0.0",
        "tesseract>=0.1.3",
        "pytesseract>=0.3.10",
        "pdf2image>=1.16.0",
        "anthropic>=0.40.0",
        "outlines>=0.0.34",
        "tqdm>=4.62.0",
        "matplotlib>=3.5.0",
        "click>=8.0.0",
        "python-docx>=0.8.11",
        "google-genai",
        "openai>=1.0.0",
        "ollama>=0.1.0",
        "markdown-it-py>=2.0.0",
        "gradio",
        "pymupdf>=1.23.0",
        "scikit-image>=0.19.3",
        "torchvision",
    ] + safetensors_deps,
    extras_require={
        "openai": ["openai>=1.0.0"],
        "gemini": ["google-genai"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "isort>=5.0",
            "flake8>=3.9",
            "mypy>=0.910",
            "pre-commit>=2.15.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)