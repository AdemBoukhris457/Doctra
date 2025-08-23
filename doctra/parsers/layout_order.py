from __future__ import annotations
from typing import Tuple
from doctra.engines.layout.layout_models import LayoutBox

def reading_order_key(b: LayoutBox) -> Tuple[float, float]:
    """
    Sort by top-to-bottom, then left-to-right.
    """
    return (b.y1, b.x1)