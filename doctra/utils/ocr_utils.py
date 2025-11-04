from __future__ import annotations

import re
from typing import Union
from PIL import Image
from doctra.engines.ocr import PytesseractOCREngine, PaddleOCREngine
from doctra.engines.layout.layout_models import LayoutBox
from doctra.utils.bbox import clip_bbox_to_image

def ocr_box_text(
    ocr_engine: Union[PytesseractOCREngine, PaddleOCREngine], 
    page_img: Image.Image, 
    box: LayoutBox
) -> str:
    """
    OCR a single layout box from a page image and return normalized text.
    Preserves line breaks; collapses excessive blank lines.
    
    Supports both PytesseractOCREngine and PaddleOCREngine.
    """
    w, h = page_img.size
    l, t, r, b = clip_bbox_to_image(box.x1, box.y1, box.x2, box.y2, w, h)
    crop = page_img.crop((l, t, r, b))
    text = ocr_engine.recognize(crop)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text