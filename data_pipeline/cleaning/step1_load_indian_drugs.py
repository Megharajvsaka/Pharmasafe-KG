"""
step1_load_indian_drugs.py
--------------------------
Phase 1 — Task 1b & 1d
Loads the Kaggle Indian Medicine Dataset, cleans it, and extracts
generic ingredient names from the composition column.

Input files  (place in phase1/data/):
    az_medicine_india.csv    — Kaggle: AZ Medicine Dataset of India
    medicines_250k.csv       — Kaggle: 250K Medicines Usage, Side Effects

Output files (written to phase1/outputs/):
    indian_drugs_cleaned.csv — cleaned, deduplicated Indian drug records

Run:
    python phase1/step1_load_indian_drugs.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import re
from pathlib import Path
from tqdm import tqdm

from config import (
    INDIAN_MED_CSV, INDIAN_250K_CSV, CLEANED_INDIAN_CSV,
    IND_COL_BRAND, IND_COL_COMP, IND_COL_COMP2,
    IND_COL_MFR, IND_COL_TYPE, IND_COL_PRICE,
    PIPELINE_REPORT,
)
from utils import get_logger, extract_generics_from_composition, print_section, write_report

log = get_logger("step1_indian")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1A — Load raw CSV files
# ─────────────────────────────────────────────────────────────────────────────
def load_raw_datasets() -> pd.DataFrame:
    """
    Loads the AZ Medicine dataset and (optionally) the 250K dataset.
    Merges them into one DataFrame.

    The Kaggle AZ Medicine dataset has these key columns:
        name                — brand name  (e.g., "Dolo 650 Tablet")
        short_composition1  — primary active ingredient (e.g., "Paracetamol 650mg")
        short_composition2  — secondary ingredient if applicable
        manufacturer_name   — e.g., "Micro Labs Ltd"
        type                — "allopathy", "ayurvedic", etc.
        price(Rs)           — price in rupees
    """
    print_section("STEP 1 — Loading Indian Medicine Datasets")

    frames = []

    # ── Primary dataset: AZ Medicine India ───────────────────────────────────
    if INDIAN_MED_CSV.exists():
        log.info(f"Loading AZ Medicine dataset: {INDIAN_MED_CSV}")
        try:
            df_az = pd.read_csv(INDIAN_MED_CSV, encoding="utf-8", low_memory=False)
            log.info(f"  AZ dataset loaded: {len(df_az):,} rows, columns: {list(df_az.columns)}")
            frames.append(df_az)
        except Exception as e:
            log.error(f"  Failed to load AZ dataset: {e}")
    else:
        log.warning(f"  AZ Medicine CSV not found at {INDIAN_MED_CSV}")
        log.warning("  Download from: https://www.kaggle.com/datasets/shudhanshusingh/az-medicine-dataset-of-india")
        log.warning("  Generating a SAMPLE dataset for testing purposes...")
        frames.append(_generate_sample_indian_dataset())

    # ── Secondary dataset: 250K Medicines ────────────────────────────────────
    if INDIAN_250K_CSV.exists():
        log.info(f"Loading 250K dataset: {INDIAN_250K_CSV}")
        try:
            df_250k = pd.read_csv(INDIAN_250K_CSV, encoding="utf-8", low_memory=False)
            log.info(f"  250K dataset loaded: {len(df_250k):,} rows")
            # Rename columns to match AZ schema if needed
            df_250k = _harmonise_250k_columns(df_250k)
            frames.append(df_250k)
        except Exception as e:
            log.warning(f"  Could not load 250K dataset: {e} — skipping.")

    if not frames:
        log.error("No Indian medicine datasets found. Check phase1/data/ directory.")
        sys.exit(1)

    # Combine all frames
    combined = pd.concat(frames, ignore_index=True)
    log.info(f"Combined total: {len(combined):,} rows before deduplication")
    return combined


def _harmonise_250k_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    The 250K Kaggle dataset may use different column names.
    This maps them to the standard schema we use throughout.
    """
    rename_map = {
        "Drug_Name":        IND_COL_BRAND,
        "drug_name":        IND_COL_BRAND,
        "Medicine Name":    IND_COL_BRAND,
        "Composition":      IND_COL_COMP,
        "composition":      IND_COL_COMP,
        "Salt Composition": IND_COL_COMP,
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    return df


def _generate_sample_indian_dataset() -> pd.DataFrame:
    """
    Generates a realistic sample dataset (100 drugs) for testing the pipeline
    when the real Kaggle file has not been downloaded yet.
    """
    log.info("  Generating 100-row sample Indian medicine dataset for testing...")
    sample_data = [
        ("Dolo 650 Tablet",        "Paracetamol 650mg",                          "",                        "Micro Labs Ltd",        "allopathy", 30),
        ("Combiflam Tablet",       "Ibuprofen 400mg + Paracetamol 325mg",         "",                        "Sanofi India Ltd",      "allopathy", 28),
        ("Ecosprin 75 Tablet",     "Aspirin 75mg",                                "",                        "USV Pvt Ltd",           "allopathy", 12),
        ("Crocin 500 Tablet",      "Paracetamol 500mg",                           "",                        "GSK Pharmaceuticals",   "allopathy", 25),
        ("Augmentin 625 Tablet",   "Amoxicillin 500mg + Clavulanic Acid 125mg",   "",                        "GSK Pharmaceuticals",   "allopathy", 185),
        ("Metformin 500 Tablet",   "Metformin Hydrochloride 500mg",               "",                        "Sun Pharma",            "allopathy", 20),
        ("Pantop 40 Tablet",       "Pantoprazole 40mg",                           "",                        "Aristo Pharmaceuticals","allopathy", 45),
        ("Atorva 10 Tablet",       "Atorvastatin 10mg",                           "",                        "Sun Pharma",            "allopathy", 65),
        ("Telma 40 Tablet",        "Telmisartan 40mg",                            "",                        "Glenmark Pharmaceuticals","allopathy", 72),
        ("Shelcal 500 Tablet",     "Calcium Carbonate 1250mg + Vitamin D3 250IU", "",                        "Elder Pharmaceuticals", "allopathy", 90),
        ("Azithral 500 Tablet",    "Azithromycin 500mg",                          "",                        "Alembic Pharmaceuticals","allopathy", 95),
        ("Nise Tablet",            "Nimesulide 100mg",                            "",                        "Dr Reddy Laboratories", "allopathy", 32),
        ("Volini Gel",             "Diclofenac Diethylamine 1.16% + Methyl Salicylate 10% + Menthol 5% + Benzyl Alcohol 1%", "", "Ranbaxy", "allopathy", 145),
        ("Glucobay 50 Tablet",     "Acarbose 50mg",                               "",                        "Bayer Zydus",           "allopathy", 280),
        ("Glycomet 500 SR Tablet", "Metformin Hydrochloride 500mg",               "",                        "USV Pvt Ltd",           "allopathy", 35),
        ("Warfarin 5mg Tablet",    "Warfarin Sodium 5mg",                         "",                        "Cipla Ltd",             "allopathy", 55),
        ("Plavix 75 Tablet",       "Clopidogrel 75mg",                            "",                        "Sanofi India Ltd",      "allopathy", 220),
        ("Amlodac 5 Tablet",       "Amlodipine 5mg",                              "",                        "Zydus Cadila",          "allopathy", 42),
        ("Loprin 75 Tablet",       "Aspirin 75mg",                                "",                        "Zydus Cadila",          "allopathy", 10),
        ("Metolar XR 25 Tablet",   "Metoprolol Succinate 25mg",                   "",                        "Sun Pharma",            "allopathy", 88),
        ("Atorlip 20 Tablet",      "Atorvastatin 20mg",                           "",                        "Cipla Ltd",             "allopathy", 105),
        ("Digoxin 0.25 Tablet",    "Digoxin 0.25mg",                              "",                        "Neon Laboratories",     "allopathy", 22),
        ("Lanoxin 0.25 Tablet",    "Digoxin 0.25mg",                              "",                        "GSK Pharmaceuticals",   "allopathy", 28),
        ("Furesimide 40 Tablet",   "Furosemide 40mg",                             "",                        "Intas Pharmaceuticals", "allopathy", 8),
        ("Lasix 40 Tablet",        "Furosemide 40mg",                             "",                        "Sanofi India Ltd",      "allopathy", 15),
        ("Spironolactone 25 Tab",  "Spironolactone 25mg",                         "",                        "Sun Pharma",            "allopathy", 18),
        ("Aldactone 25 Tablet",    "Spironolactone 25mg",                         "",                        "Pfizer Ltd",            "allopathy", 25),
        ("Lisinopril 5 Tablet",    "Lisinopril 5mg",                              "",                        "Sun Pharma",            "allopathy", 35),
        ("Zestril 5 Tablet",       "Lisinopril 5mg",                              "",                        "AstraZeneca",           "allopathy", 48),
        ("Ramipril 5 Tablet",      "Ramipril 5mg",                                "",                        "Cipla Ltd",             "allopathy", 55),
        ("Cardace 5 Tablet",       "Ramipril 5mg",                                "",                        "Sanofi India Ltd",      "allopathy", 62),
        ("Losartan 50 Tablet",     "Losartan Potassium 50mg",                     "",                        "Sun Pharma",            "allopathy", 42),
        ("Repace 50 Tablet",       "Losartan Potassium 50mg",                     "",                        "Sun Pharma",            "allopathy", 55),
        ("Ciprofloxacin 500 Tab",  "Ciprofloxacin 500mg",                         "",                        "Cipla Ltd",             "allopathy", 65),
        ("Ciplox 500 Tablet",      "Ciprofloxacin 500mg",                         "",                        "Cipla Ltd",             "allopathy", 72),
        ("Amoxicillin 500 Capsule","Amoxicillin 500mg",                           "",                        "Cipla Ltd",             "allopathy", 55),
        ("Mox 500 Capsule",        "Amoxicillin 500mg",                           "",                        "Ranbaxy",               "allopathy", 60),
        ("Paracip 500 Tablet",     "Paracetamol 500mg",                           "",                        "Cipla Ltd",             "allopathy", 22),
        ("Calpol 500 Tablet",      "Paracetamol 500mg",                           "",                        "GSK Pharmaceuticals",   "allopathy", 26),
        ("Omnacortil 5 Tablet",    "Prednisolone 5mg",                            "",                        "Macleods Pharmaceuticals","allopathy", 18),
        ("Wysolone 5 Tablet",      "Prednisolone 5mg",                            "",                        "Pfizer Ltd",            "allopathy", 22),
        ("Dexona 0.5 Tablet",      "Dexamethasone 0.5mg",                         "",                        "Samarth Pharma",        "allopathy", 12),
        ("Decadron 0.5 Tablet",    "Dexamethasone 0.5mg",                         "",                        "MSD Pharmaceuticals",   "allopathy", 18),
        ("Thyronorm 25 Tablet",    "Levothyroxine Sodium 25mcg",                  "",                        "Abbott India",          "allopathy", 45),
        ("Eltroxin 50 Tablet",     "Levothyroxine Sodium 50mcg",                  "",                        "GSK Pharmaceuticals",   "allopathy", 52),
        ("Januvia 100 Tablet",     "Sitagliptin 100mg",                           "",                        "MSD Pharmaceuticals",   "allopathy", 540),
        ("Galvus 50 Tablet",       "Vildagliptin 50mg",                           "",                        "Novartis India",        "allopathy", 380),
        ("Glipizide 5 Tablet",     "Glipizide 5mg",                               "",                        "Pfizer Ltd",            "allopathy", 45),
        ("Glucotrol 5 Tablet",     "Glipizide 5mg",                               "",                        "Pfizer Ltd",            "allopathy", 52),
        ("Glibenclamide 5 Tab",    "Glibenclamide 5mg",                           "",                        "Sun Pharma",            "allopathy", 18),
        ("Daonil 5 Tablet",        "Glibenclamide 5mg",                           "",                        "Sanofi India Ltd",      "allopathy", 22),
        ("Pioglitazone 15 Tablet", "Pioglitazone 15mg",                           "",                        "Sun Pharma",            "allopathy", 55),
        ("Actos 15 Tablet",        "Pioglitazone 15mg",                           "",                        "Eli Lilly",             "allopathy", 75),
        ("Insulin Glargine Inj",   "Insulin Glargine 100IU/ml",                   "",                        "Sanofi India Ltd",      "allopathy", 1200),
        ("Lantus Solostar Pen",    "Insulin Glargine 100IU/ml",                   "",                        "Sanofi India Ltd",      "allopathy", 1350),
        ("Omeprazole 20 Capsule",  "Omeprazole 20mg",                             "",                        "Cipla Ltd",             "allopathy", 38),
        ("Omez 20 Capsule",        "Omeprazole 20mg",                             "",                        "Dr Reddy Laboratories", "allopathy", 45),
        ("Pantocid 40 Tablet",     "Pantoprazole 40mg",                           "",                        "Sun Pharma",            "allopathy", 52),
        ("Pan D Capsule",          "Pantoprazole 40mg + Domperidone 10mg",        "",                        "Sun Pharma",            "allopathy", 68),
        ("Rabeprazole 20 Tablet",  "Rabeprazole Sodium 20mg",                     "",                        "Cipla Ltd",             "allopathy", 72),
        ("Razo 20 Tablet",         "Rabeprazole Sodium 20mg",                     "",                        "Dr Reddy Laboratories", "allopathy", 88),
        ("Metrogyl 400 Tablet",    "Metronidazole 400mg",                         "",                        "J.B. Chemicals",        "allopathy", 35),
        ("Flagyl 400 Tablet",      "Metronidazole 400mg",                         "",                        "Sanofi India Ltd",      "allopathy", 42),
        ("Tinidazole 500 Tablet",  "Tinidazole 500mg",                            "",                        "Cipla Ltd",             "allopathy", 38),
        ("Tiniba 500 Tablet",      "Tinidazole 500mg",                            "",                        "Zydus Cadila",          "allopathy", 42),
        ("Norfloxacin 400 Tablet", "Norfloxacin 400mg",                           "",                        "Cipla Ltd",             "allopathy", 55),
        ("Norflox 400 Tablet",     "Norfloxacin 400mg",                           "",                        "Torrent Pharmaceuticals","allopathy", 62),
        ("Cefixime 200 Tablet",    "Cefixime 200mg",                              "",                        "Alembic Pharmaceuticals","allopathy", 125),
        ("Taxim-O 200 Tablet",     "Cefixime 200mg",                              "",                        "Alkem Laboratories",    "allopathy", 142),
        ("Voveran 50 Tablet",      "Diclofenac Sodium 50mg",                      "",                        "Novartis India",        "allopathy", 28),
        ("Diclofenac 50 Tablet",   "Diclofenac Sodium 50mg",                      "",                        "Cipla Ltd",             "allopathy", 22),
        ("Celebrex 100 Capsule",   "Celecoxib 100mg",                             "",                        "Pfizer Ltd",            "allopathy", 185),
        ("Hifenac 100 Tablet",     "Aceclofenac 100mg",                           "",                        "Intas Pharmaceuticals", "allopathy", 72),
        ("Zerodol 100 Tablet",     "Aceclofenac 100mg",                           "",                        "Ipca Laboratories",     "allopathy", 68),
        ("Tramadol 50 Capsule",    "Tramadol Hydrochloride 50mg",                 "",                        "Sun Pharma",            "allopathy", 55),
        ("Contramal 50 Capsule",   "Tramadol Hydrochloride 50mg",                 "",                        "Novartis India",        "allopathy", 62),
        ("Roxithromycin 150 Tab",  "Roxithromycin 150mg",                         "",                        "Cipla Ltd",             "allopathy", 88),
        ("Roxid 150 Tablet",       "Roxithromycin 150mg",                         "",                        "Alembic Pharmaceuticals","allopathy", 95),
        ("Clindamycin 300 Cap",    "Clindamycin 300mg",                           "",                        "Cipla Ltd",             "allopathy", 142),
        ("Dalacin C 300 Capsule",  "Clindamycin 300mg",                           "",                        "Pfizer Ltd",            "allopathy", 165),
        ("Doxycycline 100 Cap",    "Doxycycline Monohydrate 100mg",               "",                        "Cipla Ltd",             "allopathy", 78),
        ("Doxt-SL Capsule",        "Doxycycline 100mg + Lactobacillus 5B",        "",                        "Sun Pharma",            "allopathy", 125),
        ("Cetirizine 10 Tablet",   "Cetirizine Hydrochloride 10mg",               "",                        "Cipla Ltd",             "allopathy", 18),
        ("Okacet 10 Tablet",       "Cetirizine Hydrochloride 10mg",               "",                        "Cipla Ltd",             "allopathy", 22),
        ("Loratadine 10 Tablet",   "Loratadine 10mg",                             "",                        "Sun Pharma",            "allopathy", 28),
        ("Lorfast 10 Tablet",      "Loratadine 10mg",                             "",                        "Wockhardt Ltd",         "allopathy", 35),
        ("Montair 10 Tablet",      "Montelukast 10mg",                            "",                        "Cipla Ltd",             "allopathy", 185),
        ("Singulair 10 Tablet",    "Montelukast 10mg",                            "",                        "MSD Pharmaceuticals",   "allopathy", 220),
        ("Zyrtec 10 Tablet",       "Cetirizine 10mg",                             "",                        "McNeil Consumer",       "allopathy", 25),
        ("Levocetirizine 5 Tab",   "Levocetirizine 5mg",                          "",                        "Cipla Ltd",             "allopathy", 28),
        ("Xyzal 5 Tablet",         "Levocetirizine 5mg",                          "",                        "GSK Pharmaceuticals",   "allopathy", 38),
        ("Phenytoin 100 Tablet",   "Phenytoin Sodium 100mg",                      "",                        "Sun Pharma",            "allopathy", 18),
        ("Eptoin 100 Tablet",      "Phenytoin Sodium 100mg",                      "",                        "Abbott India",          "allopathy", 22),
        ("Carbamazepine 200 Tab",  "Carbamazepine 200mg",                         "",                        "Sun Pharma",            "allopathy", 28),
        ("Tegrital 200 Tablet",    "Carbamazepine 200mg",                         "",                        "Novartis India",        "allopathy", 35),
        ("Valproate 500 Tablet",   "Sodium Valproate 500mg",                      "",                        "Sanofi India Ltd",      "allopathy", 55),
        ("Valparin 500 Tablet",    "Sodium Valproate 500mg",                      "",                        "Torrent Pharmaceuticals","allopathy", 62),
        ("Alprazolam 0.25 Tablet", "Alprazolam 0.25mg",                           "",                        "Cipla Ltd",             "allopathy", 8),
        ("Alprax 0.25 Tablet",     "Alprazolam 0.25mg",                           "",                        "Sun Pharma",            "allopathy", 10),
        ("Clonazepam 0.5 Tablet",  "Clonazepam 0.5mg",                            "",                        "Sun Pharma",            "allopathy", 12),
        ("Clonotril 0.5 Tablet",   "Clonazepam 0.5mg",                            "",                        "Torrent Pharmaceuticals","allopathy", 15),
    ]

    df = pd.DataFrame(sample_data, columns=[
        IND_COL_BRAND, IND_COL_COMP, IND_COL_COMP2,
        IND_COL_MFR, IND_COL_TYPE, IND_COL_PRICE
    ])
    log.info(f"  Sample dataset created: {len(df)} rows")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1B — Clean and filter the combined dataset
# ─────────────────────────────────────────────────────────────────────────────
def clean_indian_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the combined Indian medicine dataset:
    1. Keeps only allopathic drugs (excludes Ayurvedic, Homeopathic)
    2. Drops rows with no brand name or no composition
    3. Normalises the brand name column
    4. Combines composition columns 1 and 2
    5. Deduplicates by (brand_name, composition)
    """
    print_section("STEP 1 — Cleaning Indian Drug Dataset")
    initial_count = len(df)
    log.info(f"Initial row count: {initial_count:,}")

    # ── Ensure required columns exist ────────────────────────────────────────
    for col in [IND_COL_BRAND, IND_COL_COMP]:
        if col not in df.columns:
            # Try case-insensitive match
            matches = [c for c in df.columns if c.lower() == col.lower()]
            if matches:
                df = df.rename(columns={matches[0]: col})
                log.info(f"  Renamed column '{matches[0]}' → '{col}'")
            else:
                log.error(f"  Required column '{col}' not found. Available: {list(df.columns)}")
                sys.exit(1)

    # ── Filter: allopathic drugs only ────────────────────────────────────────
    if IND_COL_TYPE in df.columns:
        before = len(df)
        df = df[df[IND_COL_TYPE].str.lower().str.contains("allopathy|allopathic", na=True)]
        log.info(f"  Allopathic filter: {before:,} → {len(df):,} rows (removed {before - len(df):,} non-allopathic)")

    # ── Drop rows with no brand name ─────────────────────────────────────────
    df = df.dropna(subset=[IND_COL_BRAND])
    df = df[df[IND_COL_BRAND].str.strip() != ""]
    log.info(f"  After removing missing brand names: {len(df):,} rows")

    # ── Drop rows with no composition ────────────────────────────────────────
    df = df.dropna(subset=[IND_COL_COMP])
    df = df[df[IND_COL_COMP].str.strip() != ""]
    log.info(f"  After removing missing compositions: {len(df):,} rows")

    # ── Combine composition columns ──────────────────────────────────────────
    if IND_COL_COMP2 in df.columns:
        df["full_composition"] = df.apply(
            lambda r: (str(r[IND_COL_COMP]) + " + " + str(r[IND_COL_COMP2])).strip(" +").strip()
            if pd.notna(r.get(IND_COL_COMP2)) and str(r.get(IND_COL_COMP2, "")).strip()
            else str(r[IND_COL_COMP]),
            axis=1
        )
    else:
        df["full_composition"] = df[IND_COL_COMP].astype(str)

    # ── Normalise brand name: strip trailing dosage form words ───────────────
    df["brand_name_clean"] = (
        df[IND_COL_BRAND]
        .str.strip()
        .str.replace(r'\s+(tablet|tab|capsule|cap|syrup|inj|injection|cream|gel|drop|solution|sachet)s?$', '',
                     case=False, regex=True)
        .str.strip()
    )

    # ── Select and rename output columns ─────────────────────────────────────
    keep_cols = {
        "brand_name_clean": "brand_name",
        "full_composition": "composition",
    }
    if IND_COL_MFR in df.columns:
        keep_cols[IND_COL_MFR] = "manufacturer"
    if IND_COL_PRICE in df.columns:
        keep_cols[IND_COL_PRICE] = "price_rs"
    if IND_COL_TYPE in df.columns:
        keep_cols[IND_COL_TYPE] = "drug_type"

    df = df[list(keep_cols.keys())].rename(columns=keep_cols)

    # ── Deduplicate ───────────────────────────────────────────────────────────
    before = len(df)
    df = df.drop_duplicates(subset=["brand_name", "composition"])
    log.info(f"  After deduplication: {before:,} → {len(df):,} rows (removed {before - len(df):,} duplicates)")

    log.info(f"  Cleaning complete. Final row count: {len(df):,}")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1C — Extract generic ingredient names from composition column
# ─────────────────────────────────────────────────────────────────────────────
def extract_generics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies the composition parser to every row.
    Adds a 'generics' column (list of strings) and a
    'generics_str' column (pipe-separated string for CSV storage).

    Example:
        composition: "Ibuprofen (400mg) + Paracetamol (325mg)"
        generics:    ["ibuprofen", "paracetamol"]
        generics_str: "ibuprofen|paracetamol"
    """
    print_section("STEP 1 — Extracting Generic Ingredients")

    tqdm.pandas(desc="  Parsing compositions")
    df["generics"] = df["composition"].progress_apply(extract_generics_from_composition)
    df["generics_str"] = df["generics"].apply(lambda lst: "|".join(lst))
    df["num_generics"] = df["generics"].apply(len)

    # ── Statistics ────────────────────────────────────────────────────────────
    total         = len(df)
    has_generics  = (df["num_generics"] > 0).sum()
    no_generics   = (df["num_generics"] == 0).sum()
    combo_drugs   = (df["num_generics"] > 1).sum()
    single_drugs  = (df["num_generics"] == 1).sum()

    log.info(f"  Total rows processed  : {total:,}")
    log.info(f"  Rows with generics    : {has_generics:,}")
    log.info(f"  Rows with NO generics : {no_generics:,}  ← will be excluded from graph")
    log.info(f"  Single-ingredient     : {single_drugs:,}")
    log.info(f"  Combination drugs     : {combo_drugs:,}")

    # Drop rows where we couldn't extract any generic
    df = df[df["num_generics"] > 0].copy()
    log.info(f"  After dropping empty-generic rows: {len(df):,}")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("PharmaSafe-KG  |  Phase 1  |  Step 1: Indian Drug Dataset")
    log.info("=" * 60)

    # Load
    df_raw = load_raw_datasets()

    # Clean
    df_clean = clean_indian_dataset(df_raw)

    # Extract generics
    df_with_generics = extract_generics(df_clean)

    # Save
    df_with_generics.drop(columns=["generics"], inplace=True)  # lists can't go in CSV
    df_with_generics.to_csv(CLEANED_INDIAN_CSV, index=False, encoding="utf-8")
    log.info(f"\n  Saved → {CLEANED_INDIAN_CSV}")
    log.info(f"  Rows: {len(df_with_generics):,}")

    # Preview
    print_section("PREVIEW — First 5 rows of cleaned Indian dataset")
    print(df_with_generics[["brand_name", "composition", "generics_str"]].head(5).to_string(index=False))

    log.info("\n  Step 1 COMPLETE. Proceed to step2_load_drugbank.py")
    return df_with_generics


if __name__ == "__main__":
    main()
