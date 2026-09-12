"""
resolver_service.py
-------------------
Brand-to-generic formulation resolution service.
Loads master_mapping_table.csv and standardizes Indian brands to generic chemical entities.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import pandas as pd
from thefuzz import fuzz, process

ROOT_DIR = Path(__file__).resolve().parents[3]
MASTER_CSV_PRIMARY = ROOT_DIR / "data_pipeline" / "outputs" / "master_mapping_table.csv"
MASTER_CSV_FALLBACK = ROOT_DIR / "phase1" / "outputs" / "master_mapping_table.csv"

# Known alias map (Indian name <-> DrugBank standard name)
ALIASES: Dict[str, str] = {
    "paracetamol":          "acetaminophen",
    "acetaminophen":        "paracetamol",
    "aspirin":              "acetylsalicylic acid",
    "acetylsalicylic acid": "aspirin",
    "adrenaline":           "epinephrine",
    "epinephrine":          "adrenaline",
    "salbutamol":           "albuterol",
    "albuterol":            "salbutamol",
    "frusemide":            "furosemide",
    "furosemide":           "frusemide",
    "glibenclamide":        "glyburide",
    "glyburide":            "glibenclamide",
    "ciclosporin":          "cyclosporine",
    "cyclosporine":         "ciclosporin",
    "rifampicin":           "rifampin",
    "rifampin":             "rifampicin",
    "amoxycillin":          "amoxicillin",
    "amoxicillin":          "amoxycillin",
    "dothiepin":            "dosulepin",
    "dosulepin":            "dothiepin",
}


class ResolverService:
    def __init__(self, mapping_path: Optional[Path] = None):
        self._brand_to_generics: Dict[str, List[str]] = {}
        self._all_brand_names: List[str] = []
        self._all_known_generics: Set[str] = set()
        self._loaded = False
        self._mapping_path = mapping_path or (MASTER_CSV_PRIMARY if MASTER_CSV_PRIMARY.exists() else MASTER_CSV_FALLBACK)

    def load(self) -> int:
        if self._loaded:
            return len(self._brand_to_generics)

        if not self._mapping_path.exists():
            raise FileNotFoundError(f"master_mapping_table.csv not found at {self._mapping_path}")

        df = pd.read_csv(self._mapping_path, encoding="utf-8", low_memory=False)
        self._all_known_generics = set(ALIASES.keys()).union(set(ALIASES.values()))

        for _, row in df.iterrows():
            brand = str(row.get("brand_name", "")).strip()
            generic = str(row.get("drugbank_match", "")).strip()
            if not brand or not generic:
                continue
            key = brand.lower()
            g_lower = generic.lower()
            self._all_known_generics.add(g_lower)

            if key not in self._brand_to_generics:
                self._brand_to_generics[key] = []
            if generic not in self._brand_to_generics[key]:
                self._brand_to_generics[key].append(generic)

        self._all_brand_names = sorted({
            str(row["brand_name"]).strip()
            for _, row in df.iterrows()
            if str(row.get("brand_name", "")).strip()
        })
        self._loaded = True
        return len(self._brand_to_generics)

    @property
    def brand_names(self) -> List[str]:
        if not self._loaded:
            self.load()
        return self._all_brand_names

    def resolve_brand(self, brand_name: str) -> Dict[str, Any]:
        if not self._loaded:
            self.load()

        name = brand_name.strip()
        name_lower = name.lower()

        if not name:
            return {
                "input": name,
                "matched_brand": name,
                "generics": [],
                "match_type": "not_found",
                "confidence": 0,
                "review_required": False,
            }

        # 1. Exact brand match
        if name_lower in self._brand_to_generics:
            generics = self._expand_aliases(self._brand_to_generics[name_lower])
            return {
                "input": name,
                "matched_brand": name,
                "generics": generics,
                "match_type": "exact",
                "confidence": 100,
                "review_required": False,
            }

        # 2. Direct alias
        if name_lower in ALIASES:
            return {
                "input": name,
                "matched_brand": name,
                "generics": [name_lower, ALIASES[name_lower]],
                "match_type": "alias",
                "confidence": 100,
                "review_required": False,
            }

        # 3. User typed a raw generic name directly
        if name_lower in self._all_known_generics:
            generics = self._expand_aliases([name_lower])
            return {
                "input": name,
                "matched_brand": name,
                "generics": generics,
                "match_type": "generic_direct",
                "confidence": 100,
                "review_required": False,
            }

        # 4. Fuzzy match against all known brand names
        if self._all_brand_names:
            result = process.extractOne(name, self._all_brand_names, scorer=fuzz.token_sort_ratio)
            if result and result[1] >= 80:
                matched, score = result
                generics = self._expand_aliases(self._brand_to_generics.get(matched.lower(), []))
                return {
                    "input": name,
                    "matched_brand": matched,
                    "generics": generics,
                    "match_type": "fuzzy",
                    "confidence": score,
                    "review_required": score < 85,
                }

        # 5. Not found
        return {
            "input": name,
            "matched_brand": name,
            "generics": [],
            "match_type": "not_found",
            "confidence": 0,
            "review_required": False,
        }

    def resolve_multiple(self, brand_names: List[str]) -> Dict[str, Dict[str, Any]]:
        return {name: self.resolve_brand(name) for name in brand_names}

    def search_brands(self, query: str, limit: int = 10) -> List[str]:
        if not self._loaded:
            self.load()
        q = query.strip().lower()
        if not q:
            return []

        # 1. Prefix match on brand names
        prefix = [b for b in self._all_brand_names if b.lower().startswith(q)]
        if prefix:
            return sorted(prefix)[:limit]

        # 2. Prefix match on known generic names
        generic_prefix = [g.title() for g in self._all_known_generics if g.startswith(q)]
        if generic_prefix:
            return sorted(generic_prefix)[:limit]

        # 3. Fuzzy search fallback
        results = process.extract(query, self._all_brand_names, scorer=fuzz.partial_ratio, limit=limit)
        return [r[0] for r in results if r[1] >= 60]

    def _expand_aliases(self, generics: List[str]) -> List[str]:
        expanded = list(generics)
        for g in generics:
            alias = ALIASES.get(g)
            if alias and alias not in expanded:
                expanded.append(alias)
        return expanded


_resolver_instance: Optional[ResolverService] = None


def get_resolver() -> ResolverService:
    global _resolver_instance
    if _resolver_instance is None:
        _resolver_instance = ResolverService()
        _resolver_instance.load()
    return _resolver_instance
