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
from doctra.exporters.excel_writer import write_structured_excel
from doctra.utils.structured_utils import to_structured_dict
from doctra.exporters.markdown_table import render_markdown_table
from doctra.exporters.markdown_writer import write_markdown
from doctra.exporters.html_writer import write_structured_html
import json


class ChartTablePDFParser:
    """
    Specialized PDF parser for extracting charts and tables.
    
    Focuses specifically on chart and table extraction from PDF documents,
    with optional VLM (Vision Language Model) processing to convert visual
    elements into structured data.

    :param extract_charts: Whether to extract charts from the document (default: True)
    :param extract_tables: Whether to extract tables from the document (default: True)
    :param use_vlm: Whether to use VLM for structured data extraction (default: False)
    :param vlm_provider: VLM provider to use ("gemini", "openai", "anthropic", or "openrouter", default: "gemini")
    :param vlm_model: Model name to use (defaults to provider-specific defaults)
    :param vlm_api_key: API key for VLM provider (required if use_vlm is True)
    :param layout_model_name: Layout detection model name (default: "PP-DocLayout_plus-L")
    :param dpi: DPI for PDF rendering (default: 200)
    :param min_score: Minimum confidence score for layout detection (default: 0.0)
    """

    def __init__(
            self,
            *,
            extract_charts: bool = True,
            extract_tables: bool = True,
            use_vlm: bool = False,
            vlm_provider: str = "gemini",
            vlm_model: str | None = None,
            vlm_api_key: str | None = None,
            layout_model_name: str = "PP-DocLayout_plus-L",
            dpi: int = 200,
            min_score: float = 0.0,
    ):
        """
        Initialize the ChartTablePDFParser with extraction configuration.
        
        Sets up the layout detection engine and optionally the VLM service
        for structured data extraction.

        :param extract_charts: Whether to extract charts from the document
        :param extract_tables: Whether to extract tables from the document
        :param use_vlm: Whether to use VLM for structured data extraction
        :param vlm_provider: VLM provider to use ("gemini", "openai", "anthropic", or "openrouter")
        :param vlm_model: Model name to use (defaults to provider-specific defaults)
        :param vlm_api_key: API key for VLM provider
        :param layout_model_name: Layout detection model name
        :param dpi: DPI for PDF rendering
        :param min_score: Minimum confidence score for layout detection
        :raises ValueError: If neither extract_charts nor extract_tables is True
        """
        # Validation
        if not extract_charts and not extract_tables:
            raise ValueError("At least one of extract_charts or extract_tables must be True")

        self.extract_charts = extract_charts
        self.extract_tables = extract_tables
        self.layout_engine = PaddleLayoutEngine(model_name=layout_model_name)
        self.dpi = dpi
        self.min_score = min_score

        self.use_vlm = use_vlm
        self.vlm = None
        if self.use_vlm:
            self.vlm = VLMStructuredExtractor(
                vlm_provider=vlm_provider,
                vlm_model=vlm_model,
                api_key=vlm_api_key,
            )

    def parse(self, pdf_path: str, output_base_dir: str = "outputs") -> None:
        """
        Parse a PDF document and extract charts and/or tables.
        
        Processes the PDF through layout detection, extracts the specified
        element types, saves cropped images, and optionally converts them
        to structured data using VLM.

        :param pdf_path: Path to the input PDF file
        :param output_base_dir: Base directory for output files (default: "outputs")
        :return: None
        """
        # Create output directory structure: outputs/<filename>/structured_parsing/
        pdf_name = Path(pdf_path).stem
        out_dir = os.path.join(output_base_dir, pdf_name, "structured_parsing")
        os.makedirs(out_dir, exist_ok=True)

        # Create subdirectories based on what we're extracting
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

        # Determine which labels to extract
        target_labels = []
        if self.extract_charts:
            target_labels.append("chart")
        if self.extract_tables:
            target_labels.append("table")

        # Count items for progress bars
        chart_count = sum(sum(1 for b in p.boxes if b.label == "chart") for p in pages) if self.extract_charts else 0
        table_count = sum(sum(1 for b in p.boxes if b.label == "table") for p in pages) if self.extract_tables else 0

        # Prepare output content
        if self.use_vlm:
            md_lines: List[str] = ["# Extracted Charts and Tables\n"]
            structured_items: List[Dict[str, Any]] = []
            vlm_items: List[Dict[str, Any]] = []

        # Progress bar descriptions
        charts_desc = "Charts (VLM → table)" if self.use_vlm else "Charts (cropped)"
        tables_desc = "Tables (VLM → table)" if self.use_vlm else "Tables (cropped)"

        chart_counter = 1
        table_counter = 1

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
            else:
                charts_bar = stack.enter_context(
                    create_beautiful_progress_bar(total=chart_count, desc=charts_desc, leave=True)) if chart_count else None
                tables_bar = stack.enter_context(
                    create_beautiful_progress_bar(total=table_count, desc=tables_desc, leave=True)) if table_count else None

            for p in pages:
                page_num = p.page_index
                page_img: Image.Image = pil_pages[page_num - 1]

                # Only process selected item types
                target_items = [box for box in p.boxes if box.label in target_labels]

                if target_items and self.use_vlm:
                    md_lines.append(f"\n## Page {page_num}\n")

                for box in sorted(target_items, key=reading_order_key):
                    # Handle charts
                    if box.label == "chart" and self.extract_charts:
                        chart_filename = f"chart_{chart_counter:03d}.png"
                        chart_path = os.path.join(charts_dir, chart_filename)

                        # Save image
                        cropped_img = page_img.crop((box.x1, box.y1, box.x2, box.y2))
                        cropped_img.save(chart_path)

                        # Handle VLM processing if enabled
                        if self.use_vlm and self.vlm:
                            rel_path = os.path.join("charts", chart_filename)
                            wrote_table = False

                            try:
                                extracted_chart = self.vlm.extract_chart(chart_path)
                                structured_item = to_structured_dict(extracted_chart)
                                if structured_item:
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

                    # Handle tables
                    elif box.label == "table" and self.extract_tables:
                        table_filename = f"table_{table_counter:03d}.png"
                        table_path = os.path.join(tables_dir, table_filename)

                        # Save image
                        cropped_img = page_img.crop((box.x1, box.y1, box.x2, box.y2))
                        cropped_img.save(table_path)

                        # Handle VLM processing if enabled
                        if self.use_vlm and self.vlm:
                            rel_path = os.path.join("tables", table_filename)
                            wrote_table = False

                            try:
                                extracted_table = self.vlm.extract_table(table_path)
                                structured_item = to_structured_dict(extracted_table)
                                if structured_item:
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

        # Write outputs only if VLM is used
        md_path = None
        excel_path = None

        if self.use_vlm:
            # Write markdown file
            md_path = os.path.join(out_dir, "charts.md")
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(md_lines))

            # Write Excel file if we have structured data
            if structured_items:
                # Determine Excel filename based on extraction target
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
                
                # Also create HTML version
                html_filename = excel_filename.replace('.xlsx', '.html')
                html_path = os.path.join(out_dir, html_filename)
                write_structured_html(html_path, structured_items)

            # Write VLM items mapping for UI linkage
            if 'vlm_items' in locals() and vlm_items:
                with open(os.path.join(out_dir, "vlm_items.json"), 'w', encoding='utf-8') as jf:
                    json.dump(vlm_items, jf, ensure_ascii=False, indent=2)

        # Print results
        extraction_types = []
        if self.extract_charts:
            extraction_types.append("charts")
        if self.extract_tables:
            extraction_types.append("tables")
