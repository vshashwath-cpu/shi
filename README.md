# Legal Metrology (Packaged Commodities) Rules, 2011 - Automated Compliance System

**Smart India Hackathon 2026 | Problem Statement ID: 26034**  
**Ministry of Consumer Affairs, Food & Public Distribution**  
**Department of Consumer Affairs (DoCA), Government of India**

---

## Executive Summary

Across Indian retail markets, supermarkets, and e-commerce platforms, millions of packaged commodities are sold daily. Under the **Legal Metrology Act, 2009** and the **Legal Metrology (Packaged Commodities) Rules, 2011**, manufacturers, packers, and importers are legally mandated to declare essential consumer protection information on packaging labels.

Manual inspection by enforcement officers is time-consuming, resource-intensive, and prone to oversight. Common market non-compliances include:
- Missing or incomplete manufacturer/packer/importer name and registered address with PIN code (Rule 6(1)(a)).
- Missing Country of Origin on imported commodities (Rule 6(1)(a) Proviso).
- Use of non-standard, prohibited unit symbols such as `"gms"`, `"kgs"`, `"ltrs"`, `"mls"`, `"nos"`, or `"pcs"` instead of approved SI units (`g`, `kg`, `l`, `ml`, `N`) (Rule 12(2) & Rule 13).
- Omission of the mandatory statutory phrase `"inclusive of all taxes"` / `"incl. of all taxes"` in Maximum Retail Price (MRP) declarations (Rule 6(1)(e)).
- Affixing paper price stickers over printed MRP (Rule 18(2) sticker violation).
- Missing Unit Sale Price (USP) for packaging $> 1\text{ kg}$ or $> 1\text{ L}$ (Rule 6(1)(da) 2022 amendment).
- Incomplete Consumer Grievance Care contact details (missing phone number or email ID) (Rule 6(1)(f)).
- Character and numeral font heights below Schedule II statutory minimums relative to Principal Display Panel (PDP) surface area (Rule 9).

This software system delivers an automated, high-precision compliance audit and enforcement platform for Legal Metrology officers, state controllers, and e-commerce compliance auditors.

---

## Key Capabilities & Functional Architecture

```
                               ┌────────────────────────────────────────┐
                               │   Packaged Commodity Label / Photo     │
                               └──────────────────┬─────────────────────┘
                                                  │
                                                  ▼
                        ┌─────────────────────────────────────────────────────┐
                        │              Hybrid Multi-Modal Vision              │
                        │  ┌───────────────────────┐ ┌──────────────────────┐ │
                        │  │ Local Spatial OCR /   │ │ Google Gemini 2.5    │ │
                        │  │ Pillow Label Parser   │ │ Flash VLM (Optional) │ │
                        │  └───────────────────────┘ └──────────────────────┘ │
                        └─────────────────────────┬───────────────────────────┘
                                                  │
                                                  ▼
                        ┌─────────────────────────────────────────────────────┐
                        │     Deterministic LMPC 2011 Rules Engine            │
                        │  • Rule 6(1)(a): Mfg Name, Complete Address, Pincode│
                        │  • Rule 6(1)(a) Proviso: Country of Origin          │
                        │  • Rule 6(1)(b): Generic Commodity Name Prominence  │
                        │  • Rule 6(1)(c), 12, 13: Standard Units (g, kg, ml) │
                        │  • Rule 6(1)(d): Month & Year of Mfg/Packing/Import │
                        │  • Rule 6(1)(e): MRP "inclusive of all taxes"       │
                        │  • Rule 6(1)(da): Unit Sale Price (USP) Requirement │
                        │  • Rule 6(1)(f): Consumer Grievance Phone & Email   │
                        │  • Rule 9 & Schedule II: Minimum Font Height (mm)   │
                        │  • Rule 18(2): MRP Alteration & Sticker Prohibition │
                        └─────────────────────────┬───────────────────────────┘
                                                  │
                   ┌──────────────────────────────┼──────────────────────────────┐
                   ▼                              ▼                              ▼
    ┌──────────────────────────────┐ ┌───────────────────────────┐ ┌───────────────────────────┐
    │  Interactive Visual Studio   │ │   Executive Dashboard     │ │    Digital Legal Reports  │
    │  • Color-Coded Bounding Boxes│ │   • Real-Time KPIs        │ │    • Official ReportLab PDF│
    │  • Human-In-The-Loop Override│ │   • Rule Infraction Charts│ │    • Sec 36 Notice of Fine │
    │  • Live Camera Snapshot      │ │   • Case History Registry │ │    • CSV/JSON Audit Trails │
    └──────────────────────────────┘ └───────────────────────────┘ └───────────────────────────┘
```

---

## Statutory Rule Matrix Implemented

