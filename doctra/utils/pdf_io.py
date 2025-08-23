from typing import List, Tuple
from pdf2image import convert_from_path  # requires Poppler installed locally
from PIL import Image

def render_pdf_to_images(pdf_path: str, dpi: int = 200, fmt: str = "RGB") -> List[Tuple[Image.Image, int, int]]:
    """
    Render a PDF into PIL images.

    Returns:
        List of tuples (pil_image, width, height) in page order (1-based).
    """
    pil_pages = convert_from_path(pdf_path, dpi=dpi)  # may raise if Poppler missing
    images: List[Tuple[Image.Image, int, int]] = []
    for im in pil_pages:
        if fmt and im.mode != fmt:
            im = im.convert(fmt)
        w, h = im.size
        images.append((im, w, h))
    return images