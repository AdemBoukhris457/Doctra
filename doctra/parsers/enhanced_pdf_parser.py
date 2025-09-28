"""
Enhanced PDF Parser with Image Restoration

This module provides an enhanced PDF parser that combines the structured parsing
capabilities with DocRes image restoration for improved document processing.
"""

from __future__ import annotations
import os
import sys
import numpy as np
from typing import List, Dict, Any, Optional, Union
from contextlib import ExitStack
from PIL import Image
from tqdm import tqdm

from doctra.parsers.structured_pdf_parser import StructuredPDFParser
from doctra.engines.image_restoration import DocResEngine
from doctra.utils.pdf_io import render_pdf_to_images
from doctra.utils.constants import IMAGE_SUBDIRS, EXCLUDE_LABELS
from doctra.utils.file_ops import ensure_output_dirs
from doctra.utils.progress import create_beautiful_progress_bar, create_notebook_friendly_bar
from doctra.parsers.layout_order import reading_order_key
from doctra.utils.ocr_utils import ocr_box_text
from doctra.exporters.image_saver import save_box_image
from doctra.exporters.markdown_writer import write_markdown
from doctra.exporters.html_writer import write_html, write_structured_html
from doctra.exporters.excel_writer import write_structured_excel
from doctra.utils.structured_utils import to_structured_dict
from doctra.exporters.markdown_table import render_markdown_table


