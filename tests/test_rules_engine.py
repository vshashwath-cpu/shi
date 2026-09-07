"""
Unit Tests for Legal Metrology Rules Engine (LMPC Rules, 2011)
Validates compliance checking across all statutory mandatory declarations.
"""

import unittest
from core.rules_engine import LegalMetrologyRulesEngine, ViolationSeverity

class TestLegalMetrologyRulesEngine(unittest.TestCase):

    def setUp(self):
        self.engine = LegalMetrologyRulesEngine()

    def test_fully_compliant_product(self):
        """Verify that a compliant product receives 100% score and COMPLIANT status."""
        data = {
            "manufacturer_name": "ITC Limited",
            "manufacturer_address": "Virginia House, 37 J.L. Nehru Road, Kolkata, West Bengal - 700071",
            "is_imported": False,
            "commodity_name": "Whole Wheat Atta",
            "net_quantity_raw": "5 kg",
            "mfg_date_raw": "05/2024",
            "mrp_raw": "MRP ₹ 285.00 (inclusive of all taxes)",
            "unit_sale_price_raw": "USP ₹ 57.00 / kg",
            "consumer_care_name": "ITC Consumer Care Cell",
            "consumer_care_phone": "1800-425-4444",
            "consumer_care_email": "itccares@itc.in",
            "consumer_care_address": "Kolkata - 700071"
        }
        pdp_info = {
            "pdp_area_sq_cm": 912.0,
            "package_type": "normal",
            "estimated_font_height_mm": 5.0,
            "font_aspect_ratio": 0.45
        }
        result = self.engine.evaluate(data, pdp_info)
        self.assertEqual(result["status"], "COMPLIANT")
        self.assertEqual(result["compliance_score"], 100)
        self.assertEqual(len(result["violations"]), 0)

    def test_prohibited_non_standard_units(self):
        """Rule 12(2) & 13: 'gms', 'kgs', 'ltrs', 'mls' are strictly prohibited."""
        bad_units = ["500 gms", "250 gm", "1 kgs", "750 mls", "1 ltrs", "10 nos", "5 pcs"]
        for bad in bad_units:
            data = {
                "manufacturer_name": "Test Co",
                "manufacturer_address": "Delhi - 110001",
                "commodity_name": "Test",
                "net_quantity_raw": bad,
                "mfg_date_raw": "04/2024",
                "mrp_raw": "MRP ₹ 100.00 incl. of all taxes",
                "consumer_care_phone": "1800-111-2222",
                "consumer_care_email": "care@test.com"
            }
            result = self.engine.evaluate(data)
            unit_violations = [v for v in result["violations"] if "Rule 12(2)" in v["rule"] or "Rule 13" in v["rule"]]
            self.assertTrue(len(unit_violations) > 0, f"Expected violation for non-standard unit '{bad}'")
            self.assertEqual(unit_violations[0]["severity"], ViolationSeverity.CRITICAL)

    def test_missing_inclusive_of_all_taxes(self):
        """Rule 6(1)(e): MRP must state 'incl. of all taxes' or 'inclusive of all taxes'."""
        data = {
            "manufacturer_name": "Test Co",
            "manufacturer_address": "Mumbai - 400001",
            "commodity_name": "Snack",
            "net_quantity_raw": "100 g",
            "mfg_date_raw": "04/2024",
            "mrp_raw": "MRP Rs. 50.00",  # Missing 'incl. of all taxes'
            "consumer_care_phone": "1800-111-2222",
            "consumer_care_email": "care@test.com"
        }
        result = self.engine.evaluate(data)
        mrp_violations = [v for v in result["violations"] if v["rule"] == "Rule 6(1)(e)"]
        self.assertTrue(len(mrp_violations) > 0)
        self.assertEqual(mrp_violations[0]["severity"], ViolationSeverity.CRITICAL)

    def test_illegal_mrp_over_stickering(self):
        """Rule 18(2): Stickers pasted over printed MRP are strictly illegal."""
        data = {
            "manufacturer_name": "Test Co",
            "manufacturer_address": "Bangalore - 560001",
            "commodity_name": "Chocolates",
            "net_quantity_raw": "200 g",
            "mfg_date_raw": "03/2024",
            "mrp_raw": "MRP ₹ 599.00 incl. of all taxes",
            "has_sticker_over_mrp": True,  # Illegal over-stickering
            "consumer_care_phone": "1800-111-2222",
            "consumer_care_email": "care@test.com"
        }
        result = self.engine.evaluate(data)
        sticker_violations = [v for v in result["violations"] if v["rule"] == "Rule 18(2)"]
        self.assertTrue(len(sticker_violations) > 0)
        self.assertEqual(sticker_violations[0]["severity"], ViolationSeverity.CRITICAL)

    def test_missing_country_of_origin_on_imported_good(self):
        """Rule 6(1)(a) Proviso: Country of Origin is mandatory on imported commodities."""
        data = {
            "manufacturer_name": "Overseas Producer",
            "manufacturer_address": "Rome, Italy",
            "is_imported": True,
            "country_of_origin": "",  # Missing!
            "commodity_name": "Olive Oil",
            "net_quantity_raw": "500 ml",
            "mfg_date_raw": "01/2024",
            "mrp_raw": "MRP ₹ 800.00 incl. of all taxes",
            "consumer_care_phone": "1800-111-2222",
            "consumer_care_email": "care@test.com"
        }
        result = self.engine.evaluate(data)
        coo_violations = [v for v in result["violations"] if "Country of Origin" in v["declaration"]]
        self.assertTrue(len(coo_violations) > 0)
        self.assertEqual(coo_violations[0]["severity"], ViolationSeverity.CRITICAL)

    def test_unit_sale_price_mandatory_above_one_kg(self):
        """Rule 6(1)(da) (2022 Amendment): USP mandatory for > 1kg/1L."""
        data = {
            "manufacturer_name": "Test Co",
            "manufacturer_address": "Kolkata - 700001",
            "commodity_name": "Rice",
            "net_quantity_raw": "5 kg",
            "mfg_date_raw": "02/2024",
            "mrp_raw": "MRP ₹ 350.00 incl. of all taxes",
            "unit_sale_price_raw": "",  # Missing USP on 5kg pack
            "consumer_care_phone": "1800-111-2222",
            "consumer_care_email": "care@test.com"
        }
        result = self.engine.evaluate(data)
        usp_violations = [v for v in result["violations"] if "Rule 6(1)(da)" in v["rule"]]
        self.assertTrue(len(usp_violations) > 0)
        self.assertEqual(usp_violations[0]["severity"], ViolationSeverity.MAJOR)

    def test_schedule_ii_font_size_violation(self):
        """Rule 9 & Schedule II: Font height below statutory threshold for given PDP area."""
        data = {
            "manufacturer_name": "Cosmetic Labs",
            "manufacturer_address": "Bengaluru - 560001",
            "commodity_name": "Face Cream",
            "net_quantity_raw": "100 g",
            "mfg_date_raw": "01/2024",
            "mrp_raw": "MRP ₹ 250.00 incl. of all taxes",
            "consumer_care_phone": "1800-111-2222",
            "consumer_care_email": "care@test.com"
        }
        pdp_info = {
            "pdp_area_sq_cm": 150.0, # Schedule II threshold for 100-500 cm² is 2.0 mm
            "package_type": "normal",
            "estimated_font_height_mm": 1.2, # 1.2 mm is below 2.0 mm
            "font_aspect_ratio": 0.40
        }
        result = self.engine.evaluate(data, pdp_info)
        font_violations = [v for v in result["violations"] if "Schedule II" in v["rule"]]
        self.assertTrue(len(font_violations) > 0)
        self.assertEqual(font_violations[0]["severity"], ViolationSeverity.MAJOR)

if __name__ == '__main__':
    unittest.main()
