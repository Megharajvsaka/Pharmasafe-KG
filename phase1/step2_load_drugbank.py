"""
step2_load_drugbank.py  (UPDATED — works with your available datasets)
-----------------------------------------------------------------------
Phase 1 — Task 1a & 1c

This version uses TWO files you already have instead of the original
DrugBank download:

    DDI_data.csv            →  rename to  drug_interactions.csv
    db_drug_interactions.csv →  rename to  drug_descriptions.csv

Place both in:  pharmasafe-kg/phase1/data/

What each file provides:
    drug_interactions.csv  — drug pairs + DrugBank IDs + interaction_type
                             (222,696 rows, 1,868 unique drugs)
    drug_descriptions.csv  — drug pairs + plain-English mechanism text
                             (191,541 rows, 81% overlap with above)

Together they are a COMPLETE replacement for the original DrugBank file.
Severity is inferred from interaction_type using a keyword mapping.
Known name aliases (paracetamol ↔ acetaminophen, aspirin ↔ acetylsalicylic
acid, etc.) are resolved automatically before fuzzy matching.

Output: phase1/outputs/drugbank_ddi_cleaned.csv   (same format as before)

Run:
    python phase1/step2_load_drugbank.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from pathlib import Path
from tqdm import tqdm

from config import (
    CLEANED_DRUGBANK_CSV,
    AURA_MAX_RELATIONSHIPS,
    DATA_DIR,
)
from utils import get_logger, normalize_name, print_section

log = get_logger("step2_drugbank")

# ── File paths for the two available files ────────────────────────────────────
DDI_FILE  = DATA_DIR / "drug_interactions.csv"    # renamed from DDI_data.csv
DESC_FILE = DATA_DIR / "drug_descriptions.csv"    # renamed from db_drug_interactions.csv

# ── Severity inference: interaction_type keyword → severity tier ──────────────
# Based on clinical pharmacology — these interaction types carry the highest risk
MAJOR_KEYWORDS = [
    "qtc-prolonging", "rhabdomyolysis", "myopathic", "serotonin",
    "cardiotoxic", "hepatotoxic", "neuroexcitatory", "neurotoxic",
    "hyperkalemia", "renal failure", "arrhythmogenic",
    "atrioventricular blocking", "bradycardic", "torsade",
    "central neurotoxic", "nephrotoxic", "anaphylactic",
    "risk or severity of bleeding", "hypoglycemic",
    "anticoagulant activities",   # warfarin + aspirin etc
    "antiplatelet activities",    # bleeding risk combinations
    "risk or severity of hypoglycemia",
    "risk or severity of hypertension",
    "risk or severity of serotonin",
]

MINOR_KEYWORDS = [
    "absorption", "excretion", "bioavailability",
    "photosensitizing", "diagnostic",
]
# Anything not matching major or minor defaults to MODERATE

# ── Drug name alias map ───────────────────────────────────────────────────────
# These datasets use US/scientific naming. Indian prescriptions use common names.
# This map ensures fuzzy matching bridges the gap.
# Format: "name_in_dataset" → "common_indian_name_added_as_alias"
NAME_ALIASES = {
    "acetaminophen":       "paracetamol",
    "acetylsalicylic acid":"aspirin",
    "epinephrine":         "adrenaline",
    "norepinephrine":      "noradrenaline",
    "frusemide":           "furosemide",
    "salbutamol":          "albuterol",
    "pethidine":           "meperidine",
    "lignocaine":          "lidocaine",
    "adrenaline":          "epinephrine",
    "paracetamol":         "acetaminophen",
    "aspirin":             "acetylsalicylic acid",
}


# ─────────────────────────────────────────────────────────────────────────────
def check_files():
    """
    Verifies the two input files exist and gives clear instructions if not.
    """
    missing = []
    if not DDI_FILE.exists():
        missing.append(f"  MISSING: {DDI_FILE}\n  → Rename 'DDI_data.csv' to 'drug_interactions.csv' and place it in phase1/data/")
    if not DESC_FILE.exists():
        missing.append(f"  MISSING: {DESC_FILE}\n  → Rename 'db_drug_interactions.csv' to 'drug_descriptions.csv' and place it in phase1/data/")
    if missing:
        log.error("Required files not found:")
        for m in missing:
            log.error(m)
        sys.exit(1)
    log.info(f"  drug_interactions.csv  found: {DDI_FILE}")
    log.info(f"  drug_descriptions.csv  found: {DESC_FILE}")


# ─────────────────────────────────────────────────────────────────────────────
def load_ddi_data() -> pd.DataFrame:
    """
    Loads DDI_data.csv (renamed to drug_interactions.csv).
    Columns: drug1_id, drug2_id, drug1_name, drug2_name, interaction_type
    """
    log.info(f"  Loading drug interaction pairs...")
    df = pd.read_csv(DDI_FILE, encoding="utf-8", low_memory=False)
    log.info(f"  Loaded {len(df):,} rows. Columns: {list(df.columns)}")
    return df


def load_descriptions() -> dict:
    """
    Loads db_drug_interactions.csv (renamed to drug_descriptions.csv).
    Returns a dict: (drug1_lower, drug2_lower) → description_text
    Both directions are indexed so lookup is direction-agnostic.
    """
    log.info(f"  Loading mechanism descriptions...")
    df = pd.read_csv(DESC_FILE, encoding="utf-8", low_memory=False)
    log.info(f"  Loaded {len(df):,} description rows.")

    desc_map = {}
    for _, row in df.iterrows():
        d1 = str(row["Drug 1"]).strip().lower()
        d2 = str(row["Drug 2"]).strip().lower()
        text = str(row["Interaction Description"]).strip()
        desc_map[(d1, d2)] = text
        desc_map[(d2, d1)] = text   # both directions

    log.info(f"  Description lookup built: {len(desc_map):,} entries (both directions)")
    return desc_map


# ─────────────────────────────────────────────────────────────────────────────
def infer_severity(interaction_type: str) -> str:
    """
    Maps interaction_type string → MAJOR / MODERATE / MINOR.

    Logic:
    - If the interaction_type contains any MAJOR keyword → MAJOR
    - If it contains any MINOR keyword → MINOR
    - Otherwise → MODERATE (the safe default for clinical use)
    """
    it = str(interaction_type).lower().strip()

    for kw in MAJOR_KEYWORDS:
        if kw in it:
            return "MAJOR"

    for kw in MINOR_KEYWORDS:
        if kw in it:
            return "MINOR"

    return "MODERATE"


# ─────────────────────────────────────────────────────────────────────────────
def build_merged_dataframe(df_ddi: pd.DataFrame, desc_map: dict) -> pd.DataFrame:
    """
    Merges DDI interaction pairs with their mechanism descriptions.
    Infers severity from interaction_type.
    Adds alias rows for paracetamol/aspirin so fuzzy matching works correctly.
    """
    print_section("STEP 2 — Merging DDI data with descriptions")

    rows = []
    no_desc = 0

    for _, row in tqdm(df_ddi.iterrows(), total=len(df_ddi), desc="  Merging"):
        d1_orig = str(row["drug1_name"]).strip()
        d2_orig = str(row["drug2_name"]).strip()
        d1_lower = d1_orig.lower()
        d2_lower = d2_orig.lower()
        interaction_type = str(row.get("interaction_type", "")).strip()

        # Look up description (try both directions)
        description = desc_map.get((d1_lower, d2_lower)) or \
                      desc_map.get((d2_lower, d1_lower)) or \
                      f"Interaction type: {interaction_type}."

        if "Interaction type:" in description:
            no_desc += 1

        severity = infer_severity(interaction_type)

        rows.append({
            "drug1_name":       d1_orig,
            "drug2_name":       d2_orig,
            "drug1_norm":       normalize_name(d1_orig),
            "drug2_norm":       normalize_name(d2_orig),
            "drug1_id":         row.get("drug1_id", ""),
            "drug2_id":         row.get("drug2_id", ""),
            "interaction_type": interaction_type,
            "severity":         severity,
            "mechanism":        description,
        })

    df = pd.DataFrame(rows)
    log.info(f"  Total merged rows        : {len(df):,}")
    log.info(f"  Rows with full description: {len(df) - no_desc:,}  ({(len(df)-no_desc)/len(df)*100:.1f}%)")
    log.info(f"  Rows using type fallback : {no_desc:,}")
    return df


# ─────────────────────────────────────────────────────────────────────────────
def add_alias_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    The datasets use US/scientific naming while Indian prescriptions use common names.
    This function adds ALIAS ROWS so fuzzy matching in step3 catches both forms.

    Example:
        "Acetaminophen" exists in dataset
        → add alias row with name "Paracetamol" pointing to same interactions
        → fuzzy match score for "paracetamol" → "paracetamol" = 100 (perfect)
    """
    print_section("STEP 2 — Adding Indian name alias rows")
    alias_rows = []

    for _, row in df.iterrows():
        d1 = row["drug1_norm"]
        d2 = row["drug2_norm"]
        added = False

        # Check if drug1 has an alias
        if d1 in NAME_ALIASES:
            alias = NAME_ALIASES[d1]
            new_row = row.copy()
            new_row["drug1_norm"] = alias
            new_row["drug1_name"] = alias.title()
            alias_rows.append(new_row)
            added = True

        # Check if drug2 has an alias
        if d2 in NAME_ALIASES:
            alias = NAME_ALIASES[d2]
            new_row = row.copy()
            new_row["drug2_norm"] = alias
            new_row["drug2_name"] = alias.title()
            alias_rows.append(new_row)
            added = True

    if alias_rows:
        df_aliases = pd.DataFrame(alias_rows)
        df = pd.concat([df, df_aliases], ignore_index=True)
        log.info(f"  Added {len(alias_rows):,} alias rows for Indian name variants")
        log.info(f"  Key aliases resolved: acetaminophen↔paracetamol, acetylsalicylic acid↔aspirin")
    else:
        log.info("  No alias rows needed.")

    return df


