import os
import json
from database.connection import DBConnection

class DBManager:
    def __init__(self, db_path="data/medical_reports.db", schema_path="database/schema.sql"):
        self.connection = DBConnection(db_path)
        self.schema_path = schema_path
        self._init_db()

    def _init_db(self):
        conn = self.connection.get_connection()
        if os.path.exists(self.schema_path):
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()
            conn.executescript(schema)
            conn.commit()
        conn.close()

    # User operations
    def create_user(self, username, email, password_hash, full_name, age=None, gender=None):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, full_name, age, gender) VALUES (?, ?, ?, ?, ?, ?)",
                (username, email, password_hash, full_name, age, gender)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return user_id
        except Exception as e:
            return None
        finally:
            conn.close()

    def get_user_by_username(self, username):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_user_by_email(self, email):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_user_by_credential(self, credential):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (credential, credential))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_user_profile(self, user_id, full_name=None, age=None, gender=None, blood_group=None, height_cm=None, weight_kg=None, medical_conditions=None):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE users
               SET full_name = COALESCE(?, full_name),
                   age = COALESCE(?, age),
                   gender = COALESCE(?, gender),
                   blood_group = COALESCE(?, blood_group),
                   height_cm = COALESCE(?, height_cm),
                   weight_kg = COALESCE(?, weight_kg),
                   medical_conditions = COALESCE(?, medical_conditions),
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (full_name, age, gender, blood_group, height_cm, weight_kg, medical_conditions, user_id)
        )
        conn.commit()
        conn.close()
        return True

    def update_user_password(self, user_id, password_hash):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (password_hash, user_id))
        conn.commit()
        conn.close()
        return True

    def delete_report(self, report_id):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM medical_parameters WHERE report_id = ?", (report_id,))
        cursor.execute("DELETE FROM predictions WHERE report_id = ?", (report_id,))
        cursor.execute("DELETE FROM health_scores WHERE report_id = ?", (report_id,))
        cursor.execute("DELETE FROM recommendations WHERE report_id = ?", (report_id,))
        cursor.execute("DELETE FROM chat_history WHERE report_id = ?", (report_id,))
        cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        conn.commit()
        conn.close()
        return True

    def get_parameter_history(self, user_id, canonical_name=None):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        if canonical_name:
            cursor.execute(
                """SELECT p.*, r.upload_timestamp, r.report_title
                   FROM medical_parameters p
                   JOIN reports r ON p.report_id = r.id
                   WHERE r.user_id = ? AND p.canonical_name = ?
                   ORDER BY r.upload_timestamp ASC""",
                (user_id, canonical_name)
            )
        else:
            cursor.execute(
                """SELECT p.*, r.upload_timestamp, r.report_title
                   FROM medical_parameters p
                   JOIN reports r ON p.report_id = r.id
                   WHERE r.user_id = ?
                   ORDER BY r.upload_timestamp ASC""",
                (user_id,)
            )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_all_user_parameter_names(self, user_id):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT DISTINCT p.canonical_name
               FROM medical_parameters p
               JOIN reports r ON p.report_id = r.id
               WHERE r.user_id = ?
               ORDER BY p.canonical_name ASC""",
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [r['canonical_name'] for r in rows if r['canonical_name']]

    def get_health_score_history(self, user_id):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT hs.*, r.upload_timestamp, r.report_title
               FROM health_scores hs
               JOIN reports r ON hs.report_id = r.id
               WHERE r.user_id = ?
               ORDER BY r.upload_timestamp ASC""",
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # Report operations
    def create_report(self, user_id, report_title, file_name, file_path, raw_text, extraction_method='pymupdf', file_size_kb=0.0):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO reports (user_id, report_title, file_name, file_path, raw_extracted_text, extraction_method, file_size_kb)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, report_title, file_name, file_path, raw_text, extraction_method, file_size_kb)
        )
        conn.commit()
        report_id = cursor.lastrowid
        conn.close()
        return report_id

    def get_user_reports(self, user_id):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE user_id = ? ORDER BY upload_timestamp DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_report_by_id(self, report_id):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_report_parameters(self, report_id):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medical_parameters WHERE report_id = ?", (report_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_report_predictions(self, report_id):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictions WHERE report_id = ?", (report_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_report_health_score(self, report_id):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM health_scores WHERE report_id = ?", (report_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_report_recommendations(self, report_id):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recommendations WHERE report_id = ?", (report_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # Save complete analysis
    def save_full_analysis(self, user_id, report_title, file_name, file_path, raw_text, parameters, predictions, health_score, recommendations):
        report_id = self.create_report(user_id, report_title, file_name, file_path, raw_text)
        conn = self.connection.get_connection()
        cursor = conn.cursor()

        # Save parameters
        for p in parameters:
            cursor.execute(
                """INSERT INTO medical_parameters
                   (report_id, parameter_name, canonical_name, category, measured_value, unit, flag)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (report_id, p.get('raw_name', p.get('parameter_name', '')),
                 p.get('canonical_name', ''), p.get('category', 'General'),
                 float(p.get('measured_value', p.get('value', 0.0))),
                 str(p.get('unit', '')), str(p.get('flag', 'NORMAL')))
            )

        # Save predictions
        for disease, risk in predictions.items():
            level = "Critical" if risk > 0.75 else "High" if risk > 0.55 else "Moderate" if risk > 0.3 else "Low"
            cursor.execute(
                """INSERT INTO predictions (report_id, disease_type, risk_probability, risk_level, model_name)
                   VALUES (?, ?, ?, ?, ?)""",
                (report_id, disease, float(risk), level, f"{disease}_Model")
            )

        # Save health score
        cursor.execute(
            """INSERT INTO health_scores (report_id, overall_score, score_grade, score_breakdown_json)
               VALUES (?, ?, ?, ?)""",
            (report_id, float(health_score.get('overall_score', 100)), str(health_score.get('rating', 'Unknown')),
             json.dumps(health_score.get('category_scores', {})))
        )

        # Save recommendations
        for rec in recommendations:
            cursor.execute(
                """INSERT INTO recommendations (report_id, category, priority, title, description, target_condition)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (report_id, rec.get('category', 'General'), rec.get('priority', 'Medium'),
                 rec.get('title', ''), json.dumps(rec), rec.get('parameter', ''))
            )

        conn.commit()
        conn.close()
        return report_id

    # Chat history operations
    def save_chat_message(self, user_id, report_id, role, message, context_summary=None):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO chat_history (user_id, report_id, role, message, context_summary)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, report_id, role, message, context_summary)
        )
        conn.commit()
        conn.close()

    def get_chat_history(self, user_id, report_id=None):
        conn = self.connection.get_connection()
        cursor = conn.cursor()
        if report_id:
            cursor.execute("SELECT * FROM chat_history WHERE user_id = ? AND report_id = ? ORDER BY created_at ASC", (user_id, report_id))
        else:
            cursor.execute("SELECT * FROM chat_history WHERE user_id = ? ORDER BY created_at ASC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

# Alias for compatibility
DatabaseManager = DBManager
