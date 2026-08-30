"""
resolver.py  —  pharmasafe-kg/phase3/app/resolver.py
------------------------------------------------------
Indian Brand-to-Generic Resolver.

Loads master_mapping_table.csv into memory at startup.
All lookups are instant O(1) dictionary reads — no database calls.

This is the core India-specific research contribution:
    "Combiflam"   ->  ["ibuprofen", "paracetamol"]
    "Dolo 650"    ->  ["paracetamol"]
    "Ecosprin"    ->  ["aspirin", "acetylsalicylic acid"]
    "Pantop 40"   ->  ["pantoprazole"]
    "Atorva 10"   ->  ["atorvastatin"]
    "Telma 40"    ->  ["telmisartan"]
"""

import re
import pandas as pd
from pathlib import Path

try:
    from thefuzz import process as fuzz_process, fuzz
except ImportError:
    import difflib
    class FuzzFallback:
        @staticmethod
        def token_sort_ratio(s1, s2):
            s1_sorted = " ".join(sorted(str(s1).lower().split()))
            s2_sorted = " ".join(sorted(str(s2).lower().split()))
            return int(difflib.SequenceMatcher(None, s1_sorted, s2_sorted).ratio() * 100)

        @staticmethod
        def partial_ratio(s1, s2):
            return int(difflib.SequenceMatcher(None, str(s1).lower(), str(s2).lower()).ratio() * 100)

    class FuzzProcessFallback:
        @staticmethod
        def extractOne(query, choices, scorer=None):
            if not choices:
                return None
            scorer_fn = scorer if scorer else FuzzFallback.token_sort_ratio
            best_match, best_score = None, -1
            for c in choices:
                score = scorer_fn(query, c)
                if score > best_score:
                    best_score = score
                    best_match = c
            return (best_match, best_score) if best_match else None

        @staticmethod
        def extract(query, choices, scorer=None, limit=10):
            scorer_fn = scorer if scorer else FuzzFallback.partial_ratio
            scored = [(c, scorer_fn(query, c)) for c in choices]
            scored.sort(key=lambda x: x[1], reverse=True)
            return scored[:limit]

    fuzz = FuzzFallback
    fuzz_process = FuzzProcessFallback


# ── File paths ────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).parent.parent.parent          # pharmasafe-kg/
MASTER_CSV = ROOT / "phase1" / "outputs" / "master_mapping_table.csv"

# ── In-memory stores (populated once at startup) ──────────────────────────────
_brand_to_generics: dict[str, list[str]] = {}   # lowercase brand → generics
_all_brand_names:   list[str]            = []    # original-case brand names
_all_known_generics: set[str]            = set() # lowercase standardized generic names

# ── Known alias map (Indian name <-> DrugBank name) ───────────────────────────
ALIASES: dict[str, str] = {
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
}


# ── Public API ────────────────────────────────────────────────────────────────

def load_resolver() -> int:
    """
    Called once at FastAPI startup via lifespan.
    Loads master_mapping_table.csv into _brand_to_generics dict.
    Returns number of unique brand mappings loaded.
    """
    global _brand_to_generics, _all_brand_names, _all_known_generics

    if not MASTER_CSV.exists():
        raise FileNotFoundError(
            f"master_mapping_table.csv not found at {MASTER_CSV}\n"
            "Run Phase 1 first:  python phase1/run_phase1.py"
        )

    df = pd.read_csv(MASTER_CSV, encoding="utf-8", low_memory=False)
    _all_known_generics = set(ALIASES.keys()).union(set(ALIASES.values()))

    for _, row in df.iterrows():
        brand   = str(row.get("brand_name", "")).strip()
        generic = str(row.get("drugbank_match", "")).strip()
        if not brand or not generic:
            continue
        key = brand.lower()
        g_lower = generic.lower()
        _all_known_generics.add(g_lower)

        if key not in _brand_to_generics:
            _brand_to_generics[key] = []
        if generic not in _brand_to_generics[key]:
            _brand_to_generics[key].append(generic)

    _all_brand_names = sorted({
        str(row["brand_name"]).strip()
        for _, row in df.iterrows()
        if str(row.get("brand_name", "")).strip()
    })

    return len(_brand_to_generics)


