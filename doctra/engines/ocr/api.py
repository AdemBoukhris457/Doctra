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
    
    Convenience function that creates a PytesseractOCREngine instance and
    immediately runs OCR on the provided image. Useful for quick text extraction
    without needing to manage engine instances.

    :param cropped_pil: PIL Image object to perform OCR on
    :param lang: OCR language code (default: "eng")
    :param psm: Tesseract page segmentation mode (default: 4)
    :param oem: Tesseract OCR engine mode (default: 3)
    :param extra_config: Additional Tesseract configuration string (default: "")
    :param tesseract_cmd: Optional path to tesseract executable (default: None)
    :return: Extracted text string from the image
    """
    engine = PytesseractOCREngine(
        tesseract_cmd=tesseract_cmd, lang=lang, psm=psm, oem=oem, extra_config=extra_config
    )
    return engine.recognize(cropped_pil)
