from __future__ import annotations
import math
from typing import Tuple

def clip_bbox_to_image(x1: float, y1: float, x2: float, y2: float, w: int, h: int) -> Tuple[int, int, int, int]:
    """
    Clip a float bbox to image bounds, return integer crop box (left, top, right, bottom).
    Guarantees non-empty crop.
    """
    left = max(0, min(int(math.floor(x1)), w))
    top = max(0, min(int(math.floor(y1)), h))
    right = max(0, min(int(math.ceil(x2)), w))
    bottom = max(0, min(int(math.ceil(y2)), h))
    if right <= left:
        right = min(w, left + 1)
    if bottom <= top:
        bottom = min(h, top + 1)
    return left, top, right, bottom