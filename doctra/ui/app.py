import os
import shutil
import tempfile
import re
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

import gradio as gr

from doctra.parsers.structured_pdf_parser import StructuredPDFParser
from doctra.parsers.table_chart_extractor import ChartTablePDFParser


def _gather_outputs(out_dir: Path, allowed_kinds: Optional[List[str]] = None, zip_filename: Optional[str] = None, is_structured_parsing: bool = False) -> Tuple[List[tuple[str, str]], List[str], str]:
    gallery_items: List[tuple[str, str]] = []
    file_paths: List[str] = []

    if out_dir.exists():
        if is_structured_parsing:
            # For structured parsing, show ALL files in the directory
            for file_path in sorted(out_dir.rglob("*")):
                if file_path.is_file():
                    file_paths.append(str(file_path))
        else:
            # For full parsing, use the original logic
            # Always add main output files (HTML, Markdown, etc.) regardless of allowed_kinds
            main_files = [
                "result.html",
                "result.md", 
                "tables.html",
                "tables.xlsx"
            ]
            
            for main_file in main_files:
                file_path = out_dir / main_file
                if file_path.exists():
                    file_paths.append(str(file_path))
            
            # Add image files based on allowed_kinds or all images if not specified
            if allowed_kinds:
                for kind in allowed_kinds:
                    # ChartTablePDFParser saves directly to charts/ and tables/ directories
                    p = out_dir / kind
                    if p.exists():
                        for img in sorted(p.glob("*.png")):  # ChartTablePDFParser saves as .png
                            file_paths.append(str(img))
                    
                    # Also check images/ subdirectories (for StructuredPDFParser)
                    images_dir = out_dir / "images" / kind
                    if images_dir.exists():
                        for img in sorted(images_dir.glob("*.jpg")):  # StructuredPDFParser saves as .jpg
                            file_paths.append(str(img))
            else:
                # Fallback: look in both direct directories and images/ subdirectories
                for p in (out_dir / "charts").glob("*.png"):
                    file_paths.append(str(p))
                for p in (out_dir / "tables").glob("*.png"):
                    file_paths.append(str(p))
                for p in (out_dir / "images").rglob("*.jpg"):
                    file_paths.append(str(p))

            # Add Excel files based on extraction target (for structured parsing)
            if allowed_kinds:
                if "charts" in allowed_kinds and "tables" in allowed_kinds:
                    excel_files = ["parsed_tables_charts.xlsx"]
                elif "charts" in allowed_kinds:
                    excel_files = ["parsed_charts.xlsx"]
                elif "tables" in allowed_kinds:
                    excel_files = ["parsed_tables.xlsx"]
                else:
                    excel_files = []
                
                for excel_file in excel_files:
                    excel_path = out_dir / excel_file
                    if excel_path.exists():
                        file_paths.append(str(excel_path))

    kinds = allowed_kinds if allowed_kinds else ["tables", "charts", "figures"]
    for sub in kinds:
        # Look in both direct directories and images/ subdirectories
        # First try direct directories (for ChartTablePDFParser)
        p = out_dir / sub
        if p.exists():
            for img in sorted(p.glob("*.png")):  # ChartTablePDFParser saves as .png
                gallery_items.append((str(img), f"{sub}: {img.name}"))
        
        # Also try images/ subdirectories (for StructuredPDFParser)
        images_dir = out_dir / "images" / sub
        if images_dir.exists():
            for img in sorted(images_dir.glob("*.jpg")):  # StructuredPDFParser saves as .jpg
                gallery_items.append((str(img), f"{sub}: {img.name}"))

    tmp_zip_dir = Path(tempfile.mkdtemp(prefix="doctra_zip_"))
    
    # Use custom filename if provided, otherwise use default
    if zip_filename:
        # Clean the filename to be safe for file systems
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', zip_filename)
        zip_base = tmp_zip_dir / safe_filename
    else:
        zip_base = tmp_zip_dir / "doctra_outputs"
    
    # Create a filtered copy of the output directory excluding temp files
    filtered_dir = tmp_zip_dir / "filtered_outputs"
    shutil.copytree(out_dir, filtered_dir, ignore=shutil.ignore_patterns('~$*', '*.tmp', '*.temp'))
    
    zip_path = shutil.make_archive(str(zip_base), 'zip', root_dir=str(filtered_dir))

    return gallery_items, file_paths, zip_path


