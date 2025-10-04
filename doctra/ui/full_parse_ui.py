"""
Full Parse UI Module

This module contains all functionality for the Full Parse tab in the Doctra Gradio interface.
It handles PDF parsing, markdown rendering, page navigation, and image display.
"""

import tempfile
import traceback
from pathlib import Path
from typing import Tuple, List, Optional

import gradio as gr

from doctra.parsers.structured_pdf_parser import StructuredPDFParser
from doctra.utils.pdf_io import render_pdf_to_images
from doctra.ui.ui_helpers import (
    gather_outputs, 
    parse_markdown_by_pages, 
    validate_vlm_config,
    create_page_html_content
)


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
    """
    Run full PDF parsing with structured output.
    
    Args:
        pdf_file: Path to input PDF file
        use_vlm: Whether to use Vision Language Model
        vlm_provider: VLM provider name
        vlm_api_key: API key for VLM provider
        layout_model_name: Layout detection model name
        dpi: DPI for image processing
        min_score: Minimum confidence score for layout detection
        ocr_lang: OCR language code
        ocr_psm: Tesseract PSM mode
        ocr_oem: Tesseract OEM mode
        ocr_extra_config: Additional OCR configuration
        box_separator: Separator for bounding boxes
        
    Returns:
        Tuple of (status_message, markdown_preview, gallery_items, file_paths, zip_path)
    """
    if not pdf_file:
        return ("No file provided.", None, [], [], "")

    # Validate VLM configuration
    vlm_error = validate_vlm_config(use_vlm, vlm_api_key, vlm_provider)
    if vlm_error:
        return (vlm_error, None, [], [], "")

    original_filename = Path(pdf_file).stem
    
    # Create temporary directory for processing
    tmp_dir = Path(tempfile.mkdtemp(prefix="doctra_"))
    input_pdf = tmp_dir / f"{original_filename}.pdf"
    import shutil
    shutil.copy2(pdf_file, input_pdf)

    # Initialize parser with configuration
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
        parser.parse(str(input_pdf))
    except Exception as e:
        traceback.print_exc()
        # Safely encode error message for return value
        try:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            return (f"❌ VLM processing failed: {error_msg}", None, [], [], "")
        except Exception:
            return (f"❌ VLM processing failed: <Unicode encoding error>", None, [], [], "")

    # Find output directory
    outputs_root = Path("outputs")
    out_dir = outputs_root / original_filename / "full_parse"
    if not out_dir.exists():
        # fallback: search latest created dir under outputs
        candidates = sorted(outputs_root.glob("*/"), key=lambda p: p.stat().st_mtime, reverse=True)
        if candidates:
            out_dir = candidates[0] / "full_parse"
        else:
            out_dir = outputs_root

    # Read markdown file if it exists
    md_file = next(out_dir.glob("*.md"), None)
    md_preview = None
    if md_file and md_file.exists():
        try:
            with md_file.open("r", encoding="utf-8", errors="ignore") as f:
                md_preview = f.read()
        except Exception:
            md_preview = None

    # Gather output files and create ZIP
    gallery_items, file_paths, zip_path = gather_outputs(
        out_dir, 
        zip_filename=original_filename, 
        is_structured_parsing=False
    )
    
    return (
        f"✅ Parsing completed successfully!\n📁 Output directory: {out_dir}", 
        md_preview, 
        gallery_items, 
        file_paths, 
        zip_path
    )


def parse_markdown_by_pages_simple(md_content: str) -> List[dict]:
    """
    Parse markdown content and organize it by pages (simplified version).
    
    Args:
        md_content: Raw markdown content string
        
    Returns:
        List of page dictionaries with content
    """
    pages = []
    current_page = None
    
    lines = md_content.split('\n')
    i = 0
    
    # First, find all page headers
    page_headers = []
    for i, line in enumerate(lines):
        if line.strip().startswith('## Page '):
            page_num = line.strip().replace('## Page ', '').strip()
            page_headers.append((i, page_num, line))
    
    # Parse content for each page
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
    
    return pages


def update_page_selector(pages_data: List[dict]) -> gr.Dropdown:
    """
    Update the page selector dropdown with available pages.
    
    Args:
        pages_data: List of page data dictionaries
        
    Returns:
        Updated dropdown component
    """
    if not pages_data:
        return gr.Dropdown(choices=[], value=None, visible=False)
    
    page_choices = [f"Page {page['page_num']}" for page in pages_data]
    return gr.Dropdown(choices=page_choices, value=page_choices[0], visible=True)


