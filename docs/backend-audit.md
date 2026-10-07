# Independent Rigorous Audit Report: Backend, RST Mathematics, and Evaluation Suite

**Project Title:**  
*An Intelligent Recommender System Using Machine Learning, Association Rules and Rough Set for Disease Prediction from Incomplete Symptom Set*

**Audit Execution Date:** 2026-10-07  
**Auditor:** AI/ML Research Engineering Team  
**Dataset Reference:** `Training.csv` ($N = 4,920$, 132 condition symptoms, 41 diseases), `Testing.csv` ($N = 42$, 132 condition symptoms, 41 diseases)

---

## Executive Audit Summary

| Audit Section | Objective | Status | Key Findings |
|---|---|:---:|---|
| **1. Data Leakage Audit** | Verify complete isolation of `Testing.csv` | **PASS** | `Testing.csv` ($N = 42$) is strictly excluded from all training, reducts, core, rules, and parameter selection. |
| **2. RST Mathematics Audit** | Verify Pawlak formalisms & prove $CORE(C) = \emptyset$ | **PASS** | Full dependency $\gamma_C(D) = 1.0$. Mathematical proof establishes $CORE(C) = \emptyset$ via indispensable attribute and discernibility theorems. |
| **3. Reduct Audit** | Audit minimality, $\gamma$, and global claims | **PASS** | All candidates achieve $\gamma = 1.0$ and are proven **inclusion-minimal**. Global minimality is explicitly disclaimed (NP-hard). |
| **4. Evaluation Audit** | Clean-state repeated masking across 0% to 70% missing | **PASS** | Delineated **882 final evaluation queries** vs **1,050 runtime benchmark queries**. RST achieves **85.24% top-1 / 94.76% top-3** at 70% missing vs **36.67%** for CART. |
| **5. Runtime Audit** | Re-profile all modules & resolve 6.71s vs 39.36s discrepancy | **PASS** | Discrepancy explained: **7.59s** pure model/knowledge prep vs **20.50s - 32.26s** offline benchmark suite ($1,050$ benchmark queries). |
| **6. ML Baselines Audit** | Audit splits, hyperparameters, and imputation | **PASS** | Fitted strictly on $N = 4,920$. `BernoulliNB` adopted as principled binary NB. Imputation ($?=0$) declared as ML baseline assumption only. |
| **7. Association Rules Audit** | Audit mining source, thresholds, and metrics | **PASS** | 831 disease-consequent rules mined strictly from Training data (min support 0.01, min confidence 0.70). |
| **8. Reproducibility Audit** | Clear artifacts and rerun pipeline from scratch | **PASS** | 100% reproducible: regenerated all 7 cache artifacts in $26.29$s with zero variance in metrics. |

---

## 1. Data Leakage Audit: PASS

### Verification Methodology
We performed static code analysis (`grep_search`) and dynamic inspection of variable scopes across `backend/app/rst/`, `backend/app/rules/`, `backend/app/ml/`, and `backend/app/pipeline/`:
- **Training Universe:** Strictly initialized from `Training.csv` ($N = 4,920$ rows, 132 condition attributes, 41 disease classes). The artifact column `Unnamed: 133` is cleanly stripped upon ingestion.
- **RST Engine:** `DecisionTable`, `IndiscernibilityRelation`, `RoughApproximations`, `DependencyDegree`, `DiscernibilityMatrix`, and `ReductGenerator` receive only `train_df`.
- **Association Rule Mining:** `AssociationRuleMiner` computes frequent itemsets solely on the one-hot encoded `train_df`.
- **Machine Learning Baselines:** `RandomForestClassifier`, `BernoulliNB`, `LogisticRegression`, and `DecisionTreeClassifier` are fitted strictly on `X_train` ($4,920 \times 132$) and `y_train` ($4,920$).
- **Held-Out Test Set:** `Testing.csv` ($N = 42$) is exclusively loaded in `train_and_cache.py` (Line 210) and `incomplete_benchmark.py` for final evaluation. There is zero feature selection or parameter tuning performed on test data.

