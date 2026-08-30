# PharmaSafe-KG — Model Card: GraphSAGE Link Predictor
**Model Name:** GraphSAGE-DDI (PharmaSafe-KG Inductive Link Prediction Engine)  
**Version:** 1.0.0-calibrated  
**Date:** August 30, 2026  
**License:** Academic Research Use  
**Authors:** PharmaSafe-KG Engineering Team  

---

## 1. Model Overview
The **GraphSAGE-DDI** model is an inductive Graph Neural Network trained to predict the likelihood of pairwise pharmacological drug-drug interactions (DDIs) between active pharmaceutical ingredients. It operates as an AI inference fallback for candidate drug pairs not yet documented in the primary Knowledge Graph.

---

## 2. Intended Use
* **Primary Task:** Binary link prediction on pharmaceutical interaction graphs.
* **Input:** A pair of generic drug identifiers $(u, v)$ present in the training vocabulary ($N = 1,761$).
* **Output:** Interaction probability $p \in [0.0, 1.0]$ via dot-product decoder $\sigma(\mathbf{z}_u^T \mathbf{z}_v)$.
* **Out-of-Scope Uses:**
  - Automated clinical prescribing without physician oversight.
  - Extrapolation of clinical severity (the GNN predicts *interaction likelihood*, not severity grade).
  - Pure out-of-vocabulary (OOV) zero-shot drug prediction without molecular feature computation.

---

## 3. Model Architecture

```
Node Features x_u in R^10
         │
         ▼
SAGEConv(10 -> 128)  ──> BatchNorm1d ──> ReLU ──> Dropout(0.3)
         │
         ▼
SAGEConv(128 -> 64)  ──> BatchNorm1d ──> ReLU ──> Dropout(0.3)
         │
         ▼
SAGEConv(64 -> 64)   ──> Output Node Embedding z_u in R^64
         │
         ▼
Decoder: Score = dot(z_u, z_v) ──> Sigmoid ──> Interaction Probability p
```

* **Aggregation Type:** Mean neighborhood aggregation (`aggr='mean'`).
* **Input Feature Dimension ($d=10$):**
  - Dimensions 0–7: Deterministic SHA-256 character hash bits.
  - Dimension 8: DrugBank vocabulary membership flag ($1.0$).
  - Dimension 9: Normalized node degree in the training graph ($\frac{\text{deg}_{\text{train}}(u)}{100.0}$).
* **Total Trainable Parameters:** ~22,000.

---

## 4. Training Data & Provenance
* **Source Graph:** 92,161 clean positive interaction pairs ($1,761$ generic drug nodes) derived from DrugBank Release 5.1.x.
* **Negative Sampling:** 50,000 verified non-edges sampled uniformly at random with strict bidirectional non-overlapping constraint.
* **Train/Validation/Test Split:**
  - **Training Set (70%):** 64,512 positive pairs + 35,000 negative pairs ($N_{\text{total}} = 99,512$).
  - **Validation Set (15%):** 13,824 positive pairs + 7,500 negative pairs ($N_{\text{total}} = 21,324$).
  - **Test Set (15%):** 13,825 positive pairs + 7,500 negative pairs ($N_{\text{total}} = 21,325$).
* **Leakage-Free Guarantee:** The message-passing computational graph `train_edge_index` consists strictly of the 64,512 positive training edges ($129,024$ directed edges). Validation and test edges are strictly excluded from neighborhood aggregation.

---

## 5. Quantitative Evaluation Metrics

All metrics were computed on the held-out **Test Set ($N = 21,325$ candidate pairs)** at threshold $\tau = 0.50$:

| Metric | GraphSAGE (Primary) | GAT (Baseline) | Interpretation |
|---|:---:|:---:|---|
| **ROC-AUC** | **0.8834** | 0.8753 | High discriminative ranking capacity |
| **F1-Score** | **0.8330** | 0.7867 | Strong balance between precision and recall |
| **Precision** | **0.7215** | 0.6484 | 72.2% of predicted links are true positives |
| **Recall** | **0.9851** | 0.9999 | Captures 98.5% of true pharmacological interactions |

---

## 6. Inference Semantics & Safety Disclaimers

In the PharmaSafe-KG runtime engine (`phase3/app/query_engine.py`):
1. **Decision Threshold:** A conservative operating threshold of $\tau = 0.70$ is applied for link prediction alerts to minimize false positives.
2. **Clinical Severity:** GNN predictions return `severity = "UNKNOWN"` / `"UNASSESSED"`. The GNN does not fabricate clinical severity grades without empirical trial data.
3. **Evidence Tag:** All GNN predictions carry explicit metadata tags:
   ```json
   {
     "status": "predicted",
     "source": "gnn_predicted",
     "confidence": 0.824,
     "severity": "UNKNOWN",
     "evidence": [{"model": "GraphSAGE", "probability": 0.824, "threshold": 0.70}]
   }
   ```
