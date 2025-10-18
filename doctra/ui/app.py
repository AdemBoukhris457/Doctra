"""
Main Doctra Gradio Application

This module serves as the main entry point for the Doctra Gradio interface.
It imports and composes the modular UI components for a clean, maintainable structure.

The application is organized into the following modules:
- ui_helpers.py: Shared utilities, constants, and helper functions
- full_parse_ui.py: Full PDF parsing functionality with page navigation
- tables_charts_ui.py: Table and chart extraction with VLM integration
- docres_ui.py: Image restoration functionality with before/after comparison
- enhanced_parser_ui.py: Enhanced PDF parsing with DocRes image restoration

Each module is self-contained with its own state management and event handlers,
making the codebase easier to navigate, test, and extend.
"""

import gradio as gr

from doctra.ui.ui_helpers import THEME, CUSTOM_CSS, create_tips_markdown
from doctra.ui.full_parse_ui import create_full_parse_tab
from doctra.ui.tables_charts_ui import create_tables_charts_tab
from doctra.ui.docres_ui import create_docres_tab
from doctra.ui.enhanced_parser_ui import create_enhanced_parser_tab
from doctra.ui.docx_parser_ui import create_docx_parser_tab


def build_demo() -> gr.Blocks:
    """
    Build the main Doctra Gradio interface using modular components.
    
    Returns:
        Configured Gradio Blocks interface
    """
    with gr.Blocks(title="Doctra - Document Parser", theme=THEME, css=CUSTOM_CSS) as demo:
        # Header section
        gr.Markdown(
            """
<div class="header">
  <h2 style="margin:0">Doctra — Document Parser</h2>
  <div class="subtitle">Parse PDFs, extract tables/charts, preview markdown, and download outputs.</div>
</div>
            """
        )
        
        # Create modular tabs
        full_parse_tab, full_parse_state = create_full_parse_tab()
        docx_parser_tab, docx_parser_state = create_docx_parser_tab()
        tables_charts_tab, tables_charts_state = create_tables_charts_tab()
        docres_tab, docres_state = create_docres_tab()
        enhanced_parser_tab, enhanced_parser_state = create_enhanced_parser_tab()

        # Tips section
        gr.Markdown(create_tips_markdown())

    return demo


def launch_ui():
    """
    Launch the Doctra Gradio interface.
    
    This function creates and launches the main application interface.
    """
    demo = build_demo()
    demo.launch()
