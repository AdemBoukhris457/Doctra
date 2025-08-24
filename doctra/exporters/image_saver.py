from __future__ import annotations

import os
from PIL import Image
from typing import Dict

from doctra.utils.file_ops import sanitize_filename
from doctra.utils.bbox import clip_bbox_to_image
from doctra.engines.layout.layout_models import LayoutBox

def save_box_image(
    page_img: Image.Image,
    box: LayoutBox,
    out_dir: str,
    page_idx: int,
    box_idx: int,
    image_subdirs: Dict[str, str],
) -> str:
    """
    Crop and save a labeled box to the appropriate images/<subdir>/ folder.
    
    Extracts a region from a page image based on the layout box coordinates,
    crops it to the specified area, and saves it to the appropriate subdirectory
    based on the box label (e.g., figures, charts, tables).

    :param page_img: PIL Image object of the full page
    :param box: LayoutBox object containing coordinates and label
    :param out_dir: Base output directory for saving images
    :param page_idx: Page index for naming the output file
    :param box_idx: Box index for naming the output file
    :param image_subdirs: Dictionary mapping box labels to subdirectory names
    :return: Absolute file path to the saved image
    """
    w, h = page_img.size
    l, t, r, b = clip_bbox_to_image(box.x1, box.y1, box.x2, box.y2, w, h)
    crop = page_img.crop((l, t, r, b))

    sub = image_subdirs[box.label]  # e.g., 'figures' | 'charts' | 'tables'
    fname = f"page_{page_idx:03d}_{box.label}_{box_idx:03d}.jpg"
    fpath = os.path.join(out_dir, "images", sub, sanitize_filename(fname))
    crop.save(fpath, format="JPEG", quality=95)
    return os.path.abspath(fpath)