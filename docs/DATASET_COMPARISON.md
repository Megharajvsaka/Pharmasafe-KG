# PharmaSafe-KG — Comparative Analysis of Biomedical DDI Datasets
**Project:** PharmaSafe-KG (Explainable Knowledge Graph + GNN for Drug-Drug Interaction Detection)  
**Document Type:** Research Dataset Evaluation & Architecture Proposal  
**Author:** AI Systems Engineering Team  
**Date:** August 30, 2026  

---

## 1. Executive Summary

This document presents a comprehensive comparative evaluation of prominent public and research-accessible Drug-Drug Interaction (DDI) datasets. The objective is to determine whether incorporating secondary data sources alongside the primary **DrugBank** foundation would enhance the scientific rigor, clinical fidelity, and topological coverage of the PharmaSafe-KG Knowledge Graph and Graph Neural Network (GNN).

Rather than indiscriminately expanding dataset size (which risks severe semantic degradation, entity misalignment, and graph budget exhaustion on cloud infrastructure), we evaluate candidates against four strict research criteria:
1. **Identifier Interoperability:** Compatibility with standardized generic vocabularies (INN, DrugBank ID, PubChem CID, RxNorm).
2. **Clinical Severity Grading:** Existence of explicit, validated 3-tier or 4-tier severity tiers (Major/Moderate/Minor/Contraindicated).
3. **Mechanistic Explainability (XAI):** Availability of structured pharmacodynamic (PD) or pharmacokinetic (PK) mechanism explanations.
4. **Polypharmacy Suitability:** Feasibility for higher-order combination checks without introducing transductive label leakage.

---

## 2. Comparative Evaluation Matrix

| Dataset | Primary Source / Authors | Version / Year | Drug Count | Interaction Count | Interaction Type | Severity Grading | Mechanism Text | Identifiers | License / Access | PharmaSafe-KG Recommendation |
|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **DrugBank** *(Current Primary)* | Wishart et al., University of Alberta | 5.1.x (2024/2026) | ~2,000–2,500 approved | 222,696 raw (92,161 clean unique) | Binary Pairwise | Inferred via NLP Keyword Parser | Detailed English text (81.2% coverage) | DrugBank ID, Generic Name, UNII | Academic / Research Use | **CORE BENCHMARK (USE)** |
| **DDInter** | Zheng et al., *Nucleic Acids Res.* | 2022 / 2024 update | 2,042 approved | 225,000+ interactions | Binary Pairwise | Explicit 4-tier (`Major`, `Moderate`, `Minor`, `Contraindicated`) | Categorized (PK: CYP enzyme; PD: synergism) | DrugBank ID, PubChem CID, MeSH | Open Academic Research | **HIGH-PRIORITY EXPANSION (RECOMMENDED)** |
| **TWOSIDES** | Tatonetti et al., *Sci. Transl. Med.* | 2012 / 2016 | 645 drugs | 4,600,000+ triplets | Higher-Order (Drug A + Drug B $\rightarrow$ Adverse Event) | Quantified via Proportional Reporting Ratio (PRR) | Specific MedDRA Adverse Event Terms (1,300+ AEs) | RxNorm, UMLS CUI, DrugBank ID | Open Science (Zenodo / PhysioNet) | **FUTURE EXTENSION (INVESTIGATE FOR PHASE 6)** |
| **LIDDI (Literature-Derived DDI)** | Text-mined PubMed extractions | 2018–2021 | ~1,200 | ~50,000–120,000 | Binary Pairwise | None (Confidence score only) | Raw extracted literature sentences | MeSH, PubChem | Open Academic | **DO NOT USE (High False Positive Rate)** |
| **HODDI (Higher-Order DDI)** | Curated polypharmacy benchmarks | 2020–2023 | ~800 | ~15,000 triplets/quads | 3+ Drug Combinations | Qualitative risk assessment | Synergistic pathway interference | DrugBank ID, PubChem CID | Research Only | **SPECIALIZED BENCHMARK ONLY** |
| **FDA DailyMed / NDC** | US National Library of Medicine | Weekly (Live) | 40,000+ products | Variable (SPL Structured Labels) | Regulatory Label warnings | Boxed Warnings, Precautions | Regulatory Narrative | NDC, UNII, RxNorm | Public Domain (US Gov) | **REFERENCE ONLY (Raw parsing required)** |

---

## 3. In-Depth Dataset Profiles

