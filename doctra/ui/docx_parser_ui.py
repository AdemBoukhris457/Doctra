"""
DOCX Parser UI Module

This module contains all functionality for the DOCX Parser tab in the Doctra Gradio interface.
It handles DOCX parsing, content extraction, and structured data display.
"""

import tempfile
import traceback
from pathlib import Path
from typing import Tuple, List, Optional

import gradio as gr

from doctra.parsers.structured_docx_parser import StructuredDOCXParser
from doctra.ui.ui_helpers import gather_outputs, validate_vlm_config


def process_docx_wrapper(
    file_path, use_vlm, vlm_provider, vlm_api_key,
    extract_images, preserve_formatting, table_detection, export_excel
):
    """Wrapper function for DOCX processing."""
    if not file_path:
        return "Please upload a DOCX file first.", None, [], ""
    
    return run_docx_parse(
        file_path, use_vlm, vlm_provider, vlm_api_key,
        extract_images, preserve_formatting, table_detection, export_excel
    )


def toggle_vlm_options_wrapper(use_vlm):
    """Wrapper function for toggling VLM options."""
    return gr.update(visible=use_vlm)


def run_docx_parse(
    docx_file: str,
    use_vlm: bool,
    vlm_provider: str,
    vlm_api_key: str,
    extract_images: bool,
    preserve_formatting: bool,
    table_detection: bool,
    export_excel: bool,
) -> Tuple[str, Optional[str], List[str], str]:
    """
    Run DOCX parsing with structured output.
    
    Args:
        docx_file: Path to input DOCX file
        use_vlm: Whether to use Vision Language Model
        vlm_provider: VLM provider name
        vlm_api_key: API key for VLM provider
        extract_images: Whether to extract embedded images
        preserve_formatting: Whether to preserve text formatting
        table_detection: Whether to detect and extract tables
        export_excel: Whether to export tables to Excel file
        
    Returns:
        Tuple of (status_message, markdown_preview, file_paths, zip_path)
    """
    if not docx_file:
        return ("No file provided.", None, [], "")

    # Validate VLM configuration
    vlm_error = validate_vlm_config(use_vlm, vlm_api_key, vlm_provider)
    if vlm_error:
        return (vlm_error, None, [], "")

    # Extract filename from the uploaded file path
    original_filename = Path(docx_file).stem
    
    # Create temporary directory for processing
    tmp_dir = Path(tempfile.mkdtemp(prefix="doctra_docx_"))
    input_docx = tmp_dir / f"{original_filename}.docx"
    import shutil
    shutil.copy2(docx_file, input_docx)

    # Initialize parser with configuration
    parser = StructuredDOCXParser(
        use_vlm=use_vlm,
        vlm_provider=vlm_provider,
        vlm_api_key=vlm_api_key,
        extract_images=extract_images,
        preserve_formatting=preserve_formatting,
        table_detection=table_detection,
        export_excel=export_excel
    )

    try:
        # Parse the document
        parser.parse(str(input_docx))
        
        # Gather outputs
        output_dir = Path(f"outputs/{original_filename}")
        file_paths, zip_path = gather_outputs(output_dir)
        
        # Read markdown content for preview
        markdown_file = output_dir / "document.md"
        markdown_preview = None
        if markdown_file.exists():
            with open(markdown_file, 'r', encoding='utf-8') as f:
                markdown_preview = f.read()
        
        status_message = f"✅ DOCX parsing completed successfully!\n"
        status_message += f"📊 Extracted content from: {original_filename}.docx\n"
        status_message += f"📁 Output directory: {output_dir.absolute()}\n"
        status_message += f"📄 Generated {len(file_paths)} output files"
        
        return (status_message, markdown_preview, file_paths, zip_path)
        
    except Exception as e:
        error_msg = f"❌ Error during DOCX parsing: {str(e)}"
        if "python-docx" in str(e).lower():
            error_msg += "\n\nMake sure python-docx is installed: pip install python-docx"
        return (error_msg, None, [], "")


