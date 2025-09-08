"""
Doctra - Document Parsing Library
Parse, extract, and analyze documents with ease
"""

from .parsers.structured_pdf_parser import StructuredPDFParser
from .parsers.table_chart_extractor import ChartTablePDFParser
from .version import __version__
from .ui import build_demo, launch_ui

__all__ = [
    'StructuredPDFParser',
    'ChartTablePDFParser',
    'build_demo',
    'launch_ui',
    '__version__'
]

# Package metadata
__author__ = 'Adem Boukhris'
__email__ = 'boukhrisadam98@gmail.com'  # Replace with your email
__description__ = 'Parse, extract, and analyze documents with ease'