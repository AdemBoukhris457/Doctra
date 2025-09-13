from __future__ import annotations
import os
import re
import sys
from typing import List, Dict, Any
from contextlib import ExitStack
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
from doctra.utils.pdf_io import render_pdf_to_images
from doctra.engines.layout.paddle_layout import PaddleLayoutEngine
from doctra.engines.layout.layout_models import LayoutPage
from doctra.engines.ocr import PytesseractOCREngine
from doctra.utils.constants import EXCLUDE_LABELS, IMAGE_SUBDIRS
from doctra.parsers.layout_order import reading_order_key
from doctra.utils.ocr_utils import ocr_box_text
from doctra.exporters.image_saver import save_box_image
from doctra.utils.file_ops import ensure_output_dirs
from doctra.engines.vlm.service import VLMStructuredExtractor
from doctra.exporters.excel_writer import write_structured_excel
from doctra.utils.structured_utils import to_structured_dict
from doctra.exporters.markdown_table import render_markdown_table
from doctra.exporters.markdown_writer import write_markdown
from doctra.exporters.html_writer import write_html, write_structured_html
from doctra.utils.progress import create_beautiful_progress_bar, create_multi_progress_bars, create_notebook_friendly_bar


class StructuredPDFParser:
    """
    Comprehensive PDF parser for extracting all types of content.
    
    Processes PDF documents to extract text, tables, charts, and figures.
    Supports OCR for text extraction and optional VLM processing for
    converting visual elements into structured data.

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
        Initialize the StructuredPDFParser with processing configuration.
        
        Sets up the layout detection engine, OCR engine, and optionally
        the VLM service for comprehensive document processing.

        :param use_vlm: Whether to use VLM for structured data extraction
        :param vlm_provider: VLM provider to use ("gemini", "openai", "anthropic", or "openrouter")
        :param vlm_model: Model name to use (defaults to provider-specific defaults)
        :param vlm_api_key: API key for VLM provider
        :param layout_model_name: Layout detection model name
        :param dpi: DPI for PDF rendering
        :param min_score: Minimum confidence score for layout detection
        :param ocr_lang: OCR language code
        :param ocr_psm: Tesseract page segmentation mode
        :param ocr_oem: Tesseract OCR engine mode
        :param ocr_extra_config: Additional Tesseract configuration
        :param box_separator: Separator between text boxes in output
        """
        self.layout_engine = PaddleLayoutEngine(model_name=layout_model_name)
        self.dpi = dpi
        self.min_score = min_score
        self.ocr_engine = PytesseractOCREngine(
            lang=ocr_lang, psm=ocr_psm, oem=ocr_oem, extra_config=ocr_extra_config
        )
        self.box_separator = box_separator
        self.use_vlm = use_vlm
        self.vlm = None
        if self.use_vlm:
            self.vlm = VLMStructuredExtractor(
                vlm_provider=vlm_provider,
                vlm_model=vlm_model,
                api_key=vlm_api_key,
            )

    def parse(self, pdf_path: str) -> None:
        """
        Parse a PDF document and extract all content types.
        
        Processes the PDF through layout detection, extracts text using OCR,
        saves images for visual elements, and optionally converts charts/tables
        to structured data using VLM.

        :param pdf_path: Path to the input PDF file
        :return: None
        """
        # Extract filename without extension and create output directory
        pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        out_dir = f"outputs/{pdf_filename}/full_parse"

        os.makedirs(out_dir, exist_ok=True)
        ensure_output_dirs(out_dir, IMAGE_SUBDIRS)

        pages: List[LayoutPage] = self.layout_engine.predict_pdf(
            pdf_path, batch_size=1, layout_nms=True, dpi=self.dpi, min_score=self.min_score
        )
        pil_pages = [im for (im, _, _) in render_pdf_to_images(pdf_path, dpi=self.dpi)]

        # Count for progress bars
        fig_count = sum(sum(1 for b in p.boxes if b.label == "figure") for p in pages)
        chart_count = sum(sum(1 for b in p.boxes if b.label == "chart") for p in pages)
        table_count = sum(sum(1 for b in p.boxes if b.label == "table") for p in pages)

        md_lines: List[str] = ["# Extracted Content\n"]
        structured_items: List[Dict[str, Any]] = []

        charts_desc = "Charts (VLM → table)" if self.use_vlm else "Charts (cropped)"
        tables_desc = "Tables (VLM → table)" if self.use_vlm else "Tables (cropped)"
        figures_desc = "Figures (cropped)"

        with ExitStack() as stack:
            # Enhanced environment detection
            is_notebook = "ipykernel" in sys.modules or "jupyter" in sys.modules
            is_terminal = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
            
            # Use appropriate progress bars based on environment
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
                            # Figures are always images in MD
                            md_lines.append(f"![Figure — page {page_num}]({rel})\n")
                            if figures_bar: figures_bar.update(1)

                        elif box.label == "chart":
                            if self.use_vlm and self.vlm:
                                # Try structured → Markdown table; fallback to image if it fails
                                wrote_table = False
                                try:
                                    chart = self.vlm.extract_chart(abs_img_path)
                                    item = to_structured_dict(chart)
                                    if item:
                                        structured_items.append(item)
                                        md_lines.append(
                                            render_markdown_table(item.get("headers"), item.get("rows"),
                                                                  title=item.get("title"))
                                        )
                                        wrote_table = True
                                except Exception as e:
                                    pass
                                if not wrote_table:
                                    md_lines.append(f"![Chart — page {page_num}]({rel})\n")
                            else:
                                md_lines.append(f"![Chart — page {page_num}]({rel})\n")
                            if charts_bar: charts_bar.update(1)

                        elif box.label == "table":
                            if self.use_vlm and self.vlm:
                                # Try structured → Markdown table; fallback to image if it fails
                                wrote_table = False
                                try:
                                    table = self.vlm.extract_table(abs_img_path)
                                    item = to_structured_dict(table)
                                    if item:
                                        structured_items.append(item)
                                        md_lines.append(
                                            render_markdown_table(item.get("headers"), item.get("rows"),
                                                                  title=item.get("title"))
                                        )
                                        wrote_table = True
                                except Exception as e:
                                    pass
                                if not wrote_table:
                                    md_lines.append(f"![Table — page {page_num}]({rel})\n")
                            else:
                                md_lines.append(f"![Table — page {page_num}]({rel})\n")
                            if tables_bar: tables_bar.update(1)
                    else:
                        text = ocr_box_text(self.ocr_engine, page_img, box)
                        if text:
                            md_lines.append(text)
                            md_lines.append(self.box_separator if self.box_separator else "")

        md_path = write_markdown(md_lines, out_dir)
        html_path = write_html(md_lines, out_dir)
        
        excel_path = None
        html_structured_path = None
        if self.use_vlm and structured_items:
            excel_path = os.path.join(out_dir, "tables.xlsx")
            write_structured_excel(excel_path, structured_items)
            html_structured_path = os.path.join(out_dir, "tables.html")
            write_structured_html(html_structured_path, structured_items)

        # Print completion message with output directory
        print(f"✅ Parsing completed successfully!")
        print(f"📁 Output directory: {out_dir}")

    def display_pages_with_boxes(self, pdf_path: str, num_pages: int = 3, cols: int = 2,
                                 page_width: int = 800, spacing: int = 40, save_path: str = None) -> None:
        """
        Display the first N pages of a PDF with bounding boxes and labels overlaid in a modern grid layout.
        
        Creates a visualization showing layout detection results with bounding boxes,
        labels, and confidence scores overlaid on the PDF pages in a grid format.

        :param pdf_path: Path to the input PDF file
        :param num_pages: Number of pages to display (default: 3)
        :param cols: Number of columns in the grid layout (default: 2)
        :param page_width: Width to resize each page to in pixels (default: 800)
        :param spacing: Spacing between pages in pixels (default: 40)
        :param save_path: Optional path to save the visualization (if None, displays only)
        :return: None
        """
        # Get layout predictions
        pages: List[LayoutPage] = self.layout_engine.predict_pdf(
            pdf_path, batch_size=1, layout_nms=True, dpi=self.dpi, min_score=self.min_score
        )
        pil_pages = [im for (im, _, _) in render_pdf_to_images(pdf_path, dpi=self.dpi)]

        # Limit to requested number of pages
        pages_to_show = min(num_pages, len(pages))

        if pages_to_show == 0:
            print("No pages to display")
            return

        # Calculate grid dimensions
        rows = (pages_to_show + cols - 1) // cols

        # Collect unique labels from the processed pages and assign colors
        used_labels = set()
        for idx in range(pages_to_show):
            page = pages[idx]
            for box in page.boxes:
                used_labels.add(box.label.lower())

        # Create dynamic color assignment for all detected labels
        base_colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
                       '#F97316', '#EC4899', '#6B7280', '#84CC16', '#06B6D4',
                       '#DC2626', '#059669', '#7C3AED', '#DB2777', '#0891B2']

        dynamic_label_colors = {}
        for i, label in enumerate(sorted(used_labels)):
            dynamic_label_colors[label] = base_colors[i % len(base_colors)]

        # Process each page and add bounding boxes
        processed_pages = []

        for idx in range(pages_to_show):
            page = pages[idx]
            page_img = pil_pages[idx].copy()

            # Calculate scale factor to resize to target width
            scale_factor = page_width / page_img.width
            new_height = int(page_img.height * scale_factor)
            page_img = page_img.resize((page_width, new_height), Image.LANCZOS)

            # Create drawing context
            draw = ImageDraw.Draw(page_img)

            # Try to load a nice font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", 24)
                small_font = ImageFont.truetype("arial.ttf", 18)
            except:
                try:
                    font = ImageFont.load_default()
                    small_font = ImageFont.load_default()
                except:
                    font = None
                    small_font = None

            # Draw bounding boxes
            for box in page.boxes:
                # Scale coordinates
                x1 = int(box.x1 * scale_factor)
                y1 = int(box.y1 * scale_factor)
                x2 = int(box.x2 * scale_factor)
                y2 = int(box.y2 * scale_factor)

                # Get color for this label from dynamic assignment
                color = dynamic_label_colors.get(box.label.lower(), '#000000')

                # Draw rectangle with rounded corners effect
                draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

                # Draw label background
                label_text = f"{box.label} ({box.score:.2f})"
                if font:
                    bbox = draw.textbbox((0, 0), label_text, font=small_font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                else:
                    text_width = len(label_text) * 8
                    text_height = 15

                # Position label above the box
                label_x = x1
                label_y = max(0, y1 - text_height - 8)

                # Draw label background with padding
                padding = 4
                draw.rectangle([
                    label_x - padding,
                    label_y - padding,
                    label_x + text_width + padding,
                    label_y + text_height + padding
                ], fill='white', outline=color, width=2)

                # Draw label text
                draw.text((label_x, label_y), label_text, fill=color, font=small_font)

            # Add page title
            title_text = f"Page {page.page_index} ({len(page.boxes)} boxes)"
            if font:
                title_bbox = draw.textbbox((0, 0), title_text, font=font)
                title_width = title_bbox[2] - title_bbox[0]
            else:
                title_width = len(title_text) * 12

            # Draw title background
            title_x = (page_width - title_width) // 2
            title_y = 10
            draw.rectangle([title_x - 10, title_y - 5, title_x + title_width + 10, title_y + 35],
                           fill='white', outline='#1F2937', width=2)
            draw.text((title_x, title_y), title_text, fill='#1F2937', font=font)

            processed_pages.append(page_img)

        # Create grid layout with space for legend
        legend_width = 250
        grid_width = cols * page_width + (cols - 1) * spacing
        total_width = grid_width + legend_width + spacing
        grid_height = rows * (processed_pages[0].height if processed_pages else 600) + (rows - 1) * spacing

        # Create final grid image with modern background
        final_img = Image.new('RGB', (total_width, grid_height), '#F8FAFC')

        # Place pages in grid
        for idx, page_img in enumerate(processed_pages):
            row = idx // cols
            col = idx % cols

            x_pos = col * (page_width + spacing)
            y_pos = row * (page_img.height + spacing)

            final_img.paste(page_img, (x_pos, y_pos))

        # Create legend
        legend_x = grid_width + spacing
        legend_y = 20

        draw_legend = ImageDraw.Draw(final_img)

        # Legend title
        legend_title = "Element Types"
        if font:
            title_bbox = draw_legend.textbbox((0, 0), legend_title, font=font)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
        else:
            title_width = len(legend_title) * 12
            title_height = 20

        # Draw legend background
        legend_bg_height = len(used_labels) * 35 + title_height + 40
        draw_legend.rectangle([legend_x - 10, legend_y - 10,
                               legend_x + legend_width - 10, legend_y + legend_bg_height],
                              fill='white', outline='#E5E7EB', width=2)

        # Draw legend title
        draw_legend.text((legend_x + 10, legend_y + 5), legend_title,
                         fill='#1F2937', font=font)

        # Draw legend items - now using dynamic colors for actually detected labels
        current_y = legend_y + title_height + 20

        for label in sorted(used_labels):
            color = dynamic_label_colors[label]

            # Draw color square
            square_size = 20
            draw_legend.rectangle([legend_x + 10, current_y,
                                   legend_x + 10 + square_size, current_y + square_size],
                                  fill=color, outline='#6B7280', width=1)

            # Draw label text
            draw_legend.text((legend_x + 40, current_y + 2), label.title(),
                             fill='#374151', font=small_font)

            current_y += 30

        # Save or display
        if save_path:
            final_img.save(save_path, quality=95, optimize=True)
            print(f"Layout visualization saved to: {save_path}")
        else:
            # Display using PIL's default viewer
            final_img.show()

        # Print summary statistics
        print(f"\n📊 Layout Detection Summary for {os.path.basename(pdf_path)}:")
        print(f"Pages processed: {pages_to_show}")

        # Create summary by label across all pages
        total_counts = {}
        for idx in range(pages_to_show):
            page = pages[idx]
            for box in page.boxes:
                total_counts[box.label] = total_counts.get(box.label, 0) + 1

        print("\nTotal elements detected:")
        for label, count in sorted(total_counts.items()):
            print(f"  - {label}: {count}")

        return final_img