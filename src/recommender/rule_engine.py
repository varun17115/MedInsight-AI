from src.recommender.knowledge_base import RECOMMENDATION_DATABASE

class RecommendationEngine:
    def __init__(self):
        self.db = RECOMMENDATION_DATABASE

    def generate_recommendations(self, extracted_parameters, disease_risks=None):
        recommendations = []
        handled_params = set()

        for param in extracted_parameters:
            name = param.get("canonical_name")
            flag = param.get("flag", "NORMAL")

            if flag in ["HIGH", "LOW"] and name in self.db:
                if flag in self.db[name]:
                    rec_data = self.db[name][flag]
                    recommendations.append({
                        "parameter": param.get("raw_name", name),
                        "flag": flag,
                        "title": rec_data["title"],
                        "diet": rec_data.get("diet", []),
                        "lifestyle": rec_data.get("lifestyle", []),
                        "consult": rec_data.get("consult", "")
                    })
                    handled_params.add(name)

        # In case of high disease risks that weren't caught directly by isolated parameters
        if disease_risks:
            if disease_risks.get("Diabetes", 0) > 0.6 and "glucose_fasting" not in handled_params:
                if "glucose_fasting" in self.db and "HIGH" in self.db["glucose_fasting"]:
                    rec_data = self.db["glucose_fasting"]["HIGH"]
                    recommendations.append({
                        "parameter": "Predicted Diabetes Risk",
                        "flag": "HIGH RISK",
                        "title": "Diabetes Prevention & Metabolic Control",
                        "diet": rec_data.get("diet", []),
                        "lifestyle": rec_data.get("lifestyle", []),
                        "consult": rec_data.get("consult", "")
                    })

            if disease_risks.get("Heart Disease", 0) > 0.6 and "cholesterol_total" not in handled_params:
                if "cholesterol_total" in self.db and "HIGH" in self.db["cholesterol_total"]:
                    rec_data = self.db["cholesterol_total"]["HIGH"]
                    recommendations.append({
                        "parameter": "Predicted Heart Disease Risk",
                        "flag": "HIGH RISK",
                        "title": "Cardiovascular Health Management",
                        "diet": rec_data.get("diet", []),
                        "lifestyle": rec_data.get("lifestyle", []),
                        "consult": rec_data.get("consult", "")
                    })

        return recommendations

# Alias for compatibility
RuleEngine = RecommendationEngine