def _parse_markdown_by_pages(md_content: str) -> List[Dict[str, Any]]:
    """
    Parse markdown content and organize it by pages.
    Returns a list of page dictionaries with content, tables, charts, and figures.
    """
    import re
    
    pages = []
    current_page = None
    
    lines = md_content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for page header
        if line.startswith('## Page '):
            # Save previous page if exists
            if current_page:
                pages.append(current_page)
            
            # Start new page
            page_num = line.replace('## Page ', '').strip()
            current_page = {
                'page_num': page_num,
                'content': [],
                'tables': [],
                'charts': [],
                'figures': [],
                'images': [],
                'full_content': []  # Store full content with inline images
            }
            i += 1
            continue
        
        # Check for images (tables, charts, figures)
        if line.startswith('![') and '](images/' in line:
            # Extract image info
            match = re.match(r'!\[([^\]]+)\]\(([^)]+)\)', line)
            if match:
                caption = match.group(1)
                img_path = match.group(2)
                
                # Categorize by type
                if 'Table' in caption:
                    current_page['tables'].append({'caption': caption, 'path': img_path})
                elif 'Chart' in caption:
                    current_page['charts'].append({'caption': caption, 'path': img_path})
                elif 'Figure' in caption:
                    current_page['figures'].append({'caption': caption, 'path': img_path})
                
                current_page['images'].append({'caption': caption, 'path': img_path})
                
                # Add to full content with proper markdown formatting
                current_page['full_content'].append(f"![{caption}]({img_path})")
        
        # Regular content
        elif current_page:
            if line:  # Only add non-empty lines
                current_page['content'].append(line)
            current_page['full_content'].append(line)
        
        i += 1
    
    # Add the last page
    if current_page:
        pages.append(current_page)
    
    return pages


