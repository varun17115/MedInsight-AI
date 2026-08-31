import site
import sys
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class TextExtractor:
    """Provides methods to extract digital text and tables from PDFs."""
    def __init__(self):
        pass

    def extract_text_pymupdf(self, pdf_path: str) -> str:
        """
        Fast text extraction for digital non-scanned PDFs using PyMuPDF (fitz).
        """
        try:
            import fitz
        except ImportError:
            logger.error("PyMuPDF (fitz) is not installed.")
            return ""

        text = ""
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text("text") + "\n"
        except Exception as e:
            logger.error(f"Error extracting text with PyMuPDF: {e}")
        return text

    def extract_tables_pdfplumber(self, pdf_path: str) -> List[List[List[str]]]:
        """
        Extract structured tables using pdfplumber.
        Returns a list of tables, where each table is a list of rows (lists of strings).
        """
        try:
            import pdfplumber
        except ImportError:
            logger.error("pdfplumber is not installed.")
            return []

        tables = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    extracted_tables = page.extract_tables()
                    for t in extracted_tables:
                        # Clean up None values
                        clean_t = [[str(cell) if cell is not None else "" for cell in row] for row in t]
                        tables.append(clean_t)
        except Exception as e:
            logger.error(f"Error extracting tables with pdfplumber: {e}")
        return tables

    def process_digital_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Aggregate text and table extraction for digital PDFs.
        """
        return {
            "text": self.extract_text_pymupdf(pdf_path),
            "tables": self.extract_tables_pdfplumber(pdf_path)
        }