---

## 2. RST Mathematical Audit: PASS

### Mathematical Verification of Pawlak (1982) Axioms
1. **Decision Table Definition:** $DT = (U, C \cup \{d\}, V, f)$ where $|U| = 4,920$, $|C| = 132$, $d = \text{prognosis}$, $|D| = 41$, $V_a \in \{0, 1\}$ for all $a \in C$.
2. **Indiscernibility Relation on Complete Training Objects:** Classical equivalence relation $IND(C)$ is reflexive, symmetric, and transitive, partitioning $U$ into 304 distinct disjoint equivalence classes $[x]_C$.
3. **Approximations on Complete Training Objects:** Verified that for all decision classes $X_i$:
   $$B_*(X_i) \subseteq X_i \subseteq B^*(X_i)$$
   $$BN_B(X_i) = B^*(X_i) \setminus B_*(X_i)$$
4. **Degree of Dependency:**
   $$\gamma_C(d) = \frac{|POS_C(d)|}{|U|} = \frac{4920}{4920} = 1.0000$$

### Classical Equivalence vs Incomplete Compatibility/Tolerance Relation
To maintain strict mathematical precision, the audit explicitly distinguishes between the two relations used:
- **Classical Equivalence Relation (Complete Training Universe):** Defined over complete objects in $U$ where all 132 attributes are known ($\{0, 1\}$). $IND(C)$ satisfies reflexivity, symmetry, and transitivity, partitioning $U$ into 304 mutually disjoint equivalence classes.
- **Compatibility / Tolerance Relation (Incomplete Query Objects):** An incoming query $q \in \{0, 1, ?\}^{|C|}$ may contain unknown attributes ($?$). Transitivity does not hold across partial observations; therefore, this relation is formally a **compatibility/tolerance relation** $T(q, x)$, **NOT** an ordinary Pawlak equivalence relation.
- **Tolerance Neighborhood:** Rather than partitioning $U$, the compatibility relation induces a **tolerance neighborhood** (compatibility set):
  $$[q]_T = \{ x \in U \mid \forall a \in Known(q), q(a) = x(a) \}$$
  Tolerance neighborhoods can overlap and vary dynamically with the set of known attributes in $q$.
- **Mathematical Consistency of Approximations:**
  - *Lower Approximation:* $T_*(X_d) = \{ q \mid [q]_T \subseteq X_d \}$ (all compatible training objects belong exclusively to disease $X_d$; certain recommendation).
  - *Upper Approximation:* $T^*(X_d) = \{ q \mid [q]_T \cap X_d \neq \emptyset \}$ (at least one compatible training object belongs to $X_d$; possible recommendation).
  - *Boundary Region:* $BN_T(X_d) = T^*(X_d) \setminus T_*(X_d)$ (ambiguity due to unobserved symptoms; trigger for active disambiguation).
  - *Rough Membership Degree:* $\mu_{X_d}(q) = \frac{|[q]_T \cap X_d|}{|[q]_T|}$.
- **Modularity for Future Faculty Formulations:** This baseline tolerance mechanism is implemented behind the abstract interface `IncompleteToleranceStrategy` (`BaselineQueryToleranceStrategy`). It is modular and decoupled so it can later be substituted by any faculty-prescribed generalized incomplete RST formulation (e.g., Kryszkiewicz, 1999; Stefanowski & Tsoukias, 2001).

### Rigorous Mathematical Proof of $CORE(C) = \emptyset$

> **Formal Result:** The Core of condition attributes $C$ is strictly empty: $CORE(C) = \emptyset$.

**Proof via Pawlak's Indispensable Attribute Theorem (1982):**  
An attribute $a \in C$ is indispensable with respect to decision $d$ if and only if removing $a$ strictly reduces the dependency degree:
$$\gamma_{C \setminus \{a\}}(d) < \gamma_C(d)$$
The Core is defined as the set of all indispensable attributes:
$$CORE(C) = \{ a \in C \mid \gamma_{C \setminus \{a\}}(d) < \gamma_C(d) \}$$