| Rule Clause | Statutory Requirement | Non-Compliance Severity | Legal Citation & Consequences |
| :--- | :--- | :--- | :--- |
| **Rule 6(1)(a)** | Full name & complete address with postal PIN code. | **CRITICAL** | Sec 36(1), Legal Metrology Act, 2009 |
| **Rule 6(1)(a) Proviso** | Mandatory declaration of **Country of Origin** on imported items. | **CRITICAL** | Sec 36(1) penalty up to ₹ 25,000/- |
| **Rule 6(1)(b)** | Generic or common name of the commodity on the PDP. | **MAJOR** | Rule 6(1)(b) procedural defect |
| **Rule 6(1)(c) & Rule 12/13** | Standard SI units only (`g`, `kg`, `ml`, `l`, `N`). Prohibits `gms`, `kgs`, `ltrs`, `mls`, `nos`. | **CRITICAL** | Prosecutable under Rule 12(2) & 13 |
| **Rule 6(1)(d)** | Month and Year of manufacture / packing / import (`MM/YYYY`). | **CRITICAL** | Sec 36(1) offense |
| **Rule 6(1)(e)** | MRP in ₹ or Rs. strictly inclusive of all taxes (`incl. of all taxes`). | **CRITICAL** | Mandatory statutory phrase |
| **Rule 6(1)(da)** *(2022)* | Unit Sale Price (USP) for commodities $> 1\text{ kg}$ or $> 1\text{ L}$. | **MAJOR** | 2022 Amendment violation |
| **Rule 6(1)(f)** | Complete consumer care cell: contact person, address, phone, and valid email. | **MAJOR** | Grievance redressal violation |
| **Rule 9 & Schedule II** | Minimum font and numeral height in mm based on PDP surface area and net quantity. | **MAJOR** | Schedule II legibility norm |
| **Rule 18(2)** | Strict prohibition of price stickers or alterations pasted over printed MRP. | **CRITICAL** | Illegal pricing / tampering |

---

## Directory Structure

```
lmpc-compliance-system/
├── app.py                      # Flask Application factory & REST API endpoints
├── lmpc_inspections.db         # Persistent SQLite database
├── core/
│   ├── __init__.py
│   ├── rules_engine.py         # Deterministic LMPC Rules 2011 compliance validator
│   ├── font_estimator.py       # Schedule II PDP area & font height calculator
│   ├── ocr_vision_engine.py    # Multi-modal OCR & bounding box coordinator (Gemini + Local)
│   ├── database.py             # SQLite database management layer
│   ├── sample_data.py          # Benchmark Indian packaged commodities & image generator
│   └── report_generator.py     # ReportLab PDF & CSV statutory notice generator
├── templates/
│   ├── base.html               # Responsive government portal base layout (Tailwind CSS)
│   ├── dashboard.html          # Executive & Enforcement analytics dashboard
│   ├── scanner.html            # Interactive Visual Inspection Studio & Canvas
│   ├── repository.html         # Searchable inspection repository & case filter
│   ├── report_view.html        # Statutory Notice & case file view
│   └── settings.html           # Officer credentials & Gemini AI engine configuration
├── static/
│   ├── uploads/                # User uploaded packaging images
│   ├── samples/                # Benchmark commodity packaging images
│   └── reports/                # Generated official PDF inspection reports
└── tests/
    ├── test_rules_engine.py    # Unit tests for all statutory clauses
    └── test_app.py             # Integration tests for Flask app, PDF & DB
```

---

## Quickstart & Installation

### 1. Requirements
- Python 3.10+ (Tested on Python 3.14)
- Pip packages: `Flask`, `Pillow`, `ReportLab`

```bash
cd C:\Users\vshas\.gemini\antigravity\scratch\lmpc-compliance-system
python -m pip install Flask pillow reportlab
```

### 2. Run Test Suite
```bash
python -m unittest discover tests
```
*Expected: 14 tests run with 0 errors (Ran 14 tests in ~0.25s, OK).*

### 3. Launch the Application Server
```bash
python app.py
```
Open your browser and navigate to:
**`http://127.0.0.1:5000`**

---

## Benchmark Test Cases Included

The system includes pre-loaded benchmark commodities representing compliant goods and common statutory violations:
1. **Aashirvaad Superior MP Atta (5kg)**: Fully compliant baseline (Score: 100%).
2. **Parle-G Glucose Biscuits (250g)**: Missing consumer care email under Rule 6(1)(f) (Score: 88%).
3. **Himalaya Purifying Neem Face Wash (150ml)**: Illegal non-standard unit `"150 mls."` + font size below Schedule II (Score: 63%).
4. **Ferrero Rocher Chocolates (Imported)**: Missing Country of Origin + illegal paper sticker over printed MRP (Score: 50%).
5. **Fortune Sunlite Sunflower Oil (1L)**: Edible oil packaging with verified Unit Sale Price (Score: 100%).
6. **Dettol Liquid Handwash Refill (175ml)**: MRP missing mandatory statutory phrase `"inclusive of all taxes"` (Score: 75%).
