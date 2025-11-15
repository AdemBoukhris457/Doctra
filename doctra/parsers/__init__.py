"""Parsers module for Doctra."""

from .structured_pdf_parser import StructuredPDFParser
from .enhanced_pdf_parser import EnhancedPDFParser
from .table_chart_extractor import ChartTablePDFParser
from .structured_docx_parser import StructuredDOCXParser

try:
    from .paddleocr_vl_parser import PaddleOCRVLPDFParser
    __all__ = ['StructuredPDFParser', 'EnhancedPDFParser', 'ChartTablePDFParser', 'StructuredDOCXParser', 'PaddleOCRVLPDFParser']
except ImportError:
    __all__ = ['StructuredPDFParser', 'EnhancedPDFParser', 'ChartTablePDFParser', 'StructuredDOCXParser']