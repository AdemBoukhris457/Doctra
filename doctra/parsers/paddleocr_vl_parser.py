"""
PaddleOCRVL PDF Parser with Document Restoration and Split Table Merging

This module provides a PDF parser that uses PaddleOCRVL for end-to-end document parsing,
combined with DocRes image restoration and split table merging capabilities.
"""

from __future__ import annotations
import os
import sys
import re
import numpy as np
from typing import List, Dict, Any, Optional, Union
from contextlib import ExitStack
from PIL import Image
import tempfile

from doctra.engines.image_restoration import DocResEngine
from doctra.parsers.split_table_detector import SplitTableDetector, SplitTableMatch, TableSegment
from doctra.utils.pdf_io import render_pdf_to_images
from doctra.utils.constants import IMAGE_SUBDIRS
from doctra.utils.file_ops import ensure_output_dirs
from doctra.utils.progress import create_beautiful_progress_bar, create_notebook_friendly_bar
from doctra.exporters.image_saver import save_box_image
from doctra.exporters.markdown_writer import write_markdown
from doctra.exporters.html_writer import write_html, write_structured_html, render_html_table, write_html_from_lines
from doctra.exporters.excel_writer import write_structured_excel
from doctra.utils.structured_utils import to_structured_dict
from doctra.exporters.markdown_table import render_markdown_table

try:
    from paddleocr import PaddleOCRVL
    PADDLEOCR_VL_AVAILABLE = True
except ImportError:
    PADDLEOCR_VL_AVAILABLE = False


