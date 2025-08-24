from dataclasses import dataclass, asdict
from typing import List


@dataclass
class LayoutBox:
    """
    Single detected block on a page.
    
    Represents a detected layout element (text, table, chart, figure, etc.)
    with both absolute and normalized coordinates for flexibility in processing.
    
    :param label: Type of layout element (e.g., 'text', 'table', 'chart', 'figure')
    :param score: Confidence score of the detection (0.0 to 1.0)
    :param x1: Left coordinate in absolute pixels
    :param y1: Top coordinate in absolute pixels
    :param x2: Right coordinate in absolute pixels
    :param y2: Bottom coordinate in absolute pixels
    :param nx1: Left coordinate normalized to [0,1] range
    :param ny1: Top coordinate normalized to [0,1] range
    :param nx2: Right coordinate normalized to [0,1] range
    :param ny2: Bottom coordinate normalized to [0,1] range
    """
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
        """
        Create a LayoutBox from absolute coordinates.
        
        Converts absolute pixel coordinates to a LayoutBox with both
        absolute and normalized coordinates calculated.

        :param label: Type of layout element (e.g., 'text', 'table', 'chart')
        :param score: Confidence score of the detection (0.0 to 1.0)
        :param coord: List of coordinates [x1, y1, x2, y2] in absolute pixels
        :param img_w: Width of the source image in pixels
        :param img_h: Height of the source image in pixels
        :return: LayoutBox instance with both absolute and normalized coordinates
        """
        x1, y1, x2, y2 = coord
        return LayoutBox(
            label=label,
            score=score,
            x1=x1, y1=y1, x2=x2, y2=y2,
            nx1=x1 / img_w, ny1=y1 / img_h, nx2=x2 / img_w, ny2=y2 / img_h,
        )


@dataclass
class LayoutPage:
    """
    Detections for a single page.
    
    Contains all layout elements detected on a single page of a document,
    including page metadata and a list of detected layout boxes.

    :param page_index: 1-based page index within the document
    :param width: Width of the page in pixels
    :param height: Height of the page in pixels
    :param boxes: List of detected layout elements on this page
    """
    page_index: int            # 1-based
    width: int
    height: int
    boxes: List[LayoutBox]

    def to_dict(self) -> dict:
        """
        Convert the LayoutPage to a dictionary representation.
        
        Useful for serialization to JSON or other formats.

        :return: Dictionary representation of the page with all boxes serialized
        """
        return {
            "page_index": self.page_index,
            "width": self.width,
            "height": self.height,
            "boxes": [asdict(b) for b in self.boxes],
        }
