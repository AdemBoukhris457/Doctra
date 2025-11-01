"""
Split Table Detection Module

Detects and merges tables that are split across multiple pages using:
1. Proximity detection (position-based heuristics)
2. LSD (Line Segment Detector) for structure analysis - adaptive, no parameter tuning needed
3. Column alignment and validation
"""

from __future__ import annotations
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from PIL import Image
import logging

logger = logging.getLogger(__name__)


@dataclass
class TableSegment:
    """Represents a table segment with its bounding box and page information."""
    page_index: int
    box_index: int
    x1: float
    y1: float
    x2: float
    y2: float
    page_width: int
    page_height: int
    image: Image.Image  # Cropped table image
    confidence: float = 1.0
    
    def match_box(self, box, page_idx: int, tolerance: float = 2.0) -> bool:
        """Check if this segment matches a given box."""
        if page_idx != self.page_index:
            return False
        return (abs(box.x1 - self.x1) < tolerance and
                abs(box.y1 - self.y1) < tolerance and
                abs(box.x2 - self.x2) < tolerance and
                abs(box.y2 - self.y2) < tolerance)


@dataclass
class SplitTableMatch:
    """Represents a potential split table match between two segments."""
    segment1: TableSegment
    segment2: TableSegment
    confidence: float
    merge_reason: str
    column_count1: int
    column_count2: int


