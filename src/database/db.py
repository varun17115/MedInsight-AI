import sqlite3
import json
from datetime import datetime

class MedicalDatabase:
    def __init__(self, db_path="data/medical_reports.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    gender TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER,
                    report_name TEXT,
                    raw_text TEXT,
                    overall_score REAL,
                    rating TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS extracted_parameters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER,
                    canonical_name TEXT,
                    raw_name TEXT,
                    measured_value REAL,
                    unit TEXT,
                    flag TEXT,
                    FOREIGN KEY (report_id) REFERENCES reports (id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS disease_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER,
                    disease_name TEXT,
                    risk_score REAL,
                    FOREIGN KEY (report_id) REFERENCES reports (id)
                )
            """)
            conn.commit()

    def save_analysis(self, patient_name, age, gender, report_name, raw_text, score_data, parameters, predictions):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Find or insert patient
            cursor.execute("SELECT id FROM patients WHERE name = ?", (patient_name,))
            patient = cursor.fetchone()
            if patient:
                patient_id = patient['id']
            else:
                cursor.execute(
                    "INSERT INTO patients (name, age, gender) VALUES (?, ?, ?)",
                    (patient_name, age, gender)
                )
                patient_id = cursor.lastrowid

            # Insert report
            cursor.execute(
                """INSERT INTO reports (patient_id, report_name, raw_text, overall_score, rating)
                   VALUES (?, ?, ?, ?, ?)""",
                (patient_id, report_name, raw_text, score_data.get('overall_score', 100), score_data.get('rating', 'Unknown'))
            )
            report_id = cursor.lastrowid

            # Insert extracted parameters
            for p in parameters:
                cursor.execute(
                    """INSERT INTO extracted_parameters (report_id, canonical_name, raw_name, measured_value, unit, flag)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (report_id, p.get('canonical_name'), p.get('raw_name'), p.get('measured_value'), p.get('unit'), p.get('flag'))
                )

            # Insert predictions
            for disease, risk in predictions.items():
                cursor.execute(
                    """INSERT INTO disease_predictions (report_id, disease_name, risk_score)
                       VALUES (?, ?, ?)""",
                    (report_id, disease, risk)
                )

            conn.commit()
            return report_id

    def get_all_reports(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.id, p.name as patient_name, p.age, p.gender, r.report_name, r.overall_score, r.rating, r.created_at
                FROM reports r
                JOIN patients p ON r.patient_id = p.id
                ORDER BY r.created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_report_details(self, report_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.*, p.name as patient_name, p.age, p.gender
                FROM reports r
                JOIN patients p ON r.patient_id = p.id
                WHERE r.id = ?
            """, (report_id,))
            report = cursor.fetchone()
            if not report:
                return None

            cursor.execute("SELECT * FROM extracted_parameters WHERE report_id = ?", (report_id,))
            params = [dict(row) for row in cursor.fetchall()]

            cursor.execute("SELECT * FROM disease_predictions WHERE report_id = ?", (report_id,))
            preds = {row['disease_name']: row['risk_score'] for row in cursor.fetchall()}

            return {
                "report": dict(report),
                "parameters": params,
                "predictions": preds
            }
