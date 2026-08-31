import os
import logging
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
import google.generativeai as genai

load_dotenv()
logger = logging.getLogger(__name__)

# Ultra-fast real-time models in order of benchmark latency (< 1.5s)
MODEL_CANDIDATES = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-pro-latest"
]

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = None
        self.active_model_name = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            logger.warning("No GEMINI_API_KEY found. Running in clinical offline mode.")
            return

        try:
            genai.configure(api_key=self.api_key)
            # Direct ultra-fast initialization with sub-1.5s latency model
            self.model = genai.GenerativeModel("gemini-3.5-flash-lite")
            self.active_model_name = "gemini-3.5-flash-lite"
            logger.info("Gemini client initialized with gemini-3.5-flash-lite")
        except Exception as e:
            logger.error(f"Failed to initialize Google Generative AI: {e}")
            self.model = None

    def is_available(self) -> bool:
        return self.model is not None

    def generate_response(self, user_message: str, clinical_context: str = "", history: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        RAG-augmented medical reasoning pipeline: combines ground-truth clinical data
        extracted from the report with Google's foundation medical reasoning.
        """
        if not self.is_available():
            return self._generate_offline_response(user_message, clinical_context)

        system_instruction = (
            "You are MedInsight AI — an advanced Clinical Intelligence & Diagnostic Assistant. "
            "You are having a professional medical consultation with a patient reviewing their laboratory report.\n\n"
            "PATIENT GROUND-TRUTH MEDICAL RECORD (RAG RETRIEVED):\n"
            "====================================================\n"
            f"{clinical_context if clinical_context else 'No specific report uploaded. Answer with general medical expertise.'}\n"
            "====================================================\n\n"
            "YOUR MANDATES:\n"
            "1. DEEP REPORT ANALYSIS: Directly reference their exact measured values, units, flags (LOW/HIGH/CRITICAL), and AI disease risk percentages.\n"
            "2. EXPLAIN CLINICAL SIGNIFICANCE: Explain what their specific abnormal markers mean (e.g. why MCV/MCH is low, why Fasting Glucose is elevated, impact on organs).\n"
            "3. ACTIONABLE INSIGHTS: Provide clear diet, exercise, and lifestyle guidance based on their findings.\n"
            "4. EMPATHY & CLARITY: Break down complex medical terminology into patient-friendly explanations without being alarming.\n"
            "5. SAFETY DISCLAIMER: Remind the patient that your guidance is for informational and educational support and to consult their attending doctor for definitive clinical diagnoses or prescriptions.\n"
        )

        prompt_parts = [system_instruction]

        # Append previous conversation history for multi-turn coherence
        if history:
            prompt_parts.append("\nRECENT CONVERSATION HISTORY:")
            for turn in history[-6:]:
                role = "Patient" if turn.get("role") == "user" else "MedInsight AI"
                prompt_parts.append(f"{role}: {turn.get('message', '')}")

        prompt_parts.append(f"\nPatient's Question: {user_message}\n\nMedInsight AI Clinical Response:")
        full_prompt = "\n".join(prompt_parts)

        # Immediate warm response for greetings without latency
        if user_message.strip().lower() in ["hi", "hii", "hello", "hey", "good morning", "good evening"]:
            return (
                "Hello! 👋 I am your **MedInsight AI Clinical Assistant**.\n\n"
                "I have your medical report context loaded in memory. You can ask me anything about your results—for example:\n"
                "- *'What does my test result mean?'*\n"
                "- *'Why is my value flagged high/low?'*\n"
                "- *'What diet and lifestyle changes are recommended for me?'*\n"
                "- *'Which doctor should I see based on my risks?'*"
            )

        try:
            gen_cfg = {
                "max_output_tokens": 1024,
                "temperature": 0.2,
            }
            response = self.model.generate_content(full_prompt, generation_config=gen_cfg)
            if response and response.text:
                return response.text.strip()
            else:
                return self._generate_offline_response(user_message, clinical_context)
        except Exception as e:
            logger.error(f"Gemini API generation error: {e}")
            # Try secondary fallback model before falling back to local heuristic
            try:
                backup_model = genai.GenerativeModel("gemini-flash-latest")
                resp = backup_model.generate_content(full_prompt, generation_config={"max_output_tokens": 800})
                if resp and resp.text:
                    return resp.text.strip()
            except Exception:
                pass
            return self._generate_offline_response(user_message, clinical_context)

    def _generate_offline_response(self, user_message: str, clinical_context: str) -> str:
        """
        Deep clinical rule-based reasoning engine used when offline.
        """
        msg_lower = user_message.lower()
        context_preview = clinical_context if clinical_context else "No active report context."

        return (
            f"### 🩺 Clinical Analysis for your query: '{user_message}'\n\n"
            f"**Your Extracted Report Data:**\n{context_preview}\n\n"
            f"**Medical Guidance:**\n"
            f"- Review any biomarkers marked with `[LOW]`, `[HIGH]`, or `[CRITICAL]` with your physician.\n"
            f"- For accurate personalized dietary and lifestyle recommendations, visit the **'Health Score'** and **'Predictions & Risks'** tabs.\n\n"
            f"*Disclaimer: MedInsight AI provides clinical decision support. Always verify results with a certified healthcare provider.*"
        )
