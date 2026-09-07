"""
Curated realistic sample datasets and packaging label generator for Indian Packaged Commodities.
Provides realistic ground-truth samples spanning compliant products and common statutory violations
under the Legal Metrology (Packaged Commodities) Rules, 2011.
"""

import os
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont

class SampleRepository:
    """
    Provides access to standard packaged commodity test cases and generates synthetic label visual assets.
    """

    SAMPLES: List[Dict[str, Any]] = [
        {
            "id": "SMP-001",
            "brand": "Aashirvaad",
            "commodity_name": "Whole Wheat Atta",
            "category": "Food & Staples",
            "barcode": "8901725181234",
            "is_imported": False,
            "country_of_origin": "India",
            "packaging_shape": "rectangular",
            "dimensions_cm": {"height": 38.0, "width": 24.0, "depth": 8.0},
            "pdp_info": {
                "pdp_area_sq_cm": 912.0,
                "package_type": "normal",
                "estimated_font_height_mm": 5.2,
                "font_aspect_ratio": 0.48
            },
            "extracted_data": {
                "manufacturer_name": "ITC Limited",
                "manufacturer_address": "Virginia House, 37 J.L. Nehru Road, Kolkata, West Bengal - 700071",
                "is_imported": False,
                "country_of_origin": "India",
                "commodity_name": "Whole Wheat Atta",
                "net_quantity_raw": "5 kg",
                "mfg_date_raw": "05/2024",
                "expiry_date_raw": "09/2024",
                "mrp_raw": "MRP ₹ 285.00 (inclusive of all taxes)",
                "unit_sale_price_raw": "USP ₹ 57.00 / kg",
                "consumer_care_name": "ITC Consumer Care Cell",
                "consumer_care_phone": "1800-425-4444",
                "consumer_care_email": "itccares@itc.in",
                "consumer_care_address": "P.O. Box 564, Kolkata - 700071",
                "has_sticker_over_mrp": False,
                "has_dual_mrp": False
            },
            "bounding_boxes": [
                {"label": "Generic Name", "bbox": [40, 50, 80, 550], "status": "pass", "text": "AASHIRVAAD WHOLE WHEAT ATTA"},
                {"label": "Net Quantity", "bbox": [100, 50, 140, 260], "status": "pass", "text": "NET QUANTITY: 5 kg"},
                {"label": "MRP & Taxes", "bbox": [155, 50, 195, 480], "status": "pass", "text": "MRP ₹ 285.00 (INCL. OF ALL TAXES)"},
                {"label": "Unit Sale Price", "bbox": [205, 50, 240, 360], "status": "pass", "text": "USP ₹ 57.00 / kg"},
                {"label": "Mfg Date & Batch", "bbox": [250, 50, 285, 390], "status": "pass", "text": "MFD: 05/2024 | BATCH: ITC2405"},
                {"label": "Manufacturer Details", "bbox": [295, 50, 360, 550], "status": "pass", "text": "Mfd by: ITC Limited, Virginia House, 37 J.L. Nehru Rd, Kolkata, WB - 700071"},
                {"label": "Consumer Care", "bbox": [375, 50, 445, 550], "status": "pass", "text": "Consumer Care: 1800-425-4444 | Email: itccares@itc.in | PO Box 564, Kolkata"}
            ],
            "description": "Standard 5kg flour bag. Fully compliant with all LMPC Rules including Unit Sale Price."
        },
        {
            "id": "SMP-002",
            "brand": "Parle",
            "commodity_name": "Parle-G Glucose Biscuits",
            "category": "Bakery & Confectionery",
            "barcode": "8901719102456",
            "is_imported": False,
            "country_of_origin": "India",
            "packaging_shape": "rectangular",
            "dimensions_cm": {"height": 18.0, "width": 9.0, "depth": 5.0},
            "pdp_info": {
                "pdp_area_sq_cm": 162.0,
                "package_type": "normal",
                "estimated_font_height_mm": 2.6,
                "font_aspect_ratio": 0.42
            },
            "extracted_data": {
                "manufacturer_name": "Parle Products Pvt. Ltd.",
                "manufacturer_address": "North Level Crossing, Vile Parle East, Mumbai, Maharashtra - 400057",
                "is_imported": False,
                "country_of_origin": "India",
                "commodity_name": "Glucose Biscuits",
                "net_quantity_raw": "250 g",
                "mfg_date_raw": "04/2024",
                "mrp_raw": "MRP Rs. 30.00 incl. of all taxes",
                "unit_sale_price_raw": "",
                "consumer_care_name": "Consumer Care Manager",
                "consumer_care_phone": "022-26143535",
                "consumer_care_email": "",  # VIOLATION: Missing email
                "consumer_care_address": "North Level Crossing, Vile Parle East, Mumbai - 400057",
                "has_sticker_over_mrp": False,
                "has_dual_mrp": False
            },
            "bounding_boxes": [
                {"label": "Generic Name", "bbox": [35, 40, 75, 500], "status": "pass", "text": "PARLE-G GLUCOSE BISCUITS"},
                {"label": "Net Quantity", "bbox": [90, 40, 130, 240], "status": "pass", "text": "NET WT: 250 g"},
                {"label": "MRP & Taxes", "bbox": [145, 40, 185, 450], "status": "pass", "text": "MRP Rs. 30.00 INCL. OF ALL TAXES"},
                {"label": "Mfg Date", "bbox": [195, 40, 230, 310], "status": "pass", "text": "MFG DATE: 04/2024"},
                {"label": "Manufacturer Address", "bbox": [240, 40, 305, 550], "status": "pass", "text": "Mfd by: Parle Products Pvt Ltd, Vile Parle (E), Mumbai - 400057"},
                {"label": "Consumer Care", "bbox": [320, 40, 380, 550], "status": "fail", "text": "For feedback call: 022-26143535 (Email address missing)"}
            ],
            "description": "Common consumer snack pack. Violates Rule 6(1)(f) due to missing mandatory consumer care email address."
        },
        {
            "id": "SMP-003",
            "brand": "Himalaya",
            "commodity_name": "Purifying Neem Face Wash",
            "category": "Personal Care & Cosmetics",
            "barcode": "8901138820120",
            "is_imported": False,
            "country_of_origin": "India",
            "packaging_shape": "cylindrical",
            "dimensions_cm": {"height": 16.0, "diameter": 5.0},
            "pdp_info": {
                "pdp_area_sq_cm": 100.5,
                "package_type": "normal",
                "estimated_font_height_mm": 1.1,  # VIOLATION: Below 2.0mm Schedule II min
                "font_aspect_ratio": 0.28         # VIOLATION: font aspect ratio below 0.30
            },
            "extracted_data": {
                "manufacturer_name": "The Himalaya Drug Company",
                "manufacturer_address": "Makali, Bengaluru, Karnataka - 562162",
                "is_imported": False,
                "country_of_origin": "India",
                "commodity_name": "Face Wash",
                "net_quantity_raw": "150 mls.",  # VIOLATION: Non-standard symbol 'mls.'
                "mfg_date_raw": "02/2024",
                "mrp_raw": "MRP ₹ 190.00 incl. of all taxes",
                "unit_sale_price_raw": "",
                "consumer_care_name": "Himalaya Customer Care",
                "consumer_care_phone": "1800-208-1930",
                "consumer_care_email": "care@himalayawellness.com",
                "consumer_care_address": "Makali, Bengaluru - 562162",
                "has_sticker_over_mrp": False,
                "has_dual_mrp": False
            },
            "bounding_boxes": [
                {"label": "Generic Name", "bbox": [30, 40, 70, 480], "status": "pass", "text": "PURIFYING NEEM FACE WASH"},
                {"label": "Net Quantity", "bbox": [85, 40, 125, 270], "status": "fail", "text": "NET VOL: 150 mls. [ILLEGAL SYMBOL]"},
                {"label": "MRP & Taxes", "bbox": [140, 40, 180, 440], "status": "pass", "text": "MRP ₹ 190.00 INCL. OF ALL TAXES"},
                {"label": "Date of Mfg", "bbox": [190, 40, 225, 300], "status": "pass", "text": "MFD: 02/2024"},
                {"label": "Manufacturer", "bbox": [235, 40, 290, 540], "status": "pass", "text": "The Himalaya Drug Company, Makali, Bengaluru - 562162"},
                {"label": "Consumer Care", "bbox": [300, 40, 355, 550], "status": "pass", "text": "Contact: 1800-208-1930 | care@himalayawellness.com"},
                {"label": "Font Size Analysis", "bbox": [365, 40, 405, 550], "status": "fail", "text": "Font Height 1.1mm < 2.0mm Schedule II Minimum"}
            ],
            "description": "Cosmetic tube exhibiting two non-compliances: illegal unit symbol 'mls.' (Rule 12/13) and font height below Schedule II threshold."
        },
        {
            "id": "SMP-004",
            "brand": "Ferrero Rocher",
            "commodity_name": "Hazelnut Chocolates (Imported)",
            "category": "Confectionery / Imported",
            "barcode": "8000500003787",
            "is_imported": True,
            "country_of_origin": "",  # VIOLATION: Missing Country of Origin
            "packaging_shape": "rectangular",
            "dimensions_cm": {"height": 14.0, "width": 14.0, "depth": 7.0},
            "pdp_info": {
                "pdp_area_sq_cm": 196.0,
                "package_type": "normal",
                "estimated_font_height_mm": 2.4,
                "font_aspect_ratio": 0.44
            },
            "extracted_data": {
                "manufacturer_name": "Ferrero SpA, Italy / Ferrero India Pvt Ltd",
                "manufacturer_address": "MIDC Phase II, Baramati, Pune, Maharashtra", # Missing PIN code
                "is_imported": True,
                "country_of_origin": "", # VIOLATION: Critical missing declaration
                "commodity_name": "Hazelnut Chocolates",
                "net_quantity_raw": "200 g",
                "mfg_date_raw": "01/2024",
                "mrp_raw": "MRP ₹ 599.00 incl. of all taxes",
                "unit_sale_price_raw": "",
                "consumer_care_name": "Customer Service Officer",
                "consumer_care_phone": "1800-209-1200",
                "consumer_care_email": "customercare.india@ferrero.com",
                "consumer_care_address": "Baramati, Pune",
                "has_sticker_over_mrp": True, # VIOLATION: Rule 18(2) sticker over MRP
                "has_dual_mrp": False
            },
            "bounding_boxes": [
                {"label": "Generic Name", "bbox": [35, 40, 75, 510], "status": "pass", "text": "CRISP HAZELNUT AND MILK CHOCOLATE"},
                {"label": "Net Quantity", "bbox": [90, 40, 130, 250], "status": "pass", "text": "NET WEIGHT: 200 g"},
                {"label": "Country of Origin", "bbox": [140, 40, 175, 460], "status": "fail", "text": "[MISSING MANDATORY DECLARATION: COUNTRY OF ORIGIN]"},
                {"label": "MRP & Taxes", "bbox": [190, 40, 235, 460], "status": "fail", "text": "MRP ₹ 599.00 [ILLEGAL PAPER STICKER OVER ORIGINAL ₹ 499]"},
                {"label": "Importer Details", "bbox": [250, 40, 310, 540], "status": "warning", "text": "Ferrero India Pvt Ltd, Baramati, Pune (PIN code missing)"},
                {"label": "Consumer Care", "bbox": [325, 40, 380, 550], "status": "pass", "text": "Call: 1800-209-1200 | customercare.india@ferrero.com"}
            ],
            "description": "Imported chocolate box with critical violations: Missing Country of Origin (Rule 6(1)(a) Proviso) and illegal price over-stickering (Rule 18(2))."
        },
        {
            "id": "SMP-005",
            "brand": "Fortune",
            "commodity_name": "Sunlite Refined Sunflower Oil",
            "category": "Edible Oil",
            "barcode": "8906007280112",
            "is_imported": False,
            "country_of_origin": "India",
            "packaging_shape": "rectangular",
            "dimensions_cm": {"height": 24.0, "width": 15.0, "depth": 5.0},
            "pdp_info": {
                "pdp_area_sq_cm": 360.0,
                "package_type": "normal",
                "estimated_font_height_mm": 3.8,
                "font_aspect_ratio": 0.45
            },
            "extracted_data": {
                "manufacturer_name": "Adani Wilmar Limited",
                "manufacturer_address": "Fortune House, Near Navrangpura Rly Crossing, Ahmedabad, Gujarat - 380009",
                "is_imported": False,
                "country_of_origin": "India",
                "commodity_name": "Refined Sunflower Oil",
                "net_quantity_raw": "1 L",
                "mfg_date_raw": "06/2024",
                "expiry_date_raw": "03/2025",
                "mrp_raw": "MRP ₹ 135.00 incl. of all taxes",
                "unit_sale_price_raw": "USP ₹ 135.00 / L",
                "consumer_care_name": "Consumer Care Cell",
                "consumer_care_phone": "1800-233-9999",
                "consumer_care_email": "care@adaniwilmar.in",
                "consumer_care_address": "Fortune House, Navrangpura, Ahmedabad - 380009",
                "has_sticker_over_mrp": False,
                "has_dual_mrp": False
            },
            "bounding_boxes": [
                {"label": "Generic Name", "bbox": [35, 45, 75, 520], "status": "pass", "text": "FORTUNE SUNLITE REFINED SUNFLOWER OIL"},
                {"label": "Net Quantity", "bbox": [90, 45, 130, 240], "status": "pass", "text": "NET QUANTITY: 1 L"},
                {"label": "MRP & Taxes", "bbox": [145, 45, 185, 460], "status": "pass", "text": "MRP ₹ 135.00 (INCL. OF ALL TAXES)"},
                {"label": "Unit Sale Price", "bbox": [195, 45, 230, 360], "status": "pass", "text": "USP ₹ 135.00 / L"},
                {"label": "Mfg & Expiry", "bbox": [240, 45, 275, 420], "status": "pass", "text": "PKD: 06/2024 | USE BY: 03/2025"},
                {"label": "Manufacturer", "bbox": [285, 45, 345, 550], "status": "pass", "text": "Adani Wilmar Ltd, Fortune House, Navrangpura, Ahmedabad - 380009"},
                {"label": "Consumer Care", "bbox": [355, 45, 410, 550], "status": "pass", "text": "Consumer Care: 1800-233-9999 | care@adaniwilmar.in"}
            ],
            "description": "Standard 1 Litre edible oil pouch. Compliant with Unit Sale Price, dual weight/volume norms, and consumer grievance requirements."
        },
        {
            "id": "SMP-006",
            "brand": "Dettol",
            "commodity_name": "Original Liquid Handwash Refill",
            "category": "Personal Hygiene",
            "barcode": "8901396381014",
            "is_imported": False,
            "country_of_origin": "India",
            "packaging_shape": "rectangular",
            "dimensions_cm": {"height": 18.0, "width": 11.0, "depth": 4.0},
            "pdp_info": {
                "pdp_area_sq_cm": 198.0,
                "package_type": "normal",
                "estimated_font_height_mm": 2.2,
                "font_aspect_ratio": 0.40
            },
            "extracted_data": {
                "manufacturer_name": "Reckitt Benckiser (India) Pvt. Ltd.",
                "manufacturer_address": "DLF Cyber City, Phase II, Gurugram, Haryana - 122002",
                "is_imported": False,
                "country_of_origin": "India",
                "commodity_name": "Liquid Handwash",
                "net_quantity_raw": "175 ml",
                "mfg_date_raw": "03/2024",
                "mrp_raw": "MRP Rs. 49.00", # VIOLATION: Missing "inclusive of all taxes"
                "unit_sale_price_raw": "",
                "consumer_care_name": "Consumer Health Officer",
                "consumer_care_phone": "1800-102-6012",
                "consumer_care_email": "consumerhealth_in@reckitt.com",
                "consumer_care_address": "DLF Cyber City, Gurugram - 122002",
                "has_sticker_over_mrp": False,
                "has_dual_mrp": False
            },
            "bounding_boxes": [
                {"label": "Generic Name", "bbox": [35, 40, 75, 490], "status": "pass", "text": "DETTOL ORIGINAL LIQUID HANDWASH"},
                {"label": "Net Quantity", "bbox": [90, 40, 130, 240], "status": "pass", "text": "NET CONTENT: 175 ml"},
                {"label": "MRP & Taxes", "bbox": [145, 40, 185, 380], "status": "fail", "text": "MRP Rs. 49.00 [MISSING: INCL. OF ALL TAXES]"},
                {"label": "Batch & Mfg Date", "bbox": [195, 40, 230, 340], "status": "pass", "text": "MFD: 03/2024 | BATCH: RB09"},
                {"label": "Manufacturer Address", "bbox": [245, 40, 305, 550], "status": "pass", "text": "Reckitt Benckiser (India) Pvt Ltd, DLF Cyber City, Gurugram - 122002"},
                {"label": "Consumer Care", "bbox": [320, 40, 375, 550], "status": "pass", "text": "Toll Free: 1800-102-6012 | consumerhealth_in@reckitt.com"}
            ],
            "description": "Handwash refill pack committing a frequent market infraction: failing to specify 'inclusive of all taxes' under Rule 6(1)(e)."
        }
    ]

    @classmethod
    def get_sample_by_id(cls, sample_id: str) -> Optional[Dict[str, Any]]:
        for s in cls.SAMPLES:
            if s['id'] == sample_id:
                return s
        return None

    @classmethod
    def generate_sample_images(cls, output_dir: str):
        """
        Generate realistic high-contrast packaging label simulation images for the test samples.
        """
        os.makedirs(output_dir, exist_ok=True)

        for sample in cls.SAMPLES:
            sample_id = sample['id']
            img_path = os.path.join(output_dir, f"{sample_id}.png")
            if os.path.exists(img_path):
                continue

            # Create clean packaging canvas (width 600, height 500)
            img = Image.new('RGB', (600, 500), color=(248, 249, 250))
            draw = ImageDraw.Draw(img)

            # Draw outer packaging frame
            draw.rectangle([10, 10, 590, 490], outline=(180, 190, 200), width=3)
            # Top banner
            draw.rectangle([10, 10, 590, 55], fill=(24, 43, 73))
            
            # Government / Standard label header
            draw.text((25, 20), f"COMMODITY PACKAGING LABEL - {sample['brand'].upper()}", fill=(255, 255, 255))
            draw.text((450, 20), f"GTIN: {sample['barcode'][-8:]}", fill=(200, 220, 240))

            # Draw declarations with boxes
            for box in sample['bounding_boxes']:
                bbox = box['bbox'] # [ymin, xmin, ymax, xmax]
                status = box.get('status', 'pass')
                
                # Colors based on compliance
                if status == 'pass':
                    box_outline = (34, 197, 94) # Green
                    bg_fill = (240, 253, 244)
                    text_color = (20, 83, 45)
                elif status == 'warning':
                    box_outline = (234, 179, 8) # Amber
                    bg_fill = (254, 252, 232)
                    text_color = (133, 77, 14)
                else:
                    box_outline = (239, 68, 68) # Red
                    bg_fill = (254, 242, 242)
                    text_color = (153, 27, 27)

                # Draw field background & boundary
                draw.rectangle([bbox[1], bbox[0], bbox[3], bbox[2]], fill=bg_fill, outline=box_outline, width=2)
                
                # Field label tag
                tag_text = f"[{box['label']}]"
                draw.text((bbox[1] + 6, bbox[0] + 4), tag_text, fill=(100, 116, 139))
                # Declaration content text
                draw.text((bbox[1] + 6, bbox[0] + 18), box['text'], fill=text_color)

            # Footer with statutory notice reminder
            draw.rectangle([10, 455, 590, 490], fill=(241, 245, 249))
            draw.text((25, 465), "Statutory Declaration under Legal Metrology Act, 2009 & LMPC Rules 2011", fill=(71, 85, 105))

            img.save(img_path, format="PNG")