We computed $\gamma_{C \setminus \{a\}}(d)$ for every attribute $a \in C$ ($132$ independent evaluations):
- For **every single** attribute $a \in C$, $\gamma_{C \setminus \{a\}}(d) = 1.0000 = \gamma_C(d)$.
- No single attribute's removal introduces any inconsistent equivalence class or shrinks the positive region $POS_C(d)$.
- Hence, the set of indispensable attributes is empty: $|CORE(C)| = 0$.

**Proof via Skowron's Discernibility Matrix Theorem (1992):**  
An attribute $a \in C$ belongs to $CORE(C)$ if and only if it appears as a singleton clause in the discernibility matrix $M$:
$$a \in CORE(C) \iff \exists (i, j) \text{ such that } c_{ij} = \{a\}$$
where $c_{ij} = \{ a \in C \mid a(x_i) \neq a(x_j) \}$ for $d(x_i) \neq d(x_j)$.

We evaluated all 45,023 object pairs between distinct disease profiles in the discernibility matrix:
- Minimum discernibility clause size: $\min_{i, j} |c_{ij}| = 2$.
- Number of singleton clauses ($|c_{ij}| = 1$): **0**.
- Since there are no singleton clauses, no individual attribute is irreplaceable across all discerning pairs.

**Conclusion:** Both Pawlak's and Skowron's criteria independently prove that $CORE(C) = \emptyset$.

---

## 3. Reduct Audit: Inclusion-Minimality Verification (PASS)

### Terminology & Scope Correction
Finding the global minimum-cardinality reduct is an NP-hard optimization problem (Skowron & Rauszer, 1992; Wong & Ziarko, 1985). Therefore:
- All generated subsets are formally designated as **"Inclusion-Minimal Reduct Candidates"**.
- **Global minimality is explicitly disclaimed** in both the codebase and documentation.

### Candidate Verification Table

| Reduct Candidate | Discovery Algorithm | Candidate Size | $\gamma_C(d)$ | $\gamma_R(d)$ | Inclusion-Minimal? | Redundant Attributes Found | Computation Time |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Candidate 1** | Johnson Greedy Discernibility Hitting Set | **38** | 1.0000 | 1.0000 | **YES** | None ($\emptyset$) | 0.4359s |
| **Candidate 2** | QuickReduct Dependency Forward Selection | **45** | 1.0000 | 1.0000 | **YES** | None ($\emptyset$) | 3.9419s |
| **Candidate 3** | Alternative Frequency Covering | **46** | 1.0000 | 1.0000 | **YES** | None ($\emptyset$) | 0.5348s |

### Verification of the 38-Attribute Johnson Reduct Candidate
We conducted an exhaustive backward single-attribute deletion test on the 38-attribute Johnson candidate $R_{38}$:
- $\gamma_C(D) = 1.0000$
- $\gamma_{R_{38}}(D) = 1.0000$
- For each $a \in R_{38}$, we evaluated $\gamma_{R_{38} \setminus \{a\}}(D)$:
  - **All 38 single-attribute removals resulted in $\gamma < 1.0000$** (True for 38 / 38 attributes).
  - Minimum dependency upon single removal: $0.9427$.
  - Maximum dependency upon single removal: $0.9976$.
  - Mean dependency upon single removal: $0.9891$.
- **Conclusion:** Candidate $R_{38}$ is strictly **inclusion-minimal** under Pawlak's criterion (no attribute can be dropped without losing dependency degree $\gamma = 1.0$). Global minimality (minimum cardinality across all possible reducts) is **not** claimed.
- **Dimensionality Reduction:** Candidate 1 achieves a **71.2% dimensionality reduction** (from 132 to 38 symptoms).
- **Candidate Intersection:** $\bigcap_{k=1}^3 R_k = 6$ attributes: `burning_micturition`, `chest_pain`, `cough`, `fatigue`, `neck_pain`, `stiff_neck`.

