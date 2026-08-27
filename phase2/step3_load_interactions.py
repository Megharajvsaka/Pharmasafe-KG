"""
step3_load_interactions.py
---------------------------
Phase 2 — Step 3
Loads all INTERACTS_WITH relationships between Ingredient nodes.

This is the core of the Knowledge Graph — every DDI pair becomes
a directed edge with clinical metadata as properties.

Source: phase1/outputs/drugbank_ddi_cleaned.csv  (100,000 rows)

Each INTERACTS_WITH edge has properties:
    severity         — "MAJOR" | "MODERATE" | "MINOR"
    mechanism        — plain-English description of why interaction occurs
    interaction_type — raw type string from source dataset
    source           — "drugbank" | "ddinter"
    pair_key         — canonical sorted key for deduplication

Edge direction:
    (a)-[:INTERACTS_WITH]->(b)  where a < b alphabetically
    This is direction-agnostic — queries check both (a→b) and (b→a)

IMPORTANT — AuraDB free tier:
    This step loads 100,000 edges.
    AuraDB free tier allows 175,000 total relationships.
    After this step: ~100,000 of 175,000 used.
    Remaining budget for CONTAINS edges: ~75,000

Run:
    python phase2/step3_load_interactions.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv
from tqdm import tqdm
from pathlib import Path

from utils_phase2 import get_logger, print_section, batch

load_dotenv()
log = get_logger("step3_interactions")

NEO4J_URI      = os.getenv("NEO4J_URI")
NEO4J_USER     = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

ROOT           = Path(__file__).parent.parent
DRUGBANK_CSV   = ROOT / "phase1" / "outputs" / "drugbank_ddi_cleaned.csv"

# Batch size — 500 is optimal for AuraDB free tier over internet
BATCH_SIZE = 500


def get_driver():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    driver.verify_connectivity()
    return driver


def prepare_edge_records(df: pd.DataFrame) -> list[dict]:
    """
    Converts the DDI DataFrame into a list of edge records
    ready for the Cypher UNWIND statement.

    Truncates mechanism text to 500 chars to stay within
    Neo4j property size limits cleanly.
    """
    records = []
    for _, row in df.iterrows():
        mechanism = str(row.get("mechanism", "")).strip()
        if len(mechanism) > 500:
            mechanism = mechanism[:497] + "..."

        records.append({
            "drug1":            str(row["drug1_norm"]).strip(),
            "drug2":            str(row["drug2_norm"]).strip(),
            "severity":         str(row.get("severity", "MODERATE")).strip(),
            "mechanism":        mechanism,
            "interaction_type": str(row.get("interaction_type", "")).strip()[:200],
            "pair_key":         str(row.get("pair_key", "")).strip(),
        })

    # Remove any rows where either drug name is blank
    records = [r for r in records if r["drug1"] and r["drug2"]]
    return records


def load_interactions(driver, records: list[dict]) -> dict:
    """
    Loads INTERACTS_WITH edges in batches.

    Uses MERGE on the pair_key property to prevent duplicate edges
    if the script is re-run.

    The Cypher query:
    1. Finds both Ingredient nodes by name
    2. Creates the INTERACTS_WITH edge with all properties
    3. Skips if both nodes don't exist (MATCH not MERGE on nodes)
    """
    CYPHER = """
    UNWIND $rows AS row
    MATCH (a:Ingredient {name: row.drug1})
    MATCH (b:Ingredient {name: row.drug2})
    MERGE (a)-[r:INTERACTS_WITH {pair_key: row.pair_key}]->(b)
    ON CREATE SET
        r.severity         = row.severity,
        r.mechanism        = row.mechanism,
        r.interaction_type = row.interaction_type,
        r.created_at       = datetime()
    ON MATCH SET
        r.severity         = row.severity,
        r.mechanism        = row.mechanism
    """

    stats = {"loaded": 0, "skipped_no_nodes": 0}
    batches = list(batch(records, BATCH_SIZE))

    with driver.session() as session:
        for b in tqdm(batches, desc="  Loading INTERACTS_WITH edges"):
            result = session.run(CYPHER, rows=b)
            summary = result.consume()
            stats["loaded"] += summary.counters.relationships_created + summary.counters.properties_set // 3

    return stats


def main():
    log.info("=" * 60)
    log.info("PharmaSafe-KG  |  Phase 2  |  Step 3: DDI Edges")
    log.info("=" * 60)

    if not DRUGBANK_CSV.exists():
        log.error(f"Missing: {DRUGBANK_CSV}. Run Phase 1 first.")
        sys.exit(1)

    df = pd.read_csv(DRUGBANK_CSV, encoding="utf-8")
    log.info(f"  Loaded {len(df):,} DDI pairs")

    # Severity breakdown before loading
    sev = df["severity"].value_counts().to_dict()
    log.info(f"  Severity breakdown: {sev}")

    # Prepare
    print_section("Preparing edge records")
    records = prepare_edge_records(df)
    log.info(f"  Valid edge records prepared: {len(records):,}")

    # Connect
    driver = get_driver()
    log.info("  Connected to Neo4j AuraDB")

    # Load
    print_section("Loading INTERACTS_WITH edges (this takes 2–5 minutes)")
    log.info(f"  Batch size: {BATCH_SIZE} | Total batches: {len(records)//BATCH_SIZE + 1}")
    stats = load_interactions(driver, records)

    # Verify
    print_section("Verifying edge counts in Neo4j")
    with driver.session() as session:
        # Total edges
        total = session.run("MATCH ()-[r:INTERACTS_WITH]->() RETURN count(r) AS cnt").single()["cnt"]
        log.info(f"  Total INTERACTS_WITH edges in graph: {total:,}")

        # Severity breakdown in graph
        sev_result = session.run("""
            MATCH ()-[r:INTERACTS_WITH]->()
            RETURN r.severity AS sev, count(r) AS cnt
            ORDER BY cnt DESC
        """)
        log.info("  Severity distribution in graph:")
        for r in sev_result:
            log.info(f"    {r['sev']:10s}: {r['cnt']:,}")

        # Test query: warfarin interactions
        warfarin = list(session.run("""
            MATCH (a:Ingredient {name: 'warfarin'})-[r:INTERACTS_WITH]-(b:Ingredient)
            RETURN b.name AS drug, r.severity AS sev
            ORDER BY
              CASE r.severity WHEN 'MAJOR' THEN 0 WHEN 'MODERATE' THEN 1 ELSE 2 END
            LIMIT 5
        """))
        log.info(f"  Warfarin interactions (top 5):")
        for r in warfarin:
            log.info(f"    warfarin ↔ {r['drug']:30s} [{r['sev']}]")

    driver.close()
    log.info("\n  Step 3 COMPLETE. Proceed to step4_load_drugs.py")


if __name__ == "__main__":
    main()