def create_docx_parser_interface() -> gr.Blocks:
    """
    Create the DOCX Parser interface.
    
    Returns:
        Gradio Blocks interface for DOCX parsing
    """
    with gr.Blocks(title="DOCX Parser - Doctra", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 📄 DOCX Parser")
        gr.Markdown("Parse Microsoft Word documents to extract text, tables, images, and structured content.")
        
        with gr.Row():
            with gr.Column(scale=1):
                # File input
                docx_file = gr.File(
                    label="📁 Upload DOCX File",
                    file_types=[".docx"],
                    type="filepath"
                )
                
                # VLM Configuration
                gr.Markdown("### 🤖 VLM Configuration")
                use_vlm = gr.Checkbox(
                    label="Use Vision Language Model",
                    value=False,
                    info="Enable VLM for enhanced content analysis"
                )
                
                vlm_provider = gr.Dropdown(
                    choices=["gemini", "openai", "anthropic", "openrouter"],
                    value="gemini",
                    label="VLM Provider",
                    visible=True
                )
                
                vlm_api_key = gr.Textbox(
                    label="VLM API Key",
                    type="password",
                    placeholder="Enter your API key or set VLM_API_KEY environment variable",
                    info="Required if VLM is enabled"
                )
                
                # Processing Options
                gr.Markdown("### ⚙️ Processing Options")
                extract_images = gr.Checkbox(
                    label="Extract Images",
                    value=True,
                    info="Extract embedded images from the document"
                )
                
                preserve_formatting = gr.Checkbox(
                    label="Preserve Formatting",
                    value=True,
                    info="Maintain text formatting (bold, italic, etc.) in output"
                )
                
                table_detection = gr.Checkbox(
                    label="Table Detection",
                    value=True,
                    info="Detect and extract tables from the document"
                )
                
                export_excel = gr.Checkbox(
                    label="Export to Excel",
                    value=True,
                    info="Export tables to Excel file"
                )
                
                # Process button
                process_btn = gr.Button(
                    "🚀 Parse DOCX",
                    variant="primary",
                    size="lg"
                )
            
            with gr.Column(scale=2):
                # Status output
                status_output = gr.Textbox(
                    label="📊 Status",
                    lines=4,
                    interactive=False,
                    show_copy_button=True
                )
                
                # Markdown preview
                markdown_preview = gr.Markdown(
                    label="📄 Document Preview",
                    value="Upload a DOCX file and click 'Parse DOCX' to see the preview here."
                )
                
                # File outputs
                with gr.Row():
                    output_files = gr.File(
                        label="📁 Output Files",
                        file_count="multiple",
                        interactive=False
                    )
                    
                    download_zip = gr.File(
                        label="📦 Download All",
                        interactive=False
                    )
        
        # Event handlers
        process_btn.click(
            fn=process_docx_wrapper,
            inputs=[
                docx_file, use_vlm, vlm_provider, vlm_api_key,
                extract_images, preserve_formatting, table_detection, export_excel
            ],
            outputs=[status_output, markdown_preview, output_files, download_zip]
        )
        
        # Show/hide VLM options based on checkbox
        
        use_vlm.change(
            fn=toggle_vlm_options_wrapper,
            inputs=[use_vlm],
            outputs=[vlm_provider]
        )
        
        # Examples
        gr.Markdown("### 📚 Examples")
        gr.Markdown("""
        **Basic DOCX Parsing:**
        - Upload a DOCX file
        - Click "Parse DOCX" to extract content
        
        **With VLM Enhancement:**
        - Enable "Use Vision Language Model"
        - Select your VLM provider
        - Enter your API key
        - Parse for enhanced content analysis
        
        **Custom Options:**
        - Toggle image extraction on/off
        - Enable/disable formatting preservation
        - Control table detection settings
        """)
        
        # Tips
        gr.Markdown("### 💡 Tips")
        gr.Markdown("""
        - **Large files:** Processing may take longer for documents with many images
        - **VLM usage:** Requires API key and may incur costs
        - **Output formats:** Results include Markdown, HTML, and structured data
        - **Images:** Extracted images are saved in the output directory
        """)
    
    return interface


def create_docx_parser_tab() -> Tuple[gr.Tab, dict]:
    """
    Create the DOCX Parser tab with all its components and functionality.
    
    Returns:
        Tuple of (tab_component, state_variables_dict)
    """
    with gr.Tab("📄 DOCX Parser") as tab:
        # Input controls
        with gr.Row():
            docx_file = gr.File(file_types=[".docx"], label="DOCX File")
            use_vlm = gr.Checkbox(label="Use VLM (optional)", value=False)
            vlm_provider = gr.Dropdown(["gemini", "openai", "anthropic", "openrouter"], value="gemini", label="VLM Provider")
            vlm_api_key = gr.Textbox(type="password", label="VLM API Key", placeholder="Optional if VLM disabled")

        # Processing options
        with gr.Accordion("Processing Options", open=False):
            with gr.Row():
                extract_images = gr.Checkbox(label="Extract Images", value=True)
                preserve_formatting = gr.Checkbox(label="Preserve Formatting", value=True)
                table_detection = gr.Checkbox(label="Table Detection", value=True)
                export_excel = gr.Checkbox(label="Export to Excel", value=True)

        # Process button
        process_btn = gr.Button("🚀 Parse DOCX", variant="primary", size="lg")

        # Outputs
        with gr.Row():
            with gr.Column(scale=1):
                status_output = gr.Textbox(label="Status", lines=4, interactive=False, show_copy_button=True)
                output_files = gr.File(label="Output Files", file_count="multiple", interactive=False)
                download_zip = gr.File(label="Download All", interactive=False)
            
            with gr.Column(scale=2):
                markdown_preview = gr.Markdown(
                    label="Document Preview",
                    value="Upload a DOCX file and click 'Parse DOCX' to see the preview here."
                )

        # Event handlers
        process_btn.click(
            fn=process_docx_wrapper,
            inputs=[
                docx_file, use_vlm, vlm_provider, vlm_api_key,
                extract_images, preserve_formatting, table_detection, export_excel
            ],
            outputs=[status_output, markdown_preview, output_files, download_zip]
        )

        # Show/hide VLM options based on checkbox
        
        use_vlm.change(
            fn=toggle_vlm_options_wrapper,
            inputs=[use_vlm],
            outputs=[vlm_provider]
        )

    # State variables (empty for now, but following the pattern)
    state_variables = {}
    
    return tab, state_variables


if __name__ == "__main__":
    # For testing the interface standalone
    interface = create_docx_parser_interface()
    interface.launch(server_name="0.0.0.0", server_port=7860)