---

## 4. Evaluation Audit: Query Counts & Incomplete Benchmarks (PASS)

### Explanation of Evaluation Counts: 882 Evaluation Queries vs 1,050 Benchmark Queries
To eliminate any ambiguity between the evaluation numbers reported across the audit:
1. **Final Evaluation Queries (882 evaluation queries):**  
   Reported in the detailed evaluation metrics table.
   - For **0% missing** (complete symptoms), masking is the identity function ($seed$ has no effect). Therefore, $0\%$ missing was evaluated **once** across the 42 test cases:
     $$42 \times 1 = 42 \text{ evaluation queries}$$
   - For the four masked incomplete levels ($10\%$, $30\%$, $50\%$, $70\%$), each level was evaluated with **5 deterministic masking repetitions**:
     $$4 \times (5 \times 42) = 840 \text{ evaluation queries}$$
   - **Total Final Evaluation Queries:** $42 + 840 = \mathbf{882 \text{ evaluation queries}}$.
2. **Runtime Benchmark Queries (1,050 benchmark queries):**  
   Reported in `IncompleteBenchmarkRunner.run_benchmark()` for latency and execution timing.
   - Evaluated all 5 levels ($0\%$, $10\%$, $30\%$, $50\%$, $70\%$) with **5 repetitions each** to measure timing variance and execution overhead:
     $$5 \times 5 \times 42 = \mathbf{1,050 \text{ benchmark queries}}$$
   - Each query was executed across Rough Set Recommender + 4 ML baseline classifiers ($5,250$ individual model predictions).

### Full Empirical Evaluation Table (Rough Set Recommender)

| Missing Rate | Test Cases | Masking Runs | Evaluation Queries | Top-1 Accuracy (Mean $\pm$ Std) | Top-3 Accuracy (Mean $\pm$ Std) | Weighted Precision | Weighted Recall | Weighted F1 | Lower Approx. Coverage | Avg Candidates in $[q]_T$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **0% Missing** | 42 | 1 | 42 | **1.0000 $\pm$ 0.0000** | **1.0000 $\pm$ 0.0000** | 1.0000 | 1.0000 | 1.0000 | 100.0% | 1.00 |
| **10% Missing** | 42 | 5 | 210 | **0.9952 $\pm$ 0.0095** | **1.0000 $\pm$ 0.0000** | 0.9976 | 0.9952 | 0.9952 | 99.05% | 1.01 |
| **30% Missing** | 42 | 5 | 210 | **0.9952 $\pm$ 0.0095** | **1.0000 $\pm$ 0.0000** | 0.9976 | 0.9952 | 0.9952 | 97.62% | 1.03 |
| **50% Missing** | 42 | 5 | 210 | **0.9857 $\pm$ 0.0117** | **0.9952 $\pm$ 0.0095** | 0.9929 | 0.9857 | 0.9857 | 93.81% | 1.09 |
| **70% Missing** | 42 | 5 | 210 | **0.8524 $\pm$ 0.0486** | **0.9476 $\pm$ 0.0278** | 0.8020 | 0.8524 | 0.8167 | 70.95% | 1.48 |

### Comparative Baseline Trajectory Under Incomplete Information

| Model | 0% Missing | 10% Missing | 30% Missing | 50% Missing | 70% Missing | Degradation at 70% |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Rough Set Theory (Top-1)** | **100.0%** | **99.52%** | **99.52%** | **98.57%** | **85.24%** | **-14.76%** |
| **Rough Set Theory (Top-3)** | **100.0%** | **100.0%** | **100.0%** | **99.52%** | **94.76%** | **-5.24%** |
| **Bernoulli Naive Bayes** | 100.0% | 98.57% | 98.10% | 94.76% | 75.71% | -24.29% |
| **Logistic Regression** | 100.0% | 99.52% | 98.10% | 88.10% | 64.76% | -35.24% |
| **Random Forest (100 Trees)** | 97.62% | 96.67% | 94.76% | 90.00% | 63.33% | -34.29% |
| **CART Decision Tree** | 97.62% | 92.86% | 82.38% | 62.38% | **36.67%** | **-60.95%** |

