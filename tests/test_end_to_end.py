import unittest
import os
from src.parser.parser import MedicalReportParser
from src.ml.predictor import DiseasePredictor
from src.ml.health_score import HealthScoreCalculator
from src.recommender.rule_engine import RecommendationEngine
from src.database.db import MedicalDatabase
from src.reporting.pdf_generator import MedicalPDFReportGenerator

class TestEndToEndPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = MedicalReportParser("data/reference_ranges.json")
        cls.predictor = DiseasePredictor("models/saved_models")
        cls.calculator = HealthScoreCalculator("data/reference_ranges.json")
        cls.recommender = RecommendationEngine()
        cls.db = MedicalDatabase("data/test_medical.db")
        cls.pdf_gen = MedicalPDFReportGenerator()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists("data/test_medical.db"):
            try:
                os.remove("data/test_medical.db")
            except Exception:
                pass

    def test_complete_workflow(self):
        sample_text = """
        Patient: Jane Smith | Age: 52 | Gender: Female
        Fasting Glucose : 145 mg/dL
        HbA1c : 7.1 %
        Serum Creatinine : 1.6 mg/dL
        Total Cholesterol : 240 mg/dL
        ALT : 35 U/L
        AST : 30 U/L
        Hemoglobin : 13.5 g/dL
        """
        # 1. Parse Parameters
        params = self.parser.parse_text(sample_text, gender="Female")
        self.assertGreater(len(params), 0)

        # 2. Predict Multi-Disease Risks
        profile = {'age': 52, 'gender': 'Female', 'blood_pressure': 130, 'bmi': 28.0}
        for p in params:
            profile[p['canonical_name']] = p['measured_value']

        risks = self.predictor.predict_all(profile)
        self.assertIn('Diabetes', risks)
        self.assertIn('Heart Disease', risks)
        self.assertIn('Chronic Kidney Disease', risks)
        self.assertIn('Liver Disease', risks)

        # 3. Calculate Health Score
        score = self.calculator.calculate_score(params, risks)
        self.assertLess(score['overall_score'], 100.0)
        self.assertIn(score['rating'], ['Excellent', 'Good', 'Fair', 'Poor', 'Critical'])

        # 4. Generate Recommendations
        recs = self.recommender.generate_recommendations(params, risks)
        self.assertGreater(len(recs), 0)

        # 5. Database Save & Retrieve
        report_id = self.db.save_analysis(
            patient_name="Jane Smith",
            age=52,
            gender="Female",
            report_name="Lab_Report_01.pdf",
            raw_text=sample_text,
            score_data=score,
            parameters=params,
            predictions=risks
        )
        self.assertIsNotNone(report_id)
        details = self.db.get_report_details(report_id)
        self.assertEqual(details['report']['patient_name'], "Jane Smith")

        # 6. PDF Generation
        pdf_data = self.pdf_gen.generate_pdf(
            {"name": "Jane Smith", "age": 52, "gender": "Female"},
            params,
            risks,
            score,
            recs
        )
        if pdf_data is not None:
            self.assertGreater(len(pdf_data), 100)

if __name__ == "__main__":
    unittest.main()
