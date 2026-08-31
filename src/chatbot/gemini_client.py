import os
from typing import List, Dict, Optional

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            return
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        except Exception as e:
            print(f"Warning: Failed to initialize Google Generative AI: {e}")
            self.model = None

    def is_available(self) -> bool:
        return self.model is not None

    def generate_response(self, user_message: str, clinical_context: str = "", history: Optional[List[Dict]] = None) -> str:
        if not self.is_available():
            return self._generate_offline_response(user_message, clinical_context)

        system_instruction = (
            "You are MedInsight AI Clinical Assistant, an intelligent medical report analyzer. "
            "Your role is to explain medical report parameters, disease risk assessments, "
            "and health recommendations to patients in clear, empathetic, and scientifically accurate terms.\n\n"
            "CRITICAL GUIDELINES:\n"
            "1. Base your answers strictly on the patient's clinical context provided below.\n"
            "2. Clarify medical jargon into plain English without causing undue alarm.\n"
            "3. Emphasize that you are an AI assistant and not a replacement for a certified healthcare professional.\n"
            "4. Never prescribe medication or specific drug dosages.\n"
            "5. If a value is flagged CRITICAL or HIGH risk, advise consulting a physician promptly.\n\n"
            f"--- PATIENT CLINICAL CONTEXT ---\n{clinical_context}\n--------------------------------\n"
        )

        full_prompt = f"{system_instruction}\nUser Query: {user_message}"

        try:
            response = self.model.generate_content(full_prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error communicating with Gemini AI: {str(e)}\n\n(Fallback analysis): " + self._generate_offline_response(user_message, clinical_context)

    def _generate_offline_response(self, user_message: str, clinical_context: str) -> str:
        msg_lower = user_message.lower()
        context_preview = clinical_context[:500] if clinical_context else "No active report context."

        if "glucose" in msg_lower or "sugar" in msg_lower or "diabetes" in msg_lower:
            return (
                "Based on your profile and standard clinical guidelines: Fasting glucose between 70-99 mg/dL is normal. "
                "Levels between 100-125 mg/dL indicate prediabetes, while 126 mg/dL or higher on repeat tests suggests diabetes. "
                "Maintaining a balanced diet low in refined carbohydrates and regular cardiovascular exercise is recommended. "
                "\n\n*Note: Please configure a valid GEMINI_API_KEY in .env for dynamic real-time AI responses.*"
            )
        elif "cholesterol" in msg_lower or "heart" in msg_lower or "lipid" in msg_lower:
            return (
                "Regarding cardiovascular health and lipids: Total cholesterol is ideal under 200 mg/dL. "
                "High LDL ('bad') cholesterol or low HDL ('good') cholesterol increases the risk of arterial plaque buildup. "
                "Adopting a Mediterranean-style diet, limiting saturated fats, and managing blood pressure are key protective actions. "
                "\n\n*Note: Please configure a valid GEMINI_API_KEY in .env for dynamic real-time AI responses.*"
            )
        elif "kidney" in msg_lower or "creatinine" in msg_lower:
            return (
                "Regarding renal indicators: Creatinine (normal ~0.7-1.3 mg/dL) and BUN reflect kidney filtration function. "
                "Elevated creatinine may point to reduced kidney clearance or dehydration. Adequate hydration and limiting excessive NSAID usage are advisable."
            )
        elif "score" in msg_lower or "health" in msg_lower:
            return (
                "Your overall Health Score summarizes your metabolic, cardiac, renal, hepatic, and hematologic biomarkers. "
                "Review the detailed recommendations tab to target specific parameters that need improvement."
            )
        else:
            return (
                f"I reviewed your query regarding: '{user_message}'.\n\n"
                f"According to your latest medical analysis summary:\n{context_preview}...\n\n"
                "Please consult your attending physician for personalized clinical diagnosis and treatment plans."
            )
