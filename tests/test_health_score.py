import unittest
from src.ml.health_score import HealthScoreCalculator

class TestHealthScore(unittest.TestCase):
    def setUp(self):
        self.calculator = HealthScoreCalculator()

    def test_perfect_health_score(self):
        params = [
            {"canonical_name": "glucose_fasting", "value": 90, "flag": "NORMAL"},
            {"canonical_name": "hemoglobin", "value": 14.0, "flag": "NORMAL"}
        ]
        result = self.calculator.calculate_score(params)
        self.assertEqual(result['overall_score'], 100.0)
        self.assertEqual(result['rating'], "Excellent")
        self.assertEqual(result['anomalies_count'], 0)

    def test_penalized_health_score(self):
        params = [
            {"canonical_name": "glucose_fasting", "value": 250, "flag": "CRITICAL"},
            {"canonical_name": "creatinine", "value": 3.0, "flag": "HIGH"}
        ]
        result = self.calculator.calculate_score(params)
        self.assertLess(result['overall_score'], 100.0)
        self.assertEqual(result['anomalies_count'], 2)

if __name__ == '__main__':
    unittest.main()
