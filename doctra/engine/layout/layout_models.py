from dataclasses import dataclass, asdict
from typing import List


@dataclass
class LayoutBox:
    """Single detected block on a page."""
    label: str
    score: float
    x1: float
    y1: float
    x2: float
    y2: float
    nx1: float  # normalized [0,1]
    ny1: float
    nx2: float
    ny2: float

    @staticmethod
    def from_absolute(label: str, score: float, coord: List[float], img_w: int, img_h: int) -> "LayoutBox":
        x1, y1, x2, y2 = coord
        return LayoutBox(
            label=label,
            score=score,
            x1=x1, y1=y1, x2=x2, y2=y2,
            nx1=x1 / img_w, ny1=y1 / img_h, nx2=x2 / img_w, ny2=y2 / img_h,
        )


@dataclass
class LayoutPage:
    """Detections for a single page."""
    page_index: int            # 1-based
    width: int
    height: int
    boxes: List[LayoutBox]

    def to_dict(self) -> dict:
        return {
            "page_index": self.page_index,
            "width": self.width,
            "height": self.height,
            "boxes": [asdict(b) for b in self.boxes],
        }
