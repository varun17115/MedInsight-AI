import os
import logging
import numpy as np
from typing import List, Tuple, Dict, Any
from src.ocr.preprocessor import ImagePreprocessor

logger = logging.getLogger(__name__)

class OCREngine:
    def __init__(self, gpu: bool = False):
        self.gpu = gpu
        self.reader = None
        self._initialize_reader()

    def _initialize_reader(self):
        try:
            import easyocr
            # We initialize EasyOCR with English.
            self.reader = easyocr.Reader(['en'], gpu=self.gpu)
            logger.info("EasyOCR initialized successfully.")
        except ImportError:
            logger.error("easyocr is not installed.")
        except Exception as e:
            logger.error(f"Error initializing EasyOCR: {e}")

    def extract_from_image(self, image: np.ndarray, preprocess: bool = True) -> Dict[str, Any]:
        """
        Runs bounding-box heuristic extraction over an image array.
        Returns a dictionary containing full text and a list of bounding boxes.
        """
        if self.reader is None:
            return {"text": "", "blocks": []}

        try:
            if preprocess:
                proc_img = ImagePreprocessor.preprocess_for_ocr(image)
            else:
                proc_img = image

            # reader.readtext returns list of (bbox, text, prob)
            results = self.reader.readtext(proc_img)

            full_text = []
            blocks = []

            for (bbox, text, prob) in results:
                full_text.append(text)
                blocks.append({
                    "bbox": [[int(coord) for coord in pt] for pt in bbox],
                    "text": text,
                    "confidence": float(prob)
                })

            return {
                "text": "\n".join(full_text),
                "blocks": blocks
            }
        except Exception as e:
            logger.error(f"Error during OCR extraction: {e}")
            return {"text": "", "blocks": []}

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single image via file path.
        """
        import cv2
        image = cv2.imread(file_path)
        if image is None:
            logger.error(f"Failed to load image at {file_path}")
            return {"text": "", "blocks": []}

        return self.extract_from_image(image)
