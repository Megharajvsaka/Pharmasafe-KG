"""
run_phase1.py
-------------
Runs all Phase 1 steps in sequence.
Equivalent to running steps 1, 2, and 3 individually.

Usage:
    python phase1/run_phase1.py

What it does:
    Step 1 — Load and clean Indian medicine dataset
    Step 2 — Load and clean DrugBank DDI dataset
    Step 3 — Fuzzy match generics and build master mapping table

Outputs (all in phase1/outputs/):
    indian_drugs_cleaned.csv
    drugbank_ddi_cleaned.csv
    brand_generic_map.csv
    fuzzy_matched.csv
    master_mapping_table.csv     ← this is the Neo4j input
    unmatched_generics.csv       ← review these manually
    pipeline_report.txt          ← full summary

Time estimate:
    With sample data  : ~10 seconds
    With full datasets : 3–8 minutes (fuzzy matching scales with vocab size)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time
from utils import get_logger, print_section

log = get_logger("run_phase1")


def main():
    start = time.time()

    log.info("=" * 60)
    log.info("PharmaSafe-KG — Phase 1: Data Preparation Pipeline")
    log.info("=" * 60)

    # ── Step 1: Indian medicines ──────────────────────────────────────────────
    print_section("RUNNING STEP 1 — Indian Medicine Dataset")
    from step1_load_indian_drugs import main as step1
    df_indian = step1()

    # ── Step 2: DrugBank ──────────────────────────────────────────────────────
    print_section("RUNNING STEP 2 — DrugBank DDI Dataset")
    from step2_load_drugbank import main as step2
    df_ddi = step2()

    # ── Step 3: Fuzzy matching ────────────────────────────────────────────────
    print_section("RUNNING STEP 3 — Fuzzy Matching & Master Table")
    from step3_fuzzy_match import main as step3
    step3()

    elapsed = time.time() - start
    log.info(f"\n{'=' * 60}")
    log.info(f"  Phase 1 COMPLETE in {elapsed:.1f} seconds")
    log.info(f"  Check phase1/outputs/ for all output files")
    log.info(f"  Read pipeline_report.txt for a full summary")
    log.info(f"  Review unmatched_generics.csv for manual correction")
    log.info(f"  Next: Set up .env with Neo4j credentials, then run Phase 2")
    log.info(f"{'=' * 60}")


if __name__ == "__main__":
    main()
