"""
step4_load_drugs.py
--------------------
Phase 2 — Step 4
Loads Indian brand Drug nodes and CONTAINS relationships.

AuraDB Free Tier Budget Management:
    Total node limit  : 50,000
    Already used      : ~1,800  (Ingredient nodes from Step 2)
    Available for Drug: ~48,000

    Total relationship limit : 175,000
    Already used             : ~100,000  (INTERACTS_WITH from Step 3)
    Available for CONTAINS   : ~75,000

Strategy:
    Load the 48,000 most "important" Indian brands first.
    Importance = number of known DDI interactions for their generics.
    This ensures the most clinically relevant drugs are in the graph.

    The REMAINING brands (~177,000) are NOT orphaned — the FastAPI backend
    will look them up from the master_mapping_table.csv at query time and
    resolve them to their Ingredient nodes. This is the correct architecture:
    the KG handles pharmacological reasoning, the CSV handles brand lookup.

Source: phase1/outputs/master_mapping_table.csv

Each Drug node has:
    name         — brand name  (e.g. "Combiflam")
    manufacturer — company     (e.g. "Sanofi India Ltd")
    in_graph     — True  (marks that this brand has a Neo4j node)

Each CONTAINS edge has:
    generic_name — the ingredient name (redundant but useful for queries)

Run:
    python phase2/step4_load_drugs.py
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
log = get_logger("step4_drugs")

NEO4J_URI      = os.getenv("NEO4J_URI")
NEO4J_USER     = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

ROOT           = Path(__file__).parent.parent
MASTER_CSV     = ROOT / "phase1" / "outputs" / "master_mapping_table.csv"

# AuraDB free-tier limits
NODE_BUDGET    = 48_000   # leaves 2K headroom for safety
REL_BUDGET     = 72_000   # leaves 3K headroom
BATCH_SIZE     = 300


def get_driver():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    driver.verify_connectivity()
    return driver


def select_priority_brands(df: pd.DataFrame, max_brands: int) -> pd.DataFrame:
    """
    Selects the most important Indian brands to load into Neo4j.

    Priority logic:
    1. Brands whose generics have the most DDI interactions (most clinical value)
    2. Brands with MAJOR-severity DDI data get priority
    3. Within same priority, sort alphabetically for reproducibility

    Returns a DataFrame with at most `max_brands` unique brand names.
    """
    # Count DDI interactions per generic
    ddi_count = df.groupby("drugbank_match")["ddi_count"].max().reset_index()
    ddi_count.columns = ["drugbank_match", "max_ddi_count"]

    df = df.merge(ddi_count, on="drugbank_match", how="left")
    df["max_ddi_count"] = df["max_ddi_count"].fillna(0)

    # Per-brand: take max DDI count across all its generics
    brand_priority = (
        df.groupby("brand_name")["max_ddi_count"]
        .max()
        .reset_index()
        .sort_values("max_ddi_count", ascending=False)
    )

    top_brands = set(brand_priority.head(max_brands)["brand_name"].tolist())
    return df[df["brand_name"].isin(top_brands)].copy()


def build_drug_records(df: pd.DataFrame):
    """
    Returns two lists:
        drug_nodes   — unique Drug node dicts
        contains_rels— CONTAINS relationship dicts
    """
    drug_nodes = {}
    contains_rels = []

    for _, row in df.iterrows():
        brand   = str(row["brand_name"]).strip()
        generic = str(row.get("drugbank_match", "")).strip()
        mfr     = str(row.get("manufacturer", "")).strip() if "manufacturer" in row else ""

        if not brand or not generic:
            continue

        # Drug node
        if brand not in drug_nodes:
            drug_nodes[brand] = {
                "name":         brand,
                "manufacturer": mfr,
                "in_graph":     True,
            }

        # CONTAINS relationship
        contains_rels.append({
            "brand_name":   brand,
            "generic_name": generic,
        })

    return list(drug_nodes.values()), contains_rels


def load_drug_nodes(driver, drug_nodes: list[dict]) -> int:
    CYPHER = """
    UNWIND $rows AS row
    MERGE (d:Drug {name: row.name})
    ON CREATE SET
        d.manufacturer = row.manufacturer,
        d.in_graph     = true,
        d.created_at   = datetime()
    """
    total = 0
    for b in tqdm(list(batch(drug_nodes, BATCH_SIZE)), desc="  Loading Drug nodes"):
        with driver.session() as session:
            session.run(CYPHER, rows=b)
        total += len(b)
    return total


def load_contains_edges(driver, rels: list[dict], max_rels: int) -> int:
    """
    Loads CONTAINS edges, capped at max_rels for AuraDB budget.
    MATCH on both Drug and Ingredient — skip if either doesn't exist.
    """
    rels = rels[:max_rels]

    CYPHER = """
    UNWIND $rows AS row
    MATCH (d:Drug {name: row.brand_name})
    MATCH (i:Ingredient {name: row.generic_name})
    MERGE (d)-[c:CONTAINS]->(i)
    ON CREATE SET c.created_at = datetime()
    """
    total = 0
    for b in tqdm(list(batch(rels, BATCH_SIZE)), desc="  Loading CONTAINS edges"):
        with driver.session() as session:
            session.run(CYPHER, rows=b)
        total += len(b)
    return total


def main():
    log.info("=" * 60)
    log.info("PharmaSafe-KG  |  Phase 2  |  Step 4: Drug Nodes + CONTAINS")
    log.info("=" * 60)

    if not MASTER_CSV.exists():
        log.error(f"Missing: {MASTER_CSV}. Run Phase 1 first.")
        sys.exit(1)

    df = pd.read_csv(MASTER_CSV, encoding="utf-8", low_memory=False)
    log.info(f"  Master mapping loaded: {len(df):,} rows")
    log.info(f"  Unique Indian brands total: {df['brand_name'].nunique():,}")

    # Select priority brands within AuraDB node budget
    print_section("Selecting priority brands (AuraDB budget: ~48K Drug nodes)")
    df_priority = select_priority_brands(df, NODE_BUDGET)
    log.info(f"  Brands selected for graph : {df_priority['brand_name'].nunique():,}")
    log.info(f"  Brands in CSV-only lookup  : {df['brand_name'].nunique() - df_priority['brand_name'].nunique():,}")
    log.info("  (CSV-only brands resolved at query time by FastAPI backend)")

    # Build records
    print_section("Building Drug node and CONTAINS edge records")
    drug_nodes, contains_rels = build_drug_records(df_priority)
    log.info(f"  Drug nodes to load    : {len(drug_nodes):,}")
    log.info(f"  CONTAINS edges to load: {len(contains_rels):,} (capped at {REL_BUDGET:,})")

    # Connect
    driver = get_driver()
    log.info("  Connected to Neo4j AuraDB")

    # Load Drug nodes
    print_section("Loading Drug nodes")
    n = load_drug_nodes(driver, drug_nodes)
    log.info(f"  Loaded {n:,} Drug nodes")

    # Load CONTAINS edges
    print_section("Loading CONTAINS edges")
    r = load_contains_edges(driver, contains_rels, REL_BUDGET)
    log.info(f"  Loaded {r:,} CONTAINS edges")

    # Verify
    print_section("Verifying final graph state")
    with driver.session() as session:
        drug_cnt  = session.run("MATCH (d:Drug) RETURN count(d) AS c").single()["c"]
        ing_cnt   = session.run("MATCH (i:Ingredient) RETURN count(i) AS c").single()["c"]
        inter_cnt = session.run("MATCH ()-[r:INTERACTS_WITH]->() RETURN count(r) AS c").single()["c"]
        cont_cnt  = session.run("MATCH ()-[c:CONTAINS]->() RETURN count(c) AS c").single()["c"]

        log.info(f"  ── Graph Summary ───────────────────────────────────")
        log.info(f"  Drug nodes         : {drug_cnt:,}")
        log.info(f"  Ingredient nodes   : {ing_cnt:,}")
        log.info(f"  INTERACTS_WITH     : {inter_cnt:,}")
        log.info(f"  CONTAINS           : {cont_cnt:,}")
        log.info(f"  Total nodes        : {drug_cnt + ing_cnt:,}  (limit: 50,000)")
        log.info(f"  Total relationships: {inter_cnt + cont_cnt:,}  (limit: 175,000)")
        log.info(f"  ────────────────────────────────────────────────────")

        # Quick sanity check
        sample = list(session.run("""
            MATCH (d:Drug)-[:CONTAINS]->(i:Ingredient)-[r:INTERACTS_WITH]-(i2:Ingredient)
            RETURN d.name AS brand, i.name AS generic, r.severity AS sev, i2.name AS interacts_with
            LIMIT 5
        """))
        log.info("  Sample end-to-end query (brand→generic→interaction):")
        for row in sample:
            log.info(f"    {row['brand']:25s} → {row['generic']:20s} [{row['sev']}] ↔ {row['interacts_with']}")

    driver.close()
    log.info("\n  Step 4 COMPLETE. Proceed to step5_validate.py")


if __name__ == "__main__":
    main()