def display_selected_page(
    selected_page: str, 
    pages_data: List[dict], 
    pdf_path: str, 
    page_images: List[str]
) -> Tuple[str, Optional[str]]:
    """
    Display the content of the selected page and the rendered page image.
    
    Args:
        selected_page: Selected page identifier
        pages_data: List of page data dictionaries
        pdf_path: Path to the original PDF file
        page_images: List of page image file paths
        
    Returns:
        Tuple of (html_content, page_image_path)
    """
    if not selected_page or not pages_data:
        return "", None
    
    # Find the selected page
    page_num = selected_page.replace("Page ", "")
    page = next((p for p in pages_data if p['page_num'] == page_num), None)
    
    if not page:
        return "Page not found", None
    
    # Build HTML with inline base64 images and proper formatting
    base_dir = None
    try:
        stem = Path(pdf_path).stem if pdf_path else ""
        if stem:
            base_dir = Path("outputs") / stem / "full_parse"
    except Exception:
        base_dir = None
    
    content = create_page_html_content(page['content'], base_dir)

    # Ensure page images are prepared
    try:
        if pdf_path and not page_images:
            tmp_img_dir = Path(tempfile.mkdtemp(prefix="doctra_pages_"))
            pil_pages = render_pdf_to_images(pdf_path)
            saved_paths: List[str] = []
            for idx, (im, _, _) in enumerate(pil_pages, start=1):
                out_path = tmp_img_dir / f"page_{idx:03d}.jpg"
                im.save(out_path, format="JPEG", quality=90)
                saved_paths.append(str(out_path))
            page_images = saved_paths
    except Exception:
        pass

    # Select image for the current page number (1-based)
    page_img = None
    try:
        page_index = int(page_num)
        if page_images and 1 <= page_index <= len(page_images):
            page_img = page_images[page_index - 1]
    except Exception:
        page_img = None

    return content, page_img


def filter_gallery_by_image(img_path: str, caption: str, all_images: List[tuple]) -> List[tuple]:
    """
    Filter gallery to show only the selected image.
    
    Args:
        img_path: Path to the selected image
        caption: Caption of the selected image
        all_images: List of all available images
        
    Returns:
        Filtered list of images
    """
    if not img_path or not all_images:
        return all_images
    
    # Find the selected image
    filtered_images = []
    for stored_img_path, stored_caption in all_images:
        if stored_caption == caption:
            filtered_images.append((stored_img_path, stored_caption))
            break
    
    return filtered_images


def trigger_image_filter(filter_input: str) -> Tuple[str, str]:
    """
    Trigger image filtering when input changes.
    
    Args:
        filter_input: Input string in format "img_path|caption"
        
    Returns:
        Tuple of (img_path, caption)
    """
    if not filter_input:
        return "", ""
    
    # Parse the input (format: "img_path|caption")
    parts = filter_input.split("|", 1)
    if len(parts) == 2:
        img_path, caption = parts
        return img_path, caption
    return "", ""


def filter_gallery_by_trigger(
    img_path: str, 
    caption: str, 
    all_images: List[tuple]
) -> List[tuple]:
    """
    Filter gallery based on trigger values.
    
    Args:
        img_path: Path to the selected image
        caption: Caption of the selected image
        all_images: List of all available images
        
    Returns:
        Filtered list of images
    """
    if not img_path or not caption or not all_images:
        return all_images
    
    # Find the selected image
    filtered_images = []
    for stored_img_path, stored_caption in all_images:
        if stored_caption == caption:
            filtered_images.append((stored_img_path, stored_caption))
            break
    
    return filtered_images


