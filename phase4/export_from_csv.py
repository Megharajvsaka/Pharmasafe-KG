"""
phase4/export_from_csv.py
-------------------------
Direct CSV-based exporter for Phase 4 GNN training data (colab_data/).
Generates nodes.csv, edges.csv, and node_features.csv directly from
phase1/outputs/ without requiring an active Neo4j database connection.
"""

import hashlib
import random
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent.parent
PHASE1_OUT = ROOT / "phase1" / "outputs"
COLAB_DIR = ROOT / "phase4" / "colab_data"
COLAB_DIR.mkdir(parents=True, exist_ok=True)


def export_all():
    print("=" * 60)
    print("  PharmaSafe-KG | Export GNN Training Data from Phase 1 CSVs")
    print("=" * 60)

    ddi_path = PHASE1_OUT / "drugbank_ddi_cleaned.csv"
    map_path = PHASE1_OUT / "master_mapping_table.csv"

    if not ddi_path.exists() or not map_path.exists():
        print(f"Error: Required CSVs not found in {PHASE1_OUT}")
        return

    print("1. Loading DrugBank DDI and Master Mapping CSVs...")
    ddi_df = pd.read_csv(ddi_path)
    map_df = pd.read_csv(map_path)

    # 1. Build distinct ingredient nodes
    print("2. Extracting distinct ingredient nodes...")
    drugs1 = ddi_df[["drug1_name", "drug1_id"]].rename(columns={"drug1_name": "name", "drug1_id": "drugbank_id"})
    drugs2 = ddi_df[["drug2_name", "drug2_id"]].rename(columns={"drug2_name": "name", "drug2_id": "drugbank_id"})
    all_drugs = pd.concat([drugs1, drugs2]).drop_duplicates(subset=["name"]).reset_index(drop=True)
    all_drugs["name"] = all_drugs["name"].str.lower().str.strip()
    all_drugs = all_drugs.drop_duplicates(subset=["name"]).sort_values("name").reset_index(drop=True)
    all_drugs["node_id"] = range(len(all_drugs))
    all_drugs = all_drugs[["node_id", "name", "drugbank_id"]]

    all_drugs.to_csv(COLAB_DIR / "nodes.csv", index=False)
    print(f"   Exported {len(all_drugs):,} ingredient nodes -> colab_data/nodes.csv")

    name_to_id = dict(zip(all_drugs["name"], all_drugs["node_id"]))

    # 2. Build positive and negative edges
    print("3. Generating positive and negative edge samples...")
    pos_records = []
    sev_map = {"MINOR": 0, "MODERATE": 1, "MAJOR": 2}

    for _, row in ddi_df.iterrows():
        d1 = str(row["drug1_name"]).lower().strip()
        d2 = str(row["drug2_name"]).lower().strip()
        if d1 in name_to_id and d2 in name_to_id:
            sev = str(row.get("severity", "MODERATE")).upper()
            pos_records.append({
                "node1": name_to_id[d1],
                "node2": name_to_id[d2],
                "severity": sev,
                "severity_label": sev_map.get(sev, 1),
                "label": 1,
            })

    # Canonicalize pairs (node1 < node2) for undirected graph representation
    pos_records_canonical = []
    for r in pos_records:
        u, v = sorted([r["node1"], r["node2"]])
        pos_records_canonical.append({
            "node1": u,
            "node2": v,
            "severity": r["severity"],
            "severity_label": r["severity_label"],
            "label": 1,
        })

    df_pos = pd.DataFrame(pos_records_canonical).drop_duplicates(subset=["node1", "node2"]).reset_index(drop=True)
    if len(df_pos) > 100000:
        df_pos = df_pos.sample(n=100000, random_state=42).reset_index(drop=True)

    # Generate negative pairs (strictly non-interacting, zero overlap with pos_edges)
    random.seed(42)
    num_nodes = len(all_drugs)
    edge_set = set(zip(df_pos["node1"], df_pos["node2"])) | set(zip(df_pos["node2"], df_pos["node1"]))
    negatives = []
    target_neg = min(len(df_pos), 50000)
    attempts = 0
    max_attempts = target_neg * 20

    while len(negatives) < target_neg and attempts < max_attempts:
        a = random.randint(0, num_nodes - 1)
        b = random.randint(0, num_nodes - 1)
        if a != b:
            u, v = sorted([a, b])
            if (u, v) not in edge_set:
                negatives.append({
                    "node1": u,
                    "node2": v,
                    "severity": "NONE",
                    "severity_label": -1,
                    "label": 0,
                })
                edge_set.add((u, v))
                edge_set.add((v, u))
        attempts += 1

    df_neg = pd.DataFrame(negatives)
    df_edges = pd.concat([df_pos, df_neg], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
    df_edges.to_csv(COLAB_DIR / "edges.csv", index=False)
    print(f"   Exported {len(df_pos):,} positive + {len(df_neg):,} negative edges -> colab_data/edges.csv")


    # 3. Build deterministic SHA-256 node features
    print("4. Computing deterministic SHA-256 node features...")
    features = []
    for _, row in all_drugs.iterrows():
        name = str(row["name"]).lower().strip()
        has_drugbank_id = 1 if pd.notna(row["drugbank_id"]) and str(row["drugbank_id"]).strip() else 0
        digest = hashlib.sha256(name.encode("utf-8")).digest()
        hash_val = int.from_bytes(digest[:2], byteorder="big")
        bits = [(hash_val >> i) & 1 for i in range(8)]

        features.append({
            "node_id": row["node_id"],
            "name": name,
            "has_drugbank_id": has_drugbank_id,
            **{f"hash_feat_{i}": bits[i] for i in range(8)},
        })

    df_feat = pd.DataFrame(features)
    df_feat.to_csv(COLAB_DIR / "node_features.csv", index=False)
    print(f"   Exported {len(df_feat):,} node features -> colab_data/node_features.csv")

    print("\n[SUCCESS] colab_data/ exported successfully and ready for MP.ipynb in Google Colab!")


if __name__ == "__main__":
    export_all()
