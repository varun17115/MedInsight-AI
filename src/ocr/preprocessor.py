import cv2
import numpy as np
from typing import Tuple

class ImagePreprocessor:
    @staticmethod
    def grayscale(image: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def denoise(image: np.ndarray) -> np.ndarray:
        return cv2.medianBlur(image, 3)

    @staticmethod
    def thresholding(image: np.ndarray) -> np.ndarray:
        # Adaptive thresholding for better results with varying illumination
        return cv2.adaptiveThreshold(
            image, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

    @staticmethod
    def apply_clahe(image: np.ndarray) -> np.ndarray:
        """Apply Contrast Limited Adaptive Histogram Equalization"""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(image)

    @staticmethod
    def deskew(image: np.ndarray) -> np.ndarray:
        """Deskew the image based on text block orientation."""
        # Check if color or grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        gray = cv2.bitwise_not(gray)
        coords = np.column_stack(np.where(gray > 0))
        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        return rotated

    @classmethod
    def preprocess_for_ocr(cls, image: np.ndarray) -> np.ndarray:
        """
        Full pipeline for preprocessing scanned medical reports.
        """
        # Deskew image if necessary
        deskewed = cls.deskew(image)

        # Convert to grayscale
        if len(deskewed.shape) == 3:
            gray = cls.grayscale(deskewed)
        else:
            gray = deskewed

        # Apply CLAHE to improve contrast
        contrast = cls.apply_clahe(gray)

        # Denoise
        denoised = cls.denoise(contrast)

        # Binarize
        binary = cls.thresholding(denoised)

        return binary
