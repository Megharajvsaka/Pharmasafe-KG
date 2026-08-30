# PharmaSafe-KG — Data Provenance & Lineage Specification
**Document Type:** Formal Data Architecture & Provenance Record  
**Version:** 1.0.0  
**Date:** August 30, 2026  

---

## 1. Data Pipeline Overview

PharmaSafe-KG synthesizes three disparate biomedical data modalities:
1. **Commercial Pharmaceutical Records:** 304,000+ Indian brand-name medicines.
2. **Curated Chemoinformatics Knowledge:** 222,696 raw DrugBank DDI pairs and mechanism descriptions.
3. **Graph Topology & Embeddings:** 1,761 generic drug entities with dense message-passing links.

```
+-----------------------------+     +-----------------------------+
| az_medicine_india.csv       |     | drug_interactions.csv       |
| (304,000+ commercial drugs) |     | drug_descriptions.csv       |
+--------------+--------------+     +--------------+--------------+
               |                                   |
               v                                   v
   [step1_clean_indian_drugs]             [step2_load_drugbank]
               |                                   |
               v                                   v
   indian_medicines_cleaned.csv         drugbank_ddi_cleaned.csv
               \                                   /
                \                                 /
                 v                               v
            [step3_map_brands_to_generics.py]
                         |
                         v
             master_mapping_table.csv
                         |
       +-----------------+-----------------+
       |                                   |
       v                                   v
[Phase 2: Neo4j AuraDB]           [Phase 4: GNN colab_data]
• 50,073 nodes (48k Drug, 2k Ing) • nodes.csv (1,761)
• 89,367 INTERACTS_WITH           • edges.csv (92,161 pos + 50k neg)
• 71,512 CONTAINS                 • node_features.csv [1761, 10]
```

---

## 2. Source Data Artifacts & Manifests

### 2.1. Raw Input Files (`phase1/data/`)
* **`az_medicine_india.csv`**:
  - Source: Open Indian medicine retail dataset (1mg / Apollo pharmacy catalog dump).
  - Schema: `name, price, manufacturer, short_composition1, short_composition2`.
* **`drug_interactions.csv`**:
  - Source: DrugBank Open Data release.
  - Schema: `drug1, drug2, interaction_type`.
* **`drug_descriptions.csv`**:
  - Source: DrugBank interaction description narrative corpus.
  - Schema: `drugbank_id, name, description`.

### 2.2. Canonical Preprocessed Datasets (`phase1/outputs/`)
* **`drugbank_ddi_cleaned.csv`**:
  - Row Count: **92,161 unique pairs** (0 duplicates, 0 missing values).
  - Severity Breakdown:
    - `MODERATE`: 67,595 (73.34%)
    - `MAJOR`: 20,476 (22.22%)
    - `MINOR`: 4,090 (4.44%)
  - Canonical Ordering: `drug1_name < drug2_name` strictly enforced.
* **`master_mapping_table.csv`**:
  - Row Count: **304,000+ brand-to-ingredient mapping rows**.
  - Generic Entities: 1,759 standardized INN generic names.

### 2.3. ML Dataset Files (`phase4/colab_data/`)
* **`nodes.csv`**: 1,761 rows (`node_id, drug_name`).
* **`edges.csv`**: 142,161 rows (`node1, node2, label, severity`).
  - Positives (`label=1`): 92,161 pairs.
  - Negatives (`label=0`): 50,000 non-edges.
* **`node_features.csv`**: 1,761 rows $\times$ 10 feature columns.

---

## 3. Transformation & Cleaning Rules

1. **Entity Normalization:** All generic names and brand names are lowercased and stripped of dosage suffixes (e.g. `500 mg`, `SR`, `Dolo 650` $\rightarrow$ `dolo 650`, generic `paracetamol`).
2. **Canonical Pair De-duplication:** All pairwise interactions $(A, B)$ and $(B, A)$ are consolidated into a single record where $A < B$.
3. **Severity Calibration:** Removed generic uninformative phrase `"risk or severity of adverse effects"` from `MAJOR_KEYWORDS`, correctly assigning it to `MODERATE`.
4. **Leakage-Free Splitting:**
   - 70% Train ($N=64,512$ pos / $35,000$ neg).
   - 15% Val ($N=13,824$ pos / $7,500$ neg).
   - 15% Test ($N=13,825$ pos / $7,500$ neg).
   - Message-passing graph derived exclusively from `pos_train` ($129,024$ directed edges).
