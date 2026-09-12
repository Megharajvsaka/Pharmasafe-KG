"""
step2_load_ingredients.py
--------------------------
Phase 2 — Step 2
Loads all Ingredient (generic drug) nodes into Neo4j.

Source: phase1/outputs/drugbank_ddi_cleaned.csv
        Extracts all unique drug1_norm and drug2_norm values

Why Ingredients first:
  - INTERACTS_WITH edges reference Ingredient nodes by name
  - Nodes must exist before edges can be created
  - Loading ~1,800 nodes is fast (< 5 seconds)

Each Ingredient node has:
    name        — normalised generic name  (e.g. "warfarin")
    display_name— original casing          (e.g. "Warfarin")
    drugbank_id — DrugBank ID if available (e.g. "DB00682")
    source      — "drugbank" or "ddinter"

Run:
    python phase2/step2_load_ingredients.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv
from tqdm import tqdm

from utils_phase2 import get_logger, print_section, batch

load_dotenv()
log = get_logger("step2_ingredients")

NEO4J_URI      = os.getenv("NEO4J_URI")
NEO4J_USER     = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

DRUGBANK_CSV   = (
    __file__ if False else
    str(__file__).replace("phase2/step2_load_ingredients.py", "")
    .replace("phase2\\step2_load_ingredients.py", "")
)

from pathlib import Path
ROOT           = Path(__file__).parent.parent
DRUGBANK_CSV   = ROOT / "data_pipeline" / "outputs" / "drugbank_ddi_cleaned.csv"


def get_driver():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    driver.verify_connectivity()
    return driver


def extract_unique_ingredients(df: pd.DataFrame) -> list[dict]:
    """
    Extracts all unique Ingredient records from the DDI cleaned file.
    Builds a dict keyed by normalised name to avoid duplicates.
    """
    ingredients = {}

    for _, row in df.iterrows():
        for norm_col, orig_col, id_col in [
            ("drug1_norm", "drug1_name", "drug1_id"),
            ("drug2_norm", "drug2_name", "drug2_id"),
        ]:
            name = str(row.get(norm_col, "")).strip()
            if not name:
                continue

            if name not in ingredients:
                ingredients[name] = {
                    "name":         name,
                    "display_name": str(row.get(orig_col, name)).strip().title(),
                    "drugbank_id":  str(row.get(id_col, "")).strip(),
                    "source":       "drugbank",
                }
            # Prefer a row that has a drugbank_id
            elif not ingredients[name]["drugbank_id"]:
                db_id = str(row.get(id_col, "")).strip()
                if db_id:
                    ingredients[name]["drugbank_id"] = db_id

    return list(ingredients.values())


def load_ingredients(driver, ingredients: list[dict]) -> int:
    """
    MERGEs Ingredient nodes into Neo4j in batches of 200.
    MERGE = create if not exists, skip if already exists.
    Returns count of nodes processed.
    """
    CYPHER = """
    UNWIND $rows AS row
    MERGE (i:Ingredient {name: row.name})
    ON CREATE SET
        i.display_name = row.display_name,
        i.drugbank_id  = row.drugbank_id,
        i.source       = row.source,
        i.created_at   = datetime()
    ON MATCH SET
        i.drugbank_id  = CASE WHEN i.drugbank_id = '' THEN row.drugbank_id ELSE i.drugbank_id END
    """

    total = 0
    batches = list(batch(ingredients, 200))

    with driver.session() as session:
        for b in tqdm(batches, desc="  Loading Ingredient nodes"):
            session.run(CYPHER, rows=b)
            total += len(b)

    return total


def main():
    log.info("=" * 60)
    log.info("PharmaSafe-KG  |  Phase 2  |  Step 2: Ingredient Nodes")
    log.info("=" * 60)

    # Load Phase 1 output
    if not DRUGBANK_CSV.exists():
        log.error(f"Missing: {DRUGBANK_CSV}")
        log.error("Run Phase 1 first.")
        sys.exit(1)

    df = pd.read_csv(DRUGBANK_CSV, encoding="utf-8")
    log.info(f"  Loaded DDI data: {len(df):,} rows")

    # Extract unique ingredients
    print_section("Extracting unique Ingredient records")
    ingredients = extract_unique_ingredients(df)
    log.info(f"  Unique Ingredient nodes to load: {len(ingredients):,}")

    # Connect and load
    driver = get_driver()
    log.info("  Connected to Neo4j AuraDB")

    print_section("Loading Ingredient nodes into Neo4j")
    count = load_ingredients(driver, ingredients)
    log.info(f"  Loaded {count:,} Ingredient nodes")

    # Verify
    print_section("Verifying node count in Neo4j")
    with driver.session() as session:
        result = session.run("MATCH (i:Ingredient) RETURN count(i) AS cnt")
        neo4j_count = result.single()["cnt"]
        log.info(f"  Neo4j Ingredient count: {neo4j_count:,}")

        # Sample check
        sample = list(session.run(
            "MATCH (i:Ingredient) RETURN i.name, i.display_name, i.drugbank_id LIMIT 5"
        ))
        log.info("  Sample nodes:")
        for r in sample:
            log.info(f"    {r['i.name']:30s}  {r['i.drugbank_id']}")

    driver.close()
    log.info("\n  Step 2 COMPLETE. Proceed to step3_load_interactions.py")


if __name__ == "__main__":
    main()