class PaddleOCRVLPDFParser:
    """
    PDF Parser using PaddleOCRVL for end-to-end document parsing.
    
    Combines PaddleOCRVL's vision-language model capabilities with:
    - DocRes image restoration for enhanced document quality
    - Split table detection and merging across pages
    
    :param use_image_restoration: Whether to apply DocRes image restoration (default: True)
    :param restoration_task: DocRes task to use (default: "appearance")
    :param restoration_device: Device for DocRes processing (default: None for auto-detect)
    :param restoration_dpi: DPI for restoration processing (default: 200)
    :param use_chart_recognition: Enable chart recognition in PaddleOCRVL (default: True)
    :param use_doc_orientation_classify: Enable document orientation classification (default: False)
    :param use_doc_unwarping: Enable document unwarping (default: False)
    :param use_layout_detection: Enable layout detection (default: True)
    :param device: Device for PaddleOCRVL processing ("gpu" or "cpu", default: "gpu")
    :param merge_split_tables: Whether to detect and merge split tables (default: True)
    :param bottom_threshold_ratio: Ratio for "too close to bottom" detection (default: 0.20)
    :param top_threshold_ratio: Ratio for "too close to top" detection (default: 0.15)
    :param max_gap_ratio: Maximum allowed gap between tables (default: 0.25)
    :param column_alignment_tolerance: Pixel tolerance for column alignment (default: 10.0)
    :param min_merge_confidence: Minimum confidence score for merging (default: 0.65)
    """
    
    def __init__(
        self,
        *,
        use_image_restoration: bool = True,
        restoration_task: str = "appearance",
        restoration_device: Optional[str] = None,
        restoration_dpi: int = 200,
        use_chart_recognition: bool = True,
        use_doc_orientation_classify: bool = False,
        use_doc_unwarping: bool = False,
        use_layout_detection: bool = True,
        device: str = "gpu",
        merge_split_tables: bool = True,
        bottom_threshold_ratio: float = 0.20,
        top_threshold_ratio: float = 0.15,
        max_gap_ratio: float = 0.25,
        column_alignment_tolerance: float = 10.0,
        min_merge_confidence: float = 0.65,
    ):
        """
        Initialize the PaddleOCRVL PDF Parser.
        """
        if not PADDLEOCR_VL_AVAILABLE:
            raise ImportError(
                "PaddleOCRVL is not available. Please install paddleocr:\n"
                "pip install paddleocr>=2.6.0"
            )
        
        try:
            self.paddleocr_vl = PaddleOCRVL(
                use_doc_orientation_classify=use_doc_orientation_classify,
                use_doc_unwarping=use_doc_unwarping,
                use_layout_detection=use_layout_detection,
            )
            print("✅ PaddleOCRVL pipeline initialized")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize PaddleOCRVL: {e}")
        
        self.use_chart_recognition = use_chart_recognition
        self.device = device
        
        self.use_image_restoration = use_image_restoration
        self.restoration_task = restoration_task
        self.restoration_device = restoration_device
        self.restoration_dpi = restoration_dpi
        
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
    
    def parse(self, pdf_path: str, output_dir: Optional[str] = None) -> None:
        """
        Parse a PDF document using PaddleOCRVL.
        
        :param pdf_path: Path to the input PDF file
        :param output_dir: Output directory (if None, uses default)
        :return: None
        """
        pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        
        if output_dir is None:
            out_dir = f"outputs/{pdf_filename}/paddleocr_vl_parse"
        else:
            out_dir = output_dir
        
        os.makedirs(out_dir, exist_ok=True)
        ensure_output_dirs(out_dir, IMAGE_SUBDIRS)
        
        print(f"🔄 Processing PDF: {os.path.basename(pdf_path)}")
        
        if self.use_image_restoration and self.docres_engine:
            print("🔄 Applying DocRes image restoration...")
            enhanced_pages = self._process_pages_with_restoration(pdf_path, out_dir)
        else:
            enhanced_pages = [im for (im, _, _) in render_pdf_to_images(pdf_path, dpi=self.restoration_dpi)]
        
        if not enhanced_pages:
            print("❌ No pages found in PDF")
            return
        
        print("🔍 Processing pages with PaddleOCRVL...")
        all_results = []
        
        is_notebook = "ipykernel" in sys.modules or "jupyter" in sys.modules
        if is_notebook:
            progress_bar = create_notebook_friendly_bar(
                total=len(enhanced_pages),
                desc="PaddleOCRVL processing"
            )
        else:
            progress_bar = create_beautiful_progress_bar(
                total=len(enhanced_pages),
                desc="PaddleOCRVL processing",
                leave=True
            )
        
        with progress_bar:
            for page_idx, page_img in enumerate(enhanced_pages):
                try:
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                        tmp_path = tmp_file.name
                        page_img.save(tmp_path, "JPEG", quality=95)
                    
                    try:
                        output = self.paddleocr_vl.predict(
                            input=tmp_path,
                            device=self.device,
                            use_chart_recognition=self.use_chart_recognition
                        )
                        
                        if output and len(output) > 0:
                            result = output[0]
                            result['page_index'] = page_idx + 1
                            all_results.append(result)
                        
                        progress_bar.set_description(f"✅ Page {page_idx + 1}/{len(enhanced_pages)} processed")
                    finally:
                        try:
                            os.unlink(tmp_path)
                        except:
                            pass
                    
                    progress_bar.update(1)
                    
                except Exception as e:
                    print(f"⚠️ Page {page_idx + 1} processing failed: {e}")
                    progress_bar.update(1)
        
        split_table_matches: List[SplitTableMatch] = []
        merged_table_segments = []
        
        if self.merge_split_tables and self.split_table_detector:
            print("🔗 Detecting split tables...")
            try:
                pages_for_detection = self._convert_to_layout_pages(all_results, enhanced_pages)
                split_table_matches = self.split_table_detector.detect_split_tables(
                    pages_for_detection, enhanced_pages
                )
                if split_table_matches:
                    print(f"🔗 Detected {len(split_table_matches)} split table(s) to merge")
                for match in split_table_matches:
                    merged_table_segments.append(match.segment1)
                    merged_table_segments.append(match.segment2)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"⚠️ Split table detection failed: {e}")
                split_table_matches = []
        
        self._generate_outputs(
            all_results, enhanced_pages, split_table_matches, merged_table_segments, out_dir
        )
        
        print(f"✅ Parsing completed successfully!")
        print(f"📁 Output directory: {out_dir}")
    
    def _process_pages_with_restoration(self, pdf_path: str, out_dir: str) -> List[Image.Image]:
        """
        Process PDF pages with DocRes image restoration.
        
        :param pdf_path: Path to the input PDF file
        :param out_dir: Output directory for enhanced images
        :return: List of enhanced PIL images
        """
        original_pages = [im for (im, _, _) in render_pdf_to_images(pdf_path, dpi=self.restoration_dpi)]
        
        if not original_pages:
            return []
        
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
                        img_array = np.array(page_img)
                        
                        restored_img, metadata = self.docres_engine.restore_image(
                            img_array,
                            task=self.restoration_task
                        )
                        
                        enhanced_page = Image.fromarray(restored_img)
                        enhanced_pages.append(enhanced_page)
                        
                        enhanced_path = os.path.join(enhanced_dir, f"page_{i+1:03d}_enhanced.jpg")
                        enhanced_page.save(enhanced_path, "JPEG", quality=95)
                        
                        progress_bar.set_description(f"✅ Page {i+1}/{len(original_pages)} enhanced")
                        progress_bar.update(1)
                        
                    except Exception as e:
                        print(f"  ⚠️ Page {i+1} restoration failed: {e}, using original")
                        enhanced_pages.append(page_img)
                        progress_bar.update(1)
        
        finally:
            if hasattr(progress_bar, 'close'):
                progress_bar.close()
        
        return enhanced_pages
    
    def _convert_to_layout_pages(self, results: List[Dict], page_images: List[Image.Image]):
        """
        Convert PaddleOCRVL results to a format compatible with split table detector.
        
        This creates a minimal LayoutPage-like structure from PaddleOCRVL output.
        """
        from doctra.engines.layout.layout_models import LayoutBox, LayoutPage
        
        pages = []
        for result in results:
            page_idx = result.get('page_index', 1)
            if page_idx < 1 or page_idx > len(page_images):
                continue
            
            page_img = page_images[page_idx - 1]
            boxes = []
            
            layout_det = result.get('layout_det_res', {})
            layout_boxes = layout_det.get('boxes', [])
            
            for box_data in layout_boxes:
                coords = box_data.get('coordinate', [])
                if len(coords) >= 4:
                    x1, y1, x2, y2 = float(coords[0]), float(coords[1]), float(coords[2]), float(coords[3])
                    label = box_data.get('label', 'unknown')
                    score = box_data.get('score', 0.0)
                    
                    box = LayoutBox(
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2,
                        label=label,
                        score=score
                    )
                    boxes.append(box)
            
            page = LayoutPage(
                page_index=page_idx,
                width=page_img.width,
                height=page_img.height,
                boxes=boxes
            )
            pages.append(page)
        
        return pages
    
    def _generate_outputs(
        self,
        results: List[Dict],
        page_images: List[Image.Image],
        split_table_matches: List[SplitTableMatch],
        merged_table_segments: List[TableSegment],
        out_dir: str
    ) -> None:
        """
        Generate markdown, HTML, and Excel outputs from PaddleOCRVL results.
        """
        md_lines: List[str] = ["# PaddleOCRVL Document Content\n"]
        html_lines: List[str] = ["<h1>PaddleOCRVL Document Content</h1>"]
        structured_items: List[Dict[str, Any]] = []
        
        for result in results:
            page_idx = result.get('page_index', 1)
            page_img = page_images[page_idx - 1]
            
            md_lines.append(f"\n## Page {page_idx}\n")
            html_lines.append(f"<h2>Page {page_idx}</h2>")
            
            parsing_res_list = result.get('parsing_res_list', [])
            
            for item in parsing_res_list:
                if isinstance(item, dict):
                    label = item.get('block_label', item.get('label', 'unknown'))
                    bbox = item.get('block_bbox', item.get('bbox', None))
                    content = item.get('block_content', item.get('content', ''))
                else:
                    item_str = str(item)
                    
                    label_match = re.search(r'label:\s*(\w+)', item_str)
                    label = label_match.group(1) if label_match else 'unknown'
                    
                    bbox_match = re.search(r'bbox:\s*\[([\d\.,\s]+)\]', item_str)
                    bbox = None
                    if bbox_match:
                        bbox_str = bbox_match.group(1)
                        bbox = [float(x.strip()) for x in bbox_str.split(',')]
                    
                    content_match = re.search(r'content:\s*(.+?)(?=\s*#################|$)', item_str, re.DOTALL)
                    content = content_match.group(1).strip() if content_match else ''
                
                if not content:
                    continue
                
                if label == 'table':
                    table_html_match = re.search(r'<table>.*?</table>', content, re.DOTALL)
                    if table_html_match:
                        table_html = table_html_match.group(0)
                        try:
                            table_md = self._html_table_to_markdown(table_html)
                            md_lines.append(f"\n### Table\n\n{table_md}\n")
                            html_lines.append(f"<h3>Table</h3>\n{table_html}")
                            
                            structured_table = self._extract_table_data(table_html)
                            if structured_table:
                                structured_table['page'] = page_idx
                                structured_table['type'] = 'Table'
                                structured_items.append(structured_table)
                        except Exception as e:
                            if bbox:
                                self._save_element_image(page_img, bbox, out_dir, page_idx, label, md_lines, html_lines)
                
                elif label == 'chart':
                    chart_table = self._parse_chart_content(content)
                    
                    if chart_table:
                        chart_table['page'] = page_idx
                        chart_table['type'] = 'Chart'
                        structured_items.append(chart_table)
                        
                        table_md = render_markdown_table(
                            chart_table.get("headers"),
                            chart_table.get("rows"),
                            title=chart_table.get("title", "Chart")
                        )
                        table_html = render_html_table(
                            chart_table.get("headers"),
                            chart_table.get("rows"),
                            title=chart_table.get("title", "Chart")
                        )
                        md_lines.append(f"\n### Chart\n\n{table_md}\n")
                        html_lines.append(f"<h3>Chart</h3>\n{table_html}")
                    else:
                        md_lines.append(f"\n### Chart\n\n```\n{content}\n```\n")
                        html_lines.append(f"<h3>Chart</h3>\n<pre>{content}</pre>")
                
                elif label in ['header', 'text', 'figure_title', 'vision_footnote']:
                    md_lines.append(f"{content}\n")
                    html_lines.append(f"<p>{content.replace(chr(10), '<br>')}</p>")
                
                else:
                    if bbox:
                        self._save_element_image(page_img, bbox, out_dir, page_idx, label, md_lines, html_lines)
        
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
                    
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                        tmp_path = tmp_file.name
                        merged_img.save(tmp_path, "PNG")
                    
                    try:
                        merged_output = self.paddleocr_vl.predict(
                            input=tmp_path,
                            device=self.device,
                            use_chart_recognition=self.use_chart_recognition
                        )
                        
                        if merged_output and len(merged_output) > 0:
                            merged_result = merged_output[0]
                            parsing_res = merged_result.get('parsing_res_list', [])
                            
                            for item in parsing_res:
                                if isinstance(item, dict):
                                    label = item.get('block_label', item.get('label', ''))
                                    content = item.get('block_content', item.get('content', ''))
                                else:
                                    item_str = str(item)
                                    label_match = re.search(r'label:\s*(\w+)', item_str)
                                    label = label_match.group(1) if label_match else ''
                                    content_match = re.search(r'content:\s*(.+?)(?=\s*#################|$)', item_str, re.DOTALL)
                                    content = content_match.group(1).strip() if content_match else ''
                                
                                if label.lower() == 'table' and content:
                                    table_html_match = re.search(r'<table>.*?</table>', content, re.DOTALL)
                                    if table_html_match:
                                        table_html = table_html_match.group(0)
                                        table_md = self._html_table_to_markdown(table_html)
                                        md_lines.append(f"\n### Merged Table ({pages_str})\n\n{table_md}\n")
                                        html_lines.append(f"<h3>Merged Table ({pages_str})</h3>\n{table_html}")
                                        
                                        structured_table = self._extract_table_data(table_html)
                                        if structured_table:
                                            structured_table['page'] = pages_str
                                            structured_table['type'] = 'Table (Merged)'
                                            structured_table['split_merge'] = True
                                            structured_table['merge_confidence'] = match.confidence
                                            structured_items.append(structured_table)
                    finally:
                        try:
                            os.unlink(tmp_path)
                        except:
                            pass
                    
                except Exception as e:
                    print(f"⚠️ Warning: Failed to process merged table {match_idx + 1}: {e}")
        
        md_path = write_markdown(md_lines, out_dir)
        
        if structured_items:
            html_path = write_html_from_lines(html_lines, out_dir)
            excel_path = os.path.join(out_dir, "tables.xlsx")
            write_structured_excel(excel_path, structured_items)
            html_structured_path = os.path.join(out_dir, "tables.html")
            write_structured_html(html_structured_path, structured_items)
        else:
            html_path = write_html(md_lines, out_dir)
    
    def _save_element_image(
        self,
        page_img: Image.Image,
        bbox: List[float],
        out_dir: str,
        page_idx: int,
        label: str,
        md_lines: List[str],
        html_lines: List[str]
    ) -> None:
        """Save an element as an image and add references to markdown/HTML."""
        try:
            x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
            cropped = page_img.crop((x1, y1, x2, y2))
            
            label_dir = os.path.join(out_dir, label + "s" if label != 'figure' else 'figures')
            os.makedirs(label_dir, exist_ok=True)
            
            img_filename = f"page_{page_idx:03d}_{label}_1.png"
            img_path = os.path.join(label_dir, img_filename)
            cropped.save(img_path, "PNG")
            
            rel_path = os.path.relpath(img_path, out_dir)
            md_lines.append(f"![{label.title()} — page {page_idx}]({rel_path})\n")
            html_lines.append(f'<img src="{rel_path}" alt="{label.title()} — page {page_idx}" />')
        except Exception as e:
            print(f"⚠️ Failed to save {label} image: {e}")
    
    def _html_table_to_markdown(self, html_table: str) -> str:
        """Convert HTML table to markdown format."""
        try:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_table, 'html.parser')
                table = soup.find('table')
                
                if not table:
                    return self._simple_html_to_markdown(html_table)
                
                rows = []
                for tr in table.find_all('tr'):
                    cells = []
                    for td in tr.find_all(['td', 'th']):
                        text = td.get_text(strip=True)
                        cells.append(text)
                    if cells:
                        rows.append(cells)
                
                if not rows:
                    return self._simple_html_to_markdown(html_table)
                
                md_lines = []
                md_lines.append('| ' + ' | '.join(rows[0]) + ' |')
                md_lines.append('| ' + ' | '.join(['---'] * len(rows[0])) + ' |')
                
                for row in rows[1:]:
                    while len(row) < len(rows[0]):
                        row.append('')
                    md_lines.append('| ' + ' | '.join(row) + ' |')
                
                return '\n'.join(md_lines)
            except ImportError:
                return self._simple_html_to_markdown(html_table)
        except Exception as e:
            return self._simple_html_to_markdown(html_table)
    
    def _simple_html_to_markdown(self, html_table: str) -> str:
        """Simple HTML table to markdown conversion without BeautifulSoup."""
        rows = []
        row_pattern = r'<tr[^>]*>(.*?)</tr>'
        cell_pattern = r'<t[dh][^>]*>(.*?)</t[dh]>'
        
        for row_match in re.finditer(row_pattern, html_table, re.DOTALL):
            row_html = row_match.group(1)
            cells = []
            for cell_match in re.finditer(cell_pattern, row_html, re.DOTALL):
                cell_text = cell_match.group(1).strip()
                cell_text = re.sub(r'<[^>]+>', '', cell_text)
                cells.append(cell_text)
            if cells:
                rows.append(cells)
        
        if not rows:
            return html_table
        
        md_lines = []
        if rows:
            md_lines.append('| ' + ' | '.join(rows[0]) + ' |')
            md_lines.append('| ' + ' | '.join(['---'] * len(rows[0])) + ' |')
            
            for row in rows[1:]:
                while len(row) < len(rows[0]):
                    row.append('')
                md_lines.append('| ' + ' | '.join(row) + ' |')
        
        return '\n'.join(md_lines)
    
    def _extract_table_data(self, html_table: str) -> Optional[Dict[str, Any]]:
        """Extract structured table data from HTML table."""
        try:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_table, 'html.parser')
                table = soup.find('table')
                
                if not table:
                    return self._simple_extract_table_data(html_table)
                
                rows = []
                headers = None
                
                for tr in table.find_all('tr'):
                    cells = []
                    for td in tr.find_all(['td', 'th']):
                        text = td.get_text(strip=True)
                        cells.append(text)
                    
                    if cells:
                        if headers is None:
                            headers = cells
                        else:
                            rows.append(cells)
                
                if headers and rows:
                    return {
                        'title': '',
                        'headers': headers,
                        'rows': rows
                    }
                
                return None
            except ImportError:
                return self._simple_extract_table_data(html_table)
        except Exception as e:
            return self._simple_extract_table_data(html_table)
    
    def _simple_extract_table_data(self, html_table: str) -> Optional[Dict[str, Any]]:
        """Simple table data extraction without BeautifulSoup."""
        rows = []
        row_pattern = r'<tr[^>]*>(.*?)</tr>'
        cell_pattern = r'<t[dh][^>]*>(.*?)</t[dh]>'
        
        for row_match in re.finditer(row_pattern, html_table, re.DOTALL):
            row_html = row_match.group(1)
            cells = []
            for cell_match in re.finditer(cell_pattern, row_html, re.DOTALL):
                cell_text = cell_match.group(1).strip()
                cell_text = re.sub(r'<[^>]+>', '', cell_text)
                cells.append(cell_text)
            if cells:
                rows.append(cells)
        
        if not rows:
            return None
        
        headers = rows[0] if rows else None
        data_rows = rows[1:] if len(rows) > 1 else []
        
        if headers and data_rows:
            return {
                'title': '',
                'headers': headers,
                'rows': data_rows
            }
        
        return None
    
    def _parse_chart_content(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse chart content from pipe-delimited format to structured table data.
        
        Example input:
        Category | Percentage
        PCT system fees | 358.6%
        Madrid system fees | 76.2%
        
        :param content: Chart content in pipe-delimited format
        :return: Dictionary with headers and rows, or None if parsing fails
        """
        if not content or not content.strip():
            return None
        
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if not lines:
            return None
        
        header_line = lines[0]
        headers = [h.strip() for h in header_line.split('|') if h.strip()]
        
        if not headers:
            return None
        
        rows = []
        for line in lines[1:]:
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells:
                while len(cells) < len(headers):
                    cells.append('')
                if len(cells) > len(headers):
                    cells = cells[:len(headers)]
                rows.append(cells)
        
        if headers and rows:
            return {
                'title': '',
                'headers': headers,
                'rows': rows
            }
        
        return None

