import os
import unittest
import tempfile
from src.chatbot.context_builder import ContextBuilder
from src.chatbot.gemini_client import GeminiClient
from src.chatbot.chat_manager import ChatManager
from database.db_manager import DBManager

class TestChatbot(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_file = os.path.join(self.temp_dir.name, "test_chat.db")
        self.db = DBManager(db_path=self.db_file, schema_path="database/schema.sql")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_context_builder(self):
        profile = {"full_name": "Jane Doe", "age": 42, "gender": "Female"}
        params = [{"canonical_name": "Glucose", "measured_value": 140, "unit": "mg/dL", "flag": "HIGH"}]
        preds = {"Diabetes": 0.65, "Heart Disease": 0.12}
        health_score = {"overall_score": 82, "rating": "Good"}

        context = ContextBuilder.build_clinical_context(profile, params, preds, health_score)
        self.assertIn("Jane Doe", context)
        self.assertIn("Glucose: 140", context)
        self.assertIn("HIGH", context)
        self.assertIn("Diabetes: 65.0%", context)
        self.assertIn("Overall Score: 82/100", context)

    def test_gemini_client_offline_fallback(self):
        client = GeminiClient(api_key="invalid_mock_key_for_test")
        resp = client.generate_response("What does my glucose reading mean?", "Glucose: 140 mg/dL [HIGH]")
        self.assertTrue("glucose" in resp.lower() or "prediabetes" in resp.lower() or "medical" in resp.lower())

    def test_chat_manager_flow(self):
        user_id = self.db.create_user("chat_user", "chat@example.com", "hash", "Chat User")
        chat_mgr = ChatManager(db=self.db)

        resp = chat_mgr.process_message(
            user_id=user_id,
            user_message="Tell me about my heart risk",
            predictions={"Heart Disease": 0.25}
        )
        self.assertIsNotNone(resp)
        self.assertGreater(len(resp), 10)

        history = chat_mgr.get_history(user_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['role'], 'user')
        self.assertEqual(history[1]['role'], 'assistant')

if __name__ == '__main__':
    unittest.main()
