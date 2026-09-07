"""
Legal Metrology (Packaged Commodities) Compliance Software System
Smart India Hackathon 2026 - Problem Statement 26034
Ministry of Consumer Affairs, Food & Public Distribution | Department of Consumer Affairs (DoCA)
"""

import os
import uuid
import json
from datetime import datetime
from flask import (
    Flask, render_template, request, jsonify, send_file,
    redirect, url_for, flash, Response
)

from core.rules_engine import LegalMetrologyRulesEngine
from core.font_estimator import FontEstimator
from core.ocr_vision_engine import OCRVisionEngine
from core.sample_data import SampleRepository
from core.database import Database
from core.report_generator import ReportGenerator

app = Flask(__name__)
app.secret_key = "lmpc-compliance-secret-key-2026"

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
REPORT_DIR = os.path.join(BASE_DIR, "static", "reports")
SAMPLE_DIR = os.path.join(BASE_DIR, "static", "samples")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(SAMPLE_DIR, exist_ok=True)

# Initialize database & generate sample imagery
Database.init_db()
SampleRepository.generate_sample_images(SAMPLE_DIR)

# System configurations
SYSTEM_CONFIG = {
    "gemini_api_key": os.environ.get("GEMINI_API_KEY", ""),
    "officer_name": "Rajesh Sharma, Inspector Legal Metrology",
    "officer_id": "LM-INSP-DELHI-04",
    "jurisdiction": "Central Enforcement Wing, New Delhi"
}

# Pre-seed initial sample inspections into DB if empty
def seed_initial_inspections():
    stats = Database.get_dashboard_stats()
    if stats['total_inspections'] == 0:
        rules_engine = LegalMetrologyRulesEngine()
        for sample in SampleRepository.SAMPLES:
            evaluation = rules_engine.evaluate(
                sample['extracted_data'],
                sample['pdp_info']
            )
            image_filename = f"{sample['id']}.png"
            image_abs_path = os.path.join(SAMPLE_DIR, image_filename)
            image_web_url = f"/static/samples/{image_filename}"

            record_id = f"INSP-2024-{sample['id'][-3:]}"
            inspection_record = {
                "id": record_id,
                "product_id": sample['id'],
                "product_name": sample['commodity_name'],
                "brand": sample['brand'],
                "category": sample['category'],
                "barcode": sample['barcode'],
                "officer_id": SYSTEM_CONFIG["officer_id"],
                "officer_name": SYSTEM_CONFIG["officer_name"],
                "inspection_date": datetime.now().isoformat(),
                "compliance_score": evaluation['compliance_score'],
                "status": evaluation['status'],
                "verdict": evaluation['verdict'],
                "recommended_action": evaluation['recommended_action'],
                "violations": evaluation['violations'],
                "checks_passed": evaluation['checks_passed'],
                "extracted_data": sample['extracted_data'],
                "bounding_boxes": sample['bounding_boxes'],
                "pdp_info": sample['pdp_info'],
                "image_url": image_web_url,
                "notice_issued": 1 if "CRITICAL" in evaluation['status'] else 0,
                "officer_notes": f"Initial automated scan under SIH-26034 benchmark. {sample['description']}"
            }
            Database.save_inspection(inspection_record)
            
            # Pre-generate PDF report
            pdf_path = os.path.join(REPORT_DIR, f"{record_id}.pdf")
            try:
                # pass local file path for image embedding
                record_for_pdf = dict(inspection_record)
                record_for_pdf['image_url'] = image_abs_path
                ReportGenerator.generate_pdf(record_for_pdf, pdf_path)
            except Exception as e:
                print(f"[Seed] Error generating PDF for {record_id}: {e}")

seed_initial_inspections()


# ------------------- Web UI Routes -------------------

@app.route("/")
def dashboard():
    """
    Executive & Enforcement Dashboard displaying overall KPIs, charts, and recent scans.
    """
    stats = Database.get_dashboard_stats()
    return render_template("dashboard.html", stats=stats, config=SYSTEM_CONFIG)


@app.route("/scanner")
def scanner():
    """
    Interactive Visual Inspection Studio for scanning packaging labels.
    """
    sample_id = request.args.get("sample_id")
    preset_sample = None
    if sample_id:
        preset_sample = SampleRepository.get_sample_by_id(sample_id)
    return render_template(
        "scanner.html",
        samples=SampleRepository.SAMPLES,
        preset_sample=preset_sample,
        config=SYSTEM_CONFIG
    )