def resolve_brand(brand_name: str) -> dict:
    """
    Resolves one Indian brand name to its generic ingredients.

    Returns:
    {
        "input":           "Combiflam",
        "matched_brand":   "Combiflam",
        "generics":        ["ibuprofen", "paracetamol"],
        "match_type":      "exact" | "alias" | "generic_direct" | "fuzzy" | "not_found",
        "confidence":      100,
        "review_required": False
    }
    """
    name       = brand_name.strip()
    name_lower = name.lower()

    if not name:
        return {
            "input":           name,
            "matched_brand":   name,
            "generics":        [],
            "match_type":      "not_found",
            "confidence":      0,
            "review_required": False,
        }

    # 1. Exact brand match
    if name_lower in _brand_to_generics:
        generics = _expand_aliases(_brand_to_generics[name_lower])
        return {
            "input":           name,
            "matched_brand":   name,
            "generics":        generics,
            "match_type":      "exact",
            "confidence":      100,
            "review_required": False,
        }

    # 2. Direct alias
    if name_lower in ALIASES:
        return {
            "input":           name,
            "matched_brand":   name,
            "generics":        [name_lower, ALIASES[name_lower]],
            "match_type":      "alias",
            "confidence":      100,
            "review_required": False,
        }

    # 3. User typed a raw generic name directly (e.g. "warfarin", "ibuprofen", "paracetamol")
    if name_lower in _all_known_generics:
        generics = _expand_aliases([name_lower])
        return {
            "input":           name,
            "matched_brand":   name,
            "generics":        generics,
            "match_type":      "generic_direct",
            "confidence":      100,
            "review_required": False,
        }

    # 4. Fuzzy match against all known brand names
    if _all_brand_names:
        result = fuzz_process.extractOne(
            name, _all_brand_names, scorer=fuzz.token_sort_ratio
        )
        if result and result[1] >= 80:
            matched, score = result
            generics = _expand_aliases(_brand_to_generics.get(matched.lower(), []))
            return {
                "input":           name,
                "matched_brand":   matched,
                "generics":        generics,
                "match_type":      "fuzzy",
                "confidence":      score,
                "review_required": score < 85,
            }

    # 5. Not found
    return {
        "input":           name,
        "matched_brand":   name,
        "generics":        [],
        "match_type":      "not_found",
        "confidence":      0,
        "review_required": False,
    }


def resolve_multiple(brand_names: list[str]) -> dict[str, dict]:
    """Resolves a list of brand names. Returns {name: resolve_result}."""
    return {name: resolve_brand(name) for name in brand_names}


def search_brands(query: str, limit: int = 10) -> list[str]:
    """
    Returns brand names starting with `query` (case-insensitive).
    Falls back to fuzzy if no prefix match found.
    Used by GET /search autocomplete endpoint.
    """
    q = query.strip().lower()
    if not q:
        return []

    # 1. Prefix match on brand names
    prefix = [b for b in _all_brand_names if b.lower().startswith(q)]
    if prefix:
        return sorted(prefix)[:limit]

    # 2. Prefix match on known generic names
    generic_prefix = [g.title() for g in _all_known_generics if g.startswith(q)]
    if generic_prefix:
        return sorted(generic_prefix)[:limit]

    # 3. Fuzzy search fallback
    results = fuzz_process.extract(
        query, _all_brand_names, scorer=fuzz.partial_ratio, limit=limit
    )
    return [r[0] for r in results if r[1] >= 60]


def get_all_brand_names() -> list[str]:
    """Returns full sorted list of known brand names."""
    return _all_brand_names


# ── Private helpers ───────────────────────────────────────────────────────────

def _expand_aliases(generics: list[str]) -> list[str]:
    """
    For each generic, adds its alias form if one exists.
    e.g. "acetylsalicylic acid" also adds "aspirin" so Cypher catches both.
    """
    expanded = list(generics)
    for g in generics:
        alias = ALIASES.get(g)
        if alias and alias not in expanded:
            expanded.append(alias)
    return expanded