def run_full_parse(
    pdf_file: str,
    use_vlm: bool,
    vlm_provider: str,
    vlm_api_key: str,
    layout_model_name: str,
    dpi: int,
    min_score: float,
    ocr_lang: str,
    ocr_psm: int,
    ocr_oem: int,
    ocr_extra_config: str,
    box_separator: str,
) -> Tuple[str, Optional[str], List[tuple[str, str]], List[str], str]:
    if not pdf_file:
        return ("No file provided.", None, [], [], "")

    # Extract filename from the uploaded file path
    # Gradio provides the original filename in the file path
    original_filename = Path(pdf_file).stem
    
    tmp_dir = Path(tempfile.mkdtemp(prefix="doctra_"))
    # Use original filename for temp file so parser creates correct output directory
    input_pdf = tmp_dir / f"{original_filename}.pdf"
    shutil.copy2(pdf_file, input_pdf)

    # Validate VLM configuration
    if use_vlm and not vlm_api_key:
        return ("❌ Error: VLM API key is required when using VLM", None, [], [], "")
    
    if use_vlm and vlm_api_key:
        # Basic API key validation
        if len(vlm_api_key.strip()) < 10:
            return ("❌ Error: VLM API key appears to be too short or invalid", None, [], [], "")
        if vlm_api_key.strip().startswith('sk-') and len(vlm_api_key.strip()) < 20:
            return ("❌ Error: OpenAI API key appears to be invalid (too short)", None, [], [], "")

    parser = StructuredPDFParser(
        use_vlm=use_vlm,
        vlm_provider=vlm_provider,
        vlm_api_key=vlm_api_key or None,
        layout_model_name=layout_model_name,
        dpi=int(dpi),
        min_score=float(min_score),
        ocr_lang=ocr_lang,
        ocr_psm=int(ocr_psm),
        ocr_oem=int(ocr_oem),
        ocr_extra_config=ocr_extra_config or "",
        box_separator=box_separator or "\n",
    )

    try:
        print(f"DEBUG: Starting VLM processing with provider: {vlm_provider}, use_vlm: {use_vlm}")
        parser.parse(str(input_pdf))
        print("DEBUG: VLM processing completed successfully")
    except Exception as e:
        # Safely encode error message to handle Unicode characters
        try:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            print(f"ERROR: VLM processing failed: {error_msg}")
        except Exception:
            print(f"ERROR: VLM processing failed: <Unicode encoding error>")
        import traceback
        traceback.print_exc()
        # Safely encode error message for return value
        try:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            return (f"❌ VLM processing failed: {error_msg}", None, [], [], "")
        except Exception:
            return (f"❌ VLM processing failed: <Unicode encoding error>", None, [], [], "")

    outputs_root = Path("outputs")
    out_dir = outputs_root / original_filename / "full_parse"
    if not out_dir.exists():
        # fallback: search latest created dir under outputs
        candidates = sorted(outputs_root.glob("*/"), key=lambda p: p.stat().st_mtime, reverse=True)
        if candidates:
            out_dir = candidates[0] / "full_parse"
        else:
            out_dir = outputs_root

    md_file = next(out_dir.glob("*.md"), None)
    md_preview = None
    if md_file and md_file.exists():
        try:
            with md_file.open("r", encoding="utf-8", errors="ignore") as f:
                md_preview = f.read()  # Return the full markdown content
        except Exception:
            md_preview = None

    gallery_items, file_paths, zip_path = _gather_outputs(out_dir, zip_filename=original_filename, is_structured_parsing=False)
    return (f"Completed. Results in: {out_dir}", md_preview, gallery_items, file_paths, zip_path)


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
    if not pdf_file:
        return ("No file provided.", "", [], [], "")
    
    # Validate VLM configuration
    if use_vlm and not vlm_api_key:
        return ("❌ Error: VLM API key is required when using VLM", "", [], [], "")
    
    if use_vlm and vlm_api_key:
        # Basic API key validation
        if len(vlm_api_key.strip()) < 10:
            return ("❌ Error: VLM API key appears to be too short or invalid", "", [], [], "")
        if vlm_api_key.strip().startswith('sk-') and len(vlm_api_key.strip()) < 20:
            return ("❌ Error: OpenAI API key appears to be invalid (too short)", "", [], [], "")

    # Extract filename from the uploaded file path
    original_filename = Path(pdf_file).stem
    
    tmp_dir = Path(tempfile.mkdtemp(prefix="doctra_"))
    # Use original filename for temp file so parser creates correct output directory
    input_pdf = tmp_dir / f"{original_filename}.pdf"
    shutil.copy2(pdf_file, input_pdf)

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

    output_base = Path("outputs")
    parser.parse(str(input_pdf), str(output_base))

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

    gallery_items, file_paths, zip_path = _gather_outputs(out_dir, allowed_kinds, zip_filename=original_filename, is_structured_parsing=True)

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
                    import pandas as pd
                    import html as _html
                    
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

    return (f"Completed. Results in: {out_dir}", tables_html, gallery_items, file_paths, zip_path)


THEME = gr.themes.Soft(primary_hue="indigo", neutral_hue="slate")

