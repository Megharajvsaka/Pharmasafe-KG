# PharmaSafe-KG P0 Implementation Report

**Date of Implementation:** August 30, 2026  
**Status:** COMPLETE  
**Scope:** P0 Critical Fixes for Data Pipeline, Severity Calibration, Dataset Provenance, and GNN Message-Passing Leakage Elimination.

---

## 1. P0 Issues Addressed

| Issue ID | Category | Summary of Resolution |
|---|---|---|
| **P0 #1** | Platform & Ingestion | Eliminated Unicode box-drawing/arrow characters in `phase1/utils.py` and `phase1/step2_load_drugbank.py` to prevent `UnicodeEncodeError` under Windows default `cp1252` encoding. |
| **P0 #2** | Data Integrity | Re-executed `phase1/step2_load_drugbank.py` to overwrite the stale May 1, 2026 CSV. Calibrated severity distribution from 87.87% MAJOR to **73.34% MODERATE, 22.22% MAJOR, 4.44% MINOR**. |
| **P0 #3** | Data Provenance | Verified single-source lineage: `phase1/data/` $\rightarrow$ `phase1/step2_load_drugbank.py` $\rightarrow$ `phase1/outputs/drugbank_ddi_cleaned.csv` $\rightarrow$ `phase4/export_from_csv.py` $\rightarrow$ `phase4/colab_data/`. |
| **P0 #4** | ML Dataset Export | Re-exported `phase4/colab_data/` (`nodes.csv`, `edges.csv`, `node_features.csv`) with 1,761 nodes, 92,161 positive edges, and 50,000 negative edges. |
| **P0 #5** | GNN Methodology | **Fixed Data Leakage**: Replaced global graph message passing with a strict training-only message-passing graph (`train_edge_index` derived strictly from `pos_train`). Validation and test positive edges are strictly excluded from neighbor aggregation. |
| **P0 #6** | Negative Sampling | Implemented bidirectional non-edge verification, canonical sorting (`node1 < node2`), and zero self-edges to guarantee strict disjointness between positive and negative edge sets. |
| **P0 #7** | Reproducibility | Set explicit random seeds (`SEED = 42`) across Python `random`, `numpy`, and `torch` (including CUDA deterministic flags) in both `phase4/PharmaSafe_GNN_Colab.py` and `phase4/MP.ipynb`. |
| **P0 #8** | Feature Pipeline | Verified deterministic 10-dimensional feature generation (`hashlib.sha256` 8-bit binary bits + `has_drugbank_id` + normalized degree) with strict node ID ordering alignment. |
| **P0 #9** | Model Target | Formalized model formulation as **binary link prediction** ($\text{interaction exists} \in \{0, 1\}$); clinical severity is preserved as metadata/evidence attributes. |
| **P0 #10** | Evaluation Metrics | Marked historical metrics (GraphSAGE AUC 0.8867, F1 0.8637; GAT AUC 0.8430, F1 0.8304) as **Pre-Fix Baselines** pending genuine retraining on the leakage-free pipeline. |

---

## 2. Files Modified

