"""
step1_create_schema.py
----------------------
Phase 2 — Step 1
Creates Neo4j constraints and indexes before any data is loaded.

WHY this must run first:
  - UNIQUE constraints prevent duplicate nodes when we MERGE
  - Indexes make lookups on name fields instant (O(log n) vs O(n))
  - Without an index on Ingredient.name, every INTERACTS_WITH load
    would scan all nodes — loading 100K edges would take hours

Node types created here:
    (:Drug)        — Indian brand drug (e.g. "Combiflam")
    (:Ingredient)  — Generic/INN name  (e.g. "Ibuprofen")

Future node types (Phase 3 — GNN):
    (:Enzyme)      — CYP450 enzymes
    (:SideEffect)  — Adverse effects
    (:Disease)     — Conditions treated

Run:
    python phase2/step1_create_schema.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from neo4j import GraphDatabase
from dotenv import load_dotenv
from utils_phase2 import get_logger, print_section

load_dotenv()
log = get_logger("step1_schema")

NEO4J_URI      = os.getenv("NEO4J_URI")
NEO4J_USER     = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


def get_driver():
    if not NEO4J_URI or not NEO4J_PASSWORD:
        log.error("NEO4J_URI or NEO4J_PASSWORD missing from .env file")
        log.error("Create .env in pharmasafe-kg/ with your AuraDB credentials")
        sys.exit(1)
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        log.info("  Connected to Neo4j AuraDB successfully")
        return driver
    except Exception as e:
        log.error(f"  Failed to connect to Neo4j: {e}")
        log.error("  Check your .env credentials and AuraDB instance status")
        sys.exit(1)


def create_schema(driver):
    """
    Creates uniqueness constraints and indexes.
    MERGE operations need constraints to work correctly.
    """
    print_section("Creating constraints and indexes")

    schema_statements = [
        # ── Uniqueness constraints ────────────────────────────────────────────
        # These also automatically create an index on the constrained property
        (
            "Constraint: Drug.name unique",
            "CREATE CONSTRAINT drug_name_unique IF NOT EXISTS "
            "FOR (d:Drug) REQUIRE d.name IS UNIQUE"
        ),
        (
            "Constraint: Ingredient.name unique",
            "CREATE CONSTRAINT ingredient_name_unique IF NOT EXISTS "
            "FOR (i:Ingredient) REQUIRE i.name IS UNIQUE"
        ),
        # ── Extra indexes for fast lookups ────────────────────────────────────
        (
            "Index: Drug.name (for STARTS WITH autocomplete)",
            "CREATE INDEX drug_name_idx IF NOT EXISTS "
            "FOR (d:Drug) ON (d.name)"
        ),
        (
            "Index: Ingredient.name",
            "CREATE INDEX ingredient_name_idx IF NOT EXISTS "
            "FOR (i:Ingredient) ON (i.name)"
        ),
        (
            "Index: Drug.manufacturer",
            "CREATE INDEX drug_manufacturer_idx IF NOT EXISTS "
            "FOR (d:Drug) ON (d.manufacturer)"
        ),
    ]

    with driver.session() as session:
        for label, cypher in schema_statements:
            try:
                session.run(cypher)
                log.info(f"  ✓  {label}")
            except Exception as e:
                # Neo4j raises if constraint already exists in some versions
                if "already exists" in str(e).lower() or "equivalent" in str(e).lower():
                    log.info(f"  ─  {label} (already exists, skipping)")
                else:
                    log.warning(f"  ⚠  {label}: {e}")


def show_existing_schema(driver):
    """Prints what constraints and indexes currently exist."""
    print_section("Current schema summary")
    with driver.session() as session:
        constraints = list(session.run("SHOW CONSTRAINTS"))
        indexes     = list(session.run("SHOW INDEXES"))
        log.info(f"  Constraints : {len(constraints)}")
        log.info(f"  Indexes     : {len(indexes)}")
        for c in constraints:
            log.info(f"    CONSTRAINT  {c.get('name', '')}  —  {c.get('labelsOrTypes', '')}  {c.get('properties', '')}")


def main():
    log.info("=" * 60)
    log.info("PharmaSafe-KG  |  Phase 2  |  Step 1: Schema Setup")
    log.info("=" * 60)

    driver = get_driver()
    create_schema(driver)
    show_existing_schema(driver)
    driver.close()

    log.info("\n  Step 1 COMPLETE. Proceed to step2_load_ingredients.py")


if __name__ == "__main__":
    main()