### 3.1. DrugBank (Current Primary Knowledge Base)
* **Overview:** The golden standard in academic pharmacology and chemoinformatics. Contains detailed molecular properties, targets, enzymes, and curated pairwise interactions.
* **Advantages for PharmaSafe-KG:**
  - High linguistic quality of mechanism descriptions (e.g., *"The risk or severity of bleeding can be increased when Warfarin is combined with Aspirin"*).
  - Direct 1:1 mapping with standardized INN (International Nonproprietary Names) and Indian drug master records.
  - Complete graph topology suitable for both homogeneous and heterogeneous message-passing GNNs.
* **Limitations:**
  - Raw DrugBank does not provide explicit `MAJOR` / `MODERATE` / `MINOR` severity columns; severities must be inferred via calibrated pharmacological keyword parsers.
* **Role:** Remains the **primary ground truth** for PharmaSafe-KG graph construction.

---

### 3.2. DDInter (Recommended Secondary Validation & Enrichment Source)
* **Overview:** Developed by the Pharmacogenomics and Chemoinformatics Lab at Zhejiang University (*Nucleic Acids Research*, 2022). Specifically designed to harmonize DDI data from clinical guidelines, regulatory approvals, and pharmacological literature.
* **Key Strengths:**
  1. **Pre-Graded Clinical Severity:** Unlike DrugBank, DDInter natively tags interactions into `Major`, `Moderate`, `Minor`, and `Contraindicated`, calibrated against clinical guideline databases (Lexicomp, Micromedex).
  2. **Pharmacokinetic/Pharmacodynamic Annotations:** Categorizes interactions by mechanism (e.g., CYP3A4 inhibition, P-glycoprotein transport interference, QT interval prolongation).
  3. **Direct Identifier Overlap:** Uses DrugBank IDs as primary keys, allowing lossless intersection with the existing PharmaSafe-KG graph.
* **Integration Roadmap:**
  - Use DDInter as a **ground-truth validation benchmark** to verify our NLP-inferred DrugBank severities.
  - Enrich Neo4j `INTERACTS_WITH` relationships with multi-source evidence tags (`source: ["DrugBank", "DDInter"]`).

---

### 3.3. TWOSIDES (Polypharmacy Side-Effect Profile)
* **Overview:** Part of the Columbia University Adverse Drug Event repository (Tatonetti et al.). Extracted from the FDA Adverse Event Reporting System (FAERS) by applying statistical disproportionality algorithms to eliminate confounding prescribing biases.
* **Key Strengths:**
  - True polypharmacy side-effect grounding: identifies exact clinical conditions caused by combinations (e.g., `Gastrointestinal Bleeding`, `Rhabdomyolysis`, `Acute Kidney Injury`).
* **Limitations:**
  - Huge dataset volume (4.6M edges across 645 drugs) exceeds Neo4j AuraDB free-tier relationship budgets (200K limit).
  - Heavy skew toward polypharmacy adverse event discovery rather than standard therapeutic contraindications.
* **Recommendation:**
  - Do NOT load the full 4.6M graph into Neo4j.
  - Create a filtered sub-graph of top-50 high-mortality adverse events for future polypharmacy risk scoring.

---

### 3.4. LIDDI & Open Literature Text-Mining
* **Overview:** Automatically generated datasets using NLP Named Entity Recognition (NER) and Relation Extraction (RE) models over PubMed abstracts.
* **Evaluation:**
  - High false-positive rate: Co-occurrence of two drugs in an abstract describing a clinical trial does not imply a hazardous pharmacological interaction.
  - Lacks consistent severity grading.
* **Recommendation:** **DO NOT USE.** Introducing uncurated text-mined edges would degrade the high clinical fidelity of PharmaSafe-KG.

---

## 4. Architectural Recommendation for Next Phase

1. **Maintain Phase 1 DrugBank as Master Topology:**
   - The 92,161 cleaned, calibrated DrugBank pairs provide an optimal 1,761-node dense topological backbone for GNN training (129,024 message-passing edges).
2. **Incorporate DDInter as Multi-Source Clinical Provenance:**
   - In the next developmental iteration, cross-reference the 92,161 pairs against DDInter to attach secondary verification tags (`ddinter_severity`, `evidence_sources: ["DrugBank", "DDInter"]`).
3. **Strict Separation of Documented vs Inductive Evidence:**
   - All external datasets populate the **Knowledge Graph layer (`source: "knowledge_graph"`)**.
   - The **GNN layer (`source: "gnn_predicted"`)** remains reserved for unknown/unindexed pairs, returning link probabilities with explicit `severity: "UNKNOWN"` until clinical validation.