# ─────────────────────────────────────────────────────────────────────────────
def clean_final(df: pd.DataFrame) -> pd.DataFrame:
    """
    Final cleaning:
    1. Remove self-interactions
    2. Direction-agnostic deduplication (keep highest severity)
    3. Trim to AuraDB free-tier DDI budget (100K relationships)
    """
    print_section("STEP 2 — Final cleaning and deduplication")
    log.info(f"  Starting rows: {len(df):,}")

    # Remove self-interactions
    df = df[df["drug1_norm"] != df["drug2_norm"]].copy()
    log.info(f"  After removing self-interactions: {len(df):,}")

    # Direction-agnostic dedup — keep highest severity per pair
    severity_rank = {"MAJOR": 0, "MODERATE": 1, "MINOR": 2}
    df["pair_key"] = df.apply(
        lambda r: "|".join(sorted([str(r["drug1_norm"]), str(r["drug2_norm"])])), axis=1
    )
    df["sev_rank"] = df["severity"].map(severity_rank).fillna(1)
    df = df.sort_values("sev_rank").drop_duplicates(subset="pair_key", keep="first")
    df = df.drop(columns=["sev_rank"])
    log.info(f"  After deduplication: {len(df):,}")

    # AuraDB DDI budget: keep MAJOR first, then MODERATE, then MINOR
    DDI_BUDGET = 100_000
    if len(df) > DDI_BUDGET:
        log.warning(f"  Trimming to AuraDB budget ({DDI_BUDGET:,} DDI edges)...")
        # Keep ALL major interactions first (clinical safety priority)
        major = df[df["severity"] == "MAJOR"]
        remaining_budget = DDI_BUDGET - len(major)
        if remaining_budget < 0:
            # Even MAJOR alone exceeds budget — keep all, warn user
            log.warning(f"  MAJOR alone ({len(major):,}) exceeds budget. Keeping all MAJOR.")
            df = major
        else:
            moderate_budget = int(remaining_budget * 0.85)
            minor_budget    = remaining_budget - moderate_budget
            moderate = df[df["severity"] == "MODERATE"].head(moderate_budget)
            minor    = df[df["severity"] == "MINOR"].head(minor_budget)
            df = pd.concat([major, moderate, minor], ignore_index=True)
        log.info(f"  After AuraDB trim: {len(df):,}")

    sev_counts = df["severity"].value_counts()
    log.info(f"  Severity breakdown: {sev_counts.to_dict()}")
    return df


