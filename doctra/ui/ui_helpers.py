"""
Shared utilities for Doctra Gradio UI components

This module contains common functions, constants, and utilities used across
all UI modules to ensure consistency and reduce code duplication.
"""

import os
import shutil
import tempfile
import re
import html as _html
import base64
import json
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

import gradio as gr
import pandas as pd


# UI Theme and Styling Constants
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


def gather_outputs(
    out_dir: Path, 
    allowed_kinds: Optional[List[str]] = None, 
    zip_filename: Optional[str] = None, 
    is_structured_parsing: bool = False
) -> Tuple[List[tuple[str, str]], List[str], str]:
    """
    Gather output files and create a ZIP archive for download.
    
    Args:
        out_dir: Output directory path
        allowed_kinds: List of allowed file kinds (tables, charts, figures)
        zip_filename: Name for the ZIP file
        is_structured_parsing: Whether this is structured parsing output
        
    Returns:
        Tuple of (gallery_items, file_paths, zip_path)
    """
    gallery_items: List[tuple[str, str]] = []
    file_paths: List[str] = []

    if out_dir.exists():
        if is_structured_parsing:
            # For structured parsing, include all files
            for file_path in sorted(out_dir.rglob("*")):
                if file_path.is_file():
                    file_paths.append(str(file_path))
        else:
            # For full parsing, include specific main files
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
            
            # Include images based on allowed kinds
            if allowed_kinds:
                for kind in allowed_kinds:
                    p = out_dir / kind
                    if p.exists():
                        for img in sorted(p.glob("*.png")):
                            file_paths.append(str(img))
                    
                    images_dir = out_dir / "images" / kind
                    if images_dir.exists():
                        for img in sorted(images_dir.glob("*.jpg")):
                            file_paths.append(str(img))
            else:
                # Include all images if no specific kinds specified
                for p in (out_dir / "charts").glob("*.png"):
                    file_paths.append(str(p))
                for p in (out_dir / "tables").glob("*.png"):
                    file_paths.append(str(p))
                for p in (out_dir / "images").rglob("*.jpg"):
                    file_paths.append(str(p))

            # Include Excel files based on allowed kinds
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

    # Build gallery items for image display
    kinds = allowed_kinds if allowed_kinds else ["tables", "charts", "figures"]
    for sub in kinds:
        p = out_dir / sub
        if p.exists():
            for img in sorted(p.glob("*.png")):
                gallery_items.append((str(img), f"{sub}: {img.name}"))
        
        images_dir = out_dir / "images" / sub
        if images_dir.exists():
            for img in sorted(images_dir.glob("*.jpg")):
                gallery_items.append((str(img), f"{sub}: {img.name}"))

    # Create ZIP archive
    tmp_zip_dir = Path(tempfile.mkdtemp(prefix="doctra_zip_"))
    
    if zip_filename:
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', zip_filename)
        zip_base = tmp_zip_dir / safe_filename
    else:
        zip_base = tmp_zip_dir / "doctra_outputs"
    
    filtered_dir = tmp_zip_dir / "filtered_outputs"
    shutil.copytree(out_dir, filtered_dir, ignore=shutil.ignore_patterns('~$*', '*.tmp', '*.temp'))
    
    zip_path = shutil.make_archive(str(zip_base), 'zip', root_dir=str(filtered_dir))

    return gallery_items, file_paths, zip_path


def parse_markdown_by_pages(md_content: str) -> List[Dict[str, Any]]:
    """
    Parse markdown content and organize it by pages.
    
    Args:
        md_content: Raw markdown content string
        
    Returns:
        List of page dictionaries with content, tables, charts, and figures
    """
    pages = []
    current_page = None
    
    lines = md_content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Detect page headers
        if line.startswith('## Page '):
            if current_page:
                pages.append(current_page)
            
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
        
        # Detect image references
        if line.startswith('![') and '](images/' in line:
            match = re.match(r'!\[([^\]]+)\]\(([^)]+)\)', line)
            if match:
                caption = match.group(1)
                img_path = match.group(2)
                
                # Categorize images by type
                if 'Table' in caption:
                    current_page['tables'].append({'caption': caption, 'path': img_path})
                elif 'Chart' in caption:
                    current_page['charts'].append({'caption': caption, 'path': img_path})
                elif 'Figure' in caption:
                    current_page['figures'].append({'caption': caption, 'path': img_path})
                
                current_page['images'].append({'caption': caption, 'path': img_path})
                current_page['full_content'].append(f"![{caption}]({img_path})")
        
        elif current_page:
            if line:
                current_page['content'].append(line)
            current_page['full_content'].append(line)
        
        i += 1
    
    if current_page:
        pages.append(current_page)
    
    return pages


