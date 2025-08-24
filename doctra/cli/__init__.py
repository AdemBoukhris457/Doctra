"""
Doctra CLI module

This module provides command-line interface functionality for the Doctra library.
It exposes the main CLI entry point and related utilities for document processing,
chart/table extraction, layout visualization, and document analysis.
"""

from .main import cli

__all__ = ['cli']
__version__ = '1.0.0'

# Command descriptions for help documentation
COMMANDS = {
    'parse': 'Full document processing with text, tables, charts, and figures',
    'extract': 'Extract charts and/or tables from PDF documents',
    'visualize': 'Visualize layout detection results',
    'analyze': 'Quick document analysis without processing',
    'info': 'Show system information and dependencies'
}

EXTRACT_SUBCOMMANDS = {
    'charts': 'Extract only charts from the document',
    'tables': 'Extract only tables from the document',
    'both': 'Extract both charts and tables'
}