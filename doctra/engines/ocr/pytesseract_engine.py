from __future__ import annotations

from typing import Optional
from PIL import Image
import pytesseract

from .path_resolver import resolve_tesseract_cmd


class PytesseractOCREngine:
    """
    Minimal OCR engine using pytesseract.
    
    Accepts a cropped PIL image (e.g., a text block from layout detection)
    and returns raw text. Provides a simple interface to Tesseract OCR
    with configurable parameters for different use cases.

    :param tesseract_cmd: Optional path to tesseract executable
    :param lang: OCR language code (default: "eng")
    :param psm: Tesseract page segmentation mode (default: 4)
    :param oem: Tesseract OCR engine mode (default: 3)
    :param extra_config: Additional Tesseract configuration string (default: "")
    """

    def __init__(
        self,
        tesseract_cmd: Optional[str] = None,
        lang: str = "eng",
        psm: int = 4,
        oem: int = 3,
        extra_config: str = "",
    ):
        """
        Initialize the PytesseractOCREngine with OCR configuration.
        
        Sets up the Tesseract command path and stores configuration parameters
        for use during text recognition.

        :param tesseract_cmd: Optional path to tesseract executable
        :param lang: OCR language code (default: "eng")
        :param psm: Tesseract page segmentation mode (default: 4)
        :param oem: Tesseract OCR engine mode (default: 3)
        :param extra_config: Additional Tesseract configuration string (default: "")
        """
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
        
        Performs text recognition on the provided image using the configured
        Tesseract parameters and returns the extracted text with whitespace
        stripped from the beginning and end.

        :param image: PIL Image object to perform OCR on
        :return: Extracted text string with leading/trailing whitespace removed
        :raises TypeError: If the input is not a PIL Image object
        """
        if not isinstance(image, Image.Image):
            raise TypeError("PytesseractOCREngine expects a PIL.Image.Image as input.")

        config_parts = [f"--psm {self.psm}", f"--oem {self.oem}"]
        if self.extra_config:
            config_parts.append(self.extra_config)
        config = " ".join(config_parts)

        text = pytesseract.image_to_string(image, lang=self.lang, config=config)
        return text.strip()