def validate_vlm_config(use_vlm: bool, vlm_api_key: str) -> Optional[str]:
    """
    Validate VLM configuration parameters.
    
    Args:
        use_vlm: Whether VLM is enabled
        vlm_api_key: API key for VLM provider
        
    Returns:
        Error message if validation fails, None if valid
    """
    if use_vlm and not vlm_api_key:
        return "❌ Error: VLM API key is required when using VLM"
    
    if use_vlm and vlm_api_key:
        # Basic API key validation
        if len(vlm_api_key.strip()) < 10:
            return "❌ Error: VLM API key appears to be too short or invalid"
        if vlm_api_key.strip().startswith('sk-') and len(vlm_api_key.strip()) < 20:
            return "❌ Error: OpenAI API key appears to be invalid (too short)"
    
    return None


def render_markdown_table(lines: List[str]) -> str:
    """
    Render markdown table lines to HTML table.
    
    Args:
        lines: List of markdown table lines
        
    Returns:
        HTML table string
    """
    rows = [l.strip().strip('|').split('|') for l in lines]
    rows = [[_html.escape(c.strip()) for c in r] for r in rows]
    if len(rows) < 2:
        return ""
    
    header = rows[0]
    body = rows[2:] if len(rows) > 2 else []
    thead = '<thead><tr>' + ''.join(f'<th>{c}</th>' for c in header) + '</tr></thead>'
    tbody = '<tbody>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in body) + '</tbody>'
    return f'<table class="doc-table">{thead}{tbody}</table>'


def is_markdown_table_header(s: str) -> bool:
    """
    Check if a line is a markdown table header.
    
    Args:
        s: Line string to check
        
    Returns:
        True if line is a table header
    """
    return '|' in s and ('---' in s or '—' in s)


def create_page_html_content(page_content: List[str], base_dir: Optional[Path] = None) -> str:
    """
    Convert page content lines to HTML with inline images and proper formatting.
    
    Args:
        page_content: List of content lines for the page
        base_dir: Base directory for resolving image paths
        
    Returns:
        HTML content string
    """
    processed_content = []
    paragraph_buffer = []
    
    def flush_paragraph():
        """Flush accumulated paragraph content to HTML"""
        nonlocal paragraph_buffer
        if paragraph_buffer:
            joined = '<br/>'.join(_html.escape(l) for l in paragraph_buffer)
            processed_content.append(f'<p>{joined}</p>')
            paragraph_buffer = []

    i = 0
    n = len(page_content)
    
    while i < n:
        raw_line = page_content[i]
        line = raw_line.rstrip('\r\n')
        stripped = line.strip()
        
        # Handle image references
        if stripped.startswith('![') and ('](images/' in stripped or '](images\\' in stripped):
            flush_paragraph()
            match = re.match(r'!\[([^\]]+)\]\(([^)]+)\)', stripped)
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

        # Handle markdown tables
        if (stripped.startswith('|') or stripped.count('|') >= 2) and i + 1 < n and is_markdown_table_header(page_content[i + 1]):
            flush_paragraph()
            table_block = [stripped]
            i += 1
            table_block.append(page_content[i].strip())
            i += 1
            while i < n:
                nxt = page_content[i].rstrip('\r\n')
                if nxt.strip() == '' or (not nxt.strip().startswith('|') and nxt.count('|') < 2):
                    break
                table_block.append(nxt.strip())
                i += 1
            html_table = render_markdown_table(table_block)
            if html_table:
                processed_content.append(html_table)
            else:
                for tl in table_block:
                    paragraph_buffer.append(tl)
            continue

        # Handle headers and content
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
    return "\n".join(processed_content)


def create_tips_markdown() -> str:
    """
    Create the tips section markdown for the UI.
    
    Returns:
        Tips markdown content with helpful usage information
    """
    return """
<div class="card">
  <b>Tips</b>
  <ul>
    <li>On Spaces, set a secret <code>VLM_API_KEY</code> to enable VLM features.</li>
    <li>Use <strong>Enhanced Parser</strong> for documents that need image restoration before parsing (scanned docs, low-quality PDFs).</li>
    <li>Use <strong>DocRes Image Restoration</strong> for standalone image enhancement without parsing.</li>
    <li>DocRes tasks: <code>appearance</code> (default), <code>dewarping</code>, <code>deshadowing</code>, <code>deblurring</code>, <code>binarization</code>, <code>end2end</code>.</li>
    <li>Outputs are saved under <code>outputs/&lt;pdf_stem&gt;/</code>.</li>
  </ul>
</div>
    """
