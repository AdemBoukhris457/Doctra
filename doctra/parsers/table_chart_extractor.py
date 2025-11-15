from __future__ import annotations

import os
import sys
from typing import List, Dict, Any
from contextlib import ExitStack
from pathlib import Path

from PIL import Image
from tqdm import tqdm

from doctra.utils.pdf_io import render_pdf_to_images
from doctra.utils.progress import create_beautiful_progress_bar, create_multi_progress_bars, create_notebook_friendly_bar
from doctra.engines.layout.paddle_layout import PaddleLayoutEngine
from doctra.engines.layout.layout_models import LayoutPage

from doctra.parsers.layout_order import reading_order_key
from doctra.exporters.image_saver import save_box_image
from doctra.utils.file_ops import ensure_output_dirs

from doctra.engines.vlm.service import VLMStructuredExtractor
from typing import Optional
from doctra.exporters.excel_writer import write_structured_excel
from doctra.utils.structured_utils import to_structured_dict
from doctra.exporters.markdown_table import render_markdown_table
from doctra.exporters.markdown_writer import write_markdown
from doctra.exporters.html_writer import write_structured_html, render_html_table
from doctra.parsers.split_table_detector import SplitTableDetector, SplitTableMatch
import json


class ChartTablePDFParser:
    """
    Specialized PDF parser for extracting charts and tables.
    
    Focuses specifically on chart and table extraction from PDF documents,
    with optional VLM (Vision Language Model) processing to convert visual
    elements into structured data.

    :param extract_charts: Whether to extract charts from the document (default: True)
    :param extract_tables: Whether to extract tables from the document (default: True)
    :param vlm: VLM engine instance (VLMStructuredExtractor). If None, VLM processing is disabled.
    :param layout_model_name: Layout detection model name (default: "PP-DocLayout_plus-L")
    :param dpi: DPI for PDF rendering (default: 200)
    :param min_score: Minimum confidence score for layout detection (default: 0.0)
    :param merge_split_tables: Whether to detect and merge split tables (default: False)
    :param bottom_threshold_ratio: Ratio for "too close to bottom" detection (default: 0.20)
    :param top_threshold_ratio: Ratio for "too close to top" detection (default: 0.15)
    :param max_gap_ratio: Maximum allowed gap between tables (default: 0.25, accounts for headers/footers)
    :param column_alignment_tolerance: Pixel tolerance for column alignment (default: 10.0)
    :param min_merge_confidence: Minimum confidence score for merging (default: 0.65)
    """

    def __init__(
            self,
            *,
            extract_charts: bool = True,
            extract_tables: bool = True,
            vlm: Optional[VLMStructuredExtractor] = None,
            layout_model_name: str = "PP-DocLayout_plus-L",
            dpi: int = 200,
            min_score: float = 0.0,
            merge_split_tables: bool = False,
            bottom_threshold_ratio: float = 0.20,
            top_threshold_ratio: float = 0.15,
            max_gap_ratio: float = 0.25,
            column_alignment_tolerance: float = 10.0,
            min_merge_confidence: float = 0.65,
    ):
        """
        Initialize the ChartTablePDFParser with extraction configuration.

        :param extract_charts: Whether to extract charts from the document (default: True)
        :param extract_tables: Whether to extract tables from the document (default: True)
        :param vlm: VLM engine instance (VLMStructuredExtractor). If None, VLM processing is disabled.
        :param layout_model_name: Layout detection model name (default: "PP-DocLayout_plus-L")
        :param dpi: DPI for PDF rendering (default: 200)
        :param min_score: Minimum confidence score for layout detection (default: 0.0)
        :param merge_split_tables: Whether to detect and merge split tables (default: False)
        :param bottom_threshold_ratio: Ratio for "too close to bottom" detection (default: 0.20)
        :param top_threshold_ratio: Ratio for "too close to top" detection (default: 0.15)
        :param max_gap_ratio: Maximum allowed gap between tables (default: 0.25, accounts for headers/footers)
        :param column_alignment_tolerance: Pixel tolerance for column alignment (default: 10.0)
        :param min_merge_confidence: Minimum confidence score for merging (default: 0.65)
        """
        if not extract_charts and not extract_tables:
            raise ValueError("At least one of extract_charts or extract_tables must be True")

        self.extract_charts = extract_charts
        self.extract_tables = extract_tables
        self.layout_engine = PaddleLayoutEngine(model_name=layout_model_name)
        self.dpi = dpi
        self.min_score = min_score

        # Initialize VLM engine - use provided instance or None
        if vlm is None:
            self.vlm = None
        elif isinstance(vlm, VLMStructuredExtractor):
            self.vlm = vlm
        else:
            raise TypeError(
                f"vlm must be an instance of VLMStructuredExtractor or None, "
                f"got {type(vlm).__name__}"
            )
        
        # Initialize split table detector if enabled
        self.merge_split_tables = merge_split_tables
        if self.merge_split_tables and self.extract_tables:
            self.split_table_detector = SplitTableDetector(
                bottom_threshold_ratio=bottom_threshold_ratio,
                top_threshold_ratio=top_threshold_ratio,
                max_gap_ratio=max_gap_ratio,
                column_alignment_tolerance=column_alignment_tolerance,
                min_merge_confidence=min_merge_confidence,
            )
        else:
            self.split_table_detector = None

    def parse(self, pdf_path: str, output_base_dir: str = "outputs") -> None:
        """
        Parse a PDF document and extract charts and/or tables.

        :param pdf_path: Path to the input PDF file
        :param output_base_dir: Base directory for output files (default: "outputs")
        :return: None
        """
        pdf_name = Path(pdf_path).stem
        out_dir = os.path.join(output_base_dir, pdf_name, "structured_parsing")
        os.makedirs(out_dir, exist_ok=True)

        charts_dir = None
        tables_dir = None

        if self.extract_charts:
            charts_dir = os.path.join(out_dir, "charts")
            os.makedirs(charts_dir, exist_ok=True)

        if self.extract_tables:
            tables_dir = os.path.join(out_dir, "tables")
            os.makedirs(tables_dir, exist_ok=True)

        pages: List[LayoutPage] = self.layout_engine.predict_pdf(
            pdf_path, batch_size=1, layout_nms=True, dpi=self.dpi, min_score=self.min_score
        )
        pil_pages = [im for (im, _, _) in render_pdf_to_images(pdf_path, dpi=self.dpi)]

        # Detect split tables if enabled
        split_table_matches: List[SplitTableMatch] = []
        merged_table_segments = []
        
        if self.merge_split_tables and self.extract_tables:
            if self.split_table_detector:
                try:
                    split_table_matches = self.split_table_detector.detect_split_tables(pages, pil_pages)
                    if split_table_matches:
                        print(f"🔗 Detected {len(split_table_matches)} split table(s) to merge")
                    for match in split_table_matches:
                        merged_table_segments.append(match.segment1)
                        merged_table_segments.append(match.segment2)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    split_table_matches = []

        target_labels = []
        if self.extract_charts:
            target_labels.append("chart")
        if self.extract_tables:
            target_labels.append("table")

        chart_count = sum(sum(1 for b in p.boxes if b.label == "chart") for p in pages) if self.extract_charts else 0
        table_count = sum(sum(1 for b in p.boxes if b.label == "table") for p in pages) if self.extract_tables else 0

        if self.vlm is not None:
            md_lines: List[str] = ["# Extracted Charts and Tables\n"]
            structured_items: List[Dict[str, Any]] = []
            vlm_items: List[Dict[str, Any]] = []

        charts_desc = "Charts (VLM → table)" if self.vlm is not None else "Charts (cropped)"
        tables_desc = "Tables (VLM → table)" if self.vlm is not None else "Tables (cropped)"

        chart_counter = 1
        table_counter = 1

        with ExitStack() as stack:
            is_notebook = "ipykernel" in sys.modules or "jupyter" in sys.modules
            is_terminal = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
            
            if is_notebook:
                charts_bar = stack.enter_context(
                    create_notebook_friendly_bar(total=chart_count, desc=charts_desc)) if chart_count else None
                tables_bar = stack.enter_context(
                    create_notebook_friendly_bar(total=table_count, desc=tables_desc)) if table_count else None
            else:
                charts_bar = stack.enter_context(
                    create_beautiful_progress_bar(total=chart_count, desc=charts_desc, leave=True)) if chart_count else None
                tables_bar = stack.enter_context(
                    create_beautiful_progress_bar(total=table_count, desc=tables_desc, leave=True)) if table_count else None

            for p in pages:
                page_num = p.page_index
                page_img: Image.Image = pil_pages[page_num - 1]

                target_items = [box for box in p.boxes if box.label in target_labels]

                if target_items and self.vlm is not None:
                    md_lines.append(f"\n## Page {page_num}\n")

                for box in sorted(target_items, key=reading_order_key):
                    if box.label == "chart" and self.extract_charts:
                        chart_filename = f"chart_{chart_counter:03d}.png"
                        chart_path = os.path.join(charts_dir, chart_filename)

                        cropped_img = page_img.crop((box.x1, box.y1, box.x2, box.y2))
                        cropped_img.save(chart_path)

                        if self.vlm is not None:
                            rel_path = os.path.join("charts", chart_filename)
                            wrote_table = False

                            try:
                                extracted_chart = self.vlm.extract_chart(chart_path)
                                structured_item = to_structured_dict(extracted_chart)
                                if structured_item:
                                    structured_item["page"] = page_num
                                    structured_item["type"] = "Chart"
                                    structured_items.append(structured_item)
                                    vlm_items.append({
                                        "kind": "chart",
                                        "page": page_num,
                                        "image_rel_path": rel_path,
                                        "title": structured_item.get("title"),
                                        "headers": structured_item.get("headers"),
                                        "rows": structured_item.get("rows"),
                                    })
                                    md_lines.append(
                                        render_markdown_table(
                                            structured_item.get("headers"),
                                            structured_item.get("rows"),
                                            title=structured_item.get(
                                                "title") or f"Chart {chart_counter} — page {page_num}"
                                        )
                                    )
                                    wrote_table = True
                            except Exception:
                                pass

                            if not wrote_table:
                                md_lines.append(f"![Chart {chart_counter} — page {page_num}]({rel_path})\n")

                        chart_counter += 1
                        if charts_bar:
                            charts_bar.update(1)

                    elif box.label == "table" and self.extract_tables:
                        # Skip table segments that are part of merged tables
                        is_merged = any(seg.match_box(box, page_num) for seg in merged_table_segments)
                        if is_merged:
                            continue
                        
                        table_filename = f"table_{table_counter:03d}.png"
                        table_path = os.path.join(tables_dir, table_filename)

                        cropped_img = page_img.crop((box.x1, box.y1, box.x2, box.y2))
                        cropped_img.save(table_path)

                        if self.vlm is not None:
                            rel_path = os.path.join("tables", table_filename)
                            wrote_table = False

                            try:
                                extracted_table = self.vlm.extract_table(table_path)
                                structured_item = to_structured_dict(extracted_table)
                                if structured_item:
                                    structured_item["page"] = page_num
                                    structured_item["type"] = "Table"
                                    structured_items.append(structured_item)
                                    vlm_items.append({
                                        "kind": "table",
                                        "page": page_num,
                                        "image_rel_path": rel_path,
                                        "title": structured_item.get("title"),
                                        "headers": structured_item.get("headers"),
                                        "rows": structured_item.get("rows"),
                                    })
                                    md_lines.append(
                                        render_markdown_table(
                                            structured_item.get("headers"),
                                            structured_item.get("rows"),
                                            title=structured_item.get(
                                                "title") or f"Table {table_counter} — page {page_num}"
                                        )
                                    )
                                    wrote_table = True
                            except Exception:
                                pass

                            if not wrote_table:
                                md_lines.append(f"![Table {table_counter} — page {page_num}]({rel_path})\n")

                        table_counter += 1
                        if tables_bar:
                            tables_bar.update(1)

        # Process merged tables if any were detected
        if split_table_matches and self.split_table_detector and self.extract_tables:
            for match_idx, match in enumerate(split_table_matches):
                try:
                    merged_img = self.split_table_detector.merge_table_images(match)
                    
                    merged_filename = f"merged_table_{match.segment1.page_index}_{match.segment2.page_index}.png"
                    merged_path = os.path.join(tables_dir, merged_filename)
                    merged_img.save(merged_path)
                    
                    abs_merged_path = os.path.abspath(merged_path)
                    rel_merged = os.path.relpath(abs_merged_path, out_dir)
                    
                    pages_str = f"pages {match.segment1.page_index}-{match.segment2.page_index}"
                    
                    if self.vlm is not None:
                        wrote_table = False
                        try:
                            extracted_table = self.vlm.extract_table(abs_merged_path)
                            structured_item = to_structured_dict(extracted_table)
                            if structured_item:
                                structured_item["page"] = f"{match.segment1.page_index}-{match.segment2.page_index}"
                                structured_item["type"] = "Table (Merged)"
                                structured_item["split_merge"] = True
                                structured_item["merge_confidence"] = match.confidence
                                structured_items.append(structured_item)
                                
                                vlm_items.append({
                                    "kind": "table",
                                    "page": pages_str,
                                    "image_rel_path": rel_merged,
                                    "title": structured_item.get("title"),
                                    "headers": structured_item.get("headers"),
                                    "rows": structured_item.get("rows"),
                                    "split_merge": True,
                                    "merge_confidence": match.confidence,
                                })
                                
                                md_lines.append(f"\n### Merged Table ({pages_str})\n")
                                md_lines.append(
                                    render_markdown_table(
                                        structured_item.get("headers"),
                                        structured_item.get("rows"),
                                        title=structured_item.get("title") or f"Merged Table ({pages_str})"
                                    )
                                )
                                wrote_table = True
                        except Exception as e:
                            pass
                        
                        if not wrote_table:
                            md_lines.append(f"\n### Merged Table ({pages_str})\n")
                            md_lines.append(f"![Merged Table ({pages_str})]({rel_merged})\n")
                except Exception as e:
                    import traceback
                    traceback.print_exc()

        excel_path = None

        if self.vlm is not None:

            if structured_items:
                if self.extract_charts and self.extract_tables:
                    excel_filename = "parsed_tables_charts.xlsx"
                elif self.extract_charts:
                    excel_filename = "parsed_charts.xlsx"
                elif self.extract_tables:
                    excel_filename = "parsed_tables.xlsx"
                else:
                    excel_filename = "parsed_data.xlsx"  # fallback
                
                
                excel_path = os.path.join(out_dir, excel_filename)
                write_structured_excel(excel_path, structured_items)
                
                html_filename = excel_filename.replace('.xlsx', '.html')
                html_path = os.path.join(out_dir, html_filename)
                write_structured_html(html_path, structured_items)

            if 'vlm_items' in locals() and vlm_items:
                with open(os.path.join(out_dir, "vlm_items.json"), 'w', encoding='utf-8') as jf:
                    json.dump(vlm_items, jf, ensure_ascii=False, indent=2)

        extraction_types = []
        if self.extract_charts:
            extraction_types.append("charts")
        if self.extract_tables:
            extraction_types.append("tables")
        
        print(f"✅ Parsing completed successfully!")
        print(f"📁 Output directory: {out_dir}")