# ─────────────────────────────────────────────────────────────────────────────
def validate_key_interactions(df: pd.DataFrame):
    """
    Spot-checks that the most important clinical DDI pairs are present.
    These are interactions every clinical DDI system must catch.
    """
    print_section("STEP 2 — Validating key clinical interactions")

    checks = [
        ("warfarin",     "ibuprofen",         "MAJOR"),
        ("warfarin",     "acetylsalicylic acid","MAJOR"),
        ("warfarin",     "aspirin",            "MAJOR"),   # via alias
        ("paracetamol",  "warfarin",           None),      # presence only
        ("metformin",    "ibuprofen",          None),
        ("simvastatin",  "clarithromycin",     "MAJOR"),
        ("digoxin",      "amiodarone",         "MAJOR"),
    ]

    drugs = set(df["drug1_norm"].tolist()) | set(df["drug2_norm"].tolist())
    pairs = set(df["pair_key"].tolist())

    for d1, d2, expected_sev in checks:
        key = "|".join(sorted([d1, d2]))
        drug1_exists = d1 in drugs
        drug2_exists = d2 in drugs
        pair_exists  = key in pairs

        if pair_exists:
            row = df[df["pair_key"] == key].iloc[0]
            actual_sev = row["severity"]
            ok = (expected_sev is None) or (actual_sev == expected_sev)
            status = "PASS" if ok else "WARN"
            log.info(f"  {status}  {d1} + {d2} → {actual_sev}")
        elif drug1_exists and drug2_exists:
            log.info(f"  INFO  {d1} + {d2} — both drugs present but no direct interaction pair")
        else:
            missing = [d for d in [d1, d2] if d not in drugs]
            log.warning(f"  WARN  {d1} + {d2} — missing from drug vocab: {missing}")