---

## 5. Runtime Audit & Discrepancy Investigation (PASS)

### The 6.71s vs 39.36s Discrepancy Investigation
High-precision line-by-line timestamp profiling (`time.perf_counter()`) revealed the exact structural reason for the discrepancy:
1. **Pure Model & Knowledge Artifact Generation:**
   - Dataset Loading: $0.0591$s
   - Preprocessing & Decision Table: $0.0125$s
   - RST Dependency Degree: $0.5763$s
   - Discernibility Matrix (45,023 pairs): $0.6259$s
   - Reduct Candidate Discovery: $4.9126$s
   - Association Rule Mining: $0.6194$s
   - ML Baseline Fitting: $0.7832$s
   - **Subtotal (Pure Knowledge Preparation):** **$7.5890$s** ($\approx 6.71$s in early run).
2. **Offline Evaluation Benchmarking Suite:**
   - Repeated masking benchmark on `Testing.csv`: $5 \text{ rates} \times 5 \text{ reps} \times 42 \text{ cases} = 1,050 \text{ multi-model benchmark queries}$:
   - **Subtotal (Benchmark Execution):** **$20.4979$s** ($32.26$s in prior unoptimized run).
3. **Latency Profiling & Disk Serialization:**
   - 500 in-memory latency test queries: $0.3286$s
   - Serialization of 7 JSON/Joblib artifacts to disk: $0.0820$s
4. **Total Script Execution Time:** **$28.50\text{s} - 39.36\text{s}$**.

**Resolution:** In `train_and_cache.py` and `metadata.json`, we have explicitly separated `pure_model_preparation_time_seconds` ($7.59$s) from `benchmarking_time_seconds` ($20.50$s) and `total_preparation_time_seconds`.

### Measured Latencies
- **In-Memory Python Inference (500 queries):** Mean: **0.657 ms**, p50: **0.609 ms**, p95: **0.981 ms**.
- **Real FastAPI HTTP Request Latency (100 requests via TestClient):** Mean: **6.82 ms**, p50: **5.57 ms**, p95: **10.44 ms**.

---

## 6. Machine Learning Baseline Audit: PASS

- **Training Isolation:** Models fitted strictly on $N = 4,920$ records of `Training.csv`.
- **Model Choice for Naive Bayes:** Switched to **`BernoulliNB`** as the principled model for binary $\{0, 1\}$ symptom indicators. `MultinomialNB` is intended for multiset word counts, whereas `BernoulliNB` explicitly models the likelihood of both symptom presence ($P(x_i=1 \mid d)$) and symptom absence ($P(x_i=0 \mid d) = 1 - P(x_i=1 \mid d)$).
- **Exact Preprocessing Per Model:**
  - **Random Forest (`RandomForestClassifier`):** 132 condition symptom columns ingested. No feature scaling or one-hot re-encoding. Missing/unknown query symptoms ($?$) imputed to 0 ($? \to 0$, indicating absent symptom). Hyperparameters: `n_estimators=100, max_depth=15, random_state=42`.
  - **Bernoulli Naive Bayes (`BernoulliNB`):** 132 binary features $\{0, 1\}$. Missing values imputed to 0 ($? \to 0$). Hyperparameters: `alpha=1.0, fit_prior=True`.
  - **Logistic Regression (`LogisticRegression`):** 132 binary features $\{0, 1\}$. Missing values imputed to 0 ($? \to 0$). No standardization needed as all features share identical $\{0, 1\}$ binary domain. Hyperparameters: `max_iter=1000, penalty='l2', random_state=42`.
  - **Decision Tree (`DecisionTreeClassifier`):** 132 binary features $\{0, 1\}$. Missing values imputed to 0 ($? \to 0$). Splits chosen by Gini impurity directly on binary indicators. Hyperparameters: `criterion='gini', random_state=42`.
