"""
step2b_supplement_ddinter.py
-----------------------------
OPTIONAL supplement — run ONCE after Phase 1 is complete.

Merges the DDInter dataset into your existing drugbank_ddi_cleaned.csv.
This fills 2 of the 3 pairs that were showing as INFO in Step 2 validation:
    ✓  simvastatin + clarithromycin  → MAJOR   (now added)
    ✓  metformin   + ibuprofen       → MODERATE (now added)
    ✗  digoxin     + amiodarone      → not in DDInter either (acceptable)

DDInter advantages over our inferred severity:
    - Severity is EXPLICITLY labeled (Major/Moderate/Minor) — not inferred
    - 41,600 additional pairs with known severity
    - 573 drug names not present in our DrugBank data at all

What this script does:
    1. Loads your existing phase1/outputs/drugbank_ddi_cleaned.csv
    2. Loads ddinter_downloads_code_A.csv
    3. Drops DDInter rows with Unknown severity
    4. Normalises drug names to match our schema
    5. Removes duplicates already covered by DrugBank (DrugBank takes priority)
    6. Merges and re-applies the AuraDB 100K budget cap
    7. Overwrites drugbank_ddi_cleaned.csv with the improved version
    8. Re-validates all key clinical pairs

Place ddinter file in:  phase1/data/ddinter_downloads_code_A.csv
Run:
    python phase1/step2b_supplement_ddinter.py

NOTE: This is completely optional. Phase 1 already passed 7/7 validation.
      Run this only if you want better severity labeling and more coverage.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from pathlib import Path

from config import CLEANED_DRUGBANK_CSV, DATA_DIR, OUTPUTS_DIR
from utils import get_logger, normalize_name, print_section

log = get_logger("step2b_ddinter")

DDINTER_FILE = DATA_DIR / "ddinter_downloads_code_A.csv"

# DDInter severity → our schema
DDINTER_SEV_MAP = {
    "Major":    "MAJOR",
    "Moderate": "MODERATE",
    "Minor":    "MINOR",
    "Unknown":  None,   # None = drop this row
}


def load_ddinter() -> pd.DataFrame:
    if not DDINTER_FILE.exists():
        log.error(f"DDInter file not found: {DDINTER_FILE}")
        log.error("Place ddinter_downloads_code_A.csv in phase1/data/ and retry.")
        sys.exit(1)

    df = pd.read_csv(DDINTER_FILE, encoding="utf-8", low_memory=False)
    log.info(f"  DDInter loaded: {len(df):,} rows")

    # Drop Unknown severity — these have no clinical value
    before = len(df)
    df = df[df["Level"] != "Unknown"].copy()
    log.info(f"  After dropping Unknown severity: {len(df):,} rows (dropped {before-len(df):,})")

    # Map severity to our standard
    df["severity"] = df["Level"].map(DDINTER_SEV_MAP)
    df = df.dropna(subset=["severity"])

    # Normalise drug names
    df["drug1_norm"] = df["Drug_A"].apply(normalize_name)
    df["drug2_norm"] = df["Drug_B"].apply(normalize_name)

    # Build pair_key (direction-agnostic)
    df["pair_key"] = df.apply(
        lambda r: "|".join(sorted([r["drug1_norm"], r["drug2_norm"]])), axis=1
    )

    # Remove self-interactions
    df = df[df["drug1_norm"] != df["drug2_norm"]].copy()

    # Select output columns — match drugbank_ddi_cleaned.csv schema
    df = df.rename(columns={"Drug_A": "drug1_name", "Drug_B": "drug2_name"})
    df["drug2_name_orig"] = df["drug2_name"]
    df["mechanism"] = df.apply(
        lambda r: f"{r['drug1_name']} and {r['drug2_name']} have a {r['Level'].lower()} drug-drug interaction (DDInter).",
        axis=1
    )
    df["interaction_type"] = df["Level"].str.lower() + " interaction"
    df["drug1_id"] = df.get("DDInterID_A", "")
    df["drug2_id"] = df.get("DDInterID_B", "")

    return df[[
        "drug1_norm", "drug2_norm", "drug1_name", "drug2_name",
        "drug1_id", "drug2_id", "severity", "mechanism",
        "interaction_type", "pair_key"
    ]]


def merge_with_existing(df_existing: pd.DataFrame, df_ddinter: pd.DataFrame) -> pd.DataFrame:
    print_section("Merging DDInter with existing DrugBank data")

    existing_keys = set(df_existing["pair_key"].tolist())
    log.info(f"  Existing DrugBank pairs  : {len(df_existing):,}")
    log.info(f"  DDInter pairs (cleaned)  : {len(df_ddinter):,}")

    # Only add DDInter rows that are NOT already in DrugBank (DrugBank takes priority)
    df_new = df_ddinter[~df_ddinter["pair_key"].isin(existing_keys)].copy()
    df_new = df_new.drop_duplicates(subset="pair_key", keep="first")
    log.info(f"  New unique pairs from DDInter: {len(df_new):,}")

    df_merged = pd.concat([df_existing, df_new], ignore_index=True)
    log.info(f"  Total after merge        : {len(df_merged):,}")

    # Re-apply AuraDB 100K DDI budget
    DDI_BUDGET = 100_000
    if len(df_merged) > DDI_BUDGET:
        log.warning(f"  Re-applying AuraDB budget ({DDI_BUDGET:,} DDI edges)...")
        sev_rank = {"MAJOR": 0, "MODERATE": 1, "MINOR": 2}
        df_merged["sev_rank"] = df_merged["severity"].map(sev_rank).fillna(1)
        df_merged = df_merged.sort_values("sev_rank")
        df_merged = df_merged.head(DDI_BUDGET)
        df_merged = df_merged.drop(columns=["sev_rank"])
        log.info(f"  After budget trim        : {len(df_merged):,}")

    sev = df_merged["severity"].value_counts()
    log.info(f"  Final severity breakdown : {sev.to_dict()}")
    return df_merged


def validate(df: pd.DataFrame):
    print_section("Re-validating key clinical interactions")
    checks = [
        ("warfarin",     "ibuprofen"),
        ("warfarin",     "acetylsalicylic acid"),
        ("warfarin",     "aspirin"),
        ("paracetamol",  "warfarin"),
        ("metformin",    "ibuprofen"),
        ("simvastatin",  "clarithromycin"),
        ("digoxin",      "amiodarone"),
    ]
    pairs = set(df["pair_key"].tolist())
    drugs = set(df["drug1_norm"].tolist()) | set(df["drug2_norm"].tolist())
    passed = 0
    for d1, d2 in checks:
        key = "|".join(sorted([d1, d2]))
        if key in pairs:
            row = df[df["pair_key"] == key].iloc[0]
            log.info(f"  PASS  {d1} + {d2} → {row['severity']}")
            passed += 1
        elif d1 in drugs and d2 in drugs:
            log.info(f"  INFO  {d1} + {d2} — both drugs present, no direct pair")
        else:
            missing = [d for d in [d1, d2] if d not in drugs]
            log.warning(f"  WARN  missing from vocab: {missing}")
    log.info(f"\n  Validation: {passed}/{len(checks)} pairs directly confirmed")


def main():
    log.info("=" * 60)
    log.info("PharmaSafe-KG  |  Phase 1  |  Step 2b: DDInter Supplement")
    log.info("=" * 60)

    # Load existing output
    if not CLEANED_DRUGBANK_CSV.exists():
        log.error("Run phase1/run_phase1.py first before this supplement.")
        sys.exit(1)

    df_existing = pd.read_csv(CLEANED_DRUGBANK_CSV, encoding="utf-8")
    log.info(f"  Loaded existing DrugBank output: {len(df_existing):,} pairs")

    # Load and clean DDInter
    df_ddinter = load_ddinter()

    # Merge
    df_final = merge_with_existing(df_existing, df_ddinter)

    # Validate
    validate(df_final)

    # Save — overwrites the existing file
    df_final.to_csv(CLEANED_DRUGBANK_CSV, index=False, encoding="utf-8")
    log.info(f"\n  Saved → {CLEANED_DRUGBANK_CSV}")
    log.info(f"  Total DDI pairs ready for Neo4j: {len(df_final):,}")
    log.info("\n  Step 2b COMPLETE. DDInter data merged successfully.")
    log.info("  Proceed to Phase 2 — Neo4j graph loading.")


if __name__ == "__main__":
    main()
