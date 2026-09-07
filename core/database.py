"""
Persistent SQLite database layer for Legal Metrology Inspections, Products, and Case History.
"""

import sqlite3
import json
import os
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lmpc_inspections.db")

class Database:
    """
    Manages SQLite database connections and queries for the LMPC inspection system.
    """

    @classmethod
    @contextmanager
    def get_connection(cls):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    @classmethod
    def init_db(cls):
        """
        Initialize tables for products and inspections.
        """
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                brand TEXT,
                commodity_name TEXT,
                category TEXT,
                barcode TEXT,
                manufacturer_name TEXT,
                net_quantity TEXT,
                mrp TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS inspections (
                id TEXT PRIMARY KEY,
                product_id TEXT,
                product_name TEXT,
                brand TEXT,
                category TEXT,
                barcode TEXT,
                officer_id TEXT,
                officer_name TEXT,
                inspection_date TIMESTAMP,
                compliance_score REAL,
                status TEXT,
                verdict TEXT,
                recommended_action TEXT,
                violations_json TEXT,
                passed_checks_json TEXT,
                extracted_data_json TEXT,
                bounding_boxes_json TEXT,
                pdp_info_json TEXT,
                image_url TEXT,
                notice_issued INTEGER DEFAULT 0,
                officer_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()

    @classmethod
    def save_inspection(cls, record: Dict[str, Any]) -> str:
        """
        Insert or replace an inspection record.
        """
        cls.init_db()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO inspections (
                id, product_id, product_name, brand, category, barcode,
                officer_id, officer_name, inspection_date, compliance_score,
                status, verdict, recommended_action, violations_json,
                passed_checks_json, extracted_data_json, bounding_boxes_json,
                pdp_info_json, image_url, notice_issued, officer_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record['id'],
                record.get('product_id', ''),
                record.get('product_name', 'Unknown Commodity'),
                record.get('brand', 'Unknown Brand'),
                record.get('category', 'General Packaged Commodity'),
                record.get('barcode', ''),
                record.get('officer_id', 'LM-INSP-DELHI-04'),
                record.get('officer_name', 'Rajesh Sharma, Inspector Legal Metrology'),
                record.get('inspection_date', datetime.now().isoformat()),
                record.get('compliance_score', 0.0),
                record.get('status', 'PENDING'),
                record.get('verdict', ''),
                record.get('recommended_action', ''),
                json.dumps(record.get('violations', [])),
                json.dumps(record.get('checks_passed', [])),
                json.dumps(record.get('extracted_data', {})),
                json.dumps(record.get('bounding_boxes', [])),
                json.dumps(record.get('pdp_info', {})),
                record.get('image_url', ''),
                1 if record.get('notice_issued') else 0,
                record.get('officer_notes', '')
            ))
            conn.commit()
            return record['id']

    @classmethod
    def get_inspection(cls, inspection_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single inspection by ID with deserialized JSON fields.
        """
        cls.init_db()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inspections WHERE id = ?", (inspection_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return cls._row_to_dict(row)

    @classmethod
    def list_inspections(
        cls,
        search_query: Optional[str] = None,
        status_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List inspections with search and filtering.
        """
        cls.init_db()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM inspections WHERE 1=1"
            params: List[Any] = []

            if search_query:
                query += " AND (product_name LIKE ? OR brand LIKE ? OR barcode LIKE ? OR id LIKE ?)"
                term = f"%{search_query}%"
                params.extend([term, term, term, term])

            if status_filter and status_filter != 'ALL':
                query += " AND status = ?"
                params.append(status_filter)

            if category_filter and category_filter != 'ALL':
                query += " AND category = ?"
                params.append(category_filter)

            query += " ORDER BY inspection_date DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [cls._row_to_dict(r) for r in rows]

    @classmethod
    def get_dashboard_stats(cls) -> Dict[str, Any]:
        """
        Aggregate inspection KPIs for enforcement officials.
        """
        cls.init_db()
        with cls.get_connection() as conn:
            cursor = conn.cursor()

            # Total inspections
            cursor.execute("SELECT COUNT(*) FROM inspections")
            total = cursor.fetchone()[0]

            if total == 0:
                return {
                    "total_inspections": 0,
                    "compliant_count": 0,
                    "non_compliant_count": 0,
                    "compliance_rate": 100.0,
                    "notices_issued": 0,
                    "average_score": 100.0,
                    "violations_by_type": {},
                    "recent_inspections": []
                }

            # Status breakdown
            cursor.execute("SELECT status, COUNT(*) FROM inspections GROUP BY status")
            status_map = dict(cursor.fetchall())

            compliant = status_map.get("COMPLIANT", 0) + status_map.get("SUBSTANTIALLY_COMPLIANT", 0)
            non_compliant = status_map.get("NON_COMPLIANT_CRITICAL", 0) + status_map.get("NON_COMPLIANT_MAJOR", 0)

            # Average score
            cursor.execute("SELECT AVG(compliance_score) FROM inspections")
            avg_score = cursor.fetchone()[0] or 0.0

            # Notices issued
            cursor.execute("SELECT COUNT(*) FROM inspections WHERE notice_issued = 1")
            notices_issued = cursor.fetchone()[0]

            # Recent inspections
            cursor.execute("SELECT * FROM inspections ORDER BY inspection_date DESC LIMIT 5")
            recent = [cls._row_to_dict(r) for r in cursor.fetchall()]

            # Aggregate violation categories from JSON
            cursor.execute("SELECT violations_json FROM inspections")
            all_v = cursor.fetchall()
            v_counts: Dict[str, int] = {}
            for row in all_v:
                try:
                    v_list = json.loads(row[0])
                    for v in v_list:
                        rule = v.get("rule", "Other")
                        v_counts[rule] = v_counts.get(rule, 0) + 1
                except Exception:
                    pass

            return {
                "total_inspections": total,
                "compliant_count": compliant,
                "non_compliant_count": non_compliant,
                "compliance_rate": round((compliant / total) * 100, 1),
                "notices_issued": notices_issued,
                "average_score": round(avg_score, 1),
                "violations_by_type": v_counts,
                "recent_inspections": recent
            }

    @classmethod
    def update_inspection_status(cls, inspection_id: str, notice_issued: bool, notes: str):
        """
        Update notice status and officer notes.
        """
        cls.init_db()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE inspections
            SET notice_issued = ?, officer_notes = ?
            WHERE id = ?
            """, (1 if notice_issued else 0, notes, inspection_id))
            conn.commit()

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        d = dict(row)
        for json_col in ['violations_json', 'passed_checks_json', 'extracted_data_json', 'bounding_boxes_json', 'pdp_info_json']:
            if json_col in d and d[json_col]:
                try:
                    clean_key = json_col.replace('_json', '')
                    d[clean_key] = json.loads(d[json_col])
                except Exception:
                    pass
        return d