@app.route("/repository")
def repository():
    """
    Searchable and filterable repository of inspected packaged commodities.
    """
    search_query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "ALL")
    category_filter = request.args.get("category", "ALL")
    
    inspections = Database.list_inspections(
        search_query=search_query or None,
        status_filter=status_filter,
        category_filter=category_filter,
        limit=100
    )
    return render_template(
        "repository.html",
        inspections=inspections,
        search_query=search_query,
        status_filter=status_filter,
        category_filter=category_filter,
        config=SYSTEM_CONFIG
    )


@app.route("/inspection/<inspection_id>")
def view_inspection(inspection_id):
    """
    Detailed statutory inspection record view with full evidence and notice workflow.
    """
    insp = Database.get_inspection(inspection_id)
    if not insp:
        flash(f"Inspection record {inspection_id} not found.", "error")
        return redirect(url_for("repository"))
    return render_template("report_view.html", inspection=insp, config=SYSTEM_CONFIG)


@app.route("/report/<inspection_id>/pdf")
def download_pdf_report(inspection_id):
    """
    Download official Legal Metrology inspection report in PDF.
    """
    import io
    pdf_path = os.path.join(REPORT_DIR, f"{inspection_id}.pdf")
    if not os.path.exists(pdf_path):
        insp = Database.get_inspection(inspection_id)
        if not insp:
            return "Inspection not found", 404
        ReportGenerator.generate_pdf(insp, pdf_path)

    with open(pdf_path, "rb") as f:
        pdf_stream = io.BytesIO(f.read())

    return send_file(
        pdf_stream,
        as_attachment=True,
        download_name=f"Legal_Metrology_Inspection_{inspection_id}.pdf",
        mimetype="application/pdf"
    )


@app.route("/settings", methods=["GET", "POST"])
def settings():
    """
    System configuration and API key settings.
    """
    global SYSTEM_CONFIG
    if request.method == "POST":
        SYSTEM_CONFIG["gemini_api_key"] = request.form.get("gemini_api_key", "").strip()
        SYSTEM_CONFIG["officer_name"] = request.form.get("officer_name", "").strip()
        SYSTEM_CONFIG["officer_id"] = request.form.get("officer_id", "").strip()
        SYSTEM_CONFIG["jurisdiction"] = request.form.get("jurisdiction", "").strip()
        flash("System configuration updated successfully.", "success")
        return redirect(url_for("settings"))
    return render_template("settings.html", config=SYSTEM_CONFIG)


# ------------------- REST API Endpoints -------------------

