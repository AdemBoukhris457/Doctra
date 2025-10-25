from __future__ import annotations

import os
import sys
import json
import tempfile
import contextlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Tuple, Optional

from PIL import Image
from paddleocr import LayoutDetection  # pip install paddleocr>=2.7.0.3
from doctra.utils.pdf_io import render_pdf_to_images
from doctra.engines.layout.layout_models import LayoutBox, LayoutPage
from doctra.utils.progress import create_loading_bar
import warnings


@contextlib.contextmanager
def silence():
    """Context manager to suppress stdout and stderr output."""
    with open(os.devnull, "w") as devnull, \
         contextlib.redirect_stdout(devnull), \
         contextlib.redirect_stderr(devnull):
        yield


class PaddleLayoutEngine:
    """
    Thin wrapper around PaddleOCR LayoutDetection to support:
      - Multi-page PDF inputs
      - Batch prediction on page images
      - Clean, page-indexed output with absolute and normalized coords
      
    Provides a high-level interface for document layout detection using
    PaddleOCR's layout detection models with enhanced output formatting
    and multi-page PDF support.
    """

    def __init__(self, model_name: str = "PP-DocLayout_plus-L"):
        """
        Initialize the PaddleLayoutEngine with a specific model.
        
        The model is loaded lazily on first use to avoid unnecessary
        initialization overhead.

        :param model_name: Name of the PaddleOCR layout detection model to use
                          (default: "PP-DocLayout_plus-L")
        """
        self.model_name = model_name
        self.model: Optional["LayoutDetection"] = None

    def _ensure_model(self) -> None:
        """
        Ensure the PaddleOCR model is loaded and ready for inference.
        
        Loads the model on first call with comprehensive output suppression
        to minimize console noise during initialization.

        :return: None
        """
        if self.model is not None:
            return

        # Beautiful loading progress bar (no logging suppression)
        with create_loading_bar(f'Loading PaddleOCR layout model: "{self.model_name}"') as bar:
            # Suppress all output during model loading
            with silence():
                # Suppress warnings from PaddleOCR and Hugging Face during model loading
                with warnings.catch_warnings():
                    # Suppress all warnings during model initialization to avoid HF token warnings
                    warnings.simplefilter("ignore")
                    self.model = LayoutDetection(model_name=self.model_name)
            bar.update(1)

    def predict_pdf(
            self,
            pdf_path: str,
            batch_size: int = 1,
            layout_nms: bool = True,
            dpi: int = 200,
            min_score: float = 0.0,
            keep_temp_files: bool = False,
    ) -> List[LayoutPage]:
        """
        Run layout detection on every page of a PDF.

        Processes each page of the PDF through the layout detection model,
        returning structured results with both absolute and normalized coordinates
        for each detected layout element.

        :param pdf_path: Path to the input PDF file
        :param batch_size: Batch size for Paddle inference (default: 1)
        :param layout_nms: Whether to apply layout NMS in Paddle (default: True)
        :param dpi: Rendering DPI for pdf2image conversion (default: 200)
        :param min_score: Filter out detections below this confidence threshold (default: 0.0)
        :param keep_temp_files: If True, keep the intermediate JPGs for debugging (default: False)
        :return: List of LayoutPage objects in 1-based page_index order
        """
        self._ensure_model()
        pil_pages: List[Tuple[Image.Image, int, int]] = render_pdf_to_images(pdf_path, dpi=dpi)
        if not pil_pages:
            return []

        # Write pages to a temp dir because LayoutDetection expects image paths.
        with tempfile.TemporaryDirectory(prefix="doctra_layout_") as tmpdir:
            img_paths: List[str] = []
            sizes: List[Tuple[int, int]] = []
            for i, (im, w, h) in enumerate(pil_pages, start=1):
                out_path = os.path.join(tmpdir, f"page_{i:04d}.jpg")
                im.save(out_path, format="JPEG", quality=95)
                img_paths.append(out_path)
                sizes.append((w, h))

            # PaddleOCR allows list input; results align with img_paths order.
            raw_outputs: List[Dict[str, Any]] = self.model.predict(
                img_paths, batch_size=batch_size, layout_nms=layout_nms
            )

            pages: List[LayoutPage] = []
            for idx, raw in enumerate(raw_outputs, start=1):
                w, h = sizes[idx - 1]
                boxes: List[LayoutBox] = []
                for det in raw.get("boxes", []):
                    score = float(det.get("score", 0.0))
                    if score < min_score:
                        continue
                    label = str(det.get("label", "unknown"))
                    coord = det.get("coordinate", [0, 0, 0, 0])
                    boxes.append(LayoutBox.from_absolute(label=label, score=score, coord=coord, img_w=w, img_h=h))
                pages.append(LayoutPage(page_index=idx, width=w, height=h, boxes=boxes))

            # Optionally keep rendered images for inspection
            if keep_temp_files:
                debug_dir = os.path.join(os.path.dirname(pdf_path), f"_doctra_layout_{os.getpid()}")
                os.makedirs(debug_dir, exist_ok=True)
                for p in img_paths:
                    os.replace(p, os.path.join(debug_dir, os.path.basename(p)))

            return pages

    # Convenience helpers
    def predict_pdf_as_dicts(self, pdf_path: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Same as predict_pdf, but returns plain dicts for easy JSON serialization.
        
        Convenience method that converts LayoutPage objects to dictionaries,
        making it easy to serialize results to JSON or other formats.

        :param pdf_path: Path to the input PDF file
        :param kwargs: Additional arguments passed to predict_pdf
        :return: List of dictionaries representing the layout pages
        """
        return [p.to_dict() for p in self.predict_pdf(pdf_path, **kwargs)]

    def save_jsonl(self, pages: List[LayoutPage], out_path: str) -> None:
        """
        Save detections to a JSONL file (one page per line).
        
        Writes each page as a separate JSON line, making it easy to process
        large documents incrementally.

        :param pages: List of LayoutPage objects to save
        :param out_path: Output file path for the JSONL file
        :return: None
        """
        with open(out_path, "w", encoding="utf-8") as f:
            for p in pages:
                f.write(json.dumps(p.to_dict(), ensure_ascii=False) + "\n")