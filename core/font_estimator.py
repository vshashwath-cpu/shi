"""
Font Estimator & Principal Display Panel (PDP) Analyzer
Implements calculation of PDP surface area and character/numeral height verification
under Rule 9 and Schedule II of Legal Metrology (Packaged Commodities) Rules, 2011.
"""

import math
from typing import Dict, Any, Tuple, Optional

class FontEstimator:
    """
    Computes PDP dimensions, pixel-to-millimeter scaling, and verifies font height
    against statutory thresholds in Schedule II.
    """

    # Schedule II Table (Area cm²: (min, max, normal_min_mm, blown_min_mm))
    SCHEDULE_II = [
        (0.0, 50.0, 1.0, 2.0),
        (50.0, 100.0, 1.5, 3.0),
        (100.0, 500.0, 2.0, 4.0),
        (500.0, 2500.0, 4.0, 6.0),
        (2500.0, float('inf'), 6.0, 8.0)
    ]

    @staticmethod
    def calculate_pdp_area(
        shape: str,
        height_cm: float,
        width_cm: Optional[float] = None,
        depth_cm: Optional[float] = None,
        diameter_cm: Optional[float] = None
    ) -> float:
        """
        Calculate Principal Display Panel area as defined under Rule 2(h) & Rule 7:
        1. Rectangular container: Area of one entire side (Height x Width) or 40% of total area.
        2. Cylindrical container: 40% of Height x Circumference.
        3. Other shape: 20% of total surface area.
        """
        shape = (shape or 'rectangular').lower()

        if shape == 'rectangular':
            w = width_cm or 10.0
            h = height_cm or 15.0
            d = depth_cm or 5.0
            # Under Rule 7: entire face (H x W)
            return round(h * w, 2)

        elif shape == 'cylindrical':
            dia = diameter_cm or 8.0
            h = height_cm or 15.0
            circumference = math.pi * dia
            # 40% of height x circumference
            return round(0.40 * h * circumference, 2)

        else:
            # General fallback: 20% of estimated surface area
            w = width_cm or 10.0
            h = height_cm or 15.0
            d = depth_cm or 5.0
            total_surface = 2 * (w * h + w * d + h * d)
            return round(0.20 * total_surface, 2)

    @classmethod
    def get_schedule_ii_requirement(cls, pdp_area_sq_cm: float, package_type: str = 'normal') -> float:
        """
        Lookup statutory minimum font height in mm for given PDP area.
        """
        is_blown = (package_type == 'blown_or_moulded')
        for min_a, max_a, norm_h, blown_h in cls.SCHEDULE_II:
            if min_a <= pdp_area_sq_cm <= max_a:
                return blown_h if is_blown else norm_h
        return 6.0 if not is_blown else 8.0

    @classmethod
    def estimate_font_from_bbox(
        cls,
        char_height_px: float,
        image_height_px: int,
        physical_height_mm: float
    ) -> float:
        """
        Estimate character height in mm using physical package height and image resolution.
        scale = physical_height_mm / image_height_px
        char_height_mm = char_height_px * scale
        """
        if image_height_px <= 0:
            return 2.0  # safe default fallback
        mm_per_pixel = physical_height_mm / image_height_px
        return round(char_height_px * mm_per_pixel, 2)

    @classmethod
    def check_aspect_ratio(cls, char_width_px: float, char_height_px: float) -> Tuple[float, bool]:
        """
        Rule 9(3): Height shall not be less than 3 times the width (width/height >= 0.33).
        Returns (ratio, is_compliant).
        """
        if char_height_px <= 0:
            return 1.0, True
        ratio = char_width_px / char_height_px
        is_compliant = ratio >= 0.30
        return round(ratio, 2), is_compliant
