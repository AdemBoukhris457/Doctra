from __future__ import annotations
from typing import Tuple
from doctra.engines.layout.layout_models import LayoutBox

def reading_order_key(b: LayoutBox) -> Tuple[float, float]:
    """
    Generate a sorting key for layout boxes in reading order.
    
    Creates a tuple for sorting layout elements in natural reading order:
    top-to-bottom, then left-to-right. This ensures that text and other
    elements are processed in the order they would be read.

    :param b: LayoutBox object to generate a sorting key for
    :return: Tuple of (y1, x1) coordinates for sorting in reading order
    """
    return (b.y1, b.x1)