import re
from typing import List, Dict, Any, Optional
from src.parser.regex_patterns import PARAMETER_MAP, PARAMETER_LINE_REGEX
from src.parser.unit_normalizer import UnitNormalizer
from src.parser.anomaly_detector import AnomalyDetector

class MedicalReportParser:
    def __init__(self, reference_ranges_path: str = "data/reference_ranges.json"):
        self.anomaly_detector = AnomalyDetector(reference_ranges_path)
        self.normalizer = UnitNormalizer()

    def find_canonical_name(self, raw_param_name: str) -> Optional[str]:
        raw_param_name = raw_param_name.strip()
        for pattern, canonical in PARAMETER_MAP.items():
            if re.search(pattern, raw_param_name, re.IGNORECASE):
                return canonical
        return None

    def _clean_numeric(self, val_str: str) -> Optional[float]:
        """Convert string number to float, removing commas and handling edge cases."""
        try:
            cleaned = val_str.replace(',', '').strip()
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    def _create_param_dict(self, raw_param: str, canonical: str, val_float: float, unit: str, gender: str) -> Dict[str, Any]:
        flag = self.anomaly_detector.detect_flag(canonical, val_float, gender=gender)
        ref_info = self.anomaly_detector.ref_ranges.get(canonical, {})
        category = ref_info.get("category", "General")
        ranges = ref_info.get("ranges", {}).get(gender, {})
        ref_low = ranges.get("low")
        ref_high = ranges.get("high")
        expected_units = ref_info.get("units", [unit])
        final_unit = unit.strip() if unit and unit.strip() else (expected_units[0] if expected_units else "")

        return {
            "parameter_name": raw_param.strip(),
            "canonical_name": canonical,
            "category": category,
            "measured_value": val_float,
            "unit": final_unit,
            "reference_low": ref_low,
            "reference_high": ref_high,
            "flag": flag,
            "confidence_score": 0.95
        }

    def parse_tables(self, tables: List[List[List[str]]], gender: str = "Male") -> List[Dict[str, Any]]:
        """
        Extract parameters from pdfplumber extracted tabular cells.
        """
        extracted = []
        found_canonicals = set()

        for table in tables:
            for row in table:
                if not row or len(row) < 2:
                    continue

                # Filter out empty cells
                clean_row = [str(c).strip() for c in row if c is not None and str(c).strip()]
                if not clean_row:
                    continue

                # Check if first item matches a parameter name
                raw_param = clean_row[0]
                canonical = self.find_canonical_name(raw_param)
                if not canonical or canonical in found_canonicals:
                    continue

                # Find the numeric value in the remaining row cells
                val_float = None
                unit = ""
                for cell in clean_row[1:]:
                    # Check if cell is purely a numeric value or starts with one
                    num_match = re.search(r"^\s*([0-9]+(?:,[0-9]+)*(?:\.[0-9]+)?)\s*([a-zA-Z/%μuL]+)?", cell)
                    if num_match:
                        parsed_num = self._clean_numeric(num_match.group(1))
                        if parsed_num is not None:
                            val_float = parsed_num
                            if num_match.group(2):
                                unit = num_match.group(2)
                            break
                    # Also handle flag cells like 'L 18' or 'H 35.7'
                    flag_num_match = re.search(r"^[HL]\s+([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z/%μuL]+)?", cell, re.IGNORECASE)
                    if flag_num_match:
                        parsed_num = self._clean_numeric(flag_num_match.group(1))
                        if parsed_num is not None:
                            val_float = parsed_num
                            if flag_num_match.group(2):
                                unit = flag_num_match.group(2)
                            break

                # Extract unit from subsequent cell if not found in number cell
                if val_float is not None:
                    if not unit and len(clean_row) >= 3:
                        for cell in clean_row[2:]:
                            if re.match(r"^[a-zA-Z/%μuL/]+$", cell) and not re.match(r"^[HL]$", cell, re.IGNORECASE):
                                unit = cell
                                break

                    extracted.append(self._create_param_dict(raw_param, canonical, val_float, unit, gender))
                    found_canonicals.add(canonical)

        return extracted

    def parse_text(self, text: str, gender: str = "Male", tables: Optional[List] = None) -> List[Dict[str, Any]]:
        """
        Extract parameters line by line from the text or table data.
        """
        extracted = []
        found_canonicals = set()

        # 1. First extract from structured tables if provided
        if tables:
            table_results = self.parse_tables(tables, gender=gender)
            for item in table_results:
                extracted.append(item)
                found_canonicals.add(item["canonical_name"])

        # 2. Extract line by line from raw text
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        for i, line in enumerate(lines):
            # Try single line match: "HEMOGLOBIN 15 g/dl" or "Glucose : 110 mg/dL"
            canonical = None
            raw_param = None
            val_float = None
            unit = ""

            # Check if line contains a known canonical keyword
            for pattern, c_name in PARAMETER_MAP.items():
                if c_name not in found_canonicals and re.search(pattern, line, re.IGNORECASE):
                    canonical = c_name
                    # Find where the name ends
                    m = re.search(pattern, line, re.IGNORECASE)
                    raw_param = line[:m.end()].strip()
                    remainder = line[m.end():].strip()

                    # Look for number in remainder
                    num_match = re.search(r"[:=-]?\s*(?:[HL]\s+)?(?P<val>\d+(?:,\d+)*(?:\.\d+)?)\s*(?P<unit>[a-zA-Z/%μuL/]+)?", remainder)
                    if num_match and num_match.group("val"):
                        val_float = self._clean_numeric(num_match.group("val"))
                        unit = num_match.group("unit") or ""
                        break
                    
                    # If number not in same line, check next lines (multi-line layout)
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        next_num = re.search(r"^(?:[HL]\s+)?(?P<val>\d+(?:,\d+)*(?:\.\d+)?)\s*(?P<unit>[a-zA-Z/%μuL/]+)?", next_line)
                        if next_num and next_num.group("val"):
                            val_float = self._clean_numeric(next_num.group("val"))
                            unit = next_num.group("unit") or ""
                            # Next next line might be unit
                            if not unit and i + 2 < len(lines):
                                if re.match(r"^[a-zA-Z/%μuL/]+$", lines[i + 2]):
                                    unit = lines[i + 2]
                            break

            if canonical and val_float is not None and canonical not in found_canonicals:
                extracted.append(self._create_param_dict(raw_param or canonical, canonical, val_float, unit, gender))
                found_canonicals.add(canonical)

        return extracted