class EnhancedPDFParser(StructuredPDFParser):
    """
    Enhanced PDF Parser with Image Restoration capabilities.
    
    Extends the StructuredPDFParser with DocRes image restoration to improve
    document quality before processing. This is particularly useful for:
    - Scanned documents with shadows or distortion
    - Low-quality PDFs that need enhancement
    - Documents with perspective issues
    
    :param use_image_restoration: Whether to apply DocRes image restoration (default: True)
    :param restoration_task: DocRes task to use ("dewarping", "deshadowing", "appearance", "deblurring", "binarization", "end2end", default: "appearance")
    :param restoration_device: Device for DocRes processing ("cuda", "cpu", or None for auto-detect, default: None)
    :param restoration_dpi: DPI for restoration processing (default: 200)
    :param use_vlm: Whether to use VLM for structured data extraction (default: False)
    :param vlm_provider: VLM provider to use ("gemini", "openai", "anthropic", or "openrouter", default: "gemini")
    :param vlm_model: Model name to use (defaults to provider-specific defaults)
    :param vlm_api_key: API key for VLM provider (required if use_vlm is True)
    :param layout_model_name: Layout detection model name (default: "PP-DocLayout_plus-L")
    :param dpi: DPI for PDF rendering (default: 200)
    :param min_score: Minimum confidence score for layout detection (default: 0.0)
    :param ocr_lang: OCR language code (default: "eng")
    :param ocr_psm: Tesseract page segmentation mode (default: 4)
    :param ocr_oem: Tesseract OCR engine mode (default: 3)
    :param ocr_extra_config: Additional Tesseract configuration (default: "")
    :param box_separator: Separator between text boxes in output (default: "\n")
    """

    def __init__(
        self,
        *,
        use_image_restoration: bool = True,
        restoration_task: str = "appearance",
        restoration_device: Optional[str] = None,
        restoration_dpi: int = 200,
        use_vlm: bool = False,
        vlm_provider: str = "gemini",
        vlm_model: str | None = None,
        vlm_api_key: str | None = None,
        layout_model_name: str = "PP-DocLayout_plus-L",
        dpi: int = 200,
        min_score: float = 0.0,
        ocr_lang: str = "eng",
        ocr_psm: int = 4,
        ocr_oem: int = 3,
        ocr_extra_config: str = "",
        box_separator: str = "\n",
    ):
        """
        Initialize the Enhanced PDF Parser with image restoration capabilities.
        """
        # Initialize parent class
        super().__init__(
            use_vlm=use_vlm,
            vlm_provider=vlm_provider,
            vlm_model=vlm_model,
            vlm_api_key=vlm_api_key,
            layout_model_name=layout_model_name,
            dpi=dpi,
            min_score=min_score,
            ocr_lang=ocr_lang,
            ocr_psm=ocr_psm,
            ocr_oem=ocr_oem,
            ocr_extra_config=ocr_extra_config,
            box_separator=box_separator,
        )
        
        # Image restoration settings
        self.use_image_restoration = use_image_restoration
        self.restoration_task = restoration_task
        self.restoration_device = restoration_device
        self.restoration_dpi = restoration_dpi
        
        # Initialize DocRes engine if needed
        self.docres_engine = None
        if self.use_image_restoration:
            try:
                self.docres_engine = DocResEngine(
                    device=restoration_device,
                    use_half_precision=True
                )
                print(f"✅ DocRes engine initialized with task: {restoration_task}")
            except Exception as e:
                print(f"⚠️ DocRes initialization failed: {e}")
                print("   Continuing without image restoration...")
                self.use_image_restoration = False
                self.docres_engine = None

    def parse(self, pdf_path: str, enhanced_output_dir: str = None) -> None:
        """
        Parse a PDF document with optional image restoration.
        
        :param pdf_path: Path to the input PDF file
        :param enhanced_output_dir: Directory for enhanced images (if None, uses default)
        :return: None
        """
        pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # Set up output directories
        if enhanced_output_dir is None:
            out_dir = f"outputs/{pdf_filename}/enhanced_parse"
        else:
            out_dir = enhanced_output_dir
            
        os.makedirs(out_dir, exist_ok=True)
        ensure_output_dirs(out_dir, IMAGE_SUBDIRS)
        
        # Process PDF pages with optional restoration
        if self.use_image_restoration and self.docres_engine:
            print(f"🔄 Processing PDF with image restoration: {os.path.basename(pdf_path)}")
            enhanced_pages = self._process_pages_with_restoration(pdf_path, out_dir)
            
            # Create enhanced PDF file using the already processed enhanced pages
            enhanced_pdf_path = os.path.join(out_dir, f"{pdf_filename}_enhanced.pdf")
            try:
                self._create_enhanced_pdf_from_pages(enhanced_pages, enhanced_pdf_path)
            except Exception as e:
                print(f"⚠️ Failed to create enhanced PDF: {e}")
        else:
            print(f"🔄 Processing PDF without image restoration: {os.path.basename(pdf_path)}")
            enhanced_pages = [im for (im, _, _) in render_pdf_to_images(pdf_path, dpi=self.dpi)]
        
        # Run layout detection on enhanced pages
        print("🔍 Running layout detection on enhanced pages...")
        pages = self.layout_engine.predict_pdf(
            pdf_path, batch_size=1, layout_nms=True, dpi=self.dpi, min_score=self.min_score
        )
        
        # Use enhanced pages for processing
        pil_pages = enhanced_pages
        
        # Continue with standard parsing logic
        self._process_parsing_logic(pages, pil_pages, out_dir, pdf_filename, pdf_path)

    def _process_pages_with_restoration(self, pdf_path: str, out_dir: str) -> List[Image.Image]:
        """
        Process PDF pages with DocRes image restoration.
        
        :param pdf_path: Path to the input PDF file
        :param out_dir: Output directory for enhanced images
        :return: List of enhanced PIL images
        """
        # Render original pages
        original_pages = [im for (im, _, _) in render_pdf_to_images(pdf_path, dpi=self.restoration_dpi)]
        
        if not original_pages:
            print("❌ No pages found in PDF")
            return []
        
        # Create progress bar
        is_notebook = "ipykernel" in sys.modules or "jupyter" in sys.modules
        if is_notebook:
            progress_bar = create_notebook_friendly_bar(
                total=len(original_pages), 
                desc=f"DocRes {self.restoration_task}"
            )
        else:
            progress_bar = create_beautiful_progress_bar(
                total=len(original_pages), 
                desc=f"DocRes {self.restoration_task}",
                leave=True
            )
        
        enhanced_pages = []
        enhanced_dir = os.path.join(out_dir, "enhanced_pages")
        os.makedirs(enhanced_dir, exist_ok=True)
        
        try:
            with progress_bar:
                for i, page_img in enumerate(original_pages):
                    try:
                        # Convert PIL to numpy array
                        img_array = np.array(page_img)
                        
                        # Apply DocRes restoration
                        restored_img, metadata = self.docres_engine.restore_image(
                            img_array, 
                            task=self.restoration_task
                        )
                        
                        # Convert back to PIL Image
                        enhanced_page = Image.fromarray(restored_img)
                        enhanced_pages.append(enhanced_page)
                        
                        # Save enhanced page for reference
                        enhanced_path = os.path.join(enhanced_dir, f"page_{i+1:03d}_enhanced.jpg")
                        enhanced_page.save(enhanced_path, "JPEG", quality=95)
                        
                        progress_bar.set_description(f"✅ Page {i+1}/{len(original_pages)} enhanced")
                        progress_bar.update(1)
                        
                    except Exception as e:
                        print(f"  ⚠️ Page {i+1} restoration failed: {e}, using original")
                        enhanced_pages.append(page_img)
                        progress_bar.set_description(f"⚠️ Page {i+1} failed, using original")
                        progress_bar.update(1)
        
        finally:
            if hasattr(progress_bar, 'close'):
                progress_bar.close()
        
        return enhanced_pages

    def _process_parsing_logic(self, pages, pil_pages, out_dir, pdf_filename, pdf_path):
        """
        Process the parsing logic with enhanced pages.
        This is extracted from the parent class to allow customization.
        """
        
        fig_count = sum(sum(1 for b in p.boxes if b.label == "figure") for p in pages)
        chart_count = sum(sum(1 for b in p.boxes if b.label == "chart") for p in pages)
        table_count = sum(sum(1 for b in p.boxes if b.label == "table") for p in pages)

        md_lines: List[str] = ["# Enhanced Document Content\n"]
        structured_items: List[Dict[str, Any]] = []
        page_content: Dict[int, List[str]] = {}  # Store content by page

        charts_desc = "Charts (VLM → table)" if self.use_vlm else "Charts (cropped)"
        tables_desc = "Tables (VLM → table)" if self.use_vlm else "Tables (cropped)"
        figures_desc = "Figures (cropped)"

        with ExitStack() as stack:
            is_notebook = "ipykernel" in sys.modules or "jupyter" in sys.modules
            if is_notebook:
                charts_bar = stack.enter_context(
                    create_notebook_friendly_bar(total=chart_count, desc=charts_desc)) if chart_count else None
                tables_bar = stack.enter_context(
                    create_notebook_friendly_bar(total=table_count, desc=tables_desc)) if table_count else None
                figures_bar = stack.enter_context(
                    create_notebook_friendly_bar(total=fig_count, desc=figures_desc)) if fig_count else None
            else:
                charts_bar = stack.enter_context(
                    create_beautiful_progress_bar(total=chart_count, desc=charts_desc, leave=True)) if chart_count else None
                tables_bar = stack.enter_context(
                    create_beautiful_progress_bar(total=table_count, desc=tables_desc, leave=True)) if table_count else None
                figures_bar = stack.enter_context(
                    create_beautiful_progress_bar(total=fig_count, desc=figures_desc, leave=True)) if fig_count else None

            # Initialize page content for all pages first
            for page_num in range(1, len(pil_pages) + 1):
                page_content[page_num] = [f"# Page {page_num} Content\n"]
            
            for p in pages:
                page_num = p.page_index
                page_img: Image.Image = pil_pages[page_num - 1]
                md_lines.append(f"\n## Page {page_num}\n")

                for i, box in enumerate(sorted(p.boxes, key=reading_order_key), start=1):
                    if box.label in EXCLUDE_LABELS:
                        img_path = save_box_image(page_img, box, out_dir, page_num, i, IMAGE_SUBDIRS)
                        abs_img_path = os.path.abspath(img_path)
                        rel = os.path.relpath(abs_img_path, out_dir)

                        if box.label == "figure":
                            figure_line = f"![Figure — page {page_num}]({rel})\n"
                            md_lines.append(figure_line)
                            page_content[page_num].append(figure_line)
                            if figures_bar: figures_bar.update(1)

                        elif box.label == "chart":
                            if self.use_vlm and self.vlm:
                                wrote_table = False
                                try:
                                    chart = self.vlm.extract_chart(abs_img_path)
                                    item = to_structured_dict(chart)
                                    if item:
                                        # Add page and type information to structured item
                                        item["page"] = page_num
                                        item["type"] = "Chart"
                                        structured_items.append(item)
                                        table_content = render_markdown_table(item.get("headers"), item.get("rows"),
                                                                  title=item.get("title"))
                                        md_lines.append(table_content)
                                        page_content[page_num].append(table_content)
                                        wrote_table = True
                                except Exception as e:
                                    pass
                                if not wrote_table:
                                    chart_line = f"![Chart — page {page_num}]({rel})\n"
                                    md_lines.append(chart_line)
                                    page_content[page_num].append(chart_line)
                            else:
                                chart_line = f"![Chart — page {page_num}]({rel})\n"
                                md_lines.append(chart_line)
                                page_content[page_num].append(chart_line)
                            if charts_bar: charts_bar.update(1)

                        elif box.label == "table":
                            if self.use_vlm and self.vlm:
                                wrote_table = False
                                try:
                                    table = self.vlm.extract_table(abs_img_path)
                                    item = to_structured_dict(table)
                                    if item:
                                        # Add page and type information to structured item
                                        item["page"] = page_num
                                        item["type"] = "Table"
                                        structured_items.append(item)
                                        table_content = render_markdown_table(item.get("headers"), item.get("rows"),
                                                                  title=item.get("title"))
                                        md_lines.append(table_content)
                                        page_content[page_num].append(table_content)
                                        wrote_table = True
                                except Exception as e:
                                    pass
                                if not wrote_table:
                                    table_line = f"![Table — page {page_num}]({rel})\n"
                                    md_lines.append(table_line)
                                    page_content[page_num].append(table_line)
                            else:
                                table_line = f"![Table — page {page_num}]({rel})\n"
                                md_lines.append(table_line)
                                page_content[page_num].append(table_line)
                            if tables_bar: tables_bar.update(1)
                    else:
                        text = ocr_box_text(self.ocr_engine, page_img, box)
                        if text:
                            md_lines.append(text)
                            md_lines.append(self.box_separator if self.box_separator else "")
                            page_content[page_num].append(text)
                            page_content[page_num].append(self.box_separator if self.box_separator else "")

        md_path = write_markdown(md_lines, out_dir)
        html_path = write_html(md_lines, out_dir)
        
        # Create pages folder and save individual page markdown files
        pages_dir = os.path.join(out_dir, "pages")
        os.makedirs(pages_dir, exist_ok=True)
        
        for page_num, content_lines in page_content.items():
            page_md_path = os.path.join(pages_dir, f"page_{page_num:03d}.md")
            write_markdown(content_lines, os.path.dirname(page_md_path), os.path.basename(page_md_path))
        
        excel_path = None
        html_structured_path = None
        if self.use_vlm and structured_items:
            excel_path = os.path.join(out_dir, "tables.xlsx")
            write_structured_excel(excel_path, structured_items)
            html_structured_path = os.path.join(out_dir, "tables.html")
            write_structured_html(html_structured_path, structured_items)

        print(f"✅ Enhanced parsing completed successfully!")
        print(f"📁 Output directory: {out_dir}")

    def _create_enhanced_pdf_from_pages(self, enhanced_pages: List[Image.Image], output_path: str) -> None:
        """
        Create an enhanced PDF from already processed enhanced pages.
        
        :param enhanced_pages: List of enhanced PIL images
        :param output_path: Path for the enhanced PDF
        """
        if not enhanced_pages:
            raise ValueError("No enhanced pages provided")
        
        try:
            # Create enhanced PDF from the processed pages
            enhanced_pages[0].save(
                output_path,
                "PDF",
                resolution=100.0,
                save_all=True,
                append_images=enhanced_pages[1:] if len(enhanced_pages) > 1 else []
            )
            print(f"✅ Enhanced PDF saved from processed pages: {output_path}")
        except Exception as e:
            print(f"❌ Error creating enhanced PDF from pages: {e}")
            raise

    def restore_pdf_only(self, pdf_path: str, output_path: str = None, task: str = None) -> str:
        """
        Apply DocRes restoration to a PDF without parsing.
        
        :param pdf_path: Path to the input PDF file
        :param output_path: Path for the enhanced PDF (if None, auto-generates)
        :param task: DocRes restoration task (if None, uses instance default)
        :return: Path to the enhanced PDF or None if failed
        """
        if not self.use_image_restoration or not self.docres_engine:
            raise RuntimeError("Image restoration is not enabled or DocRes engine is not available")
        
        task = task or self.restoration_task
        return self.docres_engine.restore_pdf(pdf_path, output_path, task, self.restoration_dpi)

    def get_restoration_info(self) -> Dict[str, Any]:
        """
        Get information about the current restoration configuration.
        
        :return: Dictionary with restoration settings and status
        """
        return {
            'enabled': self.use_image_restoration,
            'task': self.restoration_task,
            'device': self.restoration_device,
            'dpi': self.restoration_dpi,
            'engine_available': self.docres_engine is not None,
            'supported_tasks': self.docres_engine.get_supported_tasks() if self.docres_engine else []
        }