- **Fundamental Separation Between ML and RST Preprocessing:**
  > **"Unknown symptom ≠ absent symptom in the RST system."**
  - In conventional ML, estimators require a dense real-valued matrix; missing values are imputed to 0 as an explicit ML baseline assumption.
  - In Rough Set Theory, this ML preprocessing assumption is strictly rejected. Unknown symptoms ($?$) are not imputed or replaced with 0; instead, the query compatibility relation $T(q, x)$ simply ignores attributes where $q(a) = {?}$, preserving epistemic ambiguity without penalizing unobserved symptoms.

---

## 7. Association Rules Audit: PASS

- **Dataset Source:** One-hot encoded `Training.csv` ($N = 4,920$).
- **Algorithm:** Apriori algorithm from `mlxtend` (min_support $= 0.01$, max_len $= 3$).
- **Pruning Criteria:** Consequent must contain exactly one disease; antecedents contain only symptoms; confidence $\ge 0.70$.
- **Retained Disease-Consequent Rules:** **831 rules**.
- **Top Rule Samples:**
  - `['nodal_skin_eruptions'] -> 'Fungal infection'` (Confidence: 100.0%, Lift: 41.0x, Support: 2.2%)
  - `['shivering'] -> 'Allergy'` (Confidence: 100.0%, Lift: 41.0x, Support: 2.2%)
  - `['ulcers_on_tongue'] -> 'GERD'` (Confidence: 100.0%, Lift: 41.0x, Support: 2.2%)

---

## 8. Reproducibility Audit: PASS

- **Test:** Completely deleted `backend/artifacts/` and reran `run_pipeline()`.
- **Result:** Successfully regenerated all 7 artifacts from scratch in $26.29$s.
- **Consistency:** 0% missing test accuracy reproduced at exactly 100.0% (42/42); reduct sizes reproduced at 38, 45, and 46 attributes; 831 association rules reproduced identically.

---

## 9. Current System Verification & Test Status

- **Automated Tests:** All 11 unit and integration tests passing (`pytest backend/tests/ -v`):
  - `test_decision_table_initialization`: PASSED
  - `test_indiscernibility_equivalence_relation`: PASSED
  - `test_lower_and_upper_approximations_axioms`: PASSED
  - `test_dependency_monotonicity`: PASSED
  - `test_incomplete_tolerance_never_treats_unknown_as_zero`: PASSED
  - `test_root_and_health`: PASSED
  - `test_get_symptoms_and_diseases`: PASSED
  - `test_get_metadata_reducts_benchmarks`: PASSED
  - `test_recommendation_with_incomplete_symptoms`: PASSED
  - `test_model_comparison_endpoint`: PASSED (verified with `BernoulliNB`)
  - `test_presets_endpoint`: PASSED
- **Live Servers:**
  - FastAPI daemon active on `http://127.0.0.1:8000`.
  - Vite frontend active on `http://127.0.0.1:5173`.
- **Browser Automation:** End-to-end workflow verified via Antigravity browser tools.

---

## 10. Methodological Decisions and Limitations

### 10.1 Incomplete-Information Relation Formulation
- **Selected Baseline Tolerance Relation:**
  The current strategy compares an incomplete query $q$ with complete reference objects $x \in U$ strictly on attributes where the query value is known ($q(a) \in \{0, 1\}$). Attributes where $q(a) = {?}$ are ignored during comparison.
  This is explicitly documented as the **selected baseline compatibility/tolerance relation** for incomplete information. It is **NOT** described as an ordinary Pawlak equivalence relation for incomplete queries.
