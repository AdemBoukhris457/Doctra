"""
Doctra - Advanced Document Processing Library
"""

# Core imports
from .parsers.structured_pdf_parser import StructuredPDFParser
from .parsers.table_chart_extractor import ChartTablePDFParser

# CLI
try:
    from .cli import cli
except ImportError:
    # CLI dependencies not available
    cli = None

__version__ = "1.0.0"

__all__ = [
    'StructuredPDFParser',
    'ChartTablePDFParser',
    'cli',
]