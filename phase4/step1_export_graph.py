"""
step1_export_graph.py  —  pharmasafe-kg/phase4/step1_export_graph.py
---------------------------------------------------------------------
Phase 4 — Step 1 (run on YOUR LAPTOP before opening Colab)

Exports the Neo4j Knowledge Graph to CSV files that you upload
to Google Colab for GNN training.

What this exports:
    nodes.csv         — all Ingredient nodes (node_id, name)
    edges.csv         — all INTERACTS_WITH edges (node1, node2, severity, label)
    node_features.csv — feature matrix for each node

Output folder:  pharmasafe-kg/phase4/colab_data/

Run:
    python phase4/step1_export_graph.py

Then upload the entire colab_data/ folder to your Google Drive.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI      = os.getenv("NEO4J_URI")
NEO4J_USER     = os.getenv("NEO4J_USER") or os.getenv("NEO4J_USERNAME") or "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

ROOT       = Path(__file__).parent.parent
OUTPUT_DIR = ROOT / "phase4" / "colab_data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_driver():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    driver.verify_connectivity()
    return driver


def export_nodes(driver) -> pd.DataFrame:
    print("  Exporting Ingredient nodes...")
    with driver.session() as session:
        rows = list(session.run("""
            MATCH (i:Ingredient)
            RETURN id(i) AS neo4j_id, i.name AS name,
                   i.drugbank_id AS drugbank_id
            ORDER BY i.name
        """))

    df = pd.DataFrame([{
        "neo4j_id":   r["neo4j_id"],
        "name":       r["name"],
        "drugbank_id":r["drugbank_id"] or "",
    } for r in rows])

    # Create sequential node_id for PyTorch Geometric (0-indexed)
    df["node_id"] = range(len(df))
    df.to_csv(OUTPUT_DIR / "nodes.csv", index=False)
    print(f"  Exported {len(df):,} nodes → colab_data/nodes.csv")
    return df


def export_edges(driver, node_df: pd.DataFrame) -> pd.DataFrame:
    print("  Exporting INTERACTS_WITH edges...")

    # Build name → node_id mapping
    name_to_id = dict(zip(node_df["name"], node_df["node_id"]))

    with driver.session() as session:
        rows = list(session.run("""
            MATCH (a:Ingredient)-[r:INTERACTS_WITH]->(b:Ingredient)
            RETURN a.name AS drug1, b.name AS drug2,
                   r.severity AS severity
        """))

    records = []
    skipped = 0
    for r in rows:
        n1 = name_to_id.get(r["drug1"])
        n2 = name_to_id.get(r["drug2"])
        if n1 is None or n2 is None:
            skipped += 1
            continue

        # Binary label: 1 = interaction exists
        # Severity as multi-class: MAJOR=2, MODERATE=1, MINOR=0
        sev_map = {"MAJOR": 2, "MODERATE": 1, "MINOR": 0}
        records.append({
            "node1":          n1,
            "node2":          n2,
            "severity":       r["severity"],
            "severity_label": sev_map.get(r["severity"], 1),
            "label":          1,   # positive pair
        })

    df = pd.DataFrame(records)

    # Generate NEGATIVE samples (non-interacting pairs) for training
    # Use random sampling of pairs not in edge list
    print("  Generating negative samples...")
    import random
    random.seed(42)
    num_nodes   = len(node_df)
    edge_set    = set(zip(df["node1"], df["node2"]))
    negatives   = []
    target_neg  = min(len(df), 50000)   # match positive count
    attempts    = 0
    max_attempts = target_neg * 10

    while len(negatives) < target_neg and attempts < max_attempts:
        a = random.randint(0, num_nodes - 1)
        b = random.randint(0, num_nodes - 1)
        if a != b and (a, b) not in edge_set and (b, a) not in edge_set:
            negatives.append({
                "node1": a, "node2": b,
                "severity": "NONE", "severity_label": -1, "label": 0,
            })
            edge_set.add((a, b))
        attempts += 1

    df_neg = pd.DataFrame(negatives)
    df_all = pd.concat([df, df_neg], ignore_index=True).sample(
        frac=1, random_state=42
    ).reset_index(drop=True)

    df_all.to_csv(OUTPUT_DIR / "edges.csv", index=False)
    print(f"  Exported {len(df):,} positive + {len(negatives):,} negative edges")
    print(f"  → colab_data/edges.csv  (total: {len(df_all):,} rows)")
    return df_all


def export_node_features(node_df: pd.DataFrame):
    """
    Creates a simple feature matrix.
    Each node gets:
      - Degree features will be computed in Colab from edge list
      - drugbank_id presence as binary feature
      - Name-based hash features (simple but effective for GNN init)
    """
    print("  Creating node feature matrix...")

    features = []
    import hashlib
    for _, row in node_df.iterrows():
        name = str(row["name"]).lower().strip()
        has_drugbank_id = 1 if row["drugbank_id"] else 0

        # Deterministic hash-based features (8 binary features from SHA-256)
        digest = hashlib.sha256(name.encode("utf-8")).digest()
        hash_val = int.from_bytes(digest[:2], byteorder="big")
        bits = [(hash_val >> i) & 1 for i in range(8)]

        features.append({
            "node_id":         row["node_id"],
            "name":            name,
            "has_drugbank_id": has_drugbank_id,
            **{f"hash_feat_{i}": bits[i] for i in range(8)},
        })


    df = pd.DataFrame(features)
    df.to_csv(OUTPUT_DIR / "node_features.csv", index=False)
    print(f"  Exported feature matrix ({len(df)} nodes × {len(df.columns)-2} features)")
    print(f"  → colab_data/node_features.csv")


def main():
    print("=" * 55)
    print("  PharmaSafe-KG | Phase 4 | Graph Data Export")
    print("=" * 55)

    driver = get_driver()
    print("  Connected to Neo4j AuraDB\n")

    node_df = export_nodes(driver)
    edge_df = export_edges(driver, node_df)
    export_node_features(node_df)

    driver.close()

    print("\n" + "=" * 55)
    print("  EXPORT COMPLETE")
    print(f"  Output folder: {OUTPUT_DIR}")
    print()
    print("  NEXT STEPS:")
    print("  1. Upload the colab_data/ folder to your Google Drive")
    print("  2. Open PharmaSafe_GNN_Colab.py in Google Colab")
    print("  3. Run all cells — training takes ~10 minutes on T4 GPU")
    print("  4. Download model_weights.pt to phase4/")
    print("=" * 55)


if __name__ == "__main__":
    main()
