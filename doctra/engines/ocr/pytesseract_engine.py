from __future__ import annotations

from typing import Optional
from PIL import Image
import pytesseract

from .path_resolver import resolve_tesseract_cmd


class PytesseractOCREngine:
    """
    Minimal OCR engines using pytesseract.
    Accepts a cropped PIL image (e.g., a text block from layout) and returns raw text.
    """

    def __init__(
        self,
        tesseract_cmd: Optional[str] = None,
        lang: str = "eng",
        psm: int = 4,
        oem: int = 3,
        extra_config: str = "",
    ):
        cmd = resolve_tesseract_cmd(tesseract_cmd)
        if cmd:
            pytesseract.pytesseract.tesseract_cmd = cmd
        # If not found, let pytesseract raise a clear error at call time.

        self.lang = lang
        self.psm = psm
        self.oem = oem
        self.extra_config = (extra_config or "").strip()

    def recognize(self, image: Image.Image) -> str:
        """
        Run OCR on a cropped PIL image and return extracted text (stripped).
        """
        if not isinstance(image, Image.Image):
            raise TypeError("PytesseractOCREngine expects a PIL.Image.Image as input.")

        config_parts = [f"--psm {self.psm}", f"--oem {self.oem}"]
        if self.extra_config:
            config_parts.append(self.extra_config)
        config = " ".join(config_parts)

        text = pytesseract.image_to_string(image, lang=self.lang, config=config)
        return text.strip()