@app.route("/api/scan", methods=["POST"])
def api_scan():
    """
    Process packaging label image upload and return statutory compliance evaluation.
    """
    try:
        # Check if file uploaded or sample selected
        sample_id = request.form.get("sample_id")
        file = request.files.get("image")

        package_dimensions = {
            "height": float(request.form.get("height_cm", 20.0)),
            "width": float(request.form.get("width_cm", 12.0)),
            "depth": float(request.form.get("depth_cm", 5.0)),
            "shape": request.form.get("packaging_shape", "rectangular")
        }

        # Calculate PDP area
        pdp_area = FontEstimator.calculate_pdp_area(
            shape=package_dimensions["shape"],
            height_cm=package_dimensions["height"],
            width_cm=package_dimensions["width"],
            depth_cm=package_dimensions["depth"]
        )

        image_web_url = ""
        image_local_path = ""

        # Case 1: Pre-loaded Sample
        if sample_id:
            sample = SampleRepository.get_sample_by_id(sample_id)
            if not sample:
                return jsonify({"error": f"Sample {sample_id} not found"}), 404
            
            image_local_path = os.path.join(SAMPLE_DIR, f"{sample_id}.png")
            image_web_url = f"/static/samples/{sample_id}.png"
            extracted_data = sample["extracted_data"]
            bounding_boxes = sample["bounding_boxes"]
            pdp_info = sample["pdp_info"]
            brand = sample["brand"]
            commodity_name = sample["commodity_name"]
            category = sample["category"]
            barcode = sample["barcode"]

        # Case 2: Custom Image Upload
        elif file and file.filename:
            ext = os.path.splitext(file.filename)[1] or ".png"
            unique_filename = f"scan_{uuid.uuid4().hex[:10]}{ext}"
            image_local_path = os.path.join(UPLOAD_DIR, unique_filename)
            file.save(image_local_path)
            image_web_url = f"/static/uploads/{unique_filename}"

            vision_engine = OCRVisionEngine(gemini_api_key=SYSTEM_CONFIG.get("gemini_api_key"))
            vision_result = vision_engine.analyze_image(image_local_path, package_dimensions)

            extracted_data = vision_result["extracted_data"]
            bounding_boxes = vision_result["bounding_boxes"]
            pdp_info = vision_result["pdp_info"]
            pdp_info["pdp_area_sq_cm"] = pdp_area
            brand = extracted_data.get("manufacturer_name", "Unknown Brand").split()[0]
            commodity_name = extracted_data.get("commodity_name", "Packaged Commodity")
            category = "Consumer Packaged Goods"
            barcode = request.form.get("barcode", "")

        else:
            return jsonify({"error": "No image file or sample provided"}), 400

        # Run Deterministic Legal Metrology Rules Engine
        rules_engine = LegalMetrologyRulesEngine()
        evaluation = rules_engine.evaluate(extracted_data, pdp_info)

        # Generate unique inspection ID
        random_suffix = uuid.uuid4().hex[:4].upper()
        inspection_id = f"INSP-{datetime.now().strftime('%Y%m%d')}-{random_suffix}"

        # Construct inspection record
        inspection_record = {
            "id": inspection_id,
            "product_id": sample_id or f"PRD-{random_suffix}",
            "product_name": commodity_name,
            "brand": brand,
            "category": category,
            "barcode": barcode,
            "officer_id": SYSTEM_CONFIG["officer_id"],
            "officer_name": SYSTEM_CONFIG["officer_name"],
            "inspection_date": datetime.now().isoformat(),
            "compliance_score": evaluation["compliance_score"],
            "status": evaluation["status"],
            "verdict": evaluation["verdict"],
            "recommended_action": evaluation["recommended_action"],
            "violations": evaluation["violations"],
            "checks_passed": evaluation["checks_passed"],
            "extracted_data": extracted_data,
            "bounding_boxes": bounding_boxes,
            "pdp_info": pdp_info,
            "image_url": image_web_url,
            "notice_issued": 1 if "CRITICAL" in evaluation["status"] else 0,
            "officer_notes": f"Scanned on {datetime.now().strftime('%d-%b-%Y %H:%M')}. Verdict: {evaluation['verdict']}"
        }

        # Save to SQLite Database
        Database.save_inspection(inspection_record)

        # Generate PDF report immediately
        pdf_path = os.path.join(REPORT_DIR, f"{inspection_id}.pdf")
        try:
            record_for_pdf = dict(inspection_record)
            record_for_pdf['image_url'] = image_local_path
            ReportGenerator.generate_pdf(record_for_pdf, pdf_path)
        except Exception as e:
            print(f"[API] Error generating PDF report: {e}")

        return jsonify({
            "success": True,
            "inspection_id": inspection_id,
            "evaluation": evaluation,
            "extracted_data": extracted_data,
            "bounding_boxes": bounding_boxes,
            "pdp_info": pdp_info,
            "image_url": image_web_url,
            "pdf_url": f"/report/{inspection_id}/pdf"
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/inspection/<inspection_id>/update", methods=["POST"])
def api_update_inspection(inspection_id):
    """
    Update inspection notes or toggle notice issuance.
    """
    data = request.get_json() or {}
    notice_issued = bool(data.get("notice_issued"))
    notes = data.get("officer_notes", "")
    Database.update_inspection_status(inspection_id, notice_issued, notes)
    return jsonify({"success": True, "message": "Inspection updated successfully."})


@app.route("/api/export/csv")
def api_export_csv():
    """
    Export all inspections as CSV download.
    """
    inspections = Database.list_inspections(limit=1000)
    csv_content = ReportGenerator.export_csv(inspections)
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=LMPC_Inspections_Export.csv"}
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print("\n" + "="*70)
    print("  Legal Metrology (Packaged Commodities) Rules 2011 Compliance System")
    print("  Smart India Hackathon 2026 - Problem Statement 26034")
    print("  Department of Consumer Affairs (DoCA) &bull; Ministry of Consumer Affairs")
    print("="*70)
    print(f"  Running on http://0.0.0.0:{port} (Local: http://127.0.0.1:{port})")
    print("="*70 + "\n")
    app.run(host="0.0.0.0", port=port, debug=False)