class SplitTableDetector:
    """
    Detects and validates tables that are split across pages.
    
    Uses proximity detection and LSD-based structure analysis to identify
    and validate split tables.
    """
    
    def __init__(
        self,
        bottom_threshold_ratio: float = 0.20,  # Increased from 0.15 to 0.20 (more lenient)
        top_threshold_ratio: float = 0.15,      # Increased from 0.10 to 0.15 (more lenient)
        max_gap_ratio: float = 0.25,            # Increased from 0.10 to 0.25 (accounts for headers/footers/margins)
        column_alignment_tolerance: float = 10.0,
        min_merge_confidence: float = 0.65,     # Decreased from 0.7 to 0.65 (more lenient)
        width_similarity_threshold: float = 0.20, # Increased from 0.15 to 0.20 (more lenient)
        enable_lsd: bool = True,
    ):
        """
        Initialize the SplitTableDetector.
        
        :param bottom_threshold_ratio: Ratio for "too close to bottom" (default: 0.20)
        :param top_threshold_ratio: Ratio for "too close to top" (default: 0.15)
        :param max_gap_ratio: Maximum allowed gap between tables (default: 0.25, accounts for headers/footers)
        :param column_alignment_tolerance: Pixel tolerance for column alignment (default: 10.0)
        :param min_merge_confidence: Minimum confidence score for merging (default: 0.65)
        :param width_similarity_threshold: Maximum width difference ratio (default: 0.20)
        :param enable_lsd: Whether to use LSD for structure analysis (default: True)
        """
        self.bottom_threshold_ratio = bottom_threshold_ratio
        self.top_threshold_ratio = top_threshold_ratio
        self.max_gap_ratio = max_gap_ratio
        self.column_alignment_tolerance = column_alignment_tolerance
        self.min_merge_confidence = min_merge_confidence
        self.width_similarity_threshold = width_similarity_threshold
        self.enable_lsd = enable_lsd
        
    def detect_split_tables(
        self,
        pages: List[Any],
        page_images: List[Image.Image],
    ) -> List[SplitTableMatch]:
        """
        Detect tables that are split across pages.
        
        :param pages: List of LayoutPage objects with detected boxes
        :param page_images: List of PIL Images for each page
        :return: List of SplitTableMatch objects for validated split tables
        """
        # Extract all table segments
        table_segments: List[TableSegment] = []
        for page in pages:
            page_num = page.page_index
            # Page index is 1-based, page_images is 0-based
            if page_num < 1 or page_num > len(page_images):
                logger.warning(f"Skipping page {page_num}: index out of range (max={len(page_images)})")
                continue
            page_img = page_images[page_num - 1]
            
            for i, box in enumerate(page.boxes):
                if box.label == "table":
                    # Crop table image
                    cropped = page_img.crop((box.x1, box.y1, box.x2, box.y2))
                    
                    segment = TableSegment(
                        page_index=page_num,
                        box_index=i,
                        x1=box.x1,
                        y1=box.y1,
                        x2=box.x2,
                        y2=box.y2,
                        page_width=page.width,
                        page_height=page.height,
                        image=cropped,
                        confidence=box.score,
                    )
                    table_segments.append(segment)
        
        # Find potential matches between consecutive pages
        matches: List[SplitTableMatch] = []
        
        for i, seg1 in enumerate(table_segments):
            # Only check tables from next page
            for seg2 in table_segments[i+1:]:
                if seg2.page_index != seg1.page_index + 1:
                    continue
                
                # Phase 1: Quick proximity check
                if self._check_proximity(seg1, seg2):
                    # Phase 2: Detailed structure analysis
                    match = self._validate_split_table(seg1, seg2)
                    if match and match.confidence >= self.min_merge_confidence:
                        matches.append(match)
        
        return matches
    
    def _check_proximity(self, seg1: TableSegment, seg2: TableSegment) -> bool:
        """
        Phase 1: Quick proximity check using position heuristics.
        
        :param seg1: First table segment
        :param seg2: Second table segment
        :return: True if proximity conditions are met
        """
        # Check if seg1 is close to bottom of page
        seg1_bottom_ratio = (seg1.y2) / seg1.page_height
        is_seg1_bottom = seg1_bottom_ratio >= (1.0 - self.bottom_threshold_ratio)
        
        # Check if seg2 is close to top of page
        seg2_top_ratio = seg2.y1 / seg2.page_height
        is_seg2_top = seg2_top_ratio <= self.top_threshold_ratio
        
        if not (is_seg1_bottom and is_seg2_top):
            return False
        
        # Check vertical alignment (x coordinates should be similar)
        x1_overlap = self._calculate_overlap(seg1.x1, seg1.x2, seg2.x1, seg2.x2)
        min_overlap_ratio = 0.5  # At least 50% horizontal overlap
        if x1_overlap < min_overlap_ratio:
            return False
        
        # Check gap between tables (considering page boundary)
        # Gap is from seg1.y2 to seg2.y1, accounting for page break
        gap_pixels = seg1.page_height - seg1.y2 + seg2.y1
        gap_ratio = gap_pixels / seg1.page_height
        if gap_ratio > self.max_gap_ratio:
            return False
        
        # Check width similarity
        width1 = seg1.x2 - seg1.x1
        width2 = seg2.x2 - seg2.x1
        width_ratio = abs(width1 - width2) / max(width1, width2)
        if width_ratio > self.width_similarity_threshold:
            return False
        
        return True
    
    def _validate_split_table(
        self,
        seg1: TableSegment,
        seg2: TableSegment
    ) -> Optional[SplitTableMatch]:
        """
        Phase 2: Validate split table using LSD-based structure analysis.
        
        :param seg1: First table segment
        :param seg2: Second table segment
        :return: SplitTableMatch if validated, None otherwise
        """
        if not self.enable_lsd:
            # Without LSD, use basic validation
            return SplitTableMatch(
                segment1=seg1,
                segment2=seg2,
                confidence=0.8,
                merge_reason="Proximity match (LSD disabled)",
                column_count1=0,
                column_count2=0,
            )
        
        # Convert PIL images to OpenCV format
        img1 = self._pil_to_cv2(seg1.image)
        img2 = self._pil_to_cv2(seg2.image)
        
        # Detect columns in both images
        cols1 = self._detect_columns(img1)
        cols2 = self._detect_columns(img2)
        
        # If we detected too many columns (>20), it's likely noise (horizontal lines, text boundaries, etc.)
        # Use proximity-only fallback instead of trying to validate structure
        if len(cols1) > 20 or len(cols2) > 20:
            return SplitTableMatch(
                segment1=seg1,
                segment2=seg2,
                confidence=0.70,  # Slightly higher confidence when proximity passed
                merge_reason="Proximity match (too many columns detected, likely noise)",
                column_count1=len(cols1),
                column_count2=len(cols2),
            )
        
        if len(cols1) == 0 or len(cols2) == 0:
            # If LSD fails but proximity passed, still allow merge with lower confidence
            # This handles borderless tables or poor image quality
            if len(cols1) == 0 and len(cols2) == 0:
                return SplitTableMatch(
                    segment1=seg1,
                    segment2=seg2,
                    confidence=0.65,  # Lower confidence when no structure detected
                    merge_reason="Proximity match (no columns detected by LSD)",
                    column_count1=0,
                    column_count2=0,
                )
            return None
        
        # Check column count match
        # For tables with many columns, allow more tolerance
        # Use relative difference instead of absolute
        col_count1, col_count2 = len(cols1), len(cols2)
        max_cols = max(col_count1, col_count2)
        col_diff = abs(col_count1 - col_count2)
        
        # Allow difference based on table size:
        # - Small tables (≤5 cols): Allow 1 difference
        # - Medium tables (6-10 cols): Allow 2 difference  
        # - Large tables (11-20 cols): Allow 15% difference or 3, whichever is larger
        # Note: If we have >20 cols, something is wrong (too much noise), so alignment check will handle it
        if max_cols <= 5:
            max_allowed_diff = 1
        elif max_cols <= 10:
            max_allowed_diff = 2
        elif max_cols <= 20:
            max_allowed_diff = max(3, int(max_cols * 0.15))
        else:
            # Too many columns detected - likely noise, but let alignment check decide
            max_allowed_diff = max(5, int(max_cols * 0.20))
        
        if col_diff > max_allowed_diff:
            return None
        
        # Check column alignment
        alignment_score = self._check_column_alignment(cols1, cols2, seg1, seg2)
        
        if alignment_score < 0.6:  # At least 60% alignment
            return None
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(
            seg1, seg2, cols1, cols2, alignment_score
        )
        
        if confidence < self.min_merge_confidence:
            return None
        return SplitTableMatch(
            segment1=seg1,
            segment2=seg2,
            confidence=confidence,
            merge_reason=f"LSD validation: {len(cols1)} vs {len(cols2)} columns, alignment={alignment_score:.2f}",
            column_count1=len(cols1),
            column_count2=len(cols2),
        )
    
    def _detect_columns(self, img: np.ndarray) -> List[float]:
        """
        Detect vertical lines (columns) in a table image using LSD (Line Segment Detector).
        
        LSD is adaptive and works well across different table structures without
        requiring parameter tuning like Hough Transform.
        
        :param img: OpenCV image (grayscale)
        :return: List of x-coordinates of detected vertical lines
        """
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        # Apply preprocessing to enhance line detection
        # Enhance contrast for better line visibility
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Optional: Apply threshold if needed (LSD can work with grayscale too)
        # For better results with tables, use binary image
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Optional: Morphological operations to connect broken lines
        # This helps with dashed or partially broken lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
        morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # Use LSD (Line Segment Detector) - adaptive, no parameter tuning needed
        lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD)
        
        # Detect all line segments
        lines, _, _, _ = lsd.detect(morph)
        
        if lines is None or len(lines) == 0:
            return []
        
        # Extract x-coordinates and filter by angle (near vertical: 90 degrees)
        x_coords = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Calculate angle of the line
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
            
            # Filter for near-vertical lines (75-105 degrees range)
            # This catches lines that are mostly vertical
            if 75 <= angle <= 105:
                # Add both endpoints (they'll be clustered later)
                x_coords.extend([x1, x2])
        
        if not x_coords:
            return []
        
        # Cluster nearby x-coordinates to merge lines that are close together
        # This handles cases where the same column line is detected multiple times
        x_coords = sorted(set(x_coords))
        
        # Use a more aggressive clustering threshold
        # For tables, columns are usually well-separated, so cluster more aggressively
        # Use a threshold based on image width (e.g., 1% of width)
        if len(x_coords) > 0:
            img_width = img.shape[1]
            # Use 1% of image width as clustering threshold, but at least 5px
            clustering_threshold = max(5, img_width * 0.01)
            clustered = self._cluster_values(x_coords, threshold=clustering_threshold)
        else:
            clustered = []
        
        # Filter out columns that are too close to edges (likely noise)
        if len(clustered) > 0 and len(clustered) > 2:
            img_width = img.shape[1]
            edge_margin = img_width * 0.02  # 2% margin
            clustered = [c for c in clustered if edge_margin <= c <= (img_width - edge_margin)]
        
        # If we still have too many columns, the detection is probably picking up noise
        # Real tables rarely have more than 20 columns, so if we detect more, 
        # we're likely picking up horizontal lines, text boundaries, or other noise
        # In this case, just return empty and rely on proximity-based fallback
        if len(clustered) > 20:
            return []
        
        return clustered
    
    def _cluster_values(self, values: List[float], threshold: float) -> List[float]:
        """
        Cluster nearby values together.
        
        :param values: List of values to cluster
        :param threshold: Maximum distance for clustering
        :return: List of cluster centers
        """
        if not values:
            return []
        
        sorted_vals = sorted(values)
        clusters = [[sorted_vals[0]]]
        
        for val in sorted_vals[1:]:
            if val - clusters[-1][-1] <= threshold:
                clusters[-1].append(val)
            else:
                clusters.append([val])
        
        # Return cluster centers
        return [np.mean(cluster) for cluster in clusters]
    
    def _check_column_alignment(
        self,
        cols1: List[float],
        cols2: List[float],
        seg1: TableSegment,
        seg2: TableSegment
    ) -> float:
        """
        Check if columns align between two table segments.
        
        :param cols1: Column positions in first segment (relative to segment)
        :param cols2: Column positions in second segment (relative to segment)
        :param seg1: First table segment
        :param seg2: Second table segment
        :return: Alignment score (0-1)
        """
        # Normalize column positions to segment width
        width1 = seg1.x2 - seg1.x1
        width2 = seg2.x2 - seg2.x1
        
        if width1 == 0 or width2 == 0:
            return 0.0
        
        # Normalize to [0, 1] range
        norm_cols1 = [c / width1 for c in cols1]
        norm_cols2 = [c / width2 for c in cols2]
        
        # Use dynamic programming or simple matching
        # For simplicity, use the number of matching columns
        matches = 0
        total = max(len(norm_cols1), len(norm_cols2))
        
        if total == 0:
            return 0.0
        
        # Match each column in cols1 with nearest in cols2
        tolerance = 0.05  # 5% width tolerance
        used_cols2 = set()
        
        for c1 in norm_cols1:
            best_match = None
            best_diff = float('inf')
            
            for i, c2 in enumerate(norm_cols2):
                if i in used_cols2:
                    continue
                diff = abs(c1 - c2)
                if diff < tolerance and diff < best_diff:
                    best_match = i
                    best_diff = diff
            
            if best_match is not None:
                matches += 1
                used_cols2.add(best_match)
        
        return matches / total if total > 0 else 0.0
    
    def _calculate_confidence(
        self,
        seg1: TableSegment,
        seg2: TableSegment,
        cols1: List[float],
        cols2: List[float],
        alignment_score: float
    ) -> float:
        """
        Calculate overall confidence score for merging.
        
        :param seg1: First table segment
        :param seg2: Second table segment
        :param cols1: Column positions in first segment
        :param cols2: Column positions in second segment
        :param alignment_score: Column alignment score
        :return: Confidence score (0-1)
        """
        # Base confidence from alignment
        confidence = alignment_score * 0.6
        
        # Column count match bonus
        col_diff = abs(len(cols1) - len(cols2))
        if col_diff == 0:
            confidence += 0.2
        elif col_diff == 1:
            confidence += 0.1
        
        # Width similarity bonus
        width1 = seg1.x2 - seg1.x1
        width2 = seg2.x2 - seg2.x1
        width_ratio = 1.0 - (abs(width1 - width2) / max(width1, width2))
        confidence += width_ratio * 0.1
        
        # Detection confidence bonus
        avg_detection_conf = (seg1.confidence + seg2.confidence) / 2.0
        confidence += avg_detection_conf * 0.1
        
        return min(1.0, confidence)
    
    def _calculate_overlap(self, x1_start: float, x1_end: float, x2_start: float, x2_end: float) -> float:
        """Calculate horizontal overlap ratio between two intervals."""
        overlap_start = max(x1_start, x2_start)
        overlap_end = min(x1_end, x2_end)
        overlap = max(0, overlap_end - overlap_start)
        
        union = (x1_end - x1_start) + (x2_end - x2_start) - overlap
        return overlap / union if union > 0 else 0.0
    
    def _pil_to_cv2(self, pil_img: Image.Image) -> np.ndarray:
        """Convert PIL Image to OpenCV format."""
        # Convert RGB to BGR
        if pil_img.mode == 'RGB':
            img_array = np.array(pil_img)
            return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        elif pil_img.mode == 'L':
            return np.array(pil_img)
        else:
            # Convert to RGB first
            rgb_img = pil_img.convert('RGB')
            img_array = np.array(rgb_img)
            return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    def merge_table_images(
        self,
        match: SplitTableMatch,
        gap_pixels: int = 10
    ) -> Image.Image:
        """
        Merge two table images into one.
        
        :param match: SplitTableMatch containing the two segments
        :param gap_pixels: Number of pixels to add between tables (default: 10)
        :return: Merged PIL Image
        """
        img1 = match.segment1.image
        img2 = match.segment2.image
        
        # Make widths equal (use maximum width)
        max_width = max(img1.width, img2.width)
        
        # Resize images to same width while maintaining aspect ratio
        if img1.width != max_width:
            ratio = max_width / img1.width
            new_height = int(img1.height * ratio)
            img1 = img1.resize((max_width, new_height), Image.LANCZOS)
        
        if img2.width != max_width:
            ratio = max_width / img2.width
            new_height = int(img2.height * ratio)
            img2 = img2.resize((max_width, new_height), Image.LANCZOS)
        
        # Create merged image
        total_height = img1.height + gap_pixels + img2.height
        merged = Image.new('RGB', (max_width, total_height), color='white')
        
        # Paste images
        merged.paste(img1, (0, 0))
        merged.paste(img2, (0, img1.height + gap_pixels))
        
        return merged

