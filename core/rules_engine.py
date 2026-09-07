"""
Legal Metrology (Packaged Commodities) Rules, 2011 - Statutory Compliance Rules Engine
Implements deterministic legal validation as prescribed under the Legal Metrology Act, 2009
and the Legal Metrology (Packaged Commodities) Rules, 2011, with 2017 & 2022 amendments.
"""

import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class ViolationSeverity:
    CRITICAL = "CRITICAL"  # Statutory offense under Section 36(1) of Legal Metrology Act, 2009
    MAJOR = "MAJOR"        # Procedural defect or omission under Rule 6 / Rule 18
    MINOR = "MINOR"        # Formatting/aesthetic variance or placement defect

class LegalMetrologyRulesEngine:
    """
    Validation engine strictly implementing Legal Metrology (Packaged Commodities) Rules, 2011.
    """

    # Rule 12 & 13: Standard approved SI units
    STANDARD_UNITS = {
        'weight': ['mg', 'g', 'kg'],
        'volume': ['ml', 'l', 'L', 'kL'],
        'length': ['mm', 'cm', 'm'],
        'area': ['sq cm', 'sq m'],
        'volume_solid': ['cu cm', 'cu m'],
        'count': ['N', 'U']
    }

    # Prohibited non-standard symbols under Rule 12(2) & Rule 13
    NON_STANDARD_SYMBOLS = [
        'gms', 'gm', 'g.', 'kgs', 'kg.', 'kilo', 'kilos',
        'ltrs', 'ltr', 'litres', 'liter', 'liters',
        'ml.', 'mls', 'millilitres',
        'no.', 'nos', 'pcs', 'piece', 'pieces', 'pkts', 'packets'
    ]

    # Schedule II: Minimum font height (in mm) based on PDP area in sq cm
    # (area_min, area_max, min_height_normal_mm, min_height_blown_mm)
    SCHEDULE_II_PDP_TABLE = [
        (0, 50, 1.0, 2.0),
        (50, 100, 1.5, 3.0),
        (100, 500, 2.0, 4.0),
        (500, 2500, 4.0, 6.0),
        (2500, float('inf'), 6.0, 8.0),
    ]

    # Schedule II: Minimum font height based on Net Quantity
    SCHEDULE_II_NET_QTY_TABLE = [
        (0, 50, 1.0),       # <= 50g / ml
        (50, 200, 2.0),     # 50g to 200g / ml
        (200, 1000, 4.0),   # 200g to 1kg / L
        (1000, float('inf'), 6.0), # > 1kg / L
    ]

    def __init__(self):
        pass

    def evaluate(self, extracted_data: Dict[str, Any], pdp_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate extracted label declarations against LMPC Rules 2011.
        """
        violations: List[Dict[str, Any]] = []
        checks_passed: List[Dict[str, Any]] = []

        # 1. Rule 6(1)(a): Manufacturer / Packer / Importer Name & Address
        self._check_manufacturer_details(extracted_data, violations, checks_passed)

        # 2. Rule 6(1)(a) import clause: Country of Origin
        self._check_country_of_origin(extracted_data, violations, checks_passed)

        # 3. Rule 6(1)(b): Generic / Common Name of Commodity
        self._check_commodity_name(extracted_data, violations, checks_passed)

        # 4. Rule 6(1)(c), Rule 12 & 13: Net Quantity & Standard SI Units
        net_qty_num, net_qty_unit = self._check_net_quantity(extracted_data, violations, checks_passed)

        # 5. Rule 6(1)(d): Month & Year of Manufacture / Packing / Import
        self._check_dates(extracted_data, violations, checks_passed)

        # 6. Rule 6(1)(e) & Rule 18(2): Maximum Retail Price (MRP), Taxes & Stickers
        self._check_mrp(extracted_data, violations, checks_passed)

        # 7. Rule 6(1)(da): Unit Sale Price (USP) (2022 Amendment)
        self._check_unit_sale_price(extracted_data, net_qty_num, net_qty_unit, violations, checks_passed)

        # 8. Rule 6(1)(f): Consumer Care Details (Grievance Redressal)
        self._check_consumer_care(extracted_data, violations, checks_passed)

        # 9. Rule 9 & Schedule II: Minimum Font Size & Numeral Height
        self._check_font_size(extracted_data, pdp_info, net_qty_num, net_qty_unit, violations, checks_passed)

        # 10. Compute Overall Compliance Score & Verdict
        critical_count = sum(1 for v in violations if v['severity'] == ViolationSeverity.CRITICAL)
        major_count = sum(1 for v in violations if v['severity'] == ViolationSeverity.MAJOR)
        minor_count = sum(1 for v in violations if v['severity'] == ViolationSeverity.MINOR)

        # Base scoring: 100% minus deductions
        score = 100 - (critical_count * 25) - (major_count * 12) - (minor_count * 5)
        score = max(0, min(100, score))

        if critical_count > 0:
            status = "NON_COMPLIANT_CRITICAL"
            verdict = "Violation Notice Required (Sec 36, Legal Metrology Act, 2009)"
            recommended_action = "Seizure / Compounding Notice for Prosecutable Violations"
        elif major_count > 0:
            status = "NON_COMPLIANT_MAJOR"
            verdict = "Advisory / Correction Notice Under LMPC Rules 2011"
            recommended_action = "Issue 15-Day Statutory Show-Cause Notice"
        elif minor_count > 0:
            status = "SUBSTANTIALLY_COMPLIANT"
            verdict = "Minor Observations / Technical Discrepancies"
            recommended_action = "Warning Letter / Re-inspection on Next Production Batch"
        else:
            status = "COMPLIANT"
            verdict = "Fully Compliant with LMPC Rules 2011"
            recommended_action = "Pass Inspection & Archive"

        return {
            "compliance_score": score,
            "status": status,
            "verdict": verdict,
            "recommended_action": recommended_action,
            "counts": {
                "critical": critical_count,
                "major": major_count,
                "minor": minor_count,
                "passed": len(checks_passed),
                "total_checks": len(violations) + len(checks_passed)
            },
            "violations": violations,
            "checks_passed": checks_passed,
            "timestamp": datetime.now().isoformat()
        }

    # ------------------ Individual Rule Checkers ------------------

    def _check_manufacturer_details(self, data: Dict[str, Any], violations: list, checks_passed: list):
        mfg_name = (data.get('manufacturer_name') or '').strip()
        mfg_addr = (data.get('manufacturer_address') or '').strip()

        if not mfg_name:
            violations.append({
                "rule": "Rule 6(1)(a)",
                "declaration": "Manufacturer / Packer Name",
                "severity": ViolationSeverity.CRITICAL,
                "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(a)",
                "issue": "Manufacturer / Packer / Importer name is missing from the label.",
                "remedy": "Display full legal entity name of manufacturer, packer or importer."
            })
        else:
            checks_passed.append({
                "rule": "Rule 6(1)(a)",
                "declaration": "Manufacturer / Packer Name",
                "extracted_value": mfg_name
            })

        if not mfg_addr:
            violations.append({
                "rule": "Rule 6(1)(a)",
                "declaration": "Manufacturer / Packer Address",
                "severity": ViolationSeverity.CRITICAL,
                "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(a)",
                "issue": "Complete postal address of manufacturer/packer is missing.",
                "remedy": "Provide complete factory/registered address including city, state, and 6-digit PIN code."
            })
        else:
            # Check for pincode
            pincode_match = re.search(r'\b[1-9][0-9]{5}\b', mfg_addr)
            if not pincode_match:
                violations.append({
                    "rule": "Rule 6(1)(a)",
                    "declaration": "Manufacturer Address Completeness",
                    "severity": ViolationSeverity.MAJOR,
                    "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(a) explanation",
                    "issue": f"Address lacks a valid 6-digit Indian PIN code: '{mfg_addr}'",
                    "remedy": "Include valid 6-digit postal index number (PIN code) in the manufacturer address."
                })
            else:
                checks_passed.append({
                    "rule": "Rule 6(1)(a)",
                    "declaration": "Manufacturer Address",
                    "extracted_value": mfg_addr
                })

    def _check_country_of_origin(self, data: Dict[str, Any], violations: list, checks_passed: list):
        is_imported = data.get('is_imported', False)
        country = (data.get('country_of_origin') or '').strip()

        if is_imported:
            if not country:
                violations.append({
                    "rule": "Rule 6(1)(a) - Proviso",
                    "declaration": "Country of Origin (Imported Commodity)",
                    "severity": ViolationSeverity.CRITICAL,
                    "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(a) Proviso",
                    "issue": "Mandatory declaration 'Country of Origin' is missing on imported package.",
                    "remedy": "Explicitly declare 'Country of Origin: [Country Name]' or 'Made in [Country]'."
                })
            else:
                checks_passed.append({
                    "rule": "Rule 6(1)(a) - Proviso",
                    "declaration": "Country of Origin",
                    "extracted_value": country
                })

    def _check_commodity_name(self, data: Dict[str, Any], violations: list, checks_passed: list):
        name = (data.get('commodity_name') or '').strip()
        if not name:
            violations.append({
                "rule": "Rule 6(1)(b)",
                "declaration": "Generic / Common Name",
                "severity": ViolationSeverity.MAJOR,
                "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(b)",
                "issue": "Generic or common name of the commodity is missing or unidentifiable.",
                "remedy": "Provide the common or generic name of the packaged commodity prominently on the PDP."
            })
        else:
            checks_passed.append({
                "rule": "Rule 6(1)(b)",
                "declaration": "Generic / Common Name",
                "extracted_value": name
            })

    def _check_net_quantity(self, data: Dict[str, Any], violations: list, checks_passed: list) -> Tuple[Optional[float], Optional[str]]:
        net_qty_raw = (data.get('net_quantity_raw') or '').strip()
        if not net_qty_raw:
            violations.append({
                "rule": "Rule 6(1)(c)",
                "declaration": "Net Quantity",
                "severity": ViolationSeverity.CRITICAL,
                "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(c) & Rule 11",
                "issue": "Net quantity declaration is missing entirely.",
                "remedy": "Mandatorily declare net quantity in standard units of weight, measure, or number."
            })
            return None, None

        # Check for prohibited non-standard symbols
        lower_raw = net_qty_raw.lower()
        has_non_standard = False
        for bad_sym in self.NON_STANDARD_SYMBOLS:
            pattern = rf'\b{re.escape(bad_sym)}\b'
            if re.search(pattern, lower_raw):
                violations.append({
                    "rule": "Rule 12(2) & Rule 13",
                    "declaration": "Standard Unit Symbol Compliance",
                    "severity": ViolationSeverity.CRITICAL,
                    "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 12(2) & 13",
                    "issue": f"Non-standard unit symbol '{bad_sym}' used in net quantity ('{net_qty_raw}').",
                    "remedy": f"Use standard statutory SI symbols only: 'g' instead of 'gms/gm', 'kg' instead of 'kgs', 'ml' instead of 'mls/ml.', 'N' instead of 'nos/pcs'."
                })
                has_non_standard = True
                break

        qty_pattern = r'(\d+(?:\.\d+)?)\s*([a-zA-Z]+)'
        match = re.search(qty_pattern, net_qty_raw)
        if match:
            num = float(match.group(1))
            unit = match.group(2).lower()
            
            all_valid = [u.lower() for cat in self.STANDARD_UNITS.values() for u in cat]
            if unit in all_valid and not has_non_standard:
                checks_passed.append({
                    "rule": "Rule 6(1)(c) & Rule 13",
                    "declaration": "Net Quantity & Unit Symbol",
                    "extracted_value": f"{num} {unit}"
                })
            return num, unit
        else:
            violations.append({
                "rule": "Rule 6(1)(c)",
                "declaration": "Net Quantity Parseable Format",
                "severity": ViolationSeverity.MAJOR,
                "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(c)",
                "issue": f"Cannot parse numeric net quantity and SI unit from '{net_qty_raw}'.",
                "remedy": "Format net quantity clearly as numeral followed by standard unit (e.g. '500 g', '1 kg', '200 ml', '1 N')."
            })
            return None, None

    def _check_dates(self, data: Dict[str, Any], violations: list, checks_passed: list):
        mfg_date_raw = (data.get('mfg_date_raw') or '').strip()
        if not mfg_date_raw:
            violations.append({
                "rule": "Rule 6(1)(d)",
                "declaration": "Date of Manufacture / Packing / Import",
                "severity": ViolationSeverity.CRITICAL,
                "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(d)",
                "issue": "Month and Year of manufacture, packing, or import is missing.",
                "remedy": "Declare month and year of manufacture or packing clearly (e.g., '03/2024' or 'Mar 2024')."
            })
            return

        valid_date_found = False
        date_patterns = [
            r'(0[1-9]|1[0-2])[\/\.-](\d{4})',
            r'(0[1-9]|1[0-2])[\/\.-](\d{2})',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\.,\/-]+(\d{4})'
        ]

        for pat in date_patterns:
            if re.search(pat, mfg_date_raw, re.IGNORECASE):
                valid_date_found = True
                break

        if valid_date_found:
            checks_passed.append({
                "rule": "Rule 6(1)(d)",
                "declaration": "Date of Manufacture / Packing",
                "extracted_value": mfg_date_raw
            })
        else:
            violations.append({
                "rule": "Rule 6(1)(d)",
                "declaration": "Date Format Compliance",
                "severity": ViolationSeverity.MAJOR,
                "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(d)",
                "issue": f"Date '{mfg_date_raw}' does not conform to prescribed MM/YYYY or Month YYYY format.",
                "remedy": "Use standard format such as 'MM/YYYY' or 'Month YYYY'."
            })

    def _check_mrp(self, data: Dict[str, Any], violations: list, checks_passed: list):
        mrp_raw = (data.get('mrp_raw') or '').strip()
        has_sticker = data.get('has_sticker_over_mrp', False)
        has_dual_mrp = data.get('has_dual_mrp', False)

        if has_sticker:
            violations.append({
                "rule": "Rule 18(2)",
                "declaration": "MRP Sticker / Alteration Prohibition",
                "severity": ViolationSeverity.CRITICAL,
                "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 18(2)",
                "issue": "Paper sticker or handwritten alteration detected over printed MRP. Over-stickering is illegal under Rule 18(2).",
                "remedy": "Do not affix stickers over printed retail sale price without express central government authorization."
            })

        if has_dual_mrp:
            violations.append({
                "rule": "Rule 18(2A) / Dual Pricing",
                "declaration": "Dual MRP Prohibition",
                "severity": ViolationSeverity.CRITICAL,
                "citation": "Legal Metrology (Packaged Commodities) Amendment Rules - Dual MRP Prohibition",
                "issue": "Dual pricing detected on same packaged commodity across different retail outlets/platforms.",
                "remedy": "Maintain uniform Maximum Retail Price across all distribution channels."
            })

        if not mrp_raw:
            violations.append({
                "rule": "Rule 6(1)(e)",
                "declaration": "Maximum Retail Price (MRP)",
                "severity": ViolationSeverity.CRITICAL,
                "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(e)",
                "issue": "Maximum Retail Price (MRP) declaration is missing entirely.",
                "remedy": "Declare MRP in Indian Rupees inclusive of all taxes prominently."
            })
            return

        lower_mrp = mrp_raw.lower()
        tax_inclusive_match = re.search(r'(incl\w*\.?\s*of\s*all\s*taxes|inclusive\s*of\s*all\s*taxes)', lower_mrp)
        has_currency = bool(re.search(r'(₹|rs\.?|inr)', lower_mrp))

        if not tax_inclusive_match:
            violations.append({
                "rule": "Rule 6(1)(e)",
                "declaration": "MRP Inclusive of All Taxes Clause",
                "severity": ViolationSeverity.CRITICAL,
                "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(e)",
                "issue": f"MRP '{mrp_raw}' is missing mandatory statutory phrase 'incl. of all taxes' or 'inclusive of all taxes'.",
                "remedy": "Suffix MRP with 'incl. of all taxes' or '(inclusive of all taxes)'."
            })
        elif not has_currency:
            violations.append({
                "rule": "Rule 6(1)(e)",
                "declaration": "MRP Currency Representation",
                "severity": ViolationSeverity.MAJOR,
                "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(e)",
                "issue": f"MRP '{mrp_raw}' lacks statutory currency identifier (₹ or Rs.).",
                "remedy": "Prefix price with ₹ or 'Rs.'."
            })
        else:
            checks_passed.append({
                "rule": "Rule 6(1)(e)",
                "declaration": "Maximum Retail Price (MRP)",
                "extracted_value": mrp_raw
            })

    def _check_unit_sale_price(self, data: Dict[str, Any], net_qty_num: Optional[float], net_qty_unit: Optional[str], violations: list, checks_passed: list):
        usp_raw = (data.get('unit_sale_price_raw') or '').strip()
        
        is_mandatory = False
        if net_qty_num and net_qty_unit:
            unit = net_qty_unit.lower()
            if unit == 'kg' and net_qty_num > 1.0:
                is_mandatory = True
            elif unit == 'g' and net_qty_num > 1000.0:
                is_mandatory = True
            elif unit in ['l', 'litre', 'litres'] and net_qty_num > 1.0:
                is_mandatory = True
            elif unit == 'ml' and net_qty_num > 1000.0:
                is_mandatory = True
            elif unit in ['n', 'u'] and net_qty_num > 1.0:
                is_mandatory = True

        if is_mandatory:
            if not usp_raw:
                violations.append({
                    "rule": "Rule 6(1)(da) [2022 Amendment]",
                    "declaration": "Unit Sale Price (USP)",
                    "severity": ViolationSeverity.MAJOR,
                    "citation": "Legal Metrology (Packaged Commodities) Amendment Rules, 2021/2022 - Rule 6(1)(da)",
                    "issue": f"Unit Sale Price (USP) is missing on package with Net Quantity > 1kg/1L ({net_qty_num} {net_qty_unit}).",
                    "remedy": "Declare Unit Sale Price per g/kg/ml/L/number (e.g., 'USP ₹ 0.25 / g' or 'USP ₹ 25.00 / 100g')."
                })
            else:
                checks_passed.append({
                    "rule": "Rule 6(1)(da)",
                    "declaration": "Unit Sale Price (USP)",
                    "extracted_value": usp_raw
                })
        elif usp_raw:
            checks_passed.append({
                "rule": "Rule 6(1)(da)",
                "declaration": "Unit Sale Price (USP)",
                "extracted_value": usp_raw
            })

    def _check_consumer_care(self, data: Dict[str, Any], violations: list, checks_passed: list):
        c_name = (data.get('consumer_care_name') or '').strip()
        c_phone = (data.get('consumer_care_phone') or '').strip()
        c_email = (data.get('consumer_care_email') or '').strip()
        c_addr = (data.get('consumer_care_address') or '').strip()

        missing_elements = []
        if not c_name and not c_addr:
            missing_elements.append("Designation / Office / Postal Address")
        if not c_phone:
            missing_elements.append("Telephone / Toll-Free Number")
        if not c_email:
            missing_elements.append("Email Address")

        if missing_elements:
            violations.append({
                "rule": "Rule 6(1)(f)",
                "declaration": "Consumer Care Details Completeness",
                "severity": ViolationSeverity.MAJOR,
                "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(f)",
                "issue": f"Consumer Care information incomplete. Missing mandatory elements: {', '.join(missing_elements)}.",
                "remedy": "Provide complete consumer care cell details: contact person/office, address, phone number, and email ID."
            })
        else:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, c_email):
                violations.append({
                    "rule": "Rule 6(1)(f)",
                    "declaration": "Consumer Care Email Validity",
                    "severity": ViolationSeverity.MINOR,
                    "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(f)",
                    "issue": f"Consumer care email '{c_email}' appears invalid or malformed.",
                    "remedy": "Provide a valid, monitored customer support email address."
                })
            else:
                checks_passed.append({
                    "rule": "Rule 6(1)(f)",
                    "declaration": "Consumer Care Grievance Redressal",
                    "extracted_value": f"Phone: {c_phone} | Email: {c_email}"
                })

    def _check_font_size(self, data: Dict[str, Any], pdp_info: Optional[Dict[str, Any]], net_qty_num: Optional[float], net_qty_unit: Optional[str], violations: list, checks_passed: list):
        if not pdp_info:
            return

        pdp_area = pdp_info.get('pdp_area_sq_cm')
        pkg_type = pdp_info.get('package_type', 'normal')
        est_font_height_mm = pdp_info.get('estimated_font_height_mm')
        aspect_ratio = pdp_info.get('font_aspect_ratio')

        if est_font_height_mm is None:
            return

        required_min_mm = 1.0
        if pdp_area is not None:
            for row in self.SCHEDULE_II_PDP_TABLE:
                if row[0] <= pdp_area <= row[1]:
                    required_min_mm = row[3] if pkg_type == 'blown_or_moulded' else row[2]
                    break
        elif net_qty_num is not None and net_qty_unit:
            norm_grams = net_qty_num
            if net_qty_unit in ['kg', 'l', 'litre']:
                norm_grams = net_qty_num * 1000.0
            for row in self.SCHEDULE_II_NET_QTY_TABLE:
                if row[0] <= norm_grams <= row[1]:
                    required_min_mm = row[2]
                    break

        if est_font_height_mm < required_min_mm:
            violations.append({
                "rule": "Rule 9 & Schedule II",
                "declaration": "Minimum Font Height / Numeral Size",
                "severity": ViolationSeverity.MAJOR,
                "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 9 & Schedule II Table",
                "issue": f"Estimated font height is {est_font_height_mm:.2f} mm, which is below mandatory minimum of {required_min_mm:.1f} mm for PDP area {pdp_area} sq cm.",
                "remedy": f"Increase numeral and character height to at least {required_min_mm:.1f} mm."
            })
        else:
            checks_passed.append({
                "rule": "Rule 9 & Schedule II",
                "declaration": "Font Height & Numeral Legibility",
                "extracted_value": f"{est_font_height_mm:.2f} mm (Required: >= {required_min_mm:.1f} mm)"
            })

        if aspect_ratio is not None and aspect_ratio < 0.30:
            violations.append({
                "rule": "Rule 9(3)",
                "declaration": "Letter Aspect Ratio (Legibility)",
                "severity": ViolationSeverity.MINOR,
                "citation": "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 9(3)",
                "issue": f"Character width-to-height ratio ({aspect_ratio:.2f}) is compressed below statutory 1:3 ratio.",
                "remedy": "Ensure characters are not vertically condensed beyond standard aspect ratio."
            })