- **Classical Equivalence vs Tolerance Neighborhood:**
  - *Classical Equivalence Relation on Complete Training Objects:* On complete objects where all condition attributes $C$ are known $\{0, 1\}$, the indiscernibility relation $IND(C)$ satisfies reflexivity, symmetry, and transitivity. It forms a strict partition of the training universe $U$ ($N = 4,920$) into 304 mutually disjoint equivalence classes $[x]_C$.
  - *Compatibility/Tolerance Neighborhood for Incomplete Query Objects:* When evaluating an incomplete query object $q \in \{0, 1, ?\}^{|C|}$, transitivity is violated across partial symptom observations. The relation $T(q, x)$ is reflexive and symmetric, but non-transitive. It induces a **tolerance neighborhood** (compatibility set):
    $$[q]_T = \{ x \in U \mid \forall a \in Known(q), q(a) = x(a) \}$$
    Tolerance neighborhoods do not partition $U$ and may overlap across multiple disease classes.
- **Mathematical Consistency of Lower and Upper Approximations:**
  The lower and upper approximation terminology used for the tolerance relation is mathematically consistent with the actual codebase implementation (`backend/app/rst/engine.py`):
  - *Lower Approximation:* $T_*(X_d) = \{ q \mid [q]_T \subseteq X_d \}$.  
    In code: `in_lower = (count == num_compatible)`. If all training objects compatible with $q$ belong strictly to disease class $d$, $q$ belongs to the lower approximation of $X_d$ (unambiguous / certain recommendation).
  - *Upper Approximation:* $T^*(X_d) = \{ q \mid [q]_T \cap X_d \neq \emptyset \}$.  
    In code: `in_upper = (count > 0)`. If at least one compatible training object belongs to disease class $d$, $q$ belongs to the upper approximation of $X_d$ (possible recommendation).
  - *Boundary Region:* $BN_T(X_d) = T^*(X_d) \setminus T_*(X_d)$.  
    In code: `in_boundary = (not in_lower) and in_upper`. Ambiguity arises because $q$ matches profiles belonging to more than one disease, triggering active disambiguation.
  - *Rough Membership Degree:* $\mu_{X_d}(q) = \frac{|[q]_T \cap X_d|}{|[q]_T|} = \frac{count}{num\_compatible} \in [0, 1]$.
- **Modular Baseline Extensibility:**
  This baseline is designed to be fully modular and is encapsulated behind the `IncompleteToleranceStrategy` interface (`BaselineQueryToleranceStrategy`). It can later be replaced or extended by a faculty-approved incomplete-information RST formulation (e.g., Kryszkiewicz, 1999 tolerance relations; Stefanowski & Tsoukias, 2001 valued tolerance relations; or variable precision rough set models).

### 10.2 Machine Learning Missing-Value Handling Policy
- **Explicit ML Baseline Assumption Only:**
  Conventional ML baseline algorithms require dense, real-valued input vectors without missing tokens. Therefore, in the ML baseline evaluation, unknown symptoms are imputed as 0 ($? = 0$). This is strictly an **explicit ML baseline assumption**.
- **Non-Interference Rule with Rough Set Theory:**
  > **"Unknown symptom ≠ absent symptom in the RST system."**
  - This ML preprocessing rule is strictly prevented from affecting the Rough Set reasoning engine.
  - In RST, unknown symptoms ($?$) remain explicitly unknown. They are never converted to 0, ensuring that unobserved symptoms are not falsely asserted as absent.
- **Exact Preprocessing Per ML Baseline Model:**
  - **Random Forest (`RandomForestClassifier`):** Dense 132-dimensional binary vector $x \in \{0, 1\}^{132}$. Missing values imputed as $? \to 0$ (assumed absent). 100 trees, max depth 15, random state 42.
  - **Bernoulli Naive Bayes (`BernoulliNB`):** Dense 132-dimensional binary vector $x \in \{0, 1\}^{132}$. Missing values imputed as $? \to 0$. Additive Laplace smoothing $\alpha = 1.0$. **Model Choice Justification:** `BernoulliNB` is preferred over `MultinomialNB` because symptom data consists of boolean presence/absence flags ($\{0, 1\}$). `BernoulliNB` models the likelihood of both symptom presence ($x_i=1$) and symptom absence ($x_i=0$). In contrast, `MultinomialNB` is designed for multiset word counts where 0 denotes absence of count rather than an explicit negative condition.
  - **Logistic Regression (`LogisticRegression`):** Dense 132-dimensional binary vector $x \in \{0, 1\}^{132}$. Missing values imputed as $? \to 0$. L2 regularization, max 1,000 iterations, random state 42. No scaling applied as all features share identical $\{0, 1\}$ range.
  - **CART Decision Tree (`DecisionTreeClassifier`):** Dense 132-dimensional binary vector $x \in \{0, 1\}^{132}$. Missing values imputed as $? \to 0$. Gini impurity splitting directly on binary indicators, random state 42.

### 10.3 Limited Test-Set Claims
- **Exact Dataset Counts:**
  - **Training:** 4,920 records (120 records per class across 41 classes)
  - **Testing:** 42 records (across 41 disease classes; approximately 1 record per disease class, with Fungal Infection having 2)
- **Empirical Scope and Absence of Clinical Claims:**
  All evaluation results presented in this report represent **empirical results on the supplied held-out dataset**. 
  Because the test set contains only 42 records across 41 classes, **no broad clinical, diagnostic, or epidemiological generalization claims are made or warranted**. The limited test-set size is an acknowledged empirical limitation of the benchmark dataset.

### 10.4 Scope of Reduct Minimality (The 38-Attribute Candidate Result)
- **Mathematical Verification:**
  - Full condition dependency: $\gamma(C) = 1.0000$
  - Reduct candidate dependency: $\gamma(R_{38}) = 1.0000$ (where $R_{38}$ is the 38-attribute Johnson candidate)
  - Removing every single attribute from $R_{38}$ makes $\gamma < 1.0000$ (exhaustively verified across all 38 single-attribute deletions: mean $\gamma = 0.9891$, min $\gamma = 0.9427$, max $\gamma = 0.9976$)
  - Therefore, $R_{38}$ is **strictly inclusion-minimal under the implemented Pawlak criterion** (no subset of $R_{38}$ preserves $\gamma = 1.0$).
- **Disclaimer of Global Minimality:**
  Finding the global minimum-cardinality reduct is an NP-hard problem. Reduct $R_{38}$ is an inclusion-minimal reduct candidate; **it is NOT called or claimed to be globally minimum**.

### 10.5 Benchmark Queries vs Evaluation Queries Distinction
To prevent any confusion between the evaluation counts reported:
- **Consistent Terminology:**
  - **Evaluation Queries (882 evaluation queries):**  
    Used for computing and reporting the final evaluation metrics table.
    - $0\%$ missing (complete symptoms) was evaluated **once** across the 42 test cases ($42 \times 1 = 42$ evaluation queries), because masking at rate $0.0$ is the identity function ($seed$ produces identical inputs).
    - Incomplete missing rates ($10\%$, $30\%$, $50\%$, and $70\%$) were each evaluated with **5 deterministic masking repetitions** ($4 \times 5 \times 42 = 840$ evaluation queries).
    - Total: $42 + 840 = \mathbf{882 \text{ evaluation queries}}$.
  - **Benchmark Queries (1,050 benchmark queries):**  
    Used in `IncompleteBenchmarkRunner.run_benchmark()` for measuring runtime latency and timing stability.
    - Evaluated all five rates ($0\%$, $10\%$, $30\%$, $50\%$, $70\%$) with **5 repetitions each** ($5 \times 5 \times 42 = \mathbf{1,050 \text{ benchmark queries}}$) across Rough Set Theory and all 4 ML baselines (totaling $5,250$ individual model predictions).
