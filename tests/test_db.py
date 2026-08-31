import os
import unittest
import tempfile
from database.db_manager import DBManager

class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.db_file = os.path.join(cls.temp_dir.name, "test_db.sqlite")
        cls.db = DBManager(db_path=cls.db_file, schema_path="database/schema.sql")

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_user_operations(self):
        user_id = self.db.create_user(
            username="testuser",
            email="test@example.com",
            password_hash="fakehash",
            full_name="Test User",
            age=30,
            gender="Male"
        )
        self.assertIsNotNone(user_id)
        self.assertGreater(user_id, 0)

        user = self.db.get_user_by_username("testuser")
        self.assertIsNotNone(user)
        self.assertEqual(user["email"], "test@example.com")

    def test_save_full_analysis(self):
        user_id = self.db.create_user("testuser2", "test2@example.com", "fakehash", "Test User 2")

        report_id = self.db.save_full_analysis(
            user_id=user_id,
            report_title="Annual Blood Test",
            file_name="report.pdf",
            file_path="/fake/path.pdf",
            raw_text="Glucose 110 mg/dL",
            parameters=[{"canonical_name": "glucose_fasting", "value": 110.0, "unit": "mg/dL", "flag": "HIGH"}],
            predictions={"Diabetes": 0.6},
            health_score={"overall_score": 85, "rating": "Good"},
            recommendations=[{"category": "Diet", "title": "Reduce sugar", "priority": "High"}]
        )
        self.assertGreater(report_id, 0)

        # Retrieve predictions
        preds = self.db.get_report_predictions(report_id)
        self.assertEqual(len(preds), 1)
        self.assertEqual(preds[0]["disease_type"], "Diabetes")
        self.assertEqual(preds[0]["risk_level"], "High")

        # Retrieve params
        params = self.db.get_report_parameters(report_id)
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0]["measured_value"], 110.0)

        # Retrieve score
        score = self.db.get_report_health_score(report_id)
        self.assertEqual(score["overall_score"], 85.0)

    def test_chat_history(self):
        user_id = self.db.create_user("testuser4", "test4@example.com", "fakehash", "Test User 4")
        report_id = self.db.create_report(user_id, "Report", "r.pdf", "path", "raw")

        self.db.save_chat_message(user_id, report_id, "user", "What is glucose?")
        history = self.db.get_chat_history(user_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["message"], "What is glucose?")

if __name__ == "__main__":
    unittest.main()
