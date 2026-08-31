import json
from collections import defaultdict

class HealthScoreCalculator:
    def __init__(self, reference_path="data/reference_ranges.json"):
        with open(reference_path, "r") as f:
            self.reference_data = json.load(f)

    def calculate_score(self, extracted_parameters, disease_risks=None):
        """
        Calculates an overall health score (0-100) and category breakdowns.
        """
        if not extracted_parameters:
            return {
                "overall_score": 100,
                "rating": "Unknown / Insufficient Data",
                "category_scores": {},
                "anomalies_count": 0
            }

        category_penalties = defaultdict(float)
        category_counts = defaultdict(int)
        total_penalty = 0.0

        for param in extracted_parameters:
            name = param.get("canonical_name")
            flag = param.get("flag", "NORMAL")
            ref_info = self.reference_data.get(name, {})
            category = ref_info.get("category", "General")

            category_counts[category] += 1

            # Base penalty based on flag
            penalty = 0.0
            if flag == "HIGH" or flag == "LOW":
                penalty = 12.0
            elif flag == "CRITICAL":
                penalty = 25.0

            category_penalties[category] += penalty
            total_penalty += penalty

        # Incorporate disease risk penalties if available
        if disease_risks:
            for disease, risk in disease_risks.items():
                if risk > 0.7:
                    total_penalty += 15.0
                elif risk > 0.4:
                    total_penalty += 8.0

        # Calculate final overall score
        final_score = max(0.0, min(100.0, 100.0 - total_penalty))

        # Classify rating
        if final_score >= 90:
            rating = "Excellent"
        elif final_score >= 75:
            rating = "Good"
        elif final_score >= 55:
            rating = "Fair"
        elif final_score >= 35:
            rating = "Poor"
        else:
            rating = "Critical"

        # Calculate category scores
        category_scores = {}
        for cat, count in category_counts.items():
            cat_pen = category_penalties[cat]
            category_scores[cat] = max(0.0, min(100.0, 100.0 - (cat_pen / max(1, count) * 4)))

        return {
            "overall_score": round(final_score, 1),
            "rating": rating,
            "category_scores": category_scores,
            "anomalies_count": sum(1 for p in extracted_parameters if p.get("flag") != "NORMAL")
        }
