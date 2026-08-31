import unittest
from src.ml.predictor import DiseasePredictor
from models.disease_configs import DISEASES

class TestModels(unittest.TestCase):
    def setUp(self):
        self.predictor = DiseasePredictor()

    def test_diseases_defined(self):
        self.assertEqual(len(DISEASES), 8)
        self.assertIn('diabetes', DISEASES)
        self.assertIn('heart_disease', DISEASES)

    def test_predict_all_structure(self):
        dummy_profile = {
            'glucose_fasting': 110,
            'blood_pressure': 80,
            'bmi': 24.5,
            'age': 35,
            'gender': 'Female'
        }
        predictions = self.predictor.predict_all(dummy_profile)
        self.assertIsInstance(predictions, dict)
        self.assertEqual(len(predictions), 8)
        for disease, risk in predictions.items():
            self.assertIsInstance(risk, float)
            self.assertTrue(0.0 <= risk <= 1.0)

if __name__ == '__main__':
    unittest.main()
