"""
Tables & Charts Parser UI Module

This module contains all functionality for the Tables & Charts extraction tab in the Doctra Gradio interface.
It handles table and chart extraction, VLM integration, and structured data display.
"""

import json
import tempfile
from pathlib import Path
from typing import Tuple, List, Optional

import gradio as gr
import pandas as pd
import html as _html

from doctra.parsers.table_chart_extractor import ChartTablePDFParser
from doctra.ui.ui_helpers import gather_outputs, validate_vlm_config


def run_extract(
    pdf_file: str,
    target: str,
    use_vlm: bool,
    vlm_provider: str,
    vlm_api_key: str,
    layout_model_name: str,
    dpi: int,
    min_score: float,
) -> Tuple[str, str, List[tuple[str, str]], List[str], str]:
    """
    Run table/chart extraction from PDF.
    
    Args:
        pdf_file: Path to input PDF file
        target: Extraction target ("tables", "charts", or "both")
        use_vlm: Whether to use Vision Language Model
        vlm_provider: VLM provider name
        vlm_api_key: API key for VLM provider
        layout_model_name: Layout detection model name
        dpi: DPI for image processing
        min_score: Minimum confidence score for layout detection
        
    Returns:
        Tuple of (status_message, tables_html, gallery_items, file_paths, zip_path)
    """
    if not pdf_file:
        return ("No file provided.", "", [], [], "")
    
    # Validate VLM configuration
    vlm_error = validate_vlm_config(use_vlm, vlm_api_key)
    if vlm_error:
        return (vlm_error, "", [], [], "")

    # Extract filename from the uploaded file path
    original_filename = Path(pdf_file).stem
    
    # Create temporary directory for processing
    tmp_dir = Path(tempfile.mkdtemp(prefix="doctra_"))
    input_pdf = tmp_dir / f"{original_filename}.pdf"
    import shutil
    shutil.copy2(pdf_file, input_pdf)

    # Initialize parser with configuration
    parser = ChartTablePDFParser(
        extract_charts=(target in ("charts", "both")),
        extract_tables=(target in ("tables", "both")),
        use_vlm=use_vlm,
        vlm_provider=vlm_provider,
        vlm_api_key=vlm_api_key or None,
        layout_model_name=layout_model_name,
        dpi=int(dpi),
        min_score=float(min_score),
    )

    # Run extraction
    output_base = Path("outputs")
    parser.parse(str(input_pdf), str(output_base))

    # Find output directory
    outputs_root = output_base
    out_dir = outputs_root / original_filename / "structured_parsing"
    if not out_dir.exists():
        if outputs_root.exists():
            candidates = sorted(outputs_root.glob("*/"), key=lambda p: p.stat().st_mtime, reverse=True)
            if candidates:
                out_dir = candidates[0] / "structured_parsing"
            else:
                out_dir = outputs_root
        else:
            outputs_root.mkdir(parents=True, exist_ok=True)
            out_dir = outputs_root

    # Determine which kinds to include in outputs based on target selection
    allowed_kinds: Optional[List[str]] = None
    if target in ("tables", "charts"):
        allowed_kinds = [target]
    elif target == "both":
        allowed_kinds = ["tables", "charts"]

    # Gather output files and create ZIP
    gallery_items, file_paths, zip_path = gather_outputs(
        out_dir, 
        allowed_kinds, 
        zip_filename=original_filename, 
        is_structured_parsing=True
    )

    # Build tables HTML preview from Excel data (when VLM enabled)
    tables_html = ""
    try:
        if use_vlm:
            # Find Excel file based on target
            excel_filename = None
            if target in ("tables", "charts"):
                if target == "tables":
                    excel_filename = "parsed_tables.xlsx"
                else:  # charts
                    excel_filename = "parsed_charts.xlsx"
            elif target == "both":
                excel_filename = "parsed_tables_charts.xlsx"
            
            if excel_filename:
                excel_path = out_dir / excel_filename
                if excel_path.exists():
                    # Read Excel file and create HTML tables
                    xl_file = pd.ExcelFile(excel_path)
                    html_blocks = []
                    
                    for sheet_name in xl_file.sheet_names:
                        df = pd.read_excel(excel_path, sheet_name=sheet_name)
                        if not df.empty:
                            # Create table with title
                            title = f"<h3>{_html.escape(sheet_name)}</h3>"
                            
                            # Convert DataFrame to HTML table
                            table_html = df.to_html(
                                classes="doc-table",
                                table_id=None,
                                escape=True,
                                index=False,
                                na_rep=""
                            )
                            
                            html_blocks.append(title + table_html)
                    
                    tables_html = "\n".join(html_blocks)
    except Exception as e:
        # Safely encode error message to handle Unicode characters
        try:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            print(f"Error building tables HTML: {error_msg}")
        except Exception:
            print(f"Error building tables HTML: <Unicode encoding error>")
        tables_html = ""

    return (
        f"✅ Parsing completed successfully!\n📁 Output directory: {out_dir}", 
        tables_html, 
        file_paths, 
        zip_path
    )


