"""
step5_validate.py
-----------------
Phase 2 — Step 5
Comprehensive validation of the Knowledge Graph.

Runs 10 test queries covering:
  1.  Total node and edge counts
  2.  Indian brand → ingredient resolution
  3.  Direct DDI detection (Combiflam + Ecosprin)
  4.  Multi-drug polypharmacy query (4 drugs at once)
  5.  Severity distribution
  6.  Top 5 most-connected drugs
  7.  Warfarin interaction network
  8.  End-to-end XAI path query
  9.  Performance benchmark (query time)
  10. Graph density check

All results are printed to the terminal and saved to
phase2/outputs/validation_report.txt

Run:
    python phase2/step5_validate.py
"""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from neo4j import GraphDatabase
from dotenv import load_dotenv
from pathlib import Path

from utils_phase2 import get_logger, print_section

load_dotenv()
log = get_logger("step5_validate")

NEO4J_URI      = os.getenv("NEO4J_URI")
NEO4J_USER     = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

ROOT           = Path(__file__).parent.parent
OUTPUT_DIR     = ROOT / "data_pipeline" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_FILE    = OUTPUT_DIR / "validation_report.txt"


def get_driver():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    driver.verify_connectivity()
    return driver


def run_all_tests(driver) -> list[str]:
    report_lines = []

    def log_result(title, lines):
        log.info(f"\n  {'─'*50}")
        log.info(f"  TEST: {title}")
        for line in lines:
            log.info(f"    {line}")
        report_lines.append(f"\n{'─'*50}")
        report_lines.append(f"TEST: {title}")
        report_lines.extend([f"  {l}" for l in lines])

    with driver.session() as session:

        # ── TEST 1: Graph totals ──────────────────────────────────────────────
        drug_cnt  = session.run("MATCH (d:Drug) RETURN count(d) AS c").single()["c"]
        ing_cnt   = session.run("MATCH (i:Ingredient) RETURN count(i) AS c").single()["c"]
        iw_cnt    = session.run("MATCH ()-[r:INTERACTS_WITH]->() RETURN count(r) AS c").single()["c"]
        cont_cnt  = session.run("MATCH ()-[c:CONTAINS]->() RETURN count(c) AS c").single()["c"]
        log_result("Graph Totals", [
            f"Drug nodes          : {drug_cnt:,}",
            f"Ingredient nodes    : {ing_cnt:,}",
            f"INTERACTS_WITH edges: {iw_cnt:,}",
            f"CONTAINS edges      : {cont_cnt:,}",
            f"Total nodes         : {drug_cnt+ing_cnt:,}  /  50,000 limit",
            f"Total relationships : {iw_cnt+cont_cnt:,}  /  175,000 limit",
        ])

        # ── TEST 2: Indian brand resolution ──────────────────────────────────
        results = list(session.run("""
            MATCH (d:Drug)-[:CONTAINS]->(i:Ingredient)
            WHERE d.name CONTAINS 'Combiflam' OR d.name CONTAINS 'Dolo'
               OR d.name CONTAINS 'Ecosprin' OR d.name CONTAINS 'Pantop'
            RETURN d.name AS brand, collect(i.name) AS generics
        """))
        lines = [f"{r['brand']:30s} → {r['generics']}" for r in results[:8]]
        log_result("Indian Brand Resolution (Combiflam, Dolo, Ecosprin, Pantop)", lines or ["No results — brands may not be in node budget"])

        # ── TEST 3: Direct DDI — Combiflam + Ecosprin ────────────────────────
        t0 = time.time()
        results = list(session.run("""
            MATCH (d1:Drug)-[:CONTAINS]->(i1:Ingredient)
            MATCH (d2:Drug)-[:CONTAINS]->(i2:Ingredient)
            MATCH (i1)-[r:INTERACTS_WITH]-(i2)
            WHERE d1.name CONTAINS 'Combiflam' AND d2.name CONTAINS 'Ecosprin'
            RETURN d1.name, i1.name, r.severity, r.mechanism, i2.name, d2.name
        """))
        elapsed = (time.time() - t0) * 1000
        lines = [f"Query time: {elapsed:.0f}ms"]
        for r in results:
            lines.append(f"  {r['d1.name']} → {r['i1.name']} [{r['r.severity']}] ↔ {r['i2.name']} ← {r['d2.name']}")
            lines.append(f"  Mechanism: {str(r['r.mechanism'])[:100]}...")
        if not results:
            lines.append("No direct result — brands may not have node in graph (will resolve via CSV at API layer)")
        log_result("Direct DDI Query: Combiflam + Ecosprin", lines)

        # ── TEST 4: Ingredient-level polypharmacy (4 generics) ───────────────
        t0 = time.time()
        results = list(session.run("""
            WITH ['warfarin','ibuprofen','metformin','atorvastatin'] AS drug_list
            UNWIND drug_list AS d1_name
            UNWIND drug_list AS d2_name
            WITH d1_name, d2_name
            WHERE d1_name < d2_name
            MATCH (a:Ingredient {name: d1_name})-[r:INTERACTS_WITH]-(b:Ingredient {name: d2_name})
            RETURN a.name AS drug1, b.name AS drug2, r.severity AS severity
            ORDER BY CASE r.severity WHEN 'MAJOR' THEN 0 WHEN 'MODERATE' THEN 1 ELSE 2 END
        """))
        elapsed = (time.time() - t0) * 1000
        lines = [f"Checked 6 pairs in {elapsed:.0f}ms"]
        for r in results:
            lines.append(f"  {r['drug1']:20s} ↔ {r['drug2']:20s} [{r['severity']}]")
        if not results:
            lines.append("No interactions found between these 4 drugs (expected for some pairs)")
        log_result("Polypharmacy Query: 4 drugs, all pairs", lines)

        # ── TEST 5: Severity distribution ────────────────────────────────────
        results = list(session.run("""
            MATCH ()-[r:INTERACTS_WITH]->()
            RETURN r.severity AS sev, count(r) AS cnt
            ORDER BY cnt DESC
        """))
        lines = [f"{r['sev']:10s}: {r['cnt']:,}" for r in results]
        log_result("Severity Distribution", lines)

        # ── TEST 6: Most connected ingredients ───────────────────────────────
        results = list(session.run("""
            MATCH (i:Ingredient)-[r:INTERACTS_WITH]-()
            RETURN i.name AS name, count(r) AS connections
            ORDER BY connections DESC LIMIT 10
        """))
        lines = [f"{r['name']:30s}: {r['connections']:,} interactions" for r in results]
        log_result("Top 10 Most Connected Ingredients", lines)

        # ── TEST 7: Warfarin interaction network ─────────────────────────────
        results = list(session.run("""
            MATCH (w:Ingredient {name: 'warfarin'})-[r:INTERACTS_WITH]-(other:Ingredient)
            RETURN other.name AS drug, r.severity AS sev
            ORDER BY CASE r.severity WHEN 'MAJOR' THEN 0 WHEN 'MODERATE' THEN 1 ELSE 2 END
            LIMIT 10
        """))
        lines = [f"warfarin ↔ {r['drug']:30s} [{r['sev']}]" for r in results]
        log_result("Warfarin Interaction Network (top 10)", lines)

        # ── TEST 8: XAI explanation path ─────────────────────────────────────
        results = list(session.run("""
            MATCH (a:Ingredient {name: 'warfarin'})-[r:INTERACTS_WITH]-(b:Ingredient)
            WHERE r.severity = 'MAJOR'
            RETURN
                'warfarin' AS source,
                b.name AS target,
                r.severity AS severity,
                r.mechanism AS explanation
            LIMIT 3
        """))
        lines = []
        for r in results:
            lines.append(f"  {r['source']} ↔ {r['target']}  [{r['severity']}]")
            lines.append(f"  EXPLANATION: {str(r['explanation'])[:150]}")
            lines.append("")
        log_result("XAI Explanation Path Query (Warfarin MAJOR interactions)", lines or ["No results"])

        # ── TEST 9: Autocomplete performance ─────────────────────────────────
        t0 = time.time()
        results = list(session.run("""
            MATCH (d:Drug) WHERE d.name STARTS WITH 'Metf'
            RETURN d.name LIMIT 10
        """))
        elapsed = (time.time() - t0) * 1000
        names = [r["d.name"] for r in results]
        log_result(f"Autocomplete Query (STARTS WITH 'Metf') — {elapsed:.0f}ms", names or ["No drug names starting with 'Metf' in graph"])

        # ── TEST 10: Graph stats ──────────────────────────────────────────────
        avg_connections = session.run("""
            MATCH (i:Ingredient)-[r:INTERACTS_WITH]-()
            WITH i, count(r) AS deg
            RETURN avg(deg) AS avg_degree, max(deg) AS max_degree, min(deg) AS min_degree
        """).single()
        log_result("Graph Statistics", [
            f"Avg connections per ingredient : {avg_connections['avg_degree']:.1f}",
            f"Max connections (most connected): {avg_connections['max_degree']}",
            f"Min connections                : {avg_connections['min_degree']}",
        ])

    return report_lines


def main():
    log.info("=" * 60)
    log.info("PharmaSafe-KG  |  Phase 2  |  Step 5: Graph Validation")
    log.info("=" * 60)

    driver = get_driver()
    log.info("  Connected to Neo4j AuraDB")

    print_section("Running 10 validation tests")
    report_lines = run_all_tests(driver)
    driver.close()

    # Save report
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("PharmaSafe-KG — Phase 2 Validation Report\n")
        f.write("=" * 60 + "\n")
        f.write("\n".join(report_lines))
    log.info(f"\n  Validation report saved → {REPORT_FILE}")

    log.info("\n  Step 5 COMPLETE. Phase 2 is DONE.")
    log.info("  ─────────────────────────────────────────────────────")
    log.info("  Your Knowledge Graph is live on Neo4j AuraDB.")
    log.info("  Open console.neo4j.io → your instance → Query tab")
    log.info("  Run: MATCH (n) RETURN n LIMIT 50  to see the graph")
    log.info("  ─────────────────────────────────────────────────────")
    log.info("  Next: Phase 3 — FastAPI backend")


if __name__ == "__main__":
    main()
