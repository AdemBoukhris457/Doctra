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
from doctra.utils.structured_utils import to_structured_dict, html_table_to_structured_dict
from doctra.exporters.markdown_table import render_markdown_table
from doctra.exporters.markdown_writer import write_markdown
from doctra.exporters.html_writer import write_structured_html
import json

# Try to import unitable recognize_table function
UNITABLE_IMPORT_ERROR = None
try:
    import sys
    import importlib.util
    from pathlib import Path
    
    # Get the exact path to unitable inference.py
    unitable_dir = Path(__file__).parent.parent / "third_party" / "doctra"
    inference_path = unitable_dir / "inference.py"
    
    # Use importlib to load from the specific path to avoid conflicts with docres/inference.py
    # Make sure unitable_dir is in sys.path so relative imports work
    if inference_path.exists():
        # Add unitable directory to sys.path if not already there
        # This is critical for relative imports like "from src.model import ..."
        unitable_dir_str = str(unitable_dir)
        if unitable_dir_str not in sys.path:
            sys.path.insert(0, unitable_dir_str)
        
        # Save current state
        old_cwd = Path.cwd()
        import os
        
        try:
            # Temporarily change working directory to unitable_dir for imports
            # This allows relative imports in inference.py to work correctly
            os.chdir(unitable_dir_str)
            
            # Load the module with the correct context
            spec = importlib.util.spec_from_file_location(
                "unitable_inference", 
                inference_path,
                submodule_search_locations=[unitable_dir_str]
            )
            if spec and spec.loader:
                unitable_inference = importlib.util.module_from_spec(spec)
                # Set important attributes for proper import resolution
                unitable_inference.__file__ = str(inference_path)
                unitable_inference.__name__ = "unitable_inference"
                unitable_inference.__package__ = None
                # Store in sys.modules to allow imports within the module
                sys.modules["unitable_inference"] = unitable_inference
                
                # Execute the module (this will run all imports)
                spec.loader.exec_module(unitable_inference)
                
                # Extract the recognize_table function
                recognize_table = unitable_inference.recognize_table
                UNITABLE_AVAILABLE = True
            else:
                raise ImportError("Could not create module spec for unitable inference")
        finally:
            # Always restore original working directory
            try:
                os.chdir(str(old_cwd))
            except:
                pass  # Ignore errors restoring directory
    else:
        raise ImportError(f"UniTable inference.py not found at {inference_path}")
except (ImportError, Exception) as e:
    UNITABLE_AVAILABLE = False
    recognize_table = None
    UNITABLE_IMPORT_ERROR = str(e)


