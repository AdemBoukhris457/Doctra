"""
Enhanced Parser UI Module

This module contains all functionality for the Enhanced Parser tab in the Doctra Gradio interface.
It handles PDF parsing with DocRes image restoration, providing before/after comparison
and comprehensive document enhancement capabilities.
"""

import tempfile
import traceback
from pathlib import Path
from typing import Tuple, List, Optional

import gradio as gr

from doctra.parsers.enhanced_pdf_parser import EnhancedPDFParser
from doctra.utils.pdf_io import render_pdf_to_images
from doctra.ui.ui_helpers import gather_outputs, validate_vlm_config, create_page_html_content


def run_enhanced_parse(
    pdf_file: str,
    use_image_restoration: bool,
    restoration_task: str,
    restoration_device: str,
    restoration_dpi: int,
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
) -> Tuple[str, Optional[str], List[str], str, Optional[str], Optional[str], str]:
    """
    Run enhanced PDF parsing with DocRes image restoration.
    
    Args:
        pdf_file: Path to input PDF file
        use_image_restoration: Whether to apply DocRes image restoration
        restoration_task: DocRes restoration task
        restoration_device: Device for DocRes processing
        restoration_dpi: DPI for restoration processing
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
        Tuple of (status_message, markdown_preview, file_paths, zip_path, original_pdf_path, enhanced_pdf_path, output_dir)
    """
    if not pdf_file:
        return ("No file provided.", None, [], "", None, None, "")

    # Validate VLM configuration if VLM is enabled
    if use_vlm:
        vlm_error = validate_vlm_config(use_vlm, vlm_api_key, vlm_provider)
        if vlm_error:
            return (vlm_error, None, [], "", None, None, "")

    original_filename = Path(pdf_file).stem
    
    # Create temporary directory for processing
    tmp_dir = Path(tempfile.mkdtemp(prefix="doctra_enhanced_"))
    input_pdf = tmp_dir / f"{original_filename}.pdf"
    import shutil
    shutil.copy2(pdf_file, input_pdf)

    try:
        # Initialize enhanced parser with configuration
        parser = EnhancedPDFParser(
            use_image_restoration=use_image_restoration,
            restoration_task=restoration_task,
            restoration_device=restoration_device if restoration_device != "auto" else None,
            restoration_dpi=int(restoration_dpi),
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

        # Parse the PDF with enhancement
        parser.parse(str(input_pdf))

    except Exception as e:
        traceback.print_exc()
        # Safely encode error message for return value
        try:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            return (f"❌ Enhanced parsing failed: {error_msg}", None, [], "", None, None, "")
        except Exception:
            return (f"❌ Enhanced parsing failed: <Unicode encoding error>", None, [], "", None, None, "")

    # Find output directory
    outputs_root = Path("outputs")
    out_dir = outputs_root / original_filename / "enhanced_parse"
    if not out_dir.exists():
        # fallback: search latest created dir under outputs
        candidates = sorted(outputs_root.glob("*/"), key=lambda p: p.stat().st_mtime, reverse=True)
        if candidates:
            out_dir = candidates[0] / "enhanced_parse"
        else:
            out_dir = outputs_root
    
    # If still no enhanced_parse directory, try to find any directory with enhanced files
    if not out_dir.exists():
        # Look for any directory containing enhanced PDFs
        for candidate_dir in outputs_root.rglob("*"):
            if candidate_dir.is_dir():
                enhanced_pdfs = list(candidate_dir.glob("*enhanced*.pdf"))
                if enhanced_pdfs:
                    out_dir = candidate_dir
                    break

    # Load first page content initially (page-specific content)
    md_preview = None
    try:
        # Try to load the first page content from pages folder
        pages_dir = out_dir / "pages"
        first_page_path = pages_dir / "page_001.md"
        if first_page_path.exists():
            with first_page_path.open("r", encoding="utf-8", errors="ignore") as f:
                md_content = f.read()
            
            # Convert markdown to HTML with embedded images
            md_lines = md_content.split('\n')
            md_preview = create_page_html_content(md_lines, out_dir)
        else:
            # Fallback to full markdown file if page-specific files don't exist
            md_file = next(out_dir.glob("*.md"), None)
            if md_file and md_file.exists():
                with md_file.open("r", encoding="utf-8", errors="ignore") as f:
                    md_content = f.read()
                
                # Convert markdown to HTML with embedded images
                md_lines = md_content.split('\n')
                md_preview = create_page_html_content(md_lines, out_dir)
    except Exception as e:
        print(f"❌ Error loading initial content: {e}")
        md_preview = None

    # Gather output files and create ZIP
    _, file_paths, zip_path = gather_outputs(
        out_dir, 
        zip_filename=f"{original_filename}_enhanced", 
        is_structured_parsing=False
    )

    # Look for enhanced PDF file
    enhanced_pdf_path = None
    if use_image_restoration:
        # Look for enhanced PDF in the output directory
        enhanced_pdf_candidates = list(out_dir.glob("*enhanced*.pdf"))
        if enhanced_pdf_candidates:
            enhanced_pdf_path = str(enhanced_pdf_candidates[0])
            print(f"✅ Found enhanced PDF: {enhanced_pdf_path}")
        else:
            # Look in parent directory
            parent_enhanced = list(out_dir.parent.glob("*enhanced*.pdf"))
            if parent_enhanced:
                enhanced_pdf_path = str(parent_enhanced[0])
                print(f"✅ Found enhanced PDF in parent: {enhanced_pdf_path}")
            else:
                print(f"⚠️ No enhanced PDF found in {out_dir} or parent directory")
                # Debug: list all files in the directory
                all_files = list(out_dir.glob("*"))
                print(f"📁 Files in output directory: {[f.name for f in all_files]}")

    return (
        f"✅ Enhanced parsing completed successfully!\n📁 Output directory: {out_dir}", 
        md_preview, 
        file_paths, 
        zip_path,
        pdf_file,  # Original PDF path
        enhanced_pdf_path,  # Enhanced PDF path
        str(out_dir)  # Output directory for page-specific content
    )


def render_pdf_pages_for_comparison(pdf_path: str, max_pages: int = 10) -> Tuple[List[str], List[str]]:
    """
    Render PDF pages to images for before/after comparison.
    
    Args:
        pdf_path: Path to PDF file
        max_pages: Maximum number of pages to render
        
    Returns:
        Tuple of (image_paths, page_options)
    """
    if not pdf_path or not Path(pdf_path).exists():
        return [], []
    
    try:
        # render_pdf_to_images returns (pil_image, width, height) tuples
        image_tuples = render_pdf_to_images(pdf_path)
        
        # Limit to max_pages if specified
        if max_pages and len(image_tuples) > max_pages:
            image_tuples = image_tuples[:max_pages]
        
        # Convert PIL images to file paths for display
        images = []
        page_options = []
        
        for i, (pil_image, width, height) in enumerate(image_tuples):
            # Save PIL image to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            pil_image.save(temp_file.name, 'PNG')
            images.append(temp_file.name)
            page_options.append(f"Page {i+1}")
        
        return images, page_options
    except Exception as e:
        print(f"Error rendering PDF pages: {e}")
        return [], []


def update_enhanced_page_selector(original_pdf: str, enhanced_pdf: str) -> Tuple[gr.Dropdown, List[str], List[str], str, str, Optional[str], Optional[str]]:
    """
    Update page selector when PDFs are loaded for comparison.
    
    Args:
        original_pdf: Path to original PDF file
        enhanced_pdf: Path to enhanced PDF file
        
    Returns:
        Tuple of (dropdown, original_pages, enhanced_pages, original_pdf_path, enhanced_pdf_path, first_original_image, first_enhanced_image)
    """
    original_pages, original_options = render_pdf_pages_for_comparison(original_pdf) if original_pdf else ([], [])
    enhanced_pages, enhanced_options = render_pdf_pages_for_comparison(enhanced_pdf) if enhanced_pdf else ([], [])
    
    # Use the same page options for the single selector (use the longer list)
    if len(original_options) >= len(enhanced_options):
        common_options = original_options
    else:
        common_options = enhanced_options
    
    # Set default to first page if available
    default_page = common_options[0] if common_options else None
    
    return (
        gr.Dropdown(choices=common_options, value=default_page, visible=bool(common_options)),
        original_pages,
        enhanced_pages,
        original_pdf or "",
        enhanced_pdf or "",
        original_pages[0] if original_pages else None,  # First page image
        enhanced_pages[0] if enhanced_pages else None   # First page image
    )


def sync_enhanced_page_changes(
    page_selector: str, 
    original_pages: List[str], 
    enhanced_pages: List[str], 
    original_pdf_path: str, 
    enhanced_pdf_path: str,
    output_dir: str = None
) -> Tuple[Optional[str], Optional[str], str]:
    """
    Synchronize page changes between original and enhanced PDFs and load page-specific content.
    
    Args:
        page_selector: Selected page identifier
        original_pages: List of original page image paths
        enhanced_pages: List of enhanced page image paths
        original_pdf_path: Path to original PDF
        enhanced_pdf_path: Path to enhanced PDF
        output_dir: Output directory for page-specific content
        
    Returns:
        Tuple of (original_page_image, enhanced_page_image, page_content_html)
    """
    if not page_selector:
        return None, None, ""
    
    # Get the page index
    try:
        page_index = int(page_selector.split()[1]) - 1  # "Page 1" -> index 0
        page_num = page_index + 1  # Convert back to 1-based page number
    except (ValueError, IndexError):
        return None, None, ""
    
    # Get the corresponding page from each PDF
    original_page = None
    enhanced_page = None
    
    if original_pages and 0 <= page_index < len(original_pages):
        original_page = original_pages[page_index]
    
    if enhanced_pages and 0 <= page_index < len(enhanced_pages):
        enhanced_page = enhanced_pages[page_index]
    
    # Load page-specific content
    page_content_html = ""
    if output_dir:
        try:
            # Look for page files in the pages folder
            pages_dir = Path(output_dir) / "pages"
            page_md_path = pages_dir / f"page_{page_num:03d}.md"
            if page_md_path.exists():
                with page_md_path.open("r", encoding="utf-8", errors="ignore") as f:
                    md_content = f.read()
                
                # Convert markdown to HTML with embedded images
                md_lines = md_content.split('\n')
                page_content_html = create_page_html_content(md_lines, Path(output_dir))
            else:
                print(f"⚠️ Page {page_num} content file not found: {page_md_path}")
        except Exception as e:
            print(f"❌ Error loading page {page_num} content: {e}")
    
    return original_page, enhanced_page, page_content_html


def create_enhanced_parser_tab() -> Tuple[gr.Tab, dict]:
    """
    Create the Enhanced Parser tab with all its components and functionality.
    
    Returns:
        Tuple of (tab_component, state_variables_dict)
    """
    with gr.Tab("Enhanced Parser") as tab:
        # Input controls
        with gr.Row():
            pdf_enhanced = gr.File(file_types=[".pdf"], label="PDF")
            use_image_restoration = gr.Checkbox(label="Use Image Restoration", value=True)
            restoration_task = gr.Dropdown(
                ["appearance", "dewarping", "deshadowing", "deblurring", "binarization", "end2end"], 
                value="appearance", 
                label="Restoration Task"
            )
            restoration_device = gr.Dropdown(
                ["auto", "cuda", "cpu"], 
                value="auto", 
                label="Restoration Device"
            )

        # VLM settings
        with gr.Row():
            use_vlm_enhanced = gr.Checkbox(label="Use VLM (optional)", value=False)
            vlm_provider_enhanced = gr.Dropdown(["gemini", "openai", "anthropic", "openrouter", "ollama"], value="gemini", label="VLM Provider")
            vlm_api_key_enhanced = gr.Textbox(type="password", label="VLM API Key", placeholder="Optional if VLM disabled")

        # Advanced settings accordion
        with gr.Accordion("Advanced Settings", open=False):
            with gr.Row():
                restoration_dpi = gr.Slider(100, 400, value=200, step=10, label="Restoration DPI")
                layout_model_enhanced = gr.Textbox(value="PP-DocLayout_plus-L", label="Layout model")
                dpi_enhanced = gr.Slider(100, 400, value=200, step=10, label="Processing DPI")
                min_score_enhanced = gr.Slider(0, 1, value=0.0, step=0.05, label="Min layout score")
            
            with gr.Row():
                ocr_lang_enhanced = gr.Textbox(value="eng", label="OCR Language")
                ocr_psm_enhanced = gr.Slider(0, 13, value=4, step=1, label="Tesseract PSM")
                ocr_oem_enhanced = gr.Slider(0, 3, value=3, step=1, label="Tesseract OEM")
            
            with gr.Row():
                ocr_config_enhanced = gr.Textbox(value="", label="Extra OCR config")
                box_sep_enhanced = gr.Textbox(value="\n", label="Box separator")

        # Action button
        run_enhanced_btn = gr.Button("▶ Run Enhanced Parse", variant="primary")
        enhanced_status = gr.Textbox(label="Status", elem_classes=["status-ok"])
        
        # Page selector for comparison
        with gr.Row():
            enhanced_page_selector = gr.Dropdown(label="Select Page for Comparison", interactive=True, visible=False)
        
        # Before/After comparison
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 📄 Original PDF")
                enhanced_original_pdf = gr.File(label="Original PDF File", interactive=False, visible=False)
                enhanced_original_page_image = gr.Image(label="Original PDF Page", interactive=False, height=600)
            with gr.Column():
                gr.Markdown("### ✨ Enhanced PDF")
                enhanced_enhanced_pdf = gr.File(label="Enhanced PDF File", interactive=False, visible=False)
                enhanced_enhanced_page_image = gr.Image(label="Enhanced PDF Page", interactive=False, height=600)
        
        # Content display
        with gr.Row():
            enhanced_md_preview = gr.HTML(label="Extracted Content", visible=True, elem_classes=["page-content"])
        
        # Downloads
        enhanced_files_out = gr.Files(label="Download individual output files")
        enhanced_zip_out = gr.File(label="Download all outputs (ZIP)")
        
        # State variables for PDF page data
        enhanced_original_pages_state = gr.State([])
        enhanced_enhanced_pages_state = gr.State([])
        enhanced_original_pdf_path_state = gr.State("")
        enhanced_enhanced_pdf_path_state = gr.State("")
        enhanced_output_dir_state = gr.State("")

        # Event handlers
        run_enhanced_btn.click(
            fn=run_enhanced_parse,
            inputs=[
                pdf_enhanced, use_image_restoration, restoration_task, restoration_device, restoration_dpi,
                use_vlm_enhanced, vlm_provider_enhanced, vlm_api_key_enhanced, layout_model_enhanced,
                dpi_enhanced, min_score_enhanced, ocr_lang_enhanced, ocr_psm_enhanced, ocr_oem_enhanced,
                ocr_config_enhanced, box_sep_enhanced
            ],
            outputs=[
                enhanced_status, enhanced_md_preview, enhanced_files_out, enhanced_zip_out,
                enhanced_original_pdf, enhanced_enhanced_pdf, enhanced_output_dir_state
            ]
        ).then(
            fn=update_enhanced_page_selector,
            inputs=[enhanced_original_pdf, enhanced_enhanced_pdf],
            outputs=[
                enhanced_page_selector, enhanced_original_pages_state, enhanced_enhanced_pages_state,
                enhanced_original_pdf_path_state, enhanced_enhanced_pdf_path_state, 
                enhanced_original_page_image, enhanced_enhanced_page_image
            ]
        )
        
        # Handle page selector changes
        enhanced_page_selector.change(
            fn=sync_enhanced_page_changes,
            inputs=[
                enhanced_page_selector, enhanced_original_pages_state, enhanced_enhanced_pages_state,
                enhanced_original_pdf_path_state, enhanced_enhanced_pdf_path_state, enhanced_output_dir_state
            ],
            outputs=[enhanced_original_page_image, enhanced_enhanced_page_image, enhanced_md_preview]
        )

    # Return state variables for external access
    state_vars = {
        'pdf_enhanced': pdf_enhanced,
        'use_image_restoration': use_image_restoration,
        'restoration_task': restoration_task,
        'restoration_device': restoration_device,
        'restoration_dpi': restoration_dpi,
        'use_vlm_enhanced': use_vlm_enhanced,
        'vlm_provider_enhanced': vlm_provider_enhanced,
        'vlm_api_key_enhanced': vlm_api_key_enhanced,
        'layout_model_enhanced': layout_model_enhanced,
        'dpi_enhanced': dpi_enhanced,
        'min_score_enhanced': min_score_enhanced,
        'ocr_lang_enhanced': ocr_lang_enhanced,
        'ocr_psm_enhanced': ocr_psm_enhanced,
        'ocr_oem_enhanced': ocr_oem_enhanced,
        'ocr_config_enhanced': ocr_config_enhanced,
        'box_sep_enhanced': box_sep_enhanced,
        'run_enhanced_btn': run_enhanced_btn,
        'enhanced_status': enhanced_status,
        'enhanced_page_selector': enhanced_page_selector,
        'enhanced_original_pdf': enhanced_original_pdf,
        'enhanced_original_page_image': enhanced_original_page_image,
        'enhanced_enhanced_pdf': enhanced_enhanced_pdf,
        'enhanced_enhanced_page_image': enhanced_enhanced_page_image,
        'enhanced_md_preview': enhanced_md_preview,
        'enhanced_files_out': enhanced_files_out,
        'enhanced_zip_out': enhanced_zip_out,
        'enhanced_original_pages_state': enhanced_original_pages_state,
        'enhanced_enhanced_pages_state': enhanced_enhanced_pages_state,
        'enhanced_original_pdf_path_state': enhanced_original_pdf_path_state,
        'enhanced_enhanced_pdf_path_state': enhanced_enhanced_pdf_path_state,
        'enhanced_output_dir_state': enhanced_output_dir_state
    }

    return tab, state_vars
