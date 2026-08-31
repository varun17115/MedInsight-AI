import unittest
from src.recommender.rule_engine import RecommendationEngine

class TestRecommendations(unittest.TestCase):
    def setUp(self):
        self.engine = RecommendationEngine()

    def test_high_risk_recommendations(self):
        params = [
            {"canonical_name": "glucose_fasting", "raw_name": "Fasting Glucose", "flag": "HIGH", "value": 150}
        ]
        risks = {
            'Diabetes': 0.85,
            'Heart Disease': 0.10
        }
        recs = self.engine.generate_recommendations(params, risks)
        self.assertTrue(len(recs) > 0)
        has_diabetes_rec = any("diabetes" in r.get("title", "").lower() or "sugar" in r.get("title", "").lower() for r in recs)
        self.assertTrue(has_diabetes_rec)

    def test_low_risk_general_recommendations(self):
        params = [
            {"canonical_name": "glucose_fasting", "raw_name": "Fasting Glucose", "flag": "NORMAL", "value": 90}
        ]
        risks = {d: 0.05 for d in ['Diabetes', 'Heart Disease']}
        recs = self.engine.generate_recommendations(params, risks)
        self.assertIsInstance(recs, list)

if __name__ == '__main__':
    unittest.main()