class ChartTablePDFParser:
    """
    Specialized PDF parser for extracting charts and tables.
    
    Focuses specifically on chart and table extraction from PDF documents,
    with optional VLM (Vision Language Model) processing to convert visual
    elements into structured data.

    :param extract_charts: Whether to extract charts from the document (default: True)
    :param extract_tables: Whether to extract tables from the document (default: True)
    :param use_vlm: Whether to use VLM for structured data extraction (default: False)
    :param use_unitable: Whether to use UniTable for table parsing (only for tables, not charts) (default: False)
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
            use_unitable: bool = False,
            vlm_provider: str = "gemini",
            vlm_model: str | None = None,
            vlm_api_key: str | None = None,
            layout_model_name: str = "PP-DocLayout_plus-L",
            dpi: int = 200,
            min_score: float = 0.0,
    ):
        """
        Initialize the ChartTablePDFParser with extraction configuration.

        :param extract_charts: Whether to extract charts from the document (default: True)
        :param extract_tables: Whether to extract tables from the document (default: True)
        :param use_vlm: Whether to use VLM for structured data extraction (default: False)
        :param use_unitable: Whether to use UniTable for table parsing (only for tables, not charts) (default: False)
        :param vlm_provider: VLM provider to use ("gemini", "openai", "anthropic", or "openrouter", default: "gemini")
        :param vlm_model: Model name to use (defaults to provider-specific defaults)
        :param vlm_api_key: API key for VLM provider (required if use_vlm is True)
        :param layout_model_name: Layout detection model name (default: "PP-DocLayout_plus-L")
        :param dpi: DPI for PDF rendering (default: 200)
        :param min_score: Minimum confidence score for layout detection (default: 0.0)
        """
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
        
        # Set up unitable
        self.use_unitable = use_unitable and UNITABLE_AVAILABLE and extract_tables
        
        # Warn user if they requested unitable but it's not available
        if use_unitable and not UNITABLE_AVAILABLE:
            print(f"⚠️  Warning: UniTable was requested but is not available.")
            if UNITABLE_IMPORT_ERROR:
                print(f"   Import error: {UNITABLE_IMPORT_ERROR}")
                # Provide helpful installation suggestions for common missing dependencies
                if "jsonlines" in str(UNITABLE_IMPORT_ERROR):
                    print(f"   💡 Install missing dependency: pip install jsonlines")
                elif "torch" in str(UNITABLE_IMPORT_ERROR):
                    print(f"   💡 Install missing dependency: pip install torch torchvision")
                elif "tokenizers" in str(UNITABLE_IMPORT_ERROR):
                    print(f"   💡 Install missing dependency: pip install tokenizers")
                elif "No module named" in str(UNITABLE_IMPORT_ERROR):
                    # Extract the module name from the error
                    import re
                    match = re.search(r"No module named ['\"]([^'\"]+)['\"]", str(UNITABLE_IMPORT_ERROR))
                    if match:
                        module_name = match.group(1)
                        print(f"   💡 Install missing dependency: pip install {module_name}")
            print(f"   Tables will be extracted as images only.")
        
        if self.use_unitable:
            unitable_base = Path(__file__).parent.parent / "third_party" / "doctra"
            self.unitable_model_dir = unitable_base / "experiments" / "unitable_weights"
            self.unitable_vocab_dir = unitable_base / "vocab"
        else:
            self.unitable_model_dir = None
            self.unitable_vocab_dir = None

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

        target_labels = []
        if self.extract_charts:
            target_labels.append("chart")
        if self.extract_tables:
            target_labels.append("table")

        chart_count = sum(sum(1 for b in p.boxes if b.label == "chart") for p in pages) if self.extract_charts else 0
        table_count = sum(sum(1 for b in p.boxes if b.label == "table") for p in pages) if self.extract_tables else 0

        # Initialize structured extraction variables if using VLM or unitable for tables
        if self.use_vlm or self.use_unitable:
            md_lines: List[str] = ["# Extracted Charts and Tables\n"]
            structured_items: List[Dict[str, Any]] = []
            vlm_items: List[Dict[str, Any]] = []

        charts_desc = "Charts (VLM → table)" if self.use_vlm else "Charts (cropped)"
        tables_desc = "Tables (UniTable → table)" if self.use_unitable else ("Tables (VLM → table)" if self.use_vlm else "Tables (cropped)")

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

                if target_items and (self.use_vlm or self.use_unitable):
                    md_lines.append(f"\n## Page {page_num}\n")

                for box in sorted(target_items, key=reading_order_key):
                    if box.label == "chart" and self.extract_charts:
                        chart_filename = f"chart_{chart_counter:03d}.png"
                        chart_path = os.path.join(charts_dir, chart_filename)

                        cropped_img = page_img.crop((box.x1, box.y1, box.x2, box.y2))
                        cropped_img.save(chart_path)

                        if self.use_vlm and self.vlm:
                            rel_path = os.path.join("charts", chart_filename)
                            wrote_table = False

                            try:
                                extracted_chart = self.vlm.extract_chart(chart_path)
                                structured_item = to_structured_dict(extracted_chart)
                                if structured_item:
                                    # Add page and type information to structured item
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
                        table_filename = f"table_{table_counter:03d}.png"
                        table_path = os.path.join(tables_dir, table_filename)

                        cropped_img = page_img.crop((box.x1, box.y1, box.x2, box.y2))
                        cropped_img.save(table_path)

                        rel_path = os.path.join("tables", table_filename)
                        wrote_table = False

                        # Try VLM extraction if enabled
                        if self.use_vlm and self.vlm:
                            try:
                                extracted_table = self.vlm.extract_table(table_path)
                                structured_item = to_structured_dict(extracted_table)
                                if structured_item:
                                    # Add page and type information to structured item
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
                        
                        # Try UniTable extraction if enabled (always saves images, optionally parses)
                        if self.use_unitable and not wrote_table:
                            if recognize_table is None:
                                print(f"⚠️  Warning: UniTable not available. Check if inference module can be imported.")
                            else:
                                try:
                                    # Use unitable to recognize the table
                                    result = recognize_table(
                                        table_image_path=table_path,
                                        model_dir=str(self.unitable_model_dir),
                                        vocab_dir=str(self.unitable_vocab_dir),
                                        device=None,  # Auto-detect device
                                        visualize=False,
                                        output_dir=None,  # Don't save outputs separately
                                    )
                                    
                                    # Convert HTML output to structured dict
                                    if result and result.get("html"):
                                        structured_item = html_table_to_structured_dict(
                                            result["html"],
                                            title=f"Table {table_counter} — page {page_num}"
                                        )
                                        if structured_item:
                                            # Add page and type information
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
                                                    title=structured_item.get("title")
                                                )
                                            )
                                            wrote_table = True
                                except Exception:
                                    # Silently fail and continue
                                    pass

                        if not wrote_table and (self.use_vlm or self.use_unitable):
                            md_lines.append(f"![Table {table_counter} — page {page_num}]({rel_path})\n")

                        table_counter += 1
                        if tables_bar:
                            tables_bar.update(1)

        excel_path = None

        # Generate outputs if using VLM or unitable
        if self.use_vlm or self.use_unitable:
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
            
            # Write markdown file
            if 'md_lines' in locals() and md_lines:
                write_markdown(md_lines, out_dir, "extracted_tables_charts.md")

        extraction_types = []
        if self.extract_charts:
            extraction_types.append("charts")
        if self.extract_tables:
            extraction_types.append("tables")
        
        print(f"✅ Parsing completed successfully!")
        print(f"📁 Output directory: {out_dir}")