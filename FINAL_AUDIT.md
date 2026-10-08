# FINAL END-TO-END AUDIT REPORT

**Project Title:**  
*An Intelligent Recommender System Using Machine Learning, Association Rules and Rough Set for Disease Prediction from Incomplete Symptom Set*

**Audit Completion Date:** 2026-10-08  
**Audit Status:** COMPLETE & VERIFIED  
**Overall Verdict:** **ALL 10 CATEGORIES PASSED (10/10 PASS)**  

---

## 1. Final Audit Verdict Summary

| Category | Status | Verification Criteria & Evidence |
|---|:---:|---|
| **1. Mathematical Correctness** | **PASS** | Axioms of Pawlak (1982) verified; $\gamma_C(D) = 1.0000$; Skowron discernibility matrix ($45,023$ pairs); rigorous proof that $CORE(C) = \emptyset$ via indispensable attribute theorem and singleton clause theorem. |
| **2. Data Leakage** | **PASS** | `Testing.csv` ($N = 42$) is completely isolated. Zero access during discernibility matrix creation, dependency calculation, core evaluation, reduct generation, association rule mining, ML baseline fitting, or follow-up selection. |
| **3. RST Implementation** | **PASS** | 38-attribute Johnson candidate achieves $\gamma_{R_{38}}(D) = 1.0000$. Exhaustive backward deletion across all 38 attributes proves inclusion-minimality (every removal yields $\gamma < 1.0$). Global minimum cardinality is explicitly disclaimed. |
| **4. Incomplete Reasoning** | **PASS** | Tri-state alphabet enforced ($1=\text{present}$, $0=\text{absent}$, $?=\text{unknown}$). $?$ is never converted to 0 in RST. Compatibility/tolerance relation $T(q, x)$ correctly formulated (non-transitive, reflexive, symmetric). Tolerance neighborhood $[q]_T$ derived. Disambiguation Power Heuristic variance formula audited and labeled. |
| **5. Association Rules** | **PASS** | 831 disease-consequent rules mined strictly from `Training.csv` ($N = 4,920$) with $\text{min\_support}=0.01$ and $\text{min\_confidence}=0.70$. Support, confidence, and lift match backend artifacts. |
| **6. ML Comparison** | **PASS** | `BernoulliNB` verified as primary Naive Bayes baseline for binary $\{0, 1\}$ symptoms. Imputation ($? \to 0$) declared as ML-specific baseline assumption that never interferes with RST. |
| **7. Backend Software Quality** | **PASS** | Modular FastAPI architecture. All 11 unit/integration tests passing (`pytest backend/tests/ -v`). Clear separation between model preparation ($7.59$s) and offline benchmarking suite ($20.50$s). |
| **8. Frontend Quality & Design** | **PASS** | React + TypeScript + Vite + Tailwind CSS. Production build passes with 0 errors. High-contrast academic theme, responsive layouts, interactive symptom toggle buttons, no placeholder text. |
| **9. Browser QA** | **PASS** | Verified in real Chromium browser across Scenarios A through J: Complete Dengue, 50% Unknown Dengue, Boundary Ambiguity, 1-Symptom query, 132-Unknown query (Insufficient Information card), Tab navigation, Mobile/Desktop layouts. Zero console errors. |
| **10. Reproducibility** | **PASS** | Completely reproducible: running `python -m app.pipeline.train_and_cache` regenerates all 7 disk artifacts from raw CSVs with identical metrics and zero variance. |

---

## 2. Terminology & Conceptual Audit

### 2.1 Complete Training Objects vs Incomplete Query Objects
- **Complete Training Universe ($U$):**
  - Consists of $N = 4,920$ objects where all 132 symptoms are known binary values $\{0, 1\}$.
  - The indiscernibility relation $IND(C)$ satisfies **reflexivity, symmetry, and transitivity**.
  - Classical Pawlak indiscernibility/equivalence terminology is mathematically valid: $IND(C)$ partitions $U$ into **304 disjoint equivalence classes**.
- **Incomplete Query Objects ($q$):**
  - An incoming query $q \in \{0, 1, ?\}^{|C|}$ contains unobserved attributes ($?$).
  - Transitivity does not hold across partial symptom observations.
  - The query relation is formally designated as the **selected baseline compatibility / tolerance relation** $T(q, x)$, **NOT** a classical Pawlak equivalence relation.
  - It induces a **tolerance neighborhood** $[q]_T = \{ x \in U \mid \forall a \in Known(q), q(a) = x(a) \}$ rather than a partition.
- **Frontend & Backend Labels:**
  All UI labels and API schemas have been audited to eliminate misleading terminology:
  - `"Lower Approximation under selected tolerance relation T_*(X) — Deterministic Certainty"`
  - `"Boundary Region under selected tolerance relation BN_T(X) — Incomplete Information Ambiguity"`
  - `"Upper Approximation under selected tolerance relation T^*(X) — Plausible Candidate"`
  - Table header: `"Approximation Status (Tolerance Relation)"`

---

## 3. Disambiguation-Score Audit: Discriminative Power Heuristic

### 3.1 Mathematical Formulation
When a query falls in the boundary region ($BN_T(X)$), the active recommender calculates the **Discriminative Power Heuristic** for unobserved symptoms $a \in Unknown(q)$:
$$\text{Var}(p(a)) = \frac{1}{K} \sum_{k=1}^K (p_k(a) - \bar{p}(a))^2$$
where:
- $K = \min(3, |\text{Candidate Diseases in } [q]_T|)$ is the number of top competing candidate diseases.
- $p_k(a) = \frac{1}{|U_{d_k}|} \sum_{x \in U_{d_k}} x(a)$ is the empirical prevalence of symptom $a$ among training instances of disease class $d_k \in D$.
- $\bar{p}(a) = \frac{1}{K} \sum_{k=1}^K p_k(a)$ is the average prevalence across the top candidate diseases.

### 3.2 Audit Properties
- **Inputs:** Unknown query attributes $Unknown(q)$, top candidate disease cohorts, complete training profiles in $U$.
- **Normalization:** Bounded in $[0, 0.25]$ (Bernoulli variance maximum is $0.5 \times 0.5 = 0.25$). Filtered for informative symptoms with $\text{Var}(p(a)) > 0.05$.
- **Classification:** It is a **project-specific heuristic**, **NOT** a standard classical Pawlak Rough Set metric. It is explicitly labeled in UI and schemas as the **"Discriminative Power Heuristic"**.
- **Interpretation:** **Higher means more useful.** Symptoms with higher variance exhibit the sharpest diagnostic contrast between competing diseases, maximizing disambiguation potential when answered.

---

## 4. Final Data Leakage Audit

A comprehensive variable scope and call graph audit verified:
- `Testing.csv` ($N = 42$) is **strictly quarantined**.
- It is **never** loaded or accessed during:
  1. Reduct generation (Johnson algorithm, QuickReduct)
  2. Dependency degree calculation ($\gamma_C(D)$)
  3. Core calculation ($CORE(C)$)
  4. Skowron discernibility matrix computation
  5. Association rule mining (Apriori)
  6. Machine learning baseline fitting (`RandomForest`, `BernoulliNB`, `LogisticRegression`, `DecisionTree`)
  7. Threshold selection or hyperparameter tuning
  8. Follow-up symptom recommendation (active disambiguation)
- `Testing.csv` is accessed solely in `incomplete_benchmark.py` during final offline evaluation.

---

## 5. Final RST Mathematical Audit

- **Full Dependency Degree:**
  $$\gamma_C(D) = \frac{|POS_C(D)|}{|U|} = \frac{4920}{4920} = \mathbf{1.0000}$$
  The 132 symptom attributes provide a totally consistent decision table with zero decision collisions.

- **38-Attribute Reduct Candidate ($R_{38}$):**
  - Generated via Johnson's greedy discernibility hitting set algorithm in **0.4359s**.
  - Preserves full dependency: $\gamma_{R_{38}}(D) = \mathbf{1.0000}$.
  - Backward single-attribute deletion test: evaluated across all 38 attributes:
    - **All 38 / 38 single-attribute removals strictly decrease dependency** ($\gamma < 1.0000$).
    - Minimum dependency upon removal: $0.9427$; Maximum: $0.9976$; Mean: $0.9891$.
    - **Proven strictly inclusion-minimal under Pawlak's criterion.**
    - Reduces condition attributes by **71.2%** (from 132 to 38 symptoms).
  - **Disclaimer:** Global minimum-cardinality reduct discovery is NP-hard. $R_{38}$ is an inclusion-minimal candidate; it is **NOT** claimed to be the global minimum.

- **Proof of $CORE(C) = \emptyset$:**
  1. *Pawlak Indispensable Attribute Theorem:* Evaluated $\gamma_{C \setminus \{a\}}(D)$ for all 132 attributes. Every attribute yields $\gamma = 1.0000$. Hence, $|CORE(C)| = 0$.
  2. *Skowron Singleton Clause Theorem:* Evaluated all 45,023 object pairs between distinct disease profiles in the discernibility matrix. Minimum clause size is 2; singleton clauses ($|c_{ij}|=1$) count is exactly **0**.
  3. *Conclusion:* $CORE(C) = \emptyset$ is mathematically proven.

---

## 6. Final Incomplete-Information Audit

- **Tri-State Semantics:**
  - `1`: Present
  - `0`: Absent
  - `?`: Unknown
- **Non-Interference Rule:** `?` is **never converted to 0** in the Rough Set reasoning engine.
- **Attributes Excluded from Compatibility:**
  Attributes where $q(a) = {?}$ are ignored during comparison:
  $$T(q, x) \iff \forall a \in Known(q), q(a) = x(a)$$
- **Behaviors Verified:**
  - *Complete Input:* Matches exact equivalence class; returns lower approximation (100% confidence).
  - *50% Unknown Input:* Retains 100% confidence in lower approximation without zero penalty.
  - *Ambiguous Input (e.g. 1 symptom):* $[q]_T$ expands across multiple diseases; returns boundary region and displays active disambiguation cards.
  - *Zero-Known Input (132 unknowns):* $[q]_T = U$ ($N = 4,920$). System returns explicit **"Insufficient Information"** status.

---

## 7. Final Empirical Evaluation Audit

### 7.1 Delineation of Query Counts
- **Final Evaluation Queries (882 queries):**  
  Used for computing final metrics table: $0\%$ evaluated once ($42 \times 1 = 42$), plus 4 incomplete rates evaluated with 5 repetitions ($4 \times 5 \times 42 = 840$). Total = **882 queries**.
- **Runtime Benchmark Queries (1,050 queries):**  
  Used in `run_benchmark()` for latency: 5 rates evaluated with 5 repetitions ($5 \times 5 \times 42 = \mathbf{1,050 \text{ queries}}$) across 5 models ($5,250$ inferences).

### 7.2 Audited Rough Set Evaluation Results

| Missing Rate | Test Cases | Reps | Queries | Top-1 Accuracy (Mean $\pm$ Std) | Top-3 Accuracy (Mean $\pm$ Std) | Weighted Precision | Weighted Recall | Weighted F1 | Lower Approx Coverage | Avg Candidates in $[q]_T$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **0%** | 42 | 1 | 42 | **1.0000 $\pm$ 0.0000** | **1.0000 $\pm$ 0.0000** | 1.0000 | 1.0000 | 1.0000 | 100.0% | 1.00 |
| **10%** | 42 | 5 | 210 | **0.9952 $\pm$ 0.0095** | **1.0000 $\pm$ 0.0000** | 0.9976 | 0.9952 | 0.9952 | 99.05% | 1.01 |
| **30%** | 42 | 5 | 210 | **0.9952 $\pm$ 0.0095** | **1.0000 $\pm$ 0.0000** | 0.9976 | 0.9952 | 0.9952 | 97.62% | 1.03 |
| **50%** | 42 | 5 | 210 | **0.9857 $\pm$ 0.0117** | **0.9952 $\pm$ 0.0095** | 0.9929 | 0.9857 | 0.9857 | 93.81% | 1.09 |
| **70%** | 42 | 5 | 210 | **0.8524 $\pm$ 0.0486** | **0.9476 $\pm$ 0.0278** | 0.8020 | 0.8524 | 0.8167 | 70.95% | 1.48 |

### 7.3 Comparative Model Trajectory Under Incomplete Information

| Model | 0% Missing | 10% Missing | 30% Missing | 50% Missing | 70% Missing | Degradation at 70% |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Rough Set Theory (Top-1)** | **100.0%** | **99.52%** | **99.52%** | **98.57%** | **85.24%** | **-14.76%** |
| **Rough Set Theory (Top-3)** | **100.0%** | **100.0%** | **100.0%** | **99.52%** | **94.76%** | **-5.24%** |
| **Bernoulli Naive Bayes** | 100.0% | 98.57% | 98.10% | 94.76% | 75.71% | -24.29% |
| **Logistic Regression** | 100.0% | 99.52% | 98.10% | 88.10% | 64.76% | -35.24% |
| **Random Forest (100 Trees)** | 97.62% | 96.67% | 94.76% | 90.00% | 63.33% | -34.29% |
| **CART Decision Tree** | 97.62% | 92.86% | 82.38% | 62.38% | **36.67%** | **-60.95%** |

