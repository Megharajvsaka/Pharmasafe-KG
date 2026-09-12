"""
config.py
---------
Configuration for PharmaSafe-KG Data Pipeline.
All data paths, thresholds, and constants live here.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project root & data pipeline root
ROOT = Path(__file__).resolve().parent.parent
PIPELINE_ROOT = ROOT / "data_pipeline"

# Data directories
DATA_DIR    = PIPELINE_ROOT / "data"
OUTPUTS_DIR = PIPELINE_ROOT / "outputs"
LOGS_DIR    = PIPELINE_ROOT / "logs"

for d in [DATA_DIR, OUTPUTS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Input dataset paths
DRUGBANK_DDI_CSV        = DATA_DIR / "drug_interactions.csv"
DRUGBANK_DRUGS_CSV      = DATA_DIR / "drugs.csv"
INDIAN_MED_CSV          = DATA_DIR / "az_medicine_india.csv"
INDIAN_250K_CSV         = DATA_DIR / "medicines_250k.csv"

# Output file paths
CLEANED_INDIAN_CSV      = OUTPUTS_DIR / "indian_drugs_cleaned.csv"
CLEANED_DRUGBANK_CSV    = OUTPUTS_DIR / "drugbank_ddi_cleaned.csv"
BRAND_GENERIC_MAP_CSV   = OUTPUTS_DIR / "brand_generic_map.csv"
FUZZY_MATCHED_CSV       = OUTPUTS_DIR / "fuzzy_matched.csv"
MASTER_MAP_CSV          = OUTPUTS_DIR / "master_mapping_table.csv"
UNMATCHED_CSV           = OUTPUTS_DIR / "unmatched_generics.csv"
PIPELINE_REPORT         = OUTPUTS_DIR / "pipeline_report.txt"

# NLP / scispaCy model
SCISPACY_MODEL          = "en_ner_bc5cdr_md"

# Fuzzy matching thresholds
FUZZY_HIGH_THRESHOLD    = 90
FUZZY_MED_THRESHOLD     = 75
FUZZY_LOW_THRESHOLD     = 60

# Severity mapping
SEVERITY_MAP = {
    "major":    "MAJOR",
    "moderate": "MODERATE",
    "minor":    "MINOR",
    "n/a":      "UNKNOWN",
    "":         "UNKNOWN",
}

# Column names expected in raw datasets
DB_COL_DRUG1   = "Drug1"
DB_COL_DRUG2   = "Drug2"
DB_COL_DESC    = "Description"
DB_COL_SEV     = "Severity"

IND_COL_BRAND  = "name"
IND_COL_COMP   = "short_composition1"
IND_COL_COMP2  = "short_composition2"
IND_COL_MFR    = "manufacturer_name"
IND_COL_TYPE   = "type"
IND_COL_PRICE  = "price(Rs)"
