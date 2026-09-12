"""
run_phase2.py
-------------
Master runner for Phase 2 — Neo4j Knowledge Graph Construction.

Runs all 5 steps in sequence:
    Step 1 — Create schema (constraints + indexes)
    Step 2 — Load Ingredient nodes  (generic drug names)
    Step 3 — Load INTERACTS_WITH edges  (DDI relationships)
    Step 4 — Load Drug nodes + CONTAINS edges  (Indian brands)
    Step 5 — Validate graph with test Cypher queries

Prerequisites:
    1. Phase 1 complete  (phase1/outputs/ must exist)
    2. Neo4j AuraDB free instance created at console.neo4j.io
    3. .env file has NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

Usage:
    python phase2/run_phase2.py

Time estimate: 5–15 minutes depending on internet speed to AuraDB.
"""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils_phase2 import get_logger, print_section

log = get_logger("run_phase2")


def main():
    start = time.time()
    log.info("=" * 60)
    log.info("PharmaSafe-KG — Phase 2: Knowledge Graph Construction")
    log.info("=" * 60)

    print_section("STEP 1 — Schema (constraints + indexes)")
    from step1_create_schema import main as s1
    s1()

    print_section("STEP 2 — Load Ingredient nodes")
    from step2_load_ingredients import main as s2
    s2()

    print_section("STEP 3 — Load INTERACTS_WITH edges")
    from step3_load_interactions import main as s3
    s3()

    print_section("STEP 4 — Load Drug nodes + CONTAINS edges")
    from step4_load_drugs import main as s4
    s4()

    print_section("STEP 5 — Validate graph")
    from step5_validate import main as s5
    s5()

    elapsed = time.time() - start
    log.info("=" * 60)
    log.info(f"Phase 2 COMPLETE in {elapsed:.1f} seconds")
    log.info("Open Neo4j Browser at console.neo4j.io to visualise the graph")
    log.info("Next: Phase 3 — FastAPI backend")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