| File Path | Nature of Change | Technical Rationale |
|---|---|---|
| [`phase1/utils.py`](file:///c:/pharmasafe-kg/phase1/utils.py) | Replaced `\u2500` box characters and `\u2192` arrows with standard ASCII (`-`, `=`, `->`) | Prevents `UnicodeEncodeError` on Windows `cp1252` console during Phase 1 pipeline execution. |
| [`phase1/step2_load_drugbank.py`](file:///c:/pharmasafe-kg/phase1/step2_load_drugbank.py) | Replaced non-ASCII characters in logging/headers; re-executed to write output CSV | Enables seamless Windows execution and produces the calibrated 92,161 DDI dataset. |
| [`phase1/outputs/drugbank_ddi_cleaned.csv`](file:///c:/pharmasafe-kg/phase1/outputs/drugbank_ddi_cleaned.csv) | Regenerated CSV file on disk | Overwrote stale May 1, 2026 file (which had 87,868 MAJOR rows) with fresh calibrated data. |
| [`phase4/export_from_csv.py`](file:///c:/pharmasafe-kg/phase4/export_from_csv.py) | Added canonical edge sorting (`node1 < node2`), strict bidirectional negative sampling checks, and re-exported `colab_data/` | Guarantees zero positive/negative overlap, zero self-edges, and consistent node order. |
| [`phase4/colab_data/`](file:///c:/pharmasafe-kg/phase4/colab_data/) (`nodes.csv`, `edges.csv`, `node_features.csv`) | Regenerated all 3 training artifacts | Synchronizes Google Colab training inputs with the newly calibrated Phase 1 dataset. |
| [`phase4/PharmaSafe_GNN_Colab.py`](file:///c:/pharmasafe-kg/phase4/PharmaSafe_GNN_Colab.py) | Implemented leakage-free split (`train_edge_index` from `pos_train` only) and set deterministic seeds | Eliminates structural data leakage during message-passing convolution for validation/testing. |
| [`phase4/MP.ipynb`](file:///c:/pharmasafe-kg/phase4/MP.ipynb) | Synchronized Cells 4 and 5 with the leakage-free splitting and training-graph construction | Ensures Google Colab GPU training executes the mathematically sound, leakage-free pipeline. |
| [`tests/test_p0_pipeline.py`](file:///c:/pharmasafe-kg/tests/test_p0_pipeline.py) | Created comprehensive 11-test validation suite | Provides automated regression testing for all P0 fixes. |

---

## 3. Phase 1 Verification

Execution of `phase1/step2_load_drugbank.py` on the raw DrugBank datasets (`phase1/data/drug_interactions.csv` [222,696 rows] + `phase1/data/drug_descriptions.csv` [191,541 rows]) produced the following verified outputs:

### Dataset Statistics (`phase1/outputs/drugbank_ddi_cleaned.csv`):
* **Total Cleaned Interactions:** `92,161`
* **MODERATE Interactions:** `67,595` (**73.344%**)
* **MAJOR Interactions:** `20,476` (**22.218%**)
* **MINOR Interactions:** `4,090` (**4.438%**)
* **Missing Severity Values:** `0` (100% complete)
* **Pairwise Duplicates (`pair_key`):** `0` (100% unique)
* **Self-Interactions:** `0` (all $d_1 \neq d_2$)

### Clinical Interaction Verification:
* `warfarin + ibuprofen` $\rightarrow$ **MAJOR** (PASS)
* `warfarin + acetylsalicylic acid` $\rightarrow$ **MAJOR** (PASS)
* `warfarin + aspirin` $\rightarrow$ **MAJOR** (PASS via alias)
* `paracetamol + warfarin` $\rightarrow$ **MAJOR** (PASS via alias)
* `digoxin + amiodarone` $\rightarrow$ **MODERATE** (PASS)

---

## 4. Dataset Provenance

```text
[Source Raw Data]
  ├── phase1/data/drug_interactions.csv (222,696 raw pairs)
  └── phase1/data/drug_descriptions.csv (191,541 raw mechanisms)
         │
         ▼  (phase1/step2_load_drugbank.py)
[Phase 1 Canonical Output]
  └── phase1/outputs/drugbank_ddi_cleaned.csv (92,161 unique pairs, 73.3% MODERATE / 22.2% MAJOR)
         │
         ▼  (phase4/export_from_csv.py)
[Phase 4 Training Artifacts (colab_data/)]
  ├── phase4/colab_data/nodes.csv          (1,761 distinct generic drug nodes)
  ├── phase4/colab_data/edges.csv          (92,161 pos [73.3% MOD] + 50,000 neg = 142,161 total)
  └── phase4/colab_data/node_features.csv  (1,761 rows x 10 deterministic SHA-256 features)
         │
         ▼  (Upload to Google Drive)
[Google Colab Execution]
  └── phase4/MP.ipynb (GPU Training with Leakage-Free Splits)
```

---

## 5. GNN Leakage Fix

### The Leakage Vulnerability:
* **OLD Pipeline:**
  1. `pos_edges` (all 92,161 pairs) was used to construct `graph_data.edge_index` with all 184,322 directed edges.
  2. `all_pairs` (pos + neg) was split into `train`, `val`, and `test`.
  3. During `evaluate(model, graph_data, X_val, y_val)` and `evaluate(model, graph_data, X_test, y_test)`, `model.encode(graph_data.x, graph_data.edge_index)` aggregated features across ALL edges—including the exact test edges being evaluated!
  4. This caused **transductive supervision leakage**, inflating test metrics.

### The Leakage-Free Solution:
* **NEW Pipeline:**
  1. `pos_edges` is split first: `pos_train` (70%, 64,512 pairs), `pos_val` (15%, 13,824 pairs), `pos_test` (15%, 13,825 pairs).
  2. `neg_edges` is split: `neg_train` (70%, 35,000 pairs), `neg_val` (15%, 7,500 pairs), `neg_test` (15%, 7,500 pairs).
  3. Candidate evaluation sets:
     - `train_df`: 64,512 pos + 35,000 neg = 99,512 pairs ($y_{\text{train}}$)
     - `val_df`: 13,824 pos + 7,500 neg = 21,324 pairs ($y_{\text{val}}$)
     - `test_df`: 13,825 pos + 7,500 neg = 21,325 pairs ($y_{\text{test}}$)
  4. **Message-Passing Graph Construction:**
     `train_edge_index` is created **EXCLUSIVELY from `pos_train`** (both directions = 129,024 directed edges).
  5. **Message Passing During Training & Evaluation:**
     - **Training:** `model(data.x, train_edge_index, ei_train)` $\rightarrow$ aggregation over `train_edge_index` only.
     - **Validation:** `model(data.x, train_edge_index, ei_val)` $\rightarrow$ validation pairs are strictly excluded from message passing.
     - **Testing:** `model(data.x, train_edge_index, ei_test)` $\rightarrow$ test pairs are strictly excluded from message passing.

---

## 6. Negative Sampling Verification

1. **Non-Edge Guarantee:** Negative pairs $(u, v)$ are sampled uniformly from non-edges ($u \neq v$) and verified against the complete bidirectional positive edge set: $\mathcal{E}_{\text{pos}} \cup \{(v, u) \mid (u, v) \in \mathcal{E}_{\text{pos}}\}$.
2. **Zero Overlap:** Automated testing (`TestP0ColabDataProvenance::test_negative_sampling_zero_positive_overlap`) confirms **0 intersection** between positive and negative pairs.
3. **No Duplicate Negatives:** Sampled negative pairs are added to `edge_set` in both directions during sampling, guaranteeing uniqueness.
4. **No Self-Edges:** Tested and verified $0$ occurrences of $u = v$.

---

## 7. Reproducibility

* **Deterministic Random Seeds:**
  ```python
  SEED = 42
  random.seed(42)
  np.random.seed(42)
  torch.manual_seed(42)
  if torch.cuda.is_available():
      torch.cuda.manual_seed_all(42)
      torch.backends.cudnn.deterministic = True
  ```
* **Deterministic Dataset Shuffling:** All splits and exports utilize explicit `random_state=42`.

---

## 8. Feature Pipeline Verification

* **Node Feature Dimensionality:** 10 features per node ($N = 1,761$).
  - Features 0–7: 8-bit binary representation derived from `hashlib.sha256(name.encode('utf-8')).digest()[:2]`.
  - Feature 8: `has_drugbank_id` binary flag.
  - Feature 9: Normalized node degree computed strictly from positive training edges.
* **Order Alignment:** Row $i$ in `node_features.csv` exactly matches node ID $i$ and name in `nodes.csv`.

---

## 9. Test Results

Automated test suite execution (`py -3.11 -m pytest tests/ -v`):

```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\pharmasafe-kg
collected 34 items

tests/test_api_client.py::TestAPIClient::test_check_unresolved_drugs PASSED [  2%]
tests/test_api_client.py::TestAPIClient::test_check_valid_combination PASSED [  5%]
tests/test_api_client.py::TestAPIClient::test_check_validation_too_few PASSED [  8%]
tests/test_api_client.py::TestAPIClient::test_drug_info_not_found PASSED [ 11%]
tests/test_api_client.py::TestAPIClient::test_health_endpoint PASSED     [ 14%]
tests/test_api_client.py::TestAPIClient::test_search_endpoint PASSED     [ 17%]
tests/test_gnn.py::TestGNN::test_gnn_predict_known_pair PASSED           [ 20%]
tests/test_gnn.py::TestGNN::test_gnn_predict_oov PASSED                  [ 23%]
tests/test_gnn.py::TestGNN::test_gnn_predictor_singleton PASSED          [ 26%]
tests/test_models.py::TestModels::test_check_request_too_few_drugs PASSED [ 29%]
tests/test_models.py::TestModels::test_check_request_too_many_drugs PASSED [ 32%]
tests/test_models.py::TestModels::test_check_request_whitespace_stripping PASSED [ 35%]
tests/test_models.py::TestModels::test_interaction_result_defaults PASSED [ 38%]
tests/test_models.py::TestModels::test_predicted_interaction_result PASSED [ 41%]
tests/test_models.py::TestModels::test_valid_check_request PASSED        [ 44%]
tests/test_p0_pipeline.py::TestP0WindowsSafePhase1::test_utils_print_section_ascii_safe PASSED [ 47%]
tests/test_p0_pipeline.py::TestP0WindowsSafePhase1::test_utils_write_report_ascii_safe PASSED [ 50%]
tests/test_p0_pipeline.py::TestP0SeverityRegeneration::test_severity_distribution_calibrated PASSED [ 52%]
tests/test_p0_pipeline.py::TestP0SeverityRegeneration::test_no_missing_severities PASSED [ 55%]
tests/test_p0_pipeline.py::TestP0SeverityRegeneration::test_no_pairwise_duplicates PASSED [ 58%]
tests/test_p0_pipeline.py::TestP0SeverityRegeneration::test_no_self_interactions PASSED [ 61%]
tests/test_p0_pipeline.py::TestP0ColabDataProvenance::test_node_feature_order_and_alignment PASSED [ 64%]
tests/test_p0_pipeline.py::TestP0ColabDataProvenance::test_deterministic_sha256_features PASSED [ 67%]
tests/test_p0_pipeline.py::TestP0ColabDataProvenance::test_negative_sampling_zero_positive_overlap PASSED [ 70%]
tests/test_p0_pipeline.py::TestP0ColabDataProvenance::test_no_self_edges PASSED [ 73%]
tests/test_p0_pipeline.py::TestP0GNNLeakageFreeSplit::test_leakage_free_edge_index_construction PASSED [ 76%]
tests/test_resolver.py::TestResolver::test_resolve_alias PASSED          [ 79%]
tests/test_resolver.py::TestResolver::test_resolve_case_and_whitespace_insensitivity PASSED [ 82%]
tests/test_resolver.py::TestResolver::test_resolve_direct_generic PASSED [ 85%]
tests/test_resolver.py::TestResolver::test_resolve_exact_brand_combination PASSED [ 88%]
tests/test_resolver.py::TestResolver::test_resolve_fuzzy_brand PASSED    [ 91%]
tests/test_resolver.py::TestResolver::test_resolve_multiple PASSED       [ 94%]
tests/test_resolver.py::TestResolver::test_resolve_not_found PASSED      [ 97%]
tests/test_resolver.py::TestResolver::test_search_autocomplete PASSED    [100%]

======================= 34 passed, 2 warnings in 45.39s =======================
```

---

## 10. Remaining Work

The following items are intentionally **NOT DONE** in this P0 phase:
1. **Model Retraining:** Google Colab training with `MP.ipynb` on GPU has not yet been triggered.
2. **Model Weight Replacement:** `phase4/graphsage_weights.pt`, `node_embeddings.pt`, and `gat_weights.pt` remain the previous checkpoint until Google Colab retraining is executed.
3. **Docker & Deployment:** Containerization and Cloud Run deployment remain scheduled for subsequent deployment phases.
4. **UI Refinements:** Streamlit interface enhancements remain in Phase 5 scope.
5. **Research Paper Metric Updates:** Final benchmark comparison table (Table 2) will be populated directly from the leakage-free Colab evaluation output.

---

## 11. Pre-Retraining Checklist

Before running `phase4/MP.ipynb` in Google Colab:
- [x] Phase 1 `drugbank_ddi_cleaned.csv` verified with 73.34% MODERATE / 22.22% MAJOR.
- [x] `phase4/colab_data/` files freshly exported.
- [x] `phase4/MP.ipynb` updated with deterministic seeds and leakage-free splitting.
- [x] All 34 automated unit and pipeline regression tests passing.
- [ ] Upload `phase4/colab_data/` (`nodes.csv`, `edges.csv`, `node_features.csv`) to Google Drive path `/content/drive/MyDrive/pharmasafe-kg/colab_data/`.
- [ ] Open `phase4/MP.ipynb` in Google Colab, select T4 GPU runtime, and run all cells.
- [ ] Download new weights (`graphsage_weights.pt`, `node_embeddings.pt`, `gat_weights.pt`, `training_curves.png`) into `phase4/`.
