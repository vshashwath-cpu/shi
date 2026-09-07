"""
Digital Compliance Report & Statutory Notice Generator
Generates official inspection reports and Show Cause Notices under Section 36 of Legal Metrology Act, 2009
in printable PDF format (using ReportLab) and structured JSON/CSV formats.
"""

import os
import json
import csv
from io import StringIO
from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable
)

class ReportGenerator:
    """
    Generates high-fidelity PDF and tabular compliance reports for Legal Metrology enforcement officers.
    """

    @classmethod
    def generate_pdf(cls, inspection_data: Dict[str, Any], output_pdf_path: str) -> str:
        """
        Build an official government-format statutory compliance report PDF.
        """
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        normal_style = styles['Normal']
        normal_style.fontSize = 9
        normal_style.leading = 12

        title_style = ParagraphStyle(
            'GovTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            alignment=1, # Center
            textColor=colors.HexColor('#0f172a')
        )

        subtitle_style = ParagraphStyle(
            'GovSubTitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            alignment=1, # Center
            textColor=colors.HexColor('#334155')
        )

        h2_style = ParagraphStyle(
            'Heading2',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#1e293b')
        )

        cell_style = ParagraphStyle(
            'CellText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#1e293b')
        )

        cell_bold = ParagraphStyle(
            'CellBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#0f172a')
        )

        elements = []

        # 1. Official Government Header
        elements.append(Paragraph("GOVERNMENT OF INDIA", title_style))
        elements.append(Paragraph("MINISTRY OF CONSUMER AFFAIRS, FOOD & PUBLIC DISTRIBUTION", subtitle_style))
        elements.append(Paragraph("DEPARTMENT OF CONSUMER AFFAIRS &bull; LEGAL METROLOGY DIVISION", subtitle_style))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph("<b>STATUTORY INSPECTION REPORT & COMPLIANCE ASSESSMENT</b>", ParagraphStyle(
            'ReportTitle', parent=title_style, fontSize=11, textColor=colors.HexColor('#1d4ed8')
        )))
        elements.append(Paragraph("Under Legal Metrology Act, 2009 & Legal Metrology (Packaged Commodities) Rules, 2011", subtitle_style))
        elements.append(Spacer(1, 8))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563eb'), spaceAfter=8))

        # 2. Inspection Metadata Table
        insp_id = inspection_data.get('id', 'N/A')
        date_str = inspection_data.get('inspection_date', datetime.now().strftime("%d-%b-%Y %H:%M"))
        officer = inspection_data.get('officer_name', 'Inspector, Legal Metrology')
        badge = inspection_data.get('officer_id', 'LM-INSP-01')

        meta_data = [
            [Paragraph("<b>Inspection ID:</b>", cell_bold), Paragraph(insp_id, cell_style),
             Paragraph("<b>Date & Time:</b>", cell_bold), Paragraph(str(date_str)[:19], cell_style)],
            [Paragraph("<b>Inspecting Officer:</b>", cell_bold), Paragraph(officer, cell_style),
             Paragraph("<b>Officer Badge ID:</b>", cell_bold), Paragraph(badge, cell_style)],
            [Paragraph("<b>Commodity Name:</b>", cell_bold), Paragraph(inspection_data.get('product_name', 'N/A'), cell_style),
             Paragraph("<b>Brand / Trademark:</b>", cell_bold), Paragraph(inspection_data.get('brand', 'N/A'), cell_style)],
            [Paragraph("<b>Barcode / GTIN:</b>", cell_bold), Paragraph(inspection_data.get('barcode', 'N/A') or 'Unmarked', cell_style),
             Paragraph("<b>Category:</b>", cell_bold), Paragraph(inspection_data.get('category', 'General'), cell_style)]
        ]

        meta_table = Table(meta_data, colWidths=[90, 180, 90, 180])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 8))

        # 3. Compliance Verdict Box
        score = inspection_data.get('compliance_score', 0.0)
        status = inspection_data.get('status', 'PENDING')
        verdict = inspection_data.get('verdict', 'Inspection Complete')
        rec_action = inspection_data.get('recommended_action', 'Review required')

        if "CRITICAL" in status:
            banner_bg = colors.HexColor('#fef2f2')
            banner_border = colors.HexColor('#ef4444')
            status_color = colors.HexColor('#b91c1c')
        elif "MAJOR" in status:
            banner_bg = colors.HexColor('#fffbeb')
            banner_border = colors.HexColor('#f59e0b')
            status_color = colors.HexColor('#b45309')
        else:
            banner_bg = colors.HexColor('#f0fdf4')
            banner_border = colors.HexColor('#22c55e')
            status_color = colors.HexColor('#15803d')

        verdict_data = [
            [
                Paragraph(f"<b>COMPLIANCE SCORE: {score:.1f}%</b>", ParagraphStyle('Score', parent=cell_bold, fontSize=11, textColor=status_color)),
                Paragraph(f"<b>STATUTORY STATUS:</b> {verdict}", ParagraphStyle('Status', parent=cell_style, fontSize=9, textColor=status_color)),
                Paragraph(f"<b>ENFORCEMENT DIRECTIVE:</b> {rec_action}", ParagraphStyle('Action', parent=cell_style, fontSize=8, textColor=colors.HexColor('#334155')))
            ]
        ]
        verdict_table = Table(verdict_data, colWidths=[150, 190, 200])
        verdict_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), banner_bg),
            ('BOX', (0,0), (-1,-1), 1.0, banner_border),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(verdict_table)
        elements.append(Spacer(1, 10))

        # 4. Table of Statutory Violations
        violations = inspection_data.get('violations', [])
        elements.append(Paragraph(f"<b>STATUTORY INFRACTIONS DETECTED ({len(violations)} Non-Compliances)</b>", h2_style))
        elements.append(Spacer(1, 4))

        if violations:
            v_headers = [
                Paragraph("<b>Rule Provision</b>", cell_bold),
                Paragraph("<b>Severity</b>", cell_bold),
                Paragraph("<b>Nature of Statutory Defect</b>", cell_bold),
                Paragraph("<b>Required Corrective Remedy</b>", cell_bold)
            ]
            v_rows = [v_headers]
            for v in violations:
                sev = v.get('severity', 'MAJOR')
                sev_color = '#dc2626' if sev == 'CRITICAL' else ('#d97706' if sev == 'MAJOR' else '#2563eb')
                v_rows.append([
                    Paragraph(f"<b>{v.get('rule', 'Rule')}</b><br/>{v.get('declaration', '')}", cell_style),
                    Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", cell_style),
                    Paragraph(v.get('issue', 'Non-compliant declaration'), cell_style),
                    Paragraph(v.get('remedy', 'Rectify label declaration'), cell_style),
                ])

            v_table = Table(v_rows, colWidths=[110, 65, 195, 170])
            v_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            elements.append(v_table)
        else:
            elements.append(Paragraph("<i>No statutory violations detected. All mandatory declarations comply with LMPC Rules 2011.</i>", cell_style))

        elements.append(Spacer(1, 8))

        # 5. Passed Checks Summary
        checks_passed = inspection_data.get('checks_passed', [])
        if checks_passed:
            elements.append(Paragraph(f"<b>VERIFIED COMPLIANT DECLARATIONS ({len(checks_passed)} Checks Passed)</b>", h2_style))
            elements.append(Spacer(1, 3))
            p_rows = [[
                Paragraph("<b>Statutory Rule</b>", cell_bold),
                Paragraph("<b>Mandatory Declaration Item</b>", cell_bold),
                Paragraph("<b>Verified Value / Observation</b>", cell_bold)
            ]]
            for p in checks_passed[:6]: # top 6 for brevity
                p_rows.append([
                    Paragraph(p.get('rule', ''), cell_style),
                    Paragraph(p.get('declaration', ''), cell_style),
                    Paragraph(p.get('extracted_value', 'Compliant'), cell_style)
                ])
            p_table = Table(p_rows, colWidths=[120, 180, 240])
            p_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                ('TOPPADDING', (0,0), (-1,-1), 2.5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
            ]))
            elements.append(p_table)

        elements.append(Spacer(1, 8))

        # 6. Photographic Evidence Attachment (if image exists)
        img_url = inspection_data.get('image_url')
        if img_url and os.path.exists(img_url):
            try:
                elements.append(Paragraph("<b>ANNEXURE I: PHOTOGRAPHIC EVIDENCE OF PACKAGING LABEL</b>", h2_style))
                elements.append(Spacer(1, 4))
                rl_img = RLImage(img_url, width=280, height=180)
                elements.append(rl_img)
                elements.append(Spacer(1, 6))
            except Exception as e:
                print(f"[ReportGen] Error embedding image: {e}")

        # 7. Compounding Fine & Statutory Notice Clause
        if violations:
            elements.append(Paragraph(
                "<b>STATUTORY NOTICE UNDER SECTION 36, LEGAL METROLOGY ACT, 2009:</b><br/>"
                "Whoever manufactures, packs, imports, sells, distributes or delivers any pre-packaged commodity "
                "which does not conform to declarations on the package as provided in the Act or Rules shall be punished "
                "with fine which may extend to <b>Rs. 25,000/-</b> for first offence, <b>Rs. 50,000/-</b> for second offence, "
                "and up to <b>Rs. 1,00,000/- or imprisonment</b> for subsequent offences under Section 36(1).",
                ParagraphStyle('StatutoryNotice', parent=cell_style, fontSize=7.5, leading=10, textColor=colors.HexColor('#475569'))
            ))
            elements.append(Spacer(1, 10))

        # 8. Signature Block
        sig_data = [
            [
                Paragraph("<b>Date:</b> " + datetime.now().strftime("%d-%m-%Y"), cell_style),
                Paragraph("<b>Digital Seal & Verification:</b><br/>Dept of Consumer Affairs, DoCA", cell_style),
                Paragraph("<b>Inspecting Officer Signature:</b><br/>___________________________<br/>(Inspector of Legal Metrology)", cell_style)
            ]
        ]
        sig_table = Table(sig_data, colWidths=[150, 190, 200])
        sig_table.setStyle(TableStyle([
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(sig_table)

        # Build PDF
        doc.build(elements)
        return output_pdf_path

    @classmethod
    def export_csv(cls, inspections: list) -> str:
        """
        Export inspections list to CSV string.
        """
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Inspection ID", "Date", "Brand", "Product Name", "Category",
            "Barcode", "Score (%)", "Status", "Violations Count", "Officer"
        ])

        for insp in inspections:
            v_count = len(insp.get('violations', [])) if isinstance(insp.get('violations'), list) else 0
            writer.writerow([
                insp.get('id'),
                insp.get('inspection_date', '')[:19],
                insp.get('brand'),
                insp.get('product_name'),
                insp.get('category'),
                insp.get('barcode'),
                insp.get('compliance_score'),
                insp.get('status'),
                v_count,
                insp.get('officer_name')
            ])

        return output.getvalue()
