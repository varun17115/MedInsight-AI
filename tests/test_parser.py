import unittest
from src.parser.parser import MedicalReportParser
from src.parser.unit_normalizer import UnitNormalizer
from src.parser.anomaly_detector import AnomalyDetector

class TestParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = MedicalReportParser("data/reference_ranges.json")
        cls.normalizer = UnitNormalizer()
        cls.detector = AnomalyDetector("data/reference_ranges.json")

    def test_find_canonical_name(self):
        self.assertEqual(self.parser.find_canonical_name("Fasting Blood Glucose"), "glucose_fasting")
        self.assertEqual(self.parser.find_canonical_name("HbA1c"), "hba1c")
        self.assertEqual(self.parser.find_canonical_name("Serum Creatinine"), "creatinine")
        self.assertEqual(self.parser.find_canonical_name("Total Cholesterol"), "cholesterol_total")
        self.assertIsNone(self.parser.find_canonical_name("Random Non-Medical String"))

    def test_anomaly_detection(self):
        # Male fasting glucose normal: 70 - 99
        self.assertEqual(self.detector.detect_flag("glucose_fasting", 85.0, "Male"), "NORMAL")
        self.assertEqual(self.detector.detect_flag("glucose_fasting", 125.0, "Male"), "HIGH")
        self.assertEqual(self.detector.detect_flag("glucose_fasting", 50.0, "Male"), "LOW")

    def test_parse_text(self):
        sample_report_text = """
        CLINICAL LABORATORY REPORT
        Patient Name: John Doe
        Fasting Glucose : 115 mg/dL
        Serum Creatinine : 1.1 mg/dL
        Total Cholesterol : 220 mg/dL
        Hemoglobin : 14.5 g/dL
        """
        extracted = self.parser.parse_text(sample_report_text, gender="Male")
        self.assertEqual(len(extracted), 4)

        params = {p["canonical_name"]: p for p in extracted}
        self.assertIn("glucose_fasting", params)
        self.assertEqual(params["glucose_fasting"]["flag"], "HIGH")
        self.assertEqual(params["glucose_fasting"]["measured_value"], 115.0)

        self.assertIn("creatinine", params)
        self.assertEqual(params["creatinine"]["flag"], "NORMAL")

        self.assertIn("cholesterol_total", params)
        self.assertEqual(params["cholesterol_total"]["flag"], "HIGH")

if __name__ == "__main__":
    unittest.main()
