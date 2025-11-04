from __future__ import annotations

from typing import Optional
from PIL import Image

from .pytesseract_engine import PytesseractOCREngine
from .paddleocr_engine import PaddleOCREngine


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


def ocr_image_paddleocr(
    cropped_pil: Image.Image,
    *,
    use_doc_orientation_classify: bool = False,
    use_doc_unwarping: bool = False,
    use_textline_orientation: bool = False,
    device: str = "gpu",
) -> str:
    """
    One-shot OCR: run PaddleOCR on a cropped PIL image and return text.
    
    Convenience function that creates a PaddleOCREngine instance and
    immediately runs OCR on the provided image. Useful for quick text extraction
    without needing to manage engine instances.

    :param cropped_pil: PIL Image object to perform OCR on
    :param use_doc_orientation_classify: Enable document orientation classification (default: False)
    :param use_doc_unwarping: Enable text image rectification (default: False)
    :param use_textline_orientation: Enable text line orientation classification (default: False)
    :param device: Device to use for OCR ("cpu" or "gpu", default: "gpu")
    :return: Extracted text string from the image
    """
    engine = PaddleOCREngine(
        use_doc_orientation_classify=use_doc_orientation_classify,
        use_doc_unwarping=use_doc_unwarping,
        use_textline_orientation=use_textline_orientation,
        device=device
    )
    return engine.recognize(cropped_pil)
