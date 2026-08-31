from rapidfuzz import process, fuzz

class FuzzyMatcher:
    def __init__(self, canonical_names: list):
        self.canonical_names = canonical_names

    def match(self, raw_name: str, threshold: int = 80) -> str:
        match = process.extractOne(raw_name, self.canonical_names, scorer=fuzz.token_sort_ratio)
        if match and match[1] >= threshold:
            return match[0]
        return raw_name # Or handle unmatchable?
