from __future__ import annotations
import os
import re
import sys
import logging
from typing import List, Dict, Any, Union, Optional
from contextlib import ExitStack
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
from doctra.utils.pdf_io import render_pdf_to_images
from doctra.engines.layout.paddle_layout import PaddleLayoutEngine
from doctra.engines.layout.layout_models import LayoutPage
from doctra.engines.ocr import PytesseractOCREngine, PaddleOCREngine
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
from doctra.exporters.html_writer import write_html, write_structured_html, render_html_table, write_html_from_lines
from doctra.utils.progress import create_beautiful_progress_bar, create_multi_progress_bars, create_notebook_friendly_bar
from doctra.parsers.split_table_detector import SplitTableDetector, SplitTableMatch


class StructuredPDFParser:
    """
    Comprehensive PDF parser for extracting all types of content.
    
    Processes PDF documents to extract text, tables, charts, and figures.
    Supports OCR for text extraction and optional VLM processing for
    converting visual elements into structured data.
    
    Features automatic detection and merging of tables split across pages
    using proximity detection and LSD-based structure analysis.

    :param use_vlm: Whether to use VLM for structured data extraction (default: False)
    :param vlm_provider: VLM provider to use ("gemini", "openai", "anthropic", or "openrouter", default: "gemini")
    :param vlm_model: Model name to use (defaults to provider-specific defaults)
    :param vlm_api_key: API key for VLM provider (required if use_vlm is True)
    :param layout_model_name: Layout detection model name (default: "PP-DocLayout_plus-L")
    :param dpi: DPI for PDF rendering (default: 200)
    :param min_score: Minimum confidence score for layout detection (default: 0.0)
    :param ocr_engine: OCR engine instance (PytesseractOCREngine or PaddleOCREngine). 
                       If None, creates a default PytesseractOCREngine with lang="eng", psm=4, oem=3.
    :param box_separator: Separator between text boxes in output (default: "\n")
    :param merge_split_tables: Whether to detect and merge split tables (default: False)
    :param bottom_threshold_ratio: Ratio for "too close to bottom" detection (default: 0.20)
    :param top_threshold_ratio: Ratio for "too close to top" detection (default: 0.10)
    :param max_gap_ratio: Maximum allowed gap between tables (default: 0.05)
    :param column_alignment_tolerance: Pixel tolerance for column alignment (default: 10.0)
    :param min_merge_confidence: Minimum confidence score for merging (default: 0.7)
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
            ocr_engine: Optional[Union[PytesseractOCREngine, PaddleOCREngine]] = None,
            box_separator: str = "\n",
            merge_split_tables: bool = False,
            bottom_threshold_ratio: float = 0.20,
            top_threshold_ratio: float = 0.15,
            max_gap_ratio: float = 0.25,
            column_alignment_tolerance: float = 10.0,
            min_merge_confidence: float = 0.65,
    ):
        """
        Initialize the StructuredPDFParser with processing configuration.
        
        Also suppresses noisy DEBUG logs from external libraries.

        :param use_vlm: Whether to use VLM for structured data extraction (default: False)
        :param vlm_provider: VLM provider to use ("gemini", "openai", "anthropic", or "openrouter", default: "gemini")
        :param vlm_model: Model name to use (defaults to provider-specific defaults)
        :param vlm_api_key: API key for VLM provider (required if use_vlm is True)
        :param layout_model_name: Layout detection model name (default: "PP-DocLayout_plus-L")
        :param dpi: DPI for PDF rendering (default: 200)
        :param min_score: Minimum confidence score for layout detection (default: 0.0)
        :param ocr_engine: OCR engine instance (PytesseractOCREngine or PaddleOCREngine).
                           If None, creates a default PytesseractOCREngine with lang="eng", psm=4, oem=3.
        :param box_separator: Separator between text boxes in output (default: "\n")
        :param merge_split_tables: Whether to detect and merge split tables (default: False)
        :param bottom_threshold_ratio: Ratio for "too close to bottom" detection (default: 0.20)
        :param top_threshold_ratio: Ratio for "too close to top" detection (default: 0.15)
        :param max_gap_ratio: Maximum allowed gap between tables (default: 0.25, accounts for headers/footers)
        :param column_alignment_tolerance: Pixel tolerance for column alignment (default: 10.0)
        :param min_merge_confidence: Minimum confidence score for merging (default: 0.65)
        """
        self.layout_engine = PaddleLayoutEngine(model_name=layout_model_name)
        self.dpi = dpi
        self.min_score = min_score
        
        # Initialize OCR engine - use provided instance or create default
        if ocr_engine is None:
            self.ocr_engine = PytesseractOCREngine(lang="eng", psm=4, oem=3)
        elif isinstance(ocr_engine, (PytesseractOCREngine, PaddleOCREngine)):
            self.ocr_engine = ocr_engine
        else:
            raise TypeError(
                f"ocr_engine must be an instance of PytesseractOCREngine or PaddleOCREngine, "
                f"got {type(ocr_engine).__name__}"
            )
        
        self.box_separator = box_separator
        self.use_vlm = use_vlm
        self.vlm = None
        if self.use_vlm:
            try:
                self.vlm = VLMStructuredExtractor(
                    vlm_provider=vlm_provider,
                    vlm_model=vlm_model,
                    api_key=vlm_api_key,
                )
            except Exception as e:
                self.vlm = None
        
        self.merge_split_tables = merge_split_tables
        if self.merge_split_tables:
            self.split_table_detector = SplitTableDetector(
                bottom_threshold_ratio=bottom_threshold_ratio,
                top_threshold_ratio=top_threshold_ratio,
                max_gap_ratio=max_gap_ratio,
                column_alignment_tolerance=column_alignment_tolerance,
                min_merge_confidence=min_merge_confidence,
            )
        else:
            self.split_table_detector = None
        
        # Suppress noisy DEBUG logs from external libraries
        logging.getLogger('pytesseract').setLevel(logging.WARNING)
        logging.getLogger('markdown_it').setLevel(logging.WARNING)

    def parse(self, pdf_path: str) -> None:
        """
        Parse a PDF document and extract all content types.

        :param pdf_path: Path to the input PDF file
        :return: None
        """
        pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        out_dir = f"outputs/{pdf_filename}/full_parse"

        os.makedirs(out_dir, exist_ok=True)
        ensure_output_dirs(out_dir, IMAGE_SUBDIRS)

        pages: List[LayoutPage] = self.layout_engine.predict_pdf(
            pdf_path, batch_size=1, layout_nms=True, dpi=self.dpi, min_score=self.min_score
        )
        pil_pages = [im for (im, _, _) in render_pdf_to_images(pdf_path, dpi=self.dpi)]

        split_table_matches: List[SplitTableMatch] = []
        merged_table_segments = []
        
        if self.merge_split_tables and self.split_table_detector:
            try:
                split_table_matches = self.split_table_detector.detect_split_tables(pages, pil_pages)
                for match in split_table_matches:
                    merged_table_segments.append(match.segment1)
                    merged_table_segments.append(match.segment2)
            except Exception as e:
                import traceback
                traceback.print_exc()
                split_table_matches = []

        fig_count = sum(sum(1 for b in p.boxes if b.label == "figure") for p in pages)
        chart_count = sum(sum(1 for b in p.boxes if b.label == "chart") for p in pages)
        table_count = sum(sum(1 for b in p.boxes if b.label == "table") for p in pages)

        md_lines: List[str] = ["# Extracted Content\n"]
        html_lines: List[str] = ["<h1>Extracted Content</h1>"]
        structured_items: List[Dict[str, Any]] = []

        charts_desc = "Charts (VLM → table)" if self.use_vlm else "Charts (cropped)"
        tables_desc = "Tables (VLM → table)" if self.use_vlm else "Tables (cropped)"
        figures_desc = "Figures (cropped)"

        with ExitStack() as stack:
            is_notebook = "ipykernel" in sys.modules or "jupyter" in sys.modules
            is_terminal = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
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
                html_lines.append(f"<h2>Page {page_num}</h2>")

                for i, box in enumerate(sorted(p.boxes, key=reading_order_key), start=1):
                    if box.label in EXCLUDE_LABELS:
                        img_path = save_box_image(page_img, box, out_dir, page_num, i, IMAGE_SUBDIRS)
                        abs_img_path = os.path.abspath(img_path)
                        rel = os.path.relpath(abs_img_path, out_dir)

                        if box.label == "figure":
                            figure_md = f"![Figure — page {page_num}]({rel})\n"
                            figure_html = f'<img src="{rel}" alt="Figure — page {page_num}" />'
                            md_lines.append(figure_md)
                            html_lines.append(figure_html)
                            if figures_bar: figures_bar.update(1)

                        elif box.label == "chart":
                            if self.use_vlm and self.vlm:
                                wrote_table = False
                                try:
                                    chart = self.vlm.extract_chart(abs_img_path)
                                    item = to_structured_dict(chart)
                                    if item:
                                        item["page"] = page_num
                                        item["type"] = "Chart"
                                        structured_items.append(item)
                                        
                                        table_md = render_markdown_table(item.get("headers"), item.get("rows"),
                                                                         title=item.get("title"))
                                        table_html = render_html_table(item.get("headers"), item.get("rows"),
                                                                       title=item.get("title"))
                                        
                                        md_lines.append(table_md)
                                        html_lines.append(table_html)
                                        wrote_table = True
                                except Exception as e:
                                    pass
                                if not wrote_table:
                                    chart_md = f"![Chart — page {page_num}]({rel})\n"
                                    chart_html = f'<img src="{rel}" alt="Chart — page {page_num}" />'
                                    md_lines.append(chart_md)
                                    html_lines.append(chart_html)
                            else:
                                chart_md = f"![Chart — page {page_num}]({rel})\n"
                                chart_html = f'<img src="{rel}" alt="Chart — page {page_num}" />'
                                md_lines.append(chart_md)
                                html_lines.append(chart_html)
                            if charts_bar: charts_bar.update(1)

                        elif box.label == "table":
                            is_merged = any(seg.match_box(box, page_num) for seg in merged_table_segments)
                            if is_merged:
                                continue
                            
                            if self.use_vlm and self.vlm:
                                wrote_table = False
                                try:
                                    table = self.vlm.extract_table(abs_img_path)
                                    item = to_structured_dict(table)
                                    if item:
                                        item["page"] = page_num
                                        item["type"] = "Table"
                                        structured_items.append(item)
                                        
                                        table_md = render_markdown_table(item.get("headers"), item.get("rows"),
                                                                         title=item.get("title"))
                                        table_html = render_html_table(item.get("headers"), item.get("rows"),
                                                                       title=item.get("title"))
                                        
                                        md_lines.append(table_md)
                                        html_lines.append(table_html)
                                        wrote_table = True
                                except Exception as e:
                                    pass
                                if not wrote_table:
                                    table_md = f"![Table — page {page_num}]({rel})\n"
                                    table_html = f'<img src="{rel}" alt="Table — page {page_num}" />'
                                    md_lines.append(table_md)
                                    html_lines.append(table_html)
                            else:
                                table_md = f"![Table — page {page_num}]({rel})\n"
                                table_html = f'<img src="{rel}" alt="Table — page {page_num}" />'
                                md_lines.append(table_md)
                                html_lines.append(table_html)
                            if tables_bar: tables_bar.update(1)
                    else:
                        text = ocr_box_text(self.ocr_engine, page_img, box)
                        if text:
                            md_lines.append(text)
                            md_lines.append(self.box_separator if self.box_separator else "")
                            html_text = text.replace('\n', '<br>')
                            html_lines.append(f"<p>{html_text}</p>")
                            if self.box_separator:
                                html_lines.append("<br>")

            if split_table_matches and self.split_table_detector:
                for match_idx, match in enumerate(split_table_matches):
                    try:
                        merged_img = self.split_table_detector.merge_table_images(match)
                        
                        tables_dir = os.path.join(out_dir, "tables")
                        os.makedirs(tables_dir, exist_ok=True)
                        merged_filename = f"merged_table_{match.segment1.page_index}_{match.segment2.page_index}.png"
                        merged_path = os.path.join(tables_dir, merged_filename)
                        merged_img.save(merged_path)
                        
                        abs_merged_path = os.path.abspath(merged_path)
                        rel_merged = os.path.relpath(abs_merged_path, out_dir)
                        
                        pages_str = f"pages {match.segment1.page_index}-{match.segment2.page_index}"
                        
                        if self.use_vlm and self.vlm:
                            wrote_table = False
                            try:
                                table = self.vlm.extract_table(abs_merged_path)
                                item = to_structured_dict(table)
                                if item:
                                    item["page"] = f"{match.segment1.page_index}-{match.segment2.page_index}"
                                    item["type"] = "Table (Merged)"
                                    item["split_merge"] = True
                                    item["merge_confidence"] = match.confidence
                                    structured_items.append(item)
                                    
                                    table_md = render_markdown_table(
                                        item.get("headers"), 
                                        item.get("rows"),
                                        title=item.get("title") or f"Merged Table ({pages_str})"
                                    )
                                    table_html = render_html_table(
                                        item.get("headers"), 
                                        item.get("rows"),
                                        title=item.get("title") or f"Merged Table ({pages_str})"
                                    )
                                    
                                    md_lines.append(f"\n### Merged Table ({pages_str})\n")
                                    md_lines.append(table_md)
                                    html_lines.append(f'<h3>Merged Table ({pages_str})</h3>')
                                    html_lines.append(table_html)
                                    wrote_table = True
                            except Exception as e:
                                pass
                            
                            if not wrote_table:
                                table_md = f"![Merged Table — {pages_str}]({rel_merged})\n"
                                table_html = f'<img src="{rel_merged}" alt="Merged Table — {pages_str}" />'
                                md_lines.append(f"\n### Merged Table ({pages_str})\n")
                                md_lines.append(table_md)
                                html_lines.append(f'<h3>Merged Table ({pages_str})</h3>')
                                html_lines.append(table_html)
                        else:
                            table_md = f"![Merged Table — {pages_str}]({rel_merged})\n"
                            table_html = f'<img src="{rel_merged}" alt="Merged Table — {pages_str}" />'
                            md_lines.append(f"\n### Merged Table ({pages_str})\n")
                            md_lines.append(table_md)
                            html_lines.append(f'<h3>Merged Table ({pages_str})</h3>')
                            html_lines.append(table_html)
                        
                        if tables_bar: tables_bar.update(1)
                        
                    except Exception as e:
                        print(f"⚠️  Warning: Failed to merge table {match_idx + 1}: {e}")

        md_path = write_markdown(md_lines, out_dir)
        
        if self.use_vlm and html_lines:
            html_path = write_html_from_lines(html_lines, out_dir)
        else:
            html_path = write_html(md_lines, out_dir)
        
        excel_path = None
        html_structured_path = None
        if self.use_vlm and structured_items:
            excel_path = os.path.join(out_dir, "tables.xlsx")
            write_structured_excel(excel_path, structured_items)
            html_structured_path = os.path.join(out_dir, "tables.html")
            write_structured_html(html_structured_path, structured_items)

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
        pages: List[LayoutPage] = self.layout_engine.predict_pdf(
            pdf_path, batch_size=1, layout_nms=True, dpi=self.dpi, min_score=self.min_score
        )
        pil_pages = [im for (im, _, _) in render_pdf_to_images(pdf_path, dpi=self.dpi)]

        pages_to_show = min(num_pages, len(pages))

        if pages_to_show == 0:
            print("No pages to display")
            return

        rows = (pages_to_show + cols - 1) // cols

        used_labels = set()
        for idx in range(pages_to_show):
            page = pages[idx]
            for box in page.boxes:
                used_labels.add(box.label.lower())

        base_colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
                       '#F97316', '#EC4899', '#6B7280', '#84CC16', '#06B6D4',
                       '#DC2626', '#059669', '#7C3AED', '#DB2777', '#0891B2']

        dynamic_label_colors = {}
        for i, label in enumerate(sorted(used_labels)):
            dynamic_label_colors[label] = base_colors[i % len(base_colors)]

        processed_pages = []

        for idx in range(pages_to_show):
            page = pages[idx]
            page_img = pil_pages[idx].copy()

            scale_factor = page_width / page_img.width
            new_height = int(page_img.height * scale_factor)
            page_img = page_img.resize((page_width, new_height), Image.LANCZOS)

            draw = ImageDraw.Draw(page_img)

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

            for box in page.boxes:
                x1 = int(box.x1 * scale_factor)
                y1 = int(box.y1 * scale_factor)
                x2 = int(box.x2 * scale_factor)
                y2 = int(box.y2 * scale_factor)

                color = dynamic_label_colors.get(box.label.lower(), '#000000')

                draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

                label_text = f"{box.label} ({box.score:.2f})"
                if font:
                    bbox = draw.textbbox((0, 0), label_text, font=small_font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                else:
                    text_width = len(label_text) * 8
                    text_height = 15

                label_x = x1
                label_y = max(0, y1 - text_height - 8)

                padding = 4
                draw.rectangle([
                    label_x - padding,
                    label_y - padding,
                    label_x + text_width + padding,
                    label_y + text_height + padding
                ], fill='white', outline=color, width=2)

                draw.text((label_x, label_y), label_text, fill=color, font=small_font)

            title_text = f"Page {page.page_index} ({len(page.boxes)} boxes)"
            if font:
                title_bbox = draw.textbbox((0, 0), title_text, font=font)
                title_width = title_bbox[2] - title_bbox[0]
            else:
                title_width = len(title_text) * 12

            title_x = (page_width - title_width) // 2
            title_y = 10
            draw.rectangle([title_x - 10, title_y - 5, title_x + title_width + 10, title_y + 35],
                           fill='white', outline='#1F2937', width=2)
            draw.text((title_x, title_y), title_text, fill='#1F2937', font=font)

            processed_pages.append(page_img)

        legend_width = 250
        grid_width = cols * page_width + (cols - 1) * spacing
        total_width = grid_width + legend_width + spacing
        grid_height = rows * (processed_pages[0].height if processed_pages else 600) + (rows - 1) * spacing

        final_img = Image.new('RGB', (total_width, grid_height), '#F8FAFC')

        for idx, page_img in enumerate(processed_pages):
            row = idx // cols
            col = idx % cols

            x_pos = col * (page_width + spacing)
            y_pos = row * (page_img.height + spacing)

            final_img.paste(page_img, (x_pos, y_pos))

        legend_x = grid_width + spacing
        legend_y = 20

        draw_legend = ImageDraw.Draw(final_img)

        legend_title = "Element Types"
        if font:
            title_bbox = draw_legend.textbbox((0, 0), legend_title, font=font)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
        else:
            title_width = len(legend_title) * 12
            title_height = 20

        legend_bg_height = len(used_labels) * 35 + title_height + 40
        draw_legend.rectangle([legend_x - 10, legend_y - 10,
                               legend_x + legend_width - 10, legend_y + legend_bg_height],
                              fill='white', outline='#E5E7EB', width=2)

        draw_legend.text((legend_x + 10, legend_y + 5), legend_title,
                         fill='#1F2937', font=font)

        current_y = legend_y + title_height + 20

        for label in sorted(used_labels):
            color = dynamic_label_colors[label]

            square_size = 20
            draw_legend.rectangle([legend_x + 10, current_y,
                                   legend_x + 10 + square_size, current_y + square_size],
                                  fill=color, outline='#6B7280', width=1)

            draw_legend.text((legend_x + 40, current_y + 2), label.title(),
                             fill='#374151', font=small_font)

            current_y += 30

        if save_path:
            final_img.save(save_path, quality=95, optimize=True)
            print(f"Layout visualization saved to: {save_path}")
        else:
            final_img.show()

        print(f"\n📊 Layout Detection Summary for {os.path.basename(pdf_path)}:")
        print(f"Pages processed: {pages_to_show}")

        total_counts = {}
        for idx in range(pages_to_show):
            page = pages[idx]
            for box in page.boxes:
                total_counts[box.label] = total_counts.get(box.label, 0) + 1

        print("\nTotal elements detected:")
        for label, count in sorted(total_counts.items()):
            print(f"  - {label}: {count}")

        return final_img