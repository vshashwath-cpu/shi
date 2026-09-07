"""
Integration Tests for Flask Web Application and API Endpoints.
Tests scan execution, database persistence, PDF report generation, and CSV export.
"""

import os
import unittest
import json
from app import app, Database

class TestAppIntegration(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_dashboard_route(self):
        """Dashboard renders successfully with 200 OK."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Automated Commodity Compliance Portal", response.data)

    def test_scanner_studio_route(self):
        """Scanner studio renders successfully with 200 OK."""
        response = self.client.get('/scanner')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Packaged Commodity Visual Inspection Studio", response.data)

    def test_repository_route(self):
        """Repository renders with inspected products list."""
        response = self.client.get('/repository')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Enforcement Repository & Inspection History", response.data)

    def test_api_scan_sample_commodity(self):
        """POST /api/scan with sample ID returns evaluation with bounding boxes."""
        response = self.client.post('/api/scan', data={
            'sample_id': 'SMP-001',
            'height_cm': 38.0,
            'width_cm': 24.0,
            'packaging_shape': 'rectangular'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('inspection_id', data)
        self.assertEqual(data['evaluation']['status'], 'COMPLIANT')
        self.assertEqual(data['evaluation']['compliance_score'], 100)
        self.assertTrue(len(data['bounding_boxes']) > 0)
        self.assertIn('pdf_url', data)

    def test_pdf_report_download(self):
        """GET /report/<id>/pdf returns a valid downloadable PDF file."""
        # Query an existing inspection
        inspections = Database.list_inspections(limit=1)
        self.assertTrue(len(inspections) > 0, "Expected seeded inspections in DB")
        insp_id = inspections[0]['id']

        response = self.client.get(f'/report/{insp_id}/pdf')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/pdf')
        self.assertTrue(len(response.data) > 500, "PDF content should be non-trivial")

    def test_api_export_csv(self):
        """GET /api/export/csv returns a valid CSV with inspection audit rows."""
        response = self.client.get('/api/export/csv')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"text/csv", response.content_type.encode())
        self.assertIn(b"Inspection ID,Date,Brand,Product Name", response.data)

    def test_officer_update_api(self):
        """POST /api/inspection/<id>/update updates officer notes in SQLite."""
        inspections = Database.list_inspections(limit=1)
        insp_id = inspections[0]['id']

        response = self.client.post(f'/api/inspection/{insp_id}/update',
            json={
                "notice_issued": True,
                "officer_notes": "Tested officer update note via test_app."
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

        # Verify update in DB
        updated = Database.get_inspection(insp_id)
        self.assertEqual(updated['officer_notes'], "Tested officer update note via test_app.")
        self.assertEqual(updated['notice_issued'], 1)


if __name__ == '__main__':
    unittest.main()