def capture_out_dir(status_text: str) -> str:
    """
    Capture output directory from status text.
    
    Args:
        status_text: Status message containing output directory path
        
    Returns:
        Output directory path string
    """
    if not status_text:
        return ""
    try:
        if "Output directory:" in status_text:
            return status_text.split("Output directory:", 1)[1].strip()
    except Exception:
        pass
    return ""


def build_item_selector(out_dir_path: str, target: str, use_vlm: bool) -> gr.Dropdown:
    """
    Build item selector dropdown based on VLM output data.
    
    Args:
        out_dir_path: Path to output directory
        target: Extraction target type
        use_vlm: Whether VLM was used
        
    Returns:
        Updated dropdown component
    """
    if not out_dir_path or not use_vlm:
        return gr.Dropdown(choices=[], value=None, visible=False)
    
    try:
        out_dir = Path(out_dir_path)
        mapping = out_dir / "vlm_items.json"
        if not mapping.exists():
            return gr.Dropdown(choices=[], value=None, visible=False)
        
        data = json.loads(mapping.read_text(encoding="utf-8"))
        choices = []
        
        for entry in data:
            kind = entry.get("kind")
            # Filter based on target
            if target == "both" or (target == "tables" and kind == "table") or (target == "charts" and kind == "chart"):
                title = entry.get("title") or f"{kind.title()}"
                page = entry.get("page")
                rel_path = entry.get("image_rel_path")
                label = f"{title} — Page {page}"
                choices.append((label, rel_path))
        
        return gr.Dropdown(choices=choices, value=choices[0][1] if choices else None, visible=bool(choices))
    except Exception:
        return gr.Dropdown(choices=[], value=None, visible=False)


def show_selected_item(rel_path: str, out_dir_path: str) -> Tuple[str, Optional[str]]:
    """
    Show selected item data and image.
    
    Args:
        rel_path: Relative path to the item image
        out_dir_path: Path to output directory
        
    Returns:
        Tuple of (html_table, image_path)
    """
    if not rel_path or not out_dir_path:
        return "", None
    
    try:
        out_dir = Path(out_dir_path)
        mapping = out_dir / "vlm_items.json"
        if not mapping.exists():
            return "", None
        
        data = json.loads(mapping.read_text(encoding="utf-8"))
        
        for entry in data:
            if entry.get("image_rel_path") == rel_path:
                headers = entry.get("headers") or []
                rows = entry.get("rows") or []
                title = entry.get("title") or "Data"
                kind = entry.get("kind", "table")
                
                # Create HTML table
                if headers and rows:
                    thead = '<thead><tr>' + ''.join(f'<th>{_html.escape(str(h))}</th>' for h in headers) + '</tr></thead>'
                    tbody = '<tbody>' + ''.join('<tr>' + ''.join(f'<td>{_html.escape(str(c))}</td>' for c in r) + '</tr>' for r in rows) + '</tbody>'
                    html_table = f'<h3>{_html.escape(title)} ({kind.title()})</h3><table class="doc-table">{thead}{tbody}</table>'
                else:
                    html_table = f'<h3>{_html.escape(title)} ({kind.title()})</h3><p>No structured data available</p>'
                
                # Get image path
                img_abs = str((out_dir / rel_path).resolve())
                return html_table, img_abs
        
        return "", None
    except Exception:
        return "", None


def update_content_visibility(use_vlm: bool) -> Tuple[gr.Column, gr.Column]:
    """
    Update content visibility based on VLM usage.
    
    Args:
        use_vlm: Whether VLM is being used
        
    Returns:
        Tuple of (vlm_content, non_vlm_content)
    """
    if use_vlm:
        # Show VLM content (data + selected image)
        return gr.Column(visible=True), gr.Column(visible=False)
    else:
        # Show non-VLM content (scrollable gallery)
        return gr.Column(visible=False), gr.Column(visible=True)


def populate_scrollable_gallery(file_paths: List[str], target: str) -> List[tuple[str, str]]:
    """
    Populate the scrollable gallery with image files from the extraction results, filtered by target.
    
    Args:
        file_paths: List of file paths from extraction
        target: Extraction target ("tables", "charts", or "both")
        
    Returns:
        List of (image_path, caption) tuples for image files
    """
    gallery_items = []
    for file_path in file_paths:
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            # Filter based on target
            filename = Path(file_path).name.lower()
            should_include = False
            
            if target == "both":
                # Include all images
                should_include = True
            elif target == "tables":
                # Include only table images
                if "table" in filename or "tables" in filename:
                    should_include = True
            elif target == "charts":
                # Include only chart images
                if "chart" in filename or "charts" in filename:
                    should_include = True
            
            if should_include:
                gallery_items.append((file_path, Path(file_path).name))
    
    return gallery_items