def run_full_parse_with_pages(*args) -> Tuple[str, str, Optional[str], List[tuple], List[str], str, List[dict], List[tuple], str, List[str]]:
    """
    Run full parse and parse the markdown into pages with enhanced functionality.
    
    Args:
        *args: All input arguments for run_full_parse
        
    Returns:
        Tuple of (status_msg, first_page_content, first_page_image, gallery_items, file_paths, zip_path, pages_data, all_images, input_pdf_path, saved_paths)
    """
    result = run_full_parse(*args)
    status_msg, md_content, gallery_items, file_paths, zip_path = result
    
    # Parse markdown into pages
    pages_data = []
    first_page_content = ""
    all_images = []
    
    if md_content:
        pages_data = parse_markdown_by_pages_simple(md_content)
        
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
        
        # Show only Page 1 content initially
        if pages_data:
            first_page = pages_data[0]
            first_page_content = "\n".join(first_page['content'])
    
    # Prepare first page image immediately and cache page images
    input_pdf_path = args[0]
    first_page_image = None
    saved_paths: List[str] = []
    
    try:
        if input_pdf_path:
            tmp_img_dir = Path(tempfile.mkdtemp(prefix="doctra_pages_"))
            pil_pages = render_pdf_to_images(input_pdf_path)
            for idx, (im, _, _) in enumerate(pil_pages, start=1):
                out_path = tmp_img_dir / f"page_{idx:03d}.jpg"
                im.save(out_path, format="JPEG", quality=90)
                saved_paths.append(str(out_path))
            if saved_paths:
                first_page_image = saved_paths[0]
    except Exception:
        pass

    # Build initial HTML with inline images and proper blocks for first page
    if pages_data:
        base_dir = None
        try:
            stem = Path(input_pdf_path).stem if input_pdf_path else ""
            if stem:
                base_dir = Path("outputs") / stem / "full_parse"
        except Exception:
            base_dir = None
        
        first_page_content = create_page_html_content(pages_data[0]['content'], base_dir)

    return (
        status_msg, 
        first_page_content, 
        first_page_image, 
        gallery_items, 
        file_paths, 
        zip_path, 
        pages_data, 
        all_images, 
        input_pdf_path, 
        saved_paths
    )


def create_full_parse_tab() -> Tuple[gr.Tab, dict]:
    """
    Create the Full Parse tab with all its components and functionality.
    
    Returns:
        Tuple of (tab_component, state_variables_dict)
    """
    with gr.Tab("Full Parse") as tab:
        # Input controls
        with gr.Row():
            pdf = gr.File(file_types=[".pdf"], label="PDF")
            use_vlm = gr.Checkbox(label="Use VLM (optional)", value=False)
            vlm_provider = gr.Dropdown(["gemini", "openai", "anthropic", "openrouter", "ollama"], value="gemini", label="VLM Provider")
            vlm_api_key = gr.Textbox(type="password", label="VLM API Key", placeholder="Optional if VLM disabled")

        # Advanced settings accordion
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

        # Action button
        run_btn = gr.Button("▶ Run Full Parse", variant="primary")
        status = gr.Textbox(label="Status", elem_classes=["status-ok"])
        
        # Page selector for extracted content
        page_selector = gr.Dropdown(label="Select Page to Display", interactive=True, visible=False)
        
        # Content display
        with gr.Row():
            with gr.Column():
                md_preview = gr.HTML(label="Extracted Content", visible=True, elem_classes=["page-content"])
            with gr.Column():
                page_image = gr.Image(label="Page image", interactive=False)
        
        # Gallery and downloads
        gallery = gr.Gallery(label="Extracted images (tables/charts/figures)", columns=4, height=420, preview=True)
        files_out = gr.Files(label="Download individual output files")
        zip_out = gr.File(label="Download all outputs (ZIP)")
        
        # State variables for managing page data and images
        pages_state = gr.State([])
        all_images_state = gr.State([])
        pdf_path_state = gr.State("")
        page_images_state = gr.State([])  # list of file paths per page index (1-based)
        
        # Hidden components for image filtering
        filter_trigger = gr.Button(visible=False)
        current_image_path = gr.State("")
        current_image_caption = gr.State("")
        image_filter_input = gr.Textbox(visible=False, elem_id="image_filter_input")

        # Event handlers
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

    # Return state variables for external access
    state_vars = {
        'pdf': pdf,
        'use_vlm': use_vlm,
        'vlm_provider': vlm_provider,
        'vlm_api_key': vlm_api_key,
        'layout_model': layout_model,
        'dpi': dpi,
        'min_score': min_score,
        'ocr_lang': ocr_lang,
        'ocr_psm': ocr_psm,
        'ocr_oem': ocr_oem,
        'ocr_config': ocr_config,
        'box_sep': box_sep,
        'run_btn': run_btn,
        'status': status,
        'page_selector': page_selector,
        'md_preview': md_preview,
        'page_image': page_image,
        'gallery': gallery,
        'files_out': files_out,
        'zip_out': zip_out,
        'pages_state': pages_state,
        'all_images_state': all_images_state,
        'pdf_path_state': pdf_path_state,
        'page_images_state': page_images_state,
        'filter_trigger': filter_trigger,
        'current_image_path': current_image_path,
        'current_image_caption': current_image_caption,
        'image_filter_input': image_filter_input
    }

    return tab, state_vars