CUSTOM_CSS = """
.gradio-container {max-width: 100% !important; padding-left: 24px; padding-right: 24px}
.container {max-width: 100% !important}
.app {max-width: 100% !important}
.header {margin-bottom: 8px}
.subtitle {color: var(--body-text-color-subdued)}
.card {border:1px solid var(--border-color); border-radius:12px; padding:8px}
.status-ok {color: var(--color-success)}

/* Page content styling */
.page-content img {
    max-width: 100% !important;
    height: auto !important;
    display: block !important;
    margin: 10px auto !important;
    border: 1px solid #ddd !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
}

.page-content {
    max-height: none !important;
    overflow: visible !important;
}

/* Table styling */
.page-content table.doc-table { 
    width: 100% !important; 
    border-collapse: collapse !important; 
    margin: 12px 0 !important; 
}
.page-content table.doc-table th,
.page-content table.doc-table td { 
    border: 1px solid #e5e7eb !important; 
    padding: 8px 10px !important; 
    text-align: left !important; 
}
.page-content table.doc-table thead th { 
    background: #f9fafb !important; 
    font-weight: 600 !important; 
}
.page-content table.doc-table tbody tr:nth-child(even) td { 
    background: #fafafa !important; 
}

/* Clickable image buttons */
.image-button {
    background: #0066cc !important;
    color: white !important;
    border: none !important;
    padding: 5px 10px !important;
    border-radius: 4px !important;
    cursor: pointer !important;
    margin: 2px !important;
    font-size: 14px !important;
}

.image-button:hover {
    background: #0052a3 !important;
}
"""


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="Doctra - Document Parser", theme=THEME, css=CUSTOM_CSS) as demo:
        gr.Markdown(
            """
<div class="header">
  <h2 style="margin:0">Doctra — Document Parser</h2>
  <div class="subtitle">Parse PDFs, extract tables/charts, preview markdown, and download outputs.</div>
</div>
            """
        )
        

        with gr.Tab("Full Parse"):
            with gr.Row():
                pdf = gr.File(file_types=[".pdf"], label="PDF")
                use_vlm = gr.Checkbox(label="Use VLM (optional)", value=False)
                vlm_provider = gr.Dropdown(["gemini", "openai", "anthropic", "openrouter"], value="gemini", label="VLM Provider")
                vlm_api_key = gr.Textbox(type="password", label="VLM API Key", placeholder="Optional if VLM disabled")

            with gr.Accordion("Advanced", open=False):
                with gr.Row():
                    layout_model = gr.Textbox(value="PP-DocLayout_plus-L", label="Layout model")
                    dpi = gr.Slider(100, 400, value=200, step=10, label="DPI")
                    min_score = gr.Slider(0, 1, value=0.0, step=0.05, label="Min layout score")
                with gr.Row():
                    ocr_lang = gr.Textbox(value="eng", label="OCR Language")
                    ocr_psm = gr.Slider(0, 13, value=4, step=1, label="Tesseract PSM")
                    ocr_oem = gr.Slider(0, 3, value=3, step=1, label="Tesseract OEM")
                with gr.Row():
                    ocr_config = gr.Textbox(value="", label="Extra OCR config")
                    box_sep = gr.Textbox(value="\n", label="Box separator")

            run_btn = gr.Button("▶ Run Full Parse", variant="primary")
            status = gr.Textbox(label="Status", elem_classes=["status-ok"])
            
            # Page selector for extracted content
            page_selector = gr.Dropdown(label="Select Page to Display", interactive=True, visible=False)
            
            # Full Parse components
            with gr.Row():
                with gr.Column():
                    md_preview = gr.HTML(label="Extracted Content", visible=True, elem_classes=["page-content"])
                with gr.Column():
                    page_image = gr.Image(label="Page image", interactive=False)
            gallery = gr.Gallery(label="Extracted images (tables/charts/figures)", columns=4, height=420, preview=True)
            files_out = gr.Files(label="Download individual output files")
            zip_out = gr.File(label="Download all outputs (ZIP)")
            
            # Hidden state to store pages data and all images
            pages_state = gr.State([])
            all_images_state = gr.State([])
            pdf_path_state = gr.State("")
            page_images_state = gr.State([])  # list of file paths per page index (1-based)
            
            # Hidden components for image filtering
            filter_trigger = gr.Button(visible=False)
            current_image_path = gr.State("")
            current_image_caption = gr.State("")
            image_filter_input = gr.Textbox(visible=False, elem_id="image_filter_input")

            def parse_markdown_by_pages(md_content: str):
                """Parse markdown content and organize it by pages."""
                import re
                
                pages = []
                current_page = None
                
                lines = md_content.split('\n')
                i = 0
                
                print(f"DEBUG: Parsing {len(lines)} lines of markdown")
                
                # First, let's find all page headers
                page_headers = []
                for i, line in enumerate(lines):
                    if line.strip().startswith('## Page '):
                        page_num = line.strip().replace('## Page ', '').strip()
                        page_headers.append((i, page_num, line))
                        print(f"DEBUG: Found page header at line {i}: {page_num}")
                
                print(f"DEBUG: Found {len(page_headers)} page headers")
                
                # Now parse content for each page
                for i, (line_idx, page_num, header_line) in enumerate(page_headers):
                    # Find the end of this page (start of next page or end of document)
                    start_line = line_idx
                    if i + 1 < len(page_headers):
                        end_line = page_headers[i + 1][0]
                    else:
                        end_line = len(lines)
                    
                    # Extract content for this page
                    page_content = lines[start_line:end_line]
                    
                    page = {
                        'page_num': page_num,
                        'content': page_content
                    }
                    pages.append(page)
                    print(f"DEBUG: Added page {page_num} with {len(page_content)} lines (lines {start_line}-{end_line-1})")
                
                print(f"DEBUG: Total pages parsed: {len(pages)}")
                return pages

            def update_page_selector(pages_data):
                """Update the page selector dropdown with available pages."""
                if not pages_data:
                    print("DEBUG: No pages data for selector")
                    return gr.Dropdown(choices=[], value=None, visible=False)
                
                page_choices = [f"Page {page['page_num']}" for page in pages_data]
                print(f"DEBUG: Page selector choices: {page_choices}")
                return gr.Dropdown(choices=page_choices, value=page_choices[0], visible=True)

            def display_selected_page(selected_page, pages_data, pdf_path, page_images):
                """Display the content of the selected page and the rendered page image."""
                if not selected_page or not pages_data:
                    return "", None
                
                print(f"DEBUG: Displaying page {selected_page}")
                print(f"DEBUG: Available pages: {[p['page_num'] for p in pages_data]}")
                
                # Find the selected page
                page_num = selected_page.replace("Page ", "")
                page = next((p for p in pages_data if p['page_num'] == page_num), None)
                
                if not page:
                    print(f"DEBUG: Page {page_num} not found")
                    return "Page not found", None
                
                print(f"DEBUG: Found page {page_num} with {len(page['content'])} lines")
                
                # Build HTML with inline base64 images, render markdown tables, and preserve paragraphs/line breaks
                import html as _html, base64, re as _re
                base_dir = None
                try:
                    stem = Path(pdf_path).stem if pdf_path else ""
                    if stem:
                        base_dir = Path("outputs") / stem / "full_parse"
                except Exception:
                    base_dir = None
                processed_content = []
                paragraph_buffer = []
                def flush_paragraph():
                    nonlocal paragraph_buffer
                    if paragraph_buffer:
                        joined = '<br/>'.join(_html.escape(l) for l in paragraph_buffer)
                        processed_content.append(f'<p>{joined}</p>')
                        paragraph_buffer = []

                # Simple markdown table detection and rendering
                def is_md_table_header(s: str) -> bool:
                    return '|' in s and ('---' in s or '—' in s)

                def render_md_table(lines: List[str]) -> str:
                    rows = [l.strip().strip('|').split('|') for l in lines]
                    rows = [[_html.escape(c.strip()) for c in r] for r in rows]
                    if len(rows) < 2:
                        return ""
                    header = rows[0]
                    body = rows[2:] if len(rows) > 2 else []
                    thead = '<thead><tr>' + ''.join(f'<th>{c}</th>' for c in header) + '</tr></thead>'
                    tbody = '<tbody>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in body) + '</tbody>'
                    return f'<table class="doc-table">{thead}{tbody}</table>'

                i = 0
                lines = page['content']
                n = len(lines)
                while i < n:
                    raw_line = lines[i]
                    line = raw_line.rstrip('\r\n')
                    stripped = line.strip()
                    if stripped.startswith('![') and ('](images/' in stripped or '](images\\' in stripped):
                        flush_paragraph()
                        match = _re.match(r'!\[([^\]]+)\]\(([^)]+)\)', stripped)
                        if match and base_dir is not None:
                            caption = match.group(1)
                            rel_path = match.group(2).replace('\\\\', '/').replace('\\', '/').lstrip('/')
                            abs_path = (base_dir / rel_path).resolve()
                            try:
                                with open(abs_path, 'rb') as f:
                                    b64 = base64.b64encode(f.read()).decode('ascii')
                                processed_content.append(f'<figure><img src="data:image/jpeg;base64,{b64}" alt="{_html.escape(caption)}"/><figcaption>{_html.escape(caption)}</figcaption></figure>')
                            except Exception:
                                processed_content.append(f'<div>{_html.escape(caption)} (image not found)</div>')
                        else:
                            paragraph_buffer.append(raw_line)
                        i += 1
                        continue

                    # Detect markdown table blocks - only if line starts with | or has multiple | characters
                    if (stripped.startswith('|') or stripped.count('|') >= 2) and i + 1 < n and is_md_table_header(lines[i + 1]):
                        flush_paragraph()
                        table_block = [stripped]
                        i += 1
                        table_block.append(lines[i].strip())
                        i += 1
                        while i < n:
                            nxt = lines[i].rstrip('\r\n')
                            if nxt.strip() == '' or (not nxt.strip().startswith('|') and nxt.count('|') < 2):
                                break
                            table_block.append(nxt.strip())
                            i += 1
                        html_table = render_md_table(table_block)
                        if html_table:
                            processed_content.append(html_table)
                        else:
                            for tl in table_block:
                                paragraph_buffer.append(tl)
                        continue

                    if stripped.startswith('## '):
                        flush_paragraph()
                        processed_content.append(f'<h3>{_html.escape(stripped[3:])}</h3>')
                    elif stripped.startswith('# '):
                        flush_paragraph()
                        processed_content.append(f'<h2>{_html.escape(stripped[2:])}</h2>')
                    elif stripped == '':
                        flush_paragraph()
                        processed_content.append('<br/>')
                    else:
                        paragraph_buffer.append(raw_line)
                    i += 1
                flush_paragraph()
                
                # Join the processed content lines
                content = "\n".join(processed_content)
                print(f"DEBUG: Content length: {len(content)}")

                # Ensure page images are prepared
                try:
                    if pdf_path and not page_images:
                        from doctra.utils.pdf_io import render_pdf_to_images
                        tmp_img_dir = Path(tempfile.mkdtemp(prefix="doctra_pages_"))
                        pil_pages = render_pdf_to_images(pdf_path)
                        saved_paths: List[str] = []
                        for idx, (im, _, _) in enumerate(pil_pages, start=1):
                            out_path = tmp_img_dir / f"page_{idx:03d}.jpg"
                            im.save(out_path, format="JPEG", quality=90)
                            saved_paths.append(str(out_path))
                        page_images = saved_paths
                        page_images_state.value = saved_paths  # cache
                except Exception as e:
                    print(f"WARN: Failed to render page images: {e}")

                # Select image for the current page number (1-based)
                page_img = None
                try:
                    page_index = int(page_num)
                    if page_images and 1 <= page_index <= len(page_images):
                        page_img = page_images[page_index - 1]
                except Exception:
                    page_img = None

                return content, page_img

            def filter_gallery_by_image(img_path, caption, all_images):
                """Filter gallery to show only the selected image."""
                if not img_path or not all_images:
                    return all_images
                
                # Find the selected image
                filtered_images = []
                for stored_img_path, stored_caption in all_images:
                    if stored_caption == caption:
                        filtered_images.append((stored_img_path, stored_caption))
                        break
                
                print(f"DEBUG: Filtered gallery to show: {filtered_images}")
                return filtered_images

            def trigger_image_filter(filter_input):
                """Trigger image filtering when input changes."""
                if not filter_input:
                    return "", ""
                
                # Parse the input (format: "img_path|caption")
                parts = filter_input.split("|", 1)
                if len(parts) == 2:
                    img_path, caption = parts
                    print(f"DEBUG: Triggering filter for {caption}")
                    return img_path, caption
                return "", ""

            def filter_gallery_by_trigger(img_path, caption, all_images):
                """Filter gallery based on trigger values."""
                if not img_path or not caption or not all_images:
                    return all_images
                
                # Find the selected image
                filtered_images = []
                for stored_img_path, stored_caption in all_images:
                    if stored_caption == caption:
                        filtered_images.append((stored_img_path, stored_caption))
                        break
                
                print(f"DEBUG: Filtered gallery to show: {filtered_images}")
                return filtered_images

            def run_full_parse_with_pages(*args):
                """Run full parse and parse the markdown into pages."""
                result = run_full_parse(*args)
                status_msg, md_content, gallery_items, file_paths, zip_path = result
                
                # Parse markdown into pages
                pages_data = []
                first_page_content = ""
                all_images = []
                if md_content:
                    pages_data = parse_markdown_by_pages(md_content)
                    print(f"DEBUG: Parsed {len(pages_data)} pages from markdown")
                    
                    # Collect all images from all pages
                    for page in pages_data:
                        for line in page['content']:
                            if line.strip().startswith('![') and ('](images/' in line or '](images\\' in line):
                                import re
                                match = re.match(r'!\[([^\]]+)\]\(([^)]+)\)', line.strip())
                                if match:
                                    caption = match.group(1)
                                    img_path = match.group(2)
                                    all_images.append((img_path, caption))
                    
                    print(f"DEBUG: Found {len(all_images)} images across all pages")
                    
                    # Show only Page 1 content initially
                    if pages_data:
                        first_page = pages_data[0]
                        first_page_content = "\n".join(first_page['content'])
                        print(f"DEBUG: Showing Page 1 content initially ({len(first_page_content)} chars)")
                else:
                    print("DEBUG: No markdown content to parse")
                
                # Prepare first page image immediately and cache page images
                input_pdf_path = args[0]
                first_page_image = None
                saved_paths: List[str] = []
                try:
                    if input_pdf_path:
                        from doctra.utils.pdf_io import render_pdf_to_images
                        tmp_img_dir = Path(tempfile.mkdtemp(prefix="doctra_pages_"))
                        pil_pages = render_pdf_to_images(input_pdf_path)
                        for idx, (im, _, _) in enumerate(pil_pages, start=1):
                            out_path = tmp_img_dir / f"page_{idx:03d}.jpg"
                            im.save(out_path, format="JPEG", quality=90)
                            saved_paths.append(str(out_path))
                        if saved_paths:
                            first_page_image = saved_paths[0]
                except Exception as e:
                    print(f"WARN: Failed to render initial page images: {e}")

                # Build initial HTML with inline images and proper blocks for first page
                if pages_data:
                    import html as _html, base64, re as _re
                    base_dir = None
                    try:
                        stem = Path(input_pdf_path).stem if input_pdf_path else ""
                        if stem:
                            base_dir = Path("outputs") / stem / "full_parse"
                    except Exception:
                        base_dir = None
                    html_lines: List[str] = []
                    for raw_line in pages_data[0]['content']:
                        line = raw_line.strip()
                        if line.startswith('![') and ('](images/' in line or '](images\\' in line):
                            match = _re.match(r'!\[([^\]]+)\]\(([^)]+)\)', line)
                            if match and base_dir is not None:
                                caption = match.group(1)
                                rel_path = match.group(2).replace('\\\\', '/').replace('\\', '/').lstrip('/')
                                abs_path = (base_dir / rel_path).resolve()
                                try:
                                    with open(abs_path, 'rb') as f:
                                        b64 = base64.b64encode(f.read()).decode('ascii')
                                    html_lines.append(f'<figure><img src="data:image/jpeg;base64,{b64}" alt="{_html.escape(caption)}"/><figcaption>{_html.escape(caption)}</figcaption></figure>')
                                except Exception:
                                    html_lines.append(f'<div>{_html.escape(caption)} (image not found)</div>')
                            else:
                                html_lines.append(f'<p>{_html.escape(raw_line)}</p>')
                        else:
                            if line.startswith('## '):
                                html_lines.append(f'<h3>{_html.escape(line[3:])}</h3>')
                            elif line.startswith('# '):
                                html_lines.append(f'<h2>{_html.escape(line[2:])}</h2>')
                            elif line == '':
                                html_lines.append('<br/>')
                            else:
                                html_lines.append(f'<p>{_html.escape(raw_line)}</p>')
                    first_page_content = "\n".join(html_lines)

                return status_msg, first_page_content, first_page_image, gallery_items, file_paths, zip_path, pages_data, all_images, input_pdf_path, saved_paths

            run_btn.click(
                fn=run_full_parse_with_pages,
                inputs=[pdf, use_vlm, vlm_provider, vlm_api_key, layout_model, dpi, min_score, ocr_lang, ocr_psm, ocr_oem, ocr_config, box_sep],
                outputs=[status, md_preview, page_image, gallery, files_out, zip_out, pages_state, all_images_state, pdf_path_state, page_images_state],
            ).then(
                fn=update_page_selector,
                inputs=[pages_state],
                outputs=[page_selector],
            )

            page_selector.change(
                fn=display_selected_page,
                inputs=[page_selector, pages_state, pdf_path_state, page_images_state],
                outputs=[md_preview, page_image],
            )

            image_filter_input.change(
                fn=trigger_image_filter,
                inputs=[image_filter_input],
                outputs=[current_image_path, current_image_caption],
            ).then(
                fn=filter_gallery_by_trigger,
                inputs=[current_image_path, current_image_caption, all_images_state],
                outputs=[gallery],
            )

        with gr.Tab("Extract Tables/Charts"):
            with gr.Row():
                pdf_e = gr.File(file_types=[".pdf"], label="PDF")
                target = gr.Dropdown(["tables", "charts", "both"], value="both", label="Target")
                use_vlm_e = gr.Checkbox(label="Use VLM (optional)", value=False)
                vlm_provider_e = gr.Dropdown(["gemini", "openai", "anthropic", "openrouter"], value="gemini", label="VLM Provider")
                vlm_api_key_e = gr.Textbox(type="password", label="VLM API Key", placeholder="Optional if VLM disabled")
            with gr.Accordion("Advanced", open=False):
                with gr.Row():
                    layout_model_e = gr.Textbox(value="PP-DocLayout_plus-L", label="Layout model")
                    dpi_e = gr.Slider(100, 400, value=200, step=10, label="DPI")
                    min_score_e = gr.Slider(0, 1, value=0.0, step=0.05, label="Min layout score")

            run_btn_e = gr.Button("▶ Run Extraction", variant="primary")
            status_e = gr.Textbox(label="Status")
            # Dropdown to select specific item
            item_selector_e = gr.Dropdown(label="Select Item", visible=False, interactive=True)
            
            # Display extracted data and images
            with gr.Row():
                tables_preview_e = gr.HTML(label="Extracted Data", elem_classes=["page-content"])
                image_e = gr.Image(label="Selected Image", interactive=False)
            
            # Keep gallery for reference but make it smaller
            gallery_e = gr.Gallery(label="All Extracted Images", columns=4, height=200, preview=True)
            files_out_e = gr.Files(label="Download individual output files")
            zip_out_e = gr.File(label="Download all outputs (ZIP)")

            # State to store output directory
            out_dir_state = gr.State("")
            
            def capture_out_dir(status_text):
                if not status_text:
                    return ""
                try:
                    if "Results in:" in status_text:
                        return status_text.split("Results in:", 1)[1].strip()
                except Exception:
                    pass
                return ""
            
            def build_item_selector(out_dir_path, target, use_vlm):
                if not out_dir_path or not use_vlm:
                    return gr.Dropdown(choices=[], value=None, visible=False)
                
                try:
                    out_dir = Path(out_dir_path)
                    mapping = out_dir / "vlm_items.json"
                    if not mapping.exists():
                        return gr.Dropdown(choices=[], value=None, visible=False)
                    
                    import json
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
            
            def show_selected_item(rel_path, out_dir_path):
                if not rel_path or not out_dir_path:
                    return "", None
                
                try:
                    out_dir = Path(out_dir_path)
                    mapping = out_dir / "vlm_items.json"
                    if not mapping.exists():
                        return "", None
                    
                    import json, html as _html
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
                outputs=[status_e, tables_preview_e, gallery_e, files_out_e, zip_out_e],
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
            )
            
            # Handle dropdown selection changes
            item_selector_e.change(
                fn=show_selected_item,
                inputs=[item_selector_e, out_dir_state],
                outputs=[tables_preview_e, image_e]
            )


        gr.Markdown(
            """
<div class="card">
  <b>Tips</b>
  <ul>
    <li>On Spaces, set a secret <code>VLM_API_KEY</code> to enable VLM features.</li>
    <li>Outputs are saved under <code>outputs/&lt;pdf_stem&gt;/</code>.</li>
  </ul>
</div>
            """
        )

    return demo


def launch_ui(server_name: str = "0.0.0.0", server_port: int = 7860, share: bool = False):
    demo = build_demo()
    demo.launch(server_name=server_name, server_port=server_port, share=share)