# ─────────────────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("PharmaSafe-KG  |  Phase 1  |  Step 2: DrugBank (Updated)")
    log.info("Uses: drug_interactions.csv + drug_descriptions.csv")
    log.info("=" * 60)

    check_files()

    # Load
    df_ddi   = load_ddi_data()
    desc_map = load_descriptions()

    # Merge + infer severity
    df_merged = build_merged_dataframe(df_ddi, desc_map)

    # Add Indian name aliases (paracetamol, aspirin etc.)
    df_aliased = add_alias_rows(df_merged)

    # Final cleaning
    df_clean = clean_final(df_aliased)

    # Validate
    validate_key_interactions(df_clean)

    # Save
    output_cols = ["drug1_norm", "drug2_norm", "drug1_name", "drug2_name",
                   "drug1_id", "drug2_id", "severity", "mechanism",
                   "interaction_type", "pair_key"]
    df_clean[output_cols].to_csv(CLEANED_DRUGBANK_CSV, index=False, encoding="utf-8")

    log.info(f"\n  Saved → {CLEANED_DRUGBANK_CSV}")
    log.info(f"  Total DDI pairs ready for Neo4j: {len(df_clean):,}")
    log.info("\n  Step 2 COMPLETE. Proceed to step3_fuzzy_match.py")
    return df_clean


if __name__ == "__main__":
    main()