import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from src.ocr.preprocessor import ImagePreprocessor
from src.ocr.text_extractor import TextExtractor

class TestOCR(unittest.TestCase):
    def setUp(self):
        self.preprocessor = ImagePreprocessor()
        self.extractor = TextExtractor()

    def test_preprocessor_instantiation(self):
        self.assertIsNotNone(self.preprocessor)

    def test_image_preprocessing(self):
        # Create a simple synthetic image array
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
        processed = self.preprocessor.preprocess_for_ocr(dummy_img)
        self.assertIsNotNone(processed)
        self.assertEqual(len(processed.shape), 2)  # Should be grayscale/binary

    @patch('fitz.open')
    def test_text_extractor_pymupdf(self, mock_fitz_open):
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Patient Report: Glucose 100 mg/dL"
        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc

        text = self.extractor.extract_text_pymupdf("fake_path.pdf")
        self.assertIn("Glucose", text)

if __name__ == '__main__':
    unittest.main()
