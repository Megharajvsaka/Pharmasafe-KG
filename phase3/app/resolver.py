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
from thefuzz import process as fuzz_process, fuzz

# ── File paths ────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).parent.parent.parent          # pharmasafe-kg/
MASTER_CSV = ROOT / "phase1" / "outputs" / "master_mapping_table.csv"

# ── In-memory stores (populated once at startup) ──────────────────────────────
_brand_to_generics: dict[str, list[str]] = {}   # lowercase brand → generics
_all_brand_names:   list[str]            = []    # original-case brand names

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
    global _brand_to_generics, _all_brand_names

    if not MASTER_CSV.exists():
        raise FileNotFoundError(
            f"master_mapping_table.csv not found at {MASTER_CSV}\n"
            "Run Phase 1 first:  python phase1/run_phase1.py"
        )

    df = pd.read_csv(MASTER_CSV, encoding="utf-8", low_memory=False)

    for _, row in df.iterrows():
        brand   = str(row.get("brand_name", "")).strip()
        generic = str(row.get("drugbank_match", "")).strip()
        if not brand or not generic:
            continue
        key = brand.lower()
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
        "input":         "Combiflam",
        "matched_brand": "Combiflam",
        "generics":      ["ibuprofen", "paracetamol"],
        "match_type":    "exact",
        "confidence":    100
    }
    """
    name       = brand_name.strip()
    name_lower = name.lower()

    # 1. Exact match
    if name_lower in _brand_to_generics:
        generics = _expand_aliases(_brand_to_generics[name_lower])
        return {
            "input":         name,
            "matched_brand": name,
            "generics":      generics,
            "match_type":    "exact",
            "confidence":    100,
        }

    # 2. Direct alias (user typed a generic name directly, e.g. "paracetamol" → "acetaminophen")
    if name_lower in ALIASES:
        return {
            "input":         name,
            "matched_brand": name,
            "generics":      [name_lower, ALIASES[name_lower]],
            "match_type":    "alias",
            "confidence":    100,
        }

    # 3. User typed a raw generic name directly (e.g. "warfarin", "ibuprofen")
    #    These ARE valid DrugBank generic names — treat them as their own generic
    KNOWN_GENERICS = {
        "warfarin", "ibuprofen", "paracetamol", "acetaminophen", "aspirin",
        "acetylsalicylic acid", "metformin", "atorvastatin", "simvastatin",
        "amlodipine", "metoprolol", "digoxin", "omeprazole", "pantoprazole",
        "amoxicillin", "ciprofloxacin", "azithromycin", "clarithromycin",
        "diclofenac", "prednisolone", "dexamethasone", "furosemide",
        "spironolactone", "lisinopril", "ramipril", "losartan", "telmisartan",
        "clopidogrel", "glibenclamide", "glipizide", "levothyroxine",
        "phenytoin", "carbamazepine", "valproic acid", "alprazolam",
        "clonazepam", "tramadol", "cetirizine", "montelukast", "amiodarone",
        "rifampicin", "isoniazid", "methotrexate", "cyclosporine", "lithium",
        "sertraline", "fluoxetine", "atorvastatin", "rosuvastatin",
    }
    if name_lower in KNOWN_GENERICS:
        generics = _expand_aliases([name_lower])
        return {
            "input":         name,
            "matched_brand": name,
            "generics":      generics,
            "match_type":    "generic_direct",
            "confidence":    100,
        }

    # 3. Fuzzy match against all known brand names
    if _all_brand_names:
        result = fuzz_process.extractOne(
            name, _all_brand_names, scorer=fuzz.token_sort_ratio
        )
        if result and result[1] >= 80:
            matched, score = result
            generics = _expand_aliases(_brand_to_generics.get(matched.lower(), []))
            return {
                "input":         name,
                "matched_brand": matched,
                "generics":      generics,
                "match_type":    "fuzzy",
                "confidence":    score,
            }

    # 4. Not found
    return {
        "input":         name,
        "matched_brand": name,
        "generics":      [],
        "match_type":    "not_found",
        "confidence":    0,
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

    prefix = [b for b in _all_brand_names if b.lower().startswith(q)]
    if prefix:
        return sorted(prefix)[:limit]

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
