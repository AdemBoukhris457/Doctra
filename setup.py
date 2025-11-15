"""Setup script for Doctra."""
from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import sys
import subprocess

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


class PostInstallCommand(install):
    """Post-installation command to install packages from specific index URLs."""
    
    def run(self):
        """Run the standard install, then install packages from specific indexes."""
        # Check if we're in a build environment (pip not available or can't run)
        # Skip post-install steps during build
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                # pip is not available, skip post-install
                install.run(self)
                return
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            # pip is not available, skip post-install
            install.run(self)
            return
        
        # Temporarily remove paddlepaddle-gpu and torch from install_requires
        # to avoid installation failures if they're not on PyPI
        original_requires = self.distribution.install_requires[:]
        filtered_requires = [
            req for req in original_requires 
            if not (req.startswith("paddlepaddle-gpu") or req.startswith("torch=="))
        ]
        self.distribution.install_requires = filtered_requires
        
        # Run standard install
        install.run(self)
        
        # Restore original requires
        self.distribution.install_requires = original_requires
        
        # Install paddlepaddle-gpu from PaddlePaddle's index
        paddle_index = "https://www.paddlepaddle.org.cn/packages/stable/cu118/"
        print(f"\n📦 Installing paddlepaddle-gpu==3.2.0 from {paddle_index}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "paddlepaddle-gpu==3.2.0",
                "-i", paddle_index,
                "--upgrade", "--force-reinstall"
            ])
            print("✅ Successfully installed paddlepaddle-gpu==3.2.0")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Failed to install paddlepaddle-gpu from custom index: {e}")
            print(f"   You may need to install it manually:")
            print(f"   pip install paddlepaddle-gpu==3.2.0 -i {paddle_index}")
        
        # Install torch==2.8.0
        print(f"\n📦 Installing torch==2.8.0")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "torch==2.8.0",
                "--upgrade", "--force-reinstall"
            ])
            print("✅ Successfully installed torch==2.8.0")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Failed to install torch==2.8.0: {e}")
            print(f"   You may need to install it manually:")
            print(f"   pip install torch==2.8.0")

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
    cmdclass={
        'install': PostInstallCommand,
    },
    install_requires=[
        # Note: paddlepaddle-gpu is installed via PostInstallCommand from PaddlePaddle index
        # (not available on PyPI). torch is also installed via PostInstallCommand to ensure version.
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