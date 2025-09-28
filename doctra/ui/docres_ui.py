"""
DocRes Image Restoration UI Module

This module contains all functionality for the DocRes image restoration tab in the Doctra Gradio interface.
It handles PDF restoration, before/after comparison, and enhanced file management.
"""

import tempfile
from pathlib import Path
from typing import Tuple, List, Optional

import gradio as gr

from doctra.ui.docres_wrapper import DocResUIWrapper
from doctra.utils.pdf_io import render_pdf_to_images


def render_pdf_pages(pdf_path: str, max_pages: int = 10) -> Tuple[List[str], List[str]]:
    """
    Render PDF pages to images for display.
    
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


def update_docres_page_selector(original_pdf: str, enhanced_pdf: str) -> Tuple[gr.Dropdown, List[str], List[str], str, str, Optional[str], Optional[str]]:
    """
    Update single page selector when PDFs are loaded.
    
    Args:
        original_pdf: Path to original PDF file
        enhanced_pdf: Path to enhanced PDF file
        
    Returns:
        Tuple of (dropdown, original_pages, enhanced_pages, original_pdf_path, enhanced_pdf_path, first_original_image, first_enhanced_image)
    """
    original_pages, original_options = render_pdf_pages(original_pdf) if original_pdf else ([], [])
    enhanced_pages, enhanced_options = render_pdf_pages(enhanced_pdf) if enhanced_pdf else ([], [])
    
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


def display_docres_page(page_selector: str, pages_data: List[str], pdf_path: str) -> Optional[str]:
    """
    Display selected page from PDF.
    
    Args:
        page_selector: Selected page identifier
        pages_data: List of page image paths
        pdf_path: Path to PDF file
        
    Returns:
        Path to selected page image
    """
    if not page_selector or not pages_data or not pdf_path:
        return None
    
    try:
        page_index = int(page_selector.split()[1]) - 1  # "Page 1" -> index 0
        if 0 <= page_index < len(pages_data):
            return pages_data[page_index]
    except (ValueError, IndexError):
        pass
    
    return None


def sync_page_changes(
    page_selector: str, 
    original_pages: List[str], 
    enhanced_pages: List[str], 
    original_pdf_path: str, 
    enhanced_pdf_path: str
) -> Tuple[Optional[str], Optional[str]]:
    """
    Synchronize page changes between original and enhanced PDFs.
    
    Args:
        page_selector: Selected page identifier
        original_pages: List of original page image paths
        enhanced_pages: List of enhanced page image paths
        original_pdf_path: Path to original PDF
        enhanced_pdf_path: Path to enhanced PDF
        
    Returns:
        Tuple of (original_page_image, enhanced_page_image)
    """
    if not page_selector:
        return None, None
    
    # Get the page index
    try:
        page_index = int(page_selector.split()[1]) - 1  # "Page 1" -> index 0
    except (ValueError, IndexError):
        return None, None
    
    # Get the corresponding page from each PDF
    original_page = None
    enhanced_page = None
    
    if original_pages and 0 <= page_index < len(original_pages):
        original_page = original_pages[page_index]
    
    if enhanced_pages and 0 <= page_index < len(enhanced_pages):
        enhanced_page = enhanced_pages[page_index]
    
    return original_page, enhanced_page


def run_docres_restoration(
    pdf_file: str, 
    task: str, 
    device: str, 
    dpi: int, 
    save_enhanced: bool, 
    save_images: bool
) -> Tuple[str, Optional[str], Optional[str], Optional[dict], List[str]]:
    """
    Run DocRes image restoration on PDF.
    
    Args:
        pdf_file: Path to input PDF file
        task: Restoration task type
        device: Device to use for processing
        dpi: DPI for processing
        save_enhanced: Whether to save enhanced PDF
        save_images: Whether to save enhanced images
        
    Returns:
        Tuple of (status_message, original_pdf_path, enhanced_pdf_path, metadata, file_paths)
    """
    if not pdf_file:
        return ("No file provided.", None, [], None, [])
    
    try:
        # Initialize DocRes engine
        device_str = None if device == "auto" else device
        docres = DocResUIWrapper(device=device_str)
        
        # Extract filename
        original_filename = Path(pdf_file).stem
        
        # Create output directory
        output_dir = Path("outputs") / f"{original_filename}_docres"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Run DocRes restoration
        enhanced_pdf_path = output_dir / f"{original_filename}_enhanced.pdf"
        docres.restore_pdf(
            pdf_path=pdf_file,
            output_path=str(enhanced_pdf_path),
            task=task,
            dpi=dpi
        )
        
        # Prepare outputs
        file_paths = []
        
        if save_enhanced and enhanced_pdf_path.exists():
            file_paths.append(str(enhanced_pdf_path))
        
        if save_images:
            # Look for enhanced images
            images_dir = output_dir / "enhanced_images"
            if images_dir.exists():
                for img_path in sorted(images_dir.glob("*.jpg")):
                    file_paths.append(str(img_path))
        
        # Create metadata
        metadata = {
            "task": task,
            "device": str(docres.device),
            "dpi": dpi,
            "original_file": pdf_file,
            "enhanced_file": str(enhanced_pdf_path) if enhanced_pdf_path.exists() else None,
            "output_directory": str(output_dir)
        }
        
        status_msg = f"✅ DocRes restoration completed successfully!\n📁 Output directory: {output_dir}"
        
        enhanced_pdf_file = str(enhanced_pdf_path) if enhanced_pdf_path.exists() else None
        return (status_msg, pdf_file, enhanced_pdf_file, metadata, file_paths)
        
    except Exception as e:
        error_msg = f"❌ DocRes restoration failed: {str(e)}"
        return (error_msg, None, None, None, [])


def create_docres_tab() -> Tuple[gr.Tab, dict]:
    """
    Create the DocRes Image Restoration tab with all its components and functionality.
    
    Returns:
        Tuple of (tab_component, state_variables_dict)
    """
    with gr.Tab("DocRes Image Restoration") as tab:
        # Input controls
        with gr.Row():
            pdf_docres = gr.File(file_types=[".pdf"], label="PDF")
            docres_task_standalone = gr.Dropdown(
                ["appearance", "dewarping", "deshadowing", "deblurring", "binarization", "end2end"], 
                value="appearance", 
                label="Restoration Task"
            )
            docres_device_standalone = gr.Dropdown(
                ["auto", "cuda", "cpu"], 
                value="auto", 
                label="Device"
            )
        
        # Additional settings
        with gr.Row():
            docres_dpi = gr.Slider(100, 400, value=200, step=10, label="DPI")
            docres_save_enhanced = gr.Checkbox(label="Save Enhanced PDF", value=True)
            docres_save_images = gr.Checkbox(label="Save Enhanced Images", value=True)
        
        # Action button
        run_docres_btn = gr.Button("▶ Run DocRes Restoration", variant="primary")
        docres_status = gr.Textbox(label="Status", elem_classes=["status-ok"])
        
        # Single page selector for both PDFs
        with gr.Row():
            docres_page_selector = gr.Dropdown(label="Select Page", interactive=True, visible=False)
        
        # Before/After PDF comparison
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 📄 Original PDF")
                docres_original_pdf = gr.File(label="Original PDF File", interactive=False, visible=False)
                docres_original_page_image = gr.Image(label="Original PDF Page", interactive=False, height=800)
            with gr.Column():
                gr.Markdown("### ✨ Enhanced PDF")
                docres_enhanced_pdf = gr.File(label="Enhanced PDF File", interactive=False, visible=False)
                docres_enhanced_page_image = gr.Image(label="Enhanced PDF Page", interactive=False, height=800)
        
        # DocRes outputs
        with gr.Row():
            with gr.Column():
                docres_metadata = gr.JSON(label="Restoration Metadata", visible=False)
        
        docres_files_out = gr.Files(label="Download enhanced files")
        
        # State variables for PDF page data
        docres_original_pages_state = gr.State([])
        docres_enhanced_pages_state = gr.State([])
        docres_original_pdf_path_state = gr.State("")
        docres_enhanced_pdf_path_state = gr.State("")

        # Event handlers
        run_docres_btn.click(
            fn=run_docres_restoration,
            inputs=[pdf_docres, docres_task_standalone, docres_device_standalone, docres_dpi, docres_save_enhanced, docres_save_images],
            outputs=[docres_status, docres_original_pdf, docres_enhanced_pdf, docres_metadata, docres_files_out]
        ).then(
            fn=update_docres_page_selector,
            inputs=[docres_original_pdf, docres_enhanced_pdf],
            outputs=[docres_page_selector, docres_original_pages_state, docres_enhanced_pages_state, docres_original_pdf_path_state, docres_enhanced_pdf_path_state, docres_original_page_image, docres_enhanced_page_image]
        )
        
        # Handle single page selector changes
        docres_page_selector.change(
            fn=sync_page_changes,
            inputs=[docres_page_selector, docres_original_pages_state, docres_enhanced_pages_state, docres_original_pdf_path_state, docres_enhanced_pdf_path_state],
            outputs=[docres_original_page_image, docres_enhanced_page_image]
        )

    # Return state variables for external access
    state_vars = {
        'pdf_docres': pdf_docres,
        'docres_task_standalone': docres_task_standalone,
        'docres_device_standalone': docres_device_standalone,
        'docres_dpi': docres_dpi,
        'docres_save_enhanced': docres_save_enhanced,
        'docres_save_images': docres_save_images,
        'run_docres_btn': run_docres_btn,
        'docres_status': docres_status,
        'docres_page_selector': docres_page_selector,
        'docres_original_pdf': docres_original_pdf,
        'docres_original_page_image': docres_original_page_image,
        'docres_enhanced_pdf': docres_enhanced_pdf,
        'docres_enhanced_page_image': docres_enhanced_page_image,
        'docres_metadata': docres_metadata,
        'docres_files_out': docres_files_out,
        'docres_original_pages_state': docres_original_pages_state,
        'docres_enhanced_pages_state': docres_enhanced_pages_state,
        'docres_original_pdf_path_state': docres_original_pdf_path_state,
        'docres_enhanced_pdf_path_state': docres_enhanced_pdf_path_state
    }

    return tab, state_vars