def create_tables_charts_tab() -> Tuple[gr.Tab, dict]:
    """
    Create the Tables & Charts extraction tab with all its components and functionality.
    
    Returns:
        Tuple of (tab_component, state_variables_dict)
    """
    with gr.Tab("Extract Tables/Charts") as tab:
        # Input controls
        with gr.Row():
            pdf_e = gr.File(file_types=[".pdf"], label="PDF")
            target = gr.Dropdown(["tables", "charts", "both"], value="both", label="Target")
            use_vlm_e = gr.Checkbox(label="Use VLM (optional)", value=False)
            vlm_provider_e = gr.Dropdown(["gemini", "openai", "anthropic", "openrouter"], value="gemini", label="VLM Provider")
            vlm_api_key_e = gr.Textbox(type="password", label="VLM API Key", placeholder="Optional if VLM disabled")
        
        # Advanced settings accordion
        with gr.Accordion("Advanced", open=False):
            with gr.Row():
                layout_model_e = gr.Textbox(value="PP-DocLayout_plus-L", label="Layout model")
                dpi_e = gr.Slider(100, 400, value=200, step=10, label="DPI")
                min_score_e = gr.Slider(0, 1, value=0.0, step=0.05, label="Min layout score")

        # Action button
        run_btn_e = gr.Button("▶ Run Extraction", variant="primary")
        status_e = gr.Textbox(label="Status")
        
        # Item selector for VLM outputs
        item_selector_e = gr.Dropdown(label="Select Item", visible=False, interactive=True)
        
        # Content display - different layout based on VLM usage
        with gr.Row():
            # VLM mode: show data and selected image side by side
            with gr.Column(visible=True) as vlm_content:
                tables_preview_e = gr.HTML(label="Extracted Data", elem_classes=["page-content"])
                image_e = gr.Image(label="Selected Image", interactive=False)
            
            # Non-VLM mode: show scrollable gallery of extracted images
            with gr.Column(visible=False) as non_vlm_content:
                scrollable_gallery_e = gr.Gallery(
                    label="Extracted Images", 
                    columns=2, 
                    height=600, 
                    preview=True,
                    show_label=True,
                    elem_classes=["scrollable-gallery"]
                )
        
        # Downloads
        files_out_e = gr.Files(label="Download individual output files")
        zip_out_e = gr.File(label="Download all outputs (ZIP)")

        # State variable for output directory
        out_dir_state = gr.State("")

        # Event handlers
        run_btn_e.click(
            fn=lambda f, t, a, b, c, d, e, g: run_extract(
                f.name if f else "",
                t,
                a,
                b,
                c,
                d,
                e,
                g,
            ),
            inputs=[pdf_e, target, use_vlm_e, vlm_provider_e, vlm_api_key_e, layout_model_e, dpi_e, min_score_e],
            outputs=[status_e, tables_preview_e, files_out_e, zip_out_e],
        ).then(
            fn=capture_out_dir,
            inputs=[status_e],
            outputs=[out_dir_state]
        ).then(
            fn=build_item_selector,
            inputs=[out_dir_state, target, use_vlm_e],
            outputs=[item_selector_e]
        ).then(
            fn=show_selected_item,
            inputs=[item_selector_e, out_dir_state],
            outputs=[tables_preview_e, image_e]
        ).then(
            fn=update_content_visibility,
            inputs=[use_vlm_e],
            outputs=[vlm_content, non_vlm_content]
        ).then(
            fn=populate_scrollable_gallery,
            inputs=[files_out_e, target],
            outputs=[scrollable_gallery_e]
        )
        
        # Handle dropdown selection changes
        item_selector_e.change(
            fn=show_selected_item,
            inputs=[item_selector_e, out_dir_state],
            outputs=[tables_preview_e, image_e]
        )

    # Return state variables for external access
    state_vars = {
        'pdf_e': pdf_e,
        'target': target,
        'use_vlm_e': use_vlm_e,
        'vlm_provider_e': vlm_provider_e,
        'vlm_api_key_e': vlm_api_key_e,
        'layout_model_e': layout_model_e,
        'dpi_e': dpi_e,
        'min_score_e': min_score_e,
        'run_btn_e': run_btn_e,
        'status_e': status_e,
        'item_selector_e': item_selector_e,
        'tables_preview_e': tables_preview_e,
        'image_e': image_e,
        'files_out_e': files_out_e,
        'zip_out_e': zip_out_e,
        'out_dir_state': out_dir_state,
        'vlm_content': vlm_content,
        'non_vlm_content': non_vlm_content,
        'scrollable_gallery_e': scrollable_gallery_e
    }

    return tab, state_vars
