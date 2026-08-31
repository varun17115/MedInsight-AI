import sqlite3
import os

class DBConnection:
    _instance = None

    def __init__(self, db_path="data/medical_reports.db"):
        self.db_path = db_path

    def get_connection(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
