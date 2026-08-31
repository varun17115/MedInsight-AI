import json
from typing import Dict, Any, Optional

class AnomalyDetector:
    def __init__(self, reference_ranges_path: str = "data/reference_ranges.json"):
        with open(reference_ranges_path, "r") as f:
            self.ref_ranges = json.load(f)

    def detect_flag(self, canonical_name: str, value: float, gender: str = "Male") -> str:
        """
        Determines the status of a measured parameter based on reference ranges.
        """
        if canonical_name not in self.ref_ranges:
            return "UNKNOWN"

        ranges = self.ref_ranges[canonical_name]["ranges"].get(gender)
        if not ranges:
            return "UNKNOWN"

        low = ranges["low"]
        high = ranges["high"]

        if value < low:
            return "LOW"
        elif value > high:
            return "HIGH"
        else:
            return "NORMAL"
