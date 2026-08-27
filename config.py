"""
config.py
---------
Central configuration for PharmaSafe-KG.
All file paths, thresholds, and constants live here.
Import this in every script instead of hardcoding paths.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Project root ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent

# ── Data directories ──────────────────────────────────────────────────────────
DATA_DIR    = ROOT / "phase1" / "data"
OUTPUTS_DIR = ROOT / "phase1" / "outputs"
LOGS_DIR    = ROOT / "phase1" / "logs"

# Create them if they don't exist
for d in [DATA_DIR, OUTPUTS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Input dataset paths ───────────────────────────────────────────────────────
# Place your downloaded files here:
DRUGBANK_DDI_CSV        = DATA_DIR / "drug_interactions.csv"        # from go.drugbank.com
DRUGBANK_DRUGS_CSV      = DATA_DIR / "drugs.csv"                    # from go.drugbank.com
INDIAN_MED_CSV          = DATA_DIR / "az_medicine_india.csv"        # Kaggle: shudhanshusingh
INDIAN_250K_CSV         = DATA_DIR / "medicines_250k.csv"           # Kaggle: 250K medicines

# ── Output file paths ─────────────────────────────────────────────────────────
CLEANED_INDIAN_CSV      = OUTPUTS_DIR / "indian_drugs_cleaned.csv"
CLEANED_DRUGBANK_CSV    = OUTPUTS_DIR / "drugbank_ddi_cleaned.csv"
BRAND_GENERIC_MAP_CSV   = OUTPUTS_DIR / "brand_generic_map.csv"
FUZZY_MATCHED_CSV       = OUTPUTS_DIR / "fuzzy_matched.csv"
MASTER_MAP_CSV          = OUTPUTS_DIR / "master_mapping_table.csv"
UNMATCHED_CSV           = OUTPUTS_DIR / "unmatched_generics.csv"
PIPELINE_REPORT         = OUTPUTS_DIR / "pipeline_report.txt"

# ── NLP / scispaCy model ──────────────────────────────────────────────────────
SCISPACY_MODEL          = "en_ner_bc5cdr_md"   # trained on BC5CDR (chemicals + diseases)

# ── Fuzzy matching thresholds ─────────────────────────────────────────────────
FUZZY_HIGH_THRESHOLD    = 90   # auto-accept match
FUZZY_MED_THRESHOLD     = 75   # accept but flag for review
FUZZY_LOW_THRESHOLD     = 60   # reject (too uncertain)

# ── Neo4j (loaded from .env — never hardcode credentials) ────────────────────
NEO4J_URI      = os.getenv("NEO4J_URI",  "neo4j+s://xxxxxxxx.databases.neo4j.io")
NEO4J_USER     = os.getenv("NEO4J_USER") or os.getenv("NEO4J_USERNAME") or "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

# ── AuraDB free-tier limits (safety caps) ────────────────────────────────────
AURA_MAX_NODES         = 50_000
AURA_MAX_RELATIONSHIPS = 175_000

# ── DrugBank severity mapping ─────────────────────────────────────────────────
SEVERITY_MAP = {
    "major":    "MAJOR",
    "moderate": "MODERATE",
    "minor":    "MINOR",
    "n/a":      "UNKNOWN",
    "":         "UNKNOWN",
}

# ── Column names expected in raw datasets ────────────────────────────────────
# DrugBank drug_interactions.csv columns
DB_COL_DRUG1   = "Drug1"
DB_COL_DRUG2   = "Drug2"
DB_COL_DESC    = "Description"
DB_COL_SEV     = "Severity"

# Indian medicine CSV columns (Kaggle AZ dataset)
IND_COL_BRAND  = "name"
IND_COL_COMP   = "short_composition1"   # primary composition column
IND_COL_COMP2  = "short_composition2"   # some entries split across two
IND_COL_MFR    = "manufacturer_name"
IND_COL_TYPE   = "type"
IND_COL_PRICE  = "price(Rs)"
