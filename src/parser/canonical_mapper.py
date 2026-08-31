class CanonicalMapper:
    def __init__(self, alias_map: dict):
        self.alias_map = alias_map

    def get_canonical(self, alias: str) -> str:
        return self.alias_map.get(alias.strip().lower(), alias.strip().lower())