---

## 8. ML Baseline Audit

- **Model Choice:** `BernoulliNB` verified as the principled Naive Bayes classifier for binary $\{0, 1\}$ indicator features. It models both presence ($P(x_i=1 \mid d)$) and absence ($P(x_i=0 \mid d)$), unlike `MultinomialNB`.
- **Baseline Imputation Policy:** Missing attributes are imputed to 0 ($? \to 0$) solely as an **explicit ML baseline assumption**.
- **Strict Non-Interference:** This imputation policy is strictly quarantined to ML classifiers and does **not** affect Rough Set Theory.

---

## 9. Association Rules Audit

- **Dataset Source:** One-hot encoded `Training.csv` ($N = 4,920$).
- **Rule Count:** Exactly **831 disease-consequent rules** mined via Apriori ($\text{min\_support}=0.01$, $\text{min\_confidence}=0.70$).
- **Sample Verified Rules:**
  - `['nodal_skin_eruptions'] -> 'Fungal infection'` (Confidence: 100.0%, Lift: 41.0x, Support: 2.2%)
  - `['shivering'] -> 'Allergy'` (Confidence: 100.0%, Lift: 41.0x, Support: 2.2%)
  - `['ulcers_on_tongue'] -> 'GERD'` (Confidence: 100.0%, Lift: 41.0x, Support: 2.2%)
- Displayed UI values match backend artifacts exactly.

---

## 10. Computational Runtime Profiling

| Stage | Operation | Time (seconds) |
|---|---|:---:|
| **Preparation** | Ingestion & Dataset Validation | 0.0591s |
| | Preprocessing & Decision Table | 0.0125s |
| | RST Dependency Calculation ($\gamma_C(D)$) | 0.5763s |
| | Discernibility Matrix (45,023 pairs) | 0.6259s |
| | Reduct Candidates Generation | 4.9126s |
| | Association Rule Mining (Apriori) | 0.6194s |
| | ML Baseline Fitting (4 models) | 0.7832s |
| **Subtotal** | **Pure Model & Knowledge Artifact Generation** | **7.5890s** |
| **Benchmarking** | Offline Research Benchmarking (1,050 multi-model queries) | 20.4979s |
| | Latency Profiling (500 test queries) & Artifact Serialization | 0.4106s |
| **Total** | **Full Pipeline Execution Script** | **28.4975s** |

### Online Latencies:
- **In-Memory Python Inference:** Mean: **0.657 ms** (p50: 0.609 ms, p95: 0.981 ms)
- **FastAPI HTTP Request Latency:** Mean: **6.82 ms** (p50: 5.57 ms, p95: 10.44 ms)

---

## 11. Known Limitations

> [!WARNING]
> **Mandatory Academic Evaluation Limitation Notice:**  
> *"The held-out test set contains only 42 records, so these results are empirical for this dataset and should not be interpreted as clinical generalization."*

1. **Only 42 Held-Out Test Records:** The official test dataset contains exactly 42 records across 41 disease classes (approximately 1 record per class).
2. **Dataset-Specific Empirical Results:** All reported accuracies, coverages, and degradations are empirical findings on this benchmark dataset. They should not be interpreted as generalizable clinical evidence.
3. **Selected Baseline Incomplete-Information Relation:** The compatibility/tolerance relation $T(q, x)$ comparing objects solely on known query attributes is the selected baseline; faculty may specify alternative generalized incomplete rough set formulations in future work.
4. **Inclusion-Minimal Reducts, Not Globally Minimum:** Reduct candidates (e.g., 38 attributes) are inclusion-minimal under Pawlak's dependency criterion, not proven to be the global minimum-cardinality reduct (which is NP-hard).
5. **Academic Decision-Support Prototype:** This system is an academic research demonstration of Rough Set Theory and Machine Learning, strictly NOT a medical diagnostic tool or clinical software.

---

## 12. Final Certification

This final audit confirms that:
1. All mathematical axioms of Pawlak Rough Set Theory and Skowron discernibility are strictly honored.
2. The compatibility/tolerance relation for incomplete queries is mathematically sound, cleanly separated from classical equivalence, and accompanied by the audited Discriminative Power Heuristic.
3. The codebase has zero data leakage, passes all automated unit and integration tests, compiles cleanly without warnings, and operates smoothly in browser testing.
4. All metrics, query counts, and runtimes are transparently delineated and audited.

**Signed:** AI/ML Research Engineering Team  
**Status:** **APPROVED & COMPLETE**
