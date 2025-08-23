from __future__ import annotations

from typing import Optional
from PIL import Image

from .pytesseract_engine import PytesseractOCREngine


def ocr_image(
    cropped_pil: Image.Image,
    *,
    lang: str = "eng",
    psm: int = 4,
    oem: int = 3,
    extra_config: str = "",
    tesseract_cmd: Optional[str] = None,
) -> str:
    """
    One-shot OCR: run pytesseract on a cropped PIL image and return text.
    """
    engine = PytesseractOCREngine(
        tesseract_cmd=tesseract_cmd, lang=lang, psm=psm, oem=oem, extra_config=extra_config
    )
    return engine.recognize(cropped_pil)
