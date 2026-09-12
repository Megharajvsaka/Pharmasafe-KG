"""
step3_fuzzy_match.py
--------------------
Phase 1 — Task 1e & 1f
Builds the brand_generic_map and performs fuzzy string matching
to link Indian generic names → DrugBank generic names.

This is the CORE research contribution:
    "Combiflam" → ["ibuprofen", "paracetamol"]
    "ibuprofen"  → DrugBank entry "Ibuprofen"  (match score: 100)
    "paracetamol"→ DrugBank entry "Paracetamol"(match score: 100)

Requires outputs from steps 1 and 2:
    phase1/outputs/indian_drugs_cleaned.csv
    phase1/outputs/drugbank_ddi_cleaned.csv

Output files (written to phase1/outputs/):
    brand_generic_map.csv     — brand_name → [generic1, generic2, ...]
    fuzzy_matched.csv         — each generic with its DrugBank match + score
    master_mapping_table.csv  — the complete merged table for Neo4j loading
    unmatched_generics.csv    — generics that couldn't be matched (needs manual review)

Run:
    python phase1/step3_fuzzy_match.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from thefuzz import process as fuzz_process, fuzz
from tqdm import tqdm
from collections import defaultdict

from config import (
    CLEANED_INDIAN_CSV, CLEANED_DRUGBANK_CSV,
    BRAND_GENERIC_MAP_CSV, FUZZY_MATCHED_CSV,
    MASTER_MAP_CSV, UNMATCHED_CSV,
    FUZZY_HIGH_THRESHOLD, FUZZY_MED_THRESHOLD, FUZZY_LOW_THRESHOLD,
    PIPELINE_REPORT,
)
from utils import get_logger, normalize_name, print_section, write_report

log = get_logger("step3_fuzzy")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3A — Load cleaned outputs from steps 1 and 2
# ─────────────────────────────────────────────────────────────────────────────
def load_cleaned_data():
    """Loads the outputs produced by steps 1 and 2."""
    print_section("STEP 3 — Loading Cleaned Datasets")

    if not CLEANED_INDIAN_CSV.exists():
        log.error(f"Missing: {CLEANED_INDIAN_CSV}  — run step1_load_indian_drugs.py first")
        sys.exit(1)
    if not CLEANED_DRUGBANK_CSV.exists():
        log.error(f"Missing: {CLEANED_DRUGBANK_CSV} — run step2_load_drugbank.py first")
        sys.exit(1)

    df_indian = pd.read_csv(CLEANED_INDIAN_CSV, encoding="utf-8")
    df_ddi    = pd.read_csv(CLEANED_DRUGBANK_CSV, encoding="utf-8")

    log.info(f"  Indian drugs loaded   : {len(df_indian):,} rows")
    log.info(f"  DrugBank DDIs loaded  : {len(df_ddi):,} rows")
    return df_indian, df_ddi


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3B — Build brand_generic_map
# ─────────────────────────────────────────────────────────────────────────────
def build_brand_generic_map(df_indian: pd.DataFrame) -> pd.DataFrame:
    """
    Creates the brand_generic_map DataFrame.

    Each row represents one Indian brand drug with its generic ingredients.
    Multiple ingredients are stored as a pipe-separated string.

    Example output row:
        brand_name  : "Combiflam"
        generics_str: "ibuprofen|paracetamol"
        num_generics: 2
        manufacturer: "Sanofi India Ltd"
    """
    print_section("STEP 3 — Building Brand-to-Generic Map")

    df = df_indian[["brand_name", "generics_str"]].copy()
    df["num_generics"] = df["generics_str"].apply(lambda s: len(s.split("|")) if isinstance(s, str) and s else 0)

    # Optional manufacturer column
    if "manufacturer" in df_indian.columns:
        df["manufacturer"] = df_indian["manufacturer"]

    log.info(f"  Total brand-to-generic mappings : {len(df):,}")
    log.info(f"  Single-ingredient brands        : {(df['num_generics'] == 1).sum():,}")
    log.info(f"  Multi-ingredient (combo) brands : {(df['num_generics'] > 1).sum():,}")

    # Count total unique generic names across all brands
    all_generics = set()
    for gs in df["generics_str"].dropna():
        for g in gs.split("|"):
            g = g.strip()
            if g:
                all_generics.add(g)
    log.info(f"  Total unique generic names      : {len(all_generics):,}")

    df.to_csv(BRAND_GENERIC_MAP_CSV, index=False, encoding="utf-8")
    log.info(f"  Saved → {BRAND_GENERIC_MAP_CSV}")

    return df, all_generics


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3C — Build DrugBank generic name lookup set
# ─────────────────────────────────────────────────────────────────────────────
def build_drugbank_vocab(df_ddi: pd.DataFrame) -> list[str]:
    """
    Extracts all unique drug names from DrugBank DDI pairs.
    This becomes the 'dictionary' for fuzzy matching.

    Returns a sorted list for deterministic matching.
    """
    print_section("STEP 3 — Building DrugBank Vocabulary")

    vocab = set()
    for col in ["drug1_norm", "drug2_norm"]:
        if col in df_ddi.columns:
            vocab.update(df_ddi[col].dropna().str.strip().unique())

    vocab = sorted(vocab)
    log.info(f"  DrugBank vocabulary size: {len(vocab):,} unique generic names")
    return vocab


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3D — Fuzzy matching: Indian generics → DrugBank entries
# ─────────────────────────────────────────────────────────────────────────────
def fuzzy_match_generics(
    indian_generics: set[str],
    drugbank_vocab: list[str]
) -> pd.DataFrame:
    """
    For each Indian generic name, finds the best-matching DrugBank entry
    using token_sort_ratio scoring (handles word-order variations).

    Scoring tiers:
        ≥ 90 : HIGH confidence  — auto-accept
        75–89: MEDIUM confidence — accept but flagged for manual review
        60–74: LOW confidence    — borderline, manual review strongly recommended
        < 60 : REJECT            — no reliable match found

    Returns a DataFrame with one row per Indian generic.
    """
    print_section("STEP 3 — Fuzzy Matching Indian Generics to DrugBank")
    log.info(f"  Matching {len(indian_generics):,} Indian generics against {len(drugbank_vocab):,} DrugBank entries...")
    log.info("  This may take 30–120 seconds depending on dataset size...")

    results = []

    for generic in tqdm(sorted(indian_generics), desc="  Fuzzy matching"):
        generic_clean = generic.strip()
        if not generic_clean:
            continue

        # extractOne returns (matched_string, score)
        match_result = fuzz_process.extractOne(
            generic_clean,
            drugbank_vocab,
            scorer=fuzz.token_sort_ratio,
        )

        if match_result is None:
            results.append({
                "indian_generic":   generic_clean,
                "drugbank_match":   None,
                "match_score":      0,
                "match_confidence": "REJECT",
                "action":           "no_match_in_vocabulary",
            })
            continue

        matched_name, score = match_result

        # Classify confidence tier
        if score >= FUZZY_HIGH_THRESHOLD:
            confidence = "HIGH"
            action = "auto_accept"
        elif score >= FUZZY_MED_THRESHOLD:
            confidence = "MEDIUM"
            action = "accept_review_recommended"
        elif score >= FUZZY_LOW_THRESHOLD:
            confidence = "LOW"
            action = "manual_review_required"
        else:
            confidence = "REJECT"
            action = "no_match_below_threshold"

        results.append({
            "indian_generic":   generic_clean,
            "drugbank_match":   matched_name,
            "match_score":      score,
            "match_confidence": confidence,
            "action":           action,
        })

    df_matched = pd.DataFrame(results)

    # ── Summary statistics ────────────────────────────────────────────────────
    total    = len(df_matched)
    high     = (df_matched["match_confidence"] == "HIGH").sum()
    medium   = (df_matched["match_confidence"] == "MEDIUM").sum()
    low      = (df_matched["match_confidence"] == "LOW").sum()
    rejected = (df_matched["match_confidence"] == "REJECT").sum()

    log.info(f"\n  ── Fuzzy Matching Results ──────────────────────────")
    log.info(f"  Total generics processed  : {total:,}")
    log.info(f"  HIGH confidence  (≥{FUZZY_HIGH_THRESHOLD})  : {high:,}  ({high/total*100:.1f}%)")
    log.info(f"  MEDIUM confidence({FUZZY_MED_THRESHOLD}-{FUZZY_HIGH_THRESHOLD-1}) : {medium:,}  ({medium/total*100:.1f}%)")
    log.info(f"  LOW confidence   ({FUZZY_LOW_THRESHOLD}-{FUZZY_MED_THRESHOLD-1})  : {low:,}   ({low/total*100:.1f}%)")
    log.info(f"  REJECTED         (<{FUZZY_LOW_THRESHOLD})  : {rejected:,}   ({rejected/total*100:.1f}%)")
    log.info(f"  ────────────────────────────────────────────────────")

    # Save unmatched for manual review
    unmatched = df_matched[df_matched["match_confidence"].isin(["LOW", "REJECT"])].copy()
    unmatched.to_csv(UNMATCHED_CSV, index=False, encoding="utf-8")
    log.info(f"\n  Unmatched/low-confidence generics saved for review → {UNMATCHED_CSV}")
    log.info(f"  (These {len(unmatched):,} generics need manual DrugBank name verification)")

    # Save all matches
    df_matched.to_csv(FUZZY_MATCHED_CSV, index=False, encoding="utf-8")
    log.info(f"  Full fuzzy match results saved → {FUZZY_MATCHED_CSV}")

    return df_matched


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3E — Build the master mapping table
# ─────────────────────────────────────────────────────────────────────────────
def build_master_table(
    df_indian: pd.DataFrame,
    df_fuzzy: pd.DataFrame,
    df_ddi: pd.DataFrame
) -> pd.DataFrame:
    """
    Joins all three sources to produce the master mapping table.
    This is the final output consumed by Neo4j loading scripts.

    Output columns:
        brand_name          — Indian brand name (node: Drug)
        indian_generic      — extracted generic from composition
        drugbank_match      — matched DrugBank entry name
        match_score         — fuzzy match confidence score
        match_confidence    — HIGH / MEDIUM / LOW / REJECT
        manufacturer        — drug manufacturer
        has_ddi_data        — True if DrugBank has DDI records for this generic
        ddi_count           — number of DDI pairs involving this generic

    Filters to HIGH + MEDIUM confidence matches only.
    """
    print_section("STEP 3 — Building Master Mapping Table")

    # ── Explode brand_generic_map to long format ──────────────────────────────
    # Each row will be: brand_name | one_generic
    rows = []
    for _, row in df_indian.iterrows():
        generics = [g.strip() for g in str(row["generics_str"]).split("|") if g.strip()]
        for generic in generics:
            r = {"brand_name": row["brand_name"], "indian_generic": generic}
            if "manufacturer" in row:
                r["manufacturer"] = row.get("manufacturer", "")
            rows.append(r)

    df_long = pd.DataFrame(rows)
    log.info(f"  Exploded brand-generic pairs: {len(df_long):,} rows")

    # ── Merge with fuzzy match results ────────────────────────────────────────
    df_master = df_long.merge(
        df_fuzzy[["indian_generic", "drugbank_match", "match_score", "match_confidence", "action"]],
        on="indian_generic",
        how="left"
    )
    log.info(f"  After merging fuzzy matches: {len(df_master):,} rows")

    # ── Keep only HIGH + MEDIUM confidence ────────────────────────────────────
    before = len(df_master)
    df_master = df_master[
        df_master["match_confidence"].isin(["HIGH", "MEDIUM"])
    ].copy()
    log.info(f"  After filtering HIGH/MEDIUM: {before:,} → {len(df_master):,} rows")
    log.info(f"  Dropped {before - len(df_master):,} LOW/REJECT rows (check unmatched_generics.csv)")

    # ── Count DDI records per DrugBank match ──────────────────────────────────
    # How many DDI pairs does each matched generic appear in?
    ddi_drug1_counts = df_ddi["drug1_norm"].value_counts()
    ddi_drug2_counts = df_ddi["drug2_norm"].value_counts()
    ddi_total = ddi_drug1_counts.add(ddi_drug2_counts, fill_value=0)

    df_master["ddi_count"] = df_master["drugbank_match"].map(ddi_total).fillna(0).astype(int)
    df_master["has_ddi_data"] = df_master["ddi_count"] > 0

    # ── Summary ───────────────────────────────────────────────────────────────
    brands_with_ddi   = df_master[df_master["has_ddi_data"]]["brand_name"].nunique()
    brands_total      = df_master["brand_name"].nunique()
    generics_in_graph = df_master["drugbank_match"].nunique()

    log.info(f"\n  ── Master Mapping Summary ──────────────────────────")
    log.info(f"  Total brand-generic-DDI triplets : {len(df_master):,}")
    log.info(f"  Unique Indian brand drugs        : {brands_total:,}")
    log.info(f"  Brands with DDI data             : {brands_with_ddi:,}  ({brands_with_ddi/brands_total*100:.1f}%)")
    log.info(f"  Unique DrugBank generics linked  : {generics_in_graph:,}")
    log.info(f"  ────────────────────────────────────────────────────")

    df_master.to_csv(MASTER_MAP_CSV, index=False, encoding="utf-8")
    log.info(f"\n  Master mapping table saved → {MASTER_MAP_CSV}")

    return df_master


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE VALIDATION — Spot-check expected drug mappings
# ─────────────────────────────────────────────────────────────────────────────
def validate_known_mappings(df_master: pd.DataFrame) -> None:
    """
    Validates the pipeline against a set of known brand→generic relationships.
    These are ground-truth examples every Indian pharmacist would know.
    If these fail, something is wrong with the composition parsing or fuzzy matching.
    """
    print_section("STEP 3 — Validating Known Drug Mappings")

    known = [
        ("Combiflam",  ["ibuprofen", "paracetamol"]),
        ("Ecosprin",   ["aspirin"]),
        ("Dolo 650",   ["paracetamol"]),
        ("Pantop 40",  ["pantoprazole"]),
        ("Atorva 10",  ["atorvastatin"]),
        ("Telma 40",   ["telmisartan"]),
        ("Metolar XR", ["metoprolol"]),
        ("Shelcal 500",["calcium carbonate"]),
    ]

    passed = 0
    failed = 0

    for brand, expected_generics in known:
        # Case-insensitive partial match on brand name
        brand_rows = df_master[df_master["brand_name"].str.lower().str.contains(brand.lower(), na=False)]

        if brand_rows.empty:
            log.warning(f"  WARN  [{brand}] — not found in master table (drug may not be in dataset)")
            continue

        found_generics = set(brand_rows["indian_generic"].str.lower().tolist())

        for expected in expected_generics:
            if any(expected in fg for fg in found_generics):
                log.info(f"  PASS  [{brand}] → found '{expected}' in generics: {found_generics}")
                passed += 1
            else:
                log.warning(f"  FAIL  [{brand}] → expected '{expected}' but found: {found_generics}")
                failed += 1

    log.info(f"\n  Validation: {passed} PASSED, {failed} FAILED")
    if failed > 0:
        log.warning("  Review failed cases — check composition parsing in utils.py")
    else:
        log.info("  All known mappings validated successfully!")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("PharmaSafe-KG  |  Phase 1  |  Step 3: Fuzzy Matching")
    log.info("=" * 60)

    df_indian, df_ddi = load_cleaned_data()

    # Build brand-to-generic map and get all unique Indian generics
    df_brand_map, all_indian_generics = build_brand_generic_map(df_indian)

    # Build DrugBank vocabulary
    drugbank_vocab = build_drugbank_vocab(df_ddi)

    # Fuzzy match
    df_fuzzy = fuzzy_match_generics(all_indian_generics, drugbank_vocab)

    # Build master table
    df_master = build_master_table(df_indian, df_fuzzy, df_ddi)

    # Validate
    validate_known_mappings(df_master)

    # Write pipeline report
    report_lines = [
        f"Step 1 — Indian drugs cleaned      : {len(df_indian):,} rows",
        f"Step 2 — DrugBank DDIs cleaned     : {len(df_ddi):,} rows",
        f"Step 3 — Unique Indian generics    : {len(all_indian_generics):,}",
        f"Step 3 — DrugBank vocab size       : {len(drugbank_vocab):,}",
        f"Step 3 — Master mapping rows       : {len(df_master):,}",
        f"Step 3 — Brands with DDI data      : {df_master[df_master['has_ddi_data']]['brand_name'].nunique():,}",
        "",
        "OUTPUT FILES:",
        f"  {BRAND_GENERIC_MAP_CSV}",
        f"  {FUZZY_MATCHED_CSV}",
        f"  {MASTER_MAP_CSV}",
        f"  {UNMATCHED_CSV}",
        "",
        "NEXT STEP: Run phase2/step1_neo4j_setup.py to load the graph",
    ]
    write_report(report_lines, PIPELINE_REPORT)

    log.info("\n  Step 3 COMPLETE. Phase 1 data preparation is DONE.")
    log.info("  Next: Run phase2/step1_neo4j_setup.py to build the Knowledge Graph.")


if __name__ == "__main__":
    main()
