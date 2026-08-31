from typing import List, Dict, Any, Optional
from database.db_manager import DBManager
from src.chatbot.gemini_client import GeminiClient
from src.chatbot.context_builder import ContextBuilder

class ChatManager:
    def __init__(self, db: Optional[DBManager] = None, gemini_client: Optional[GeminiClient] = None):
        # Support positional or keyword args in any order for maximum compatibility
        if isinstance(db, GeminiClient):
            self.client = db
            self.db = gemini_client or DBManager()
        elif isinstance(gemini_client, DBManager):
            self.db = gemini_client
            self.client = db or GeminiClient()
        else:
            self.db = db or DBManager()
            self.client = gemini_client or GeminiClient()

    def handle_message(self, user_id: int, report_id: Optional[int], user_message: str) -> str:
        """
        Convenience method to fetch patient context from DB automatically by report_id.
        """
        params = self.db.get_report_parameters(report_id) if report_id else []
        preds_list = self.db.get_report_predictions(report_id) if report_id else []
        preds = {p['disease_type']: p['risk_probability'] for p in preds_list} if preds_list else {}
        health_score = self.db.get_report_health_score(report_id) if report_id else None
        recs = self.db.get_report_recommendations(report_id) if report_id else []

        return self.process_message(
            user_id=user_id,
            user_message=user_message,
            report_id=report_id,
            parameters=params,
            predictions=preds,
            health_score=health_score,
            recommendations=recs
        )

    def process_message(
        self,
        user_id: int,
        user_message: str,
        report_id: Optional[int] = None,
        patient_profile: Optional[Dict[str, Any]] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        predictions: Optional[Dict[str, float]] = None,
        health_score: Optional[Dict[str, Any]] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        # Build context
        context = ContextBuilder.build_clinical_context(
            patient_profile=patient_profile,
            parameters=parameters,
            predictions=predictions,
            health_score=health_score,
            recommendations=recommendations
        )

        # Retrieve prior history
        history = self.get_history(user_id, report_id)

        # Generate response
        bot_response = self.client.generate_response(
            user_message=user_message,
            clinical_context=context,
            history=history
        )

        # Persist conversation to SQLite
        try:
            self.db.save_chat_message(user_id, report_id, "user", user_message, context[:300])
            self.db.save_chat_message(user_id, report_id, "assistant", bot_response)
        except Exception as e:
            print(f"Notice: Failed to persist chat message: {e}")

        return bot_response

    def get_history(self, user_id: int, report_id: Optional[int] = None) -> List[Dict[str, Any]]:
        try:
            return self.db.get_chat_history(user_id, report_id)
        except Exception:
            return []
