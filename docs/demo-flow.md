# Faculty Demonstration Flow & Interactive Presentation Script

**Project:** An Intelligent Recommender System Using Machine Learning, Association Rules and Rough Set for Disease Prediction from Incomplete Symptom Set  
**Document:** Live Demonstration Guide and Faculty Defense Script  
**Audience:** Academic Committee, Faculty Evaluators, and AI/ML Research Engineers  

---

## 1. Overview of Live Demonstration

This script provides a structured, reproducible walkthrough for demonstrating the web application to the faculty examination committee. It highlights the theoretical rigor of Rough Set Theory, contrasts it with classical machine learning under incomplete information, and demonstrates interactive disambiguation.

---

## 2. Step-by-Step Scenario Walkthrough

### Scenario A: Complete Symptoms — Deterministic Certainty
- **Goal:** Demonstrate classical Pawlak lower approximation behavior when symptoms are complete.
- **Action:**
  1. Navigate to **Recommender** tab.
  2. Click **Preset 1: Dengue (Complete Symptoms)**.
  3. Observe that 14 symptoms are explicitly marked `YES`, 118 marked `NO`, and 0 marked `UNKNOWN`.
  4. Click **Run Disease Recommendation**.
- **Observations:**
  - **Primary Recommendation:** Dengue (100.0% Rough Membership Degree).
  - **Approximation Status:** `Lower Approximation under selected tolerance relation T_*(X) — Deterministic Certainty`.
  - **Tolerance Class Size:** 66 training objects (all 66 compatible objects belong strictly to Dengue).
  - **Boundary Region:** Empty ($BN_T(X) = \emptyset$).
- **Talking Point:** *"When symptom knowledge is complete, the tolerance neighborhood coincides with the classical Pawlak equivalence class, yielding deterministic certainty without any heuristic guesswork."*

---

### Scenario B: 50% Unknown Symptoms — Tolerance Resilience
- **Goal:** Demonstrate that Rough Set Theory ignores unobserved symptoms without applying an artificial zero penalty.
- **Action:**
  1. Click **Preset 2: Dengue (50% Missing / Unknown)**.
  2. Observe that 7 symptoms are marked `YES`, 59 marked `NO`, and 66 marked `UNKNOWN (?)`.
  3. Click **Run Disease Recommendation**.
- **Observations:**
  - **Primary Recommendation:** Dengue (100.0% Rough Membership Degree).
  - **Approximation Status:** `Lower Approximation under selected tolerance relation T_*(X) — Deterministic Certainty`.
  - **Tolerance Class Size:** 78 training objects (all 78 compatible training objects belong exclusively to Dengue).
  - **Machine Learning Comparison (click 'Compare with ML Baselines'):**
    - RST: Dengue (100%).
    - Random Forest: 90% confidence.
    - CART Decision Tree: Already suffering degradation due to false zero-imputations.
- **Talking Point:** *"Notice that 66 symptoms are completely unknown. Unlike ML models that treat 'unknown' as 'absent', RST simply compares known symptoms against reference profiles. Dengue remains uniquely isolated in the lower approximation."*

---

### Scenario C: Boundary Region Ambiguity — Interactive Disambiguation
- **Goal:** Demonstrate how the system behaves when symptoms match multiple disease profiles and how the **Discriminative Power Heuristic** guides follow-up questions.
- **Action:**
  1. Click **Preset 4: Single Symptom (Vomiting Only)**.
  2. Observe that `vomiting` is `YES`, and the remaining 131 symptoms are `UNKNOWN (?)`.
  3. Click **Run Disease Recommendation**.
- **Observations:**
  - **Tolerance Neighborhood Size:** 1,914 compatible training objects across multiple diseases.
  - **Approximation Status:** `Boundary Region under selected tolerance relation BN_T(X) — Incomplete Information Ambiguity`.
  - **Candidate Diseases:** GERD (6.3%), Hepatitis (6.3%), Jaundice (6.3%), Gastroenteritis, etc.
  - **Active Disambiguation Guide Card Appears:**
    - Recommends unobserved symptoms ranked by **Discriminative Power Heuristic** ($\text{Var}(p(a)) \in [0, 0.25]$).
    - Suggests symptoms like `acidity`, `chest_pain`, `yellowish_skin`.
  4. In the follow-up question card, click **Yes** on `yellowish_skin` and re-run.
  5. The tolerance neighborhood immediately contracts, isolating hepatic conditions and eliminating gastrointestinal ones.
- **Talking Point:** *"A single symptom cannot deterministically isolate a disease. RST acknowledges this epistemic ambiguity through the boundary region. The Discriminative Power Heuristic identifies which unasked symptom will create the maximum variance between competing diseases, minimizing subsequent clinical questions."*

---

### Scenario D: Zero Known Symptoms — Epistemic Honesty
- **Goal:** Demonstrate system defense against uninformative input.
- **Action:**
  1. Click **Reset All (Set all 132 to Unknown)**.
  2. Observe that all 132 symptoms are `UNKNOWN (?)`.
  3. Click **Run Disease Recommendation**.
- **Observations:**
  - System intercepts the query and displays a dedicated **"Insufficient Information Provided"** card.
  - Explanation: $[q]_T = U$ ($N = 4,920$). Every training record is compatible when nothing is known.
  - The system refuses to produce a speculative primary diagnosis.
- **Talking Point:** *"Most machine learning models will output an arbitrary prediction based on dataset prior probabilities if given a vector of zeros. RST mathematically proves that $[q]_T = U$ and transparently informs the clinician that information is insufficient."*

---

### Scenario E: ML Comparison Lab & Empirical Benchmarks
- **Goal:** Demonstrate empirical resilience across 0% to 70% missing symptom rates against classical ML baselines.
- **Action:**
  1. Navigate to **RST vs ML Lab** tab.
  2. Click the missing rate switcher buttons: **Complete (0%)**, **10% Missing**, **30% Missing**, **50% Missing**, **70% Missing**.
- **Observations:**
  - At **0% Missing**: All models achieve 97.6% - 100.0% accuracy.
  - At **50% Missing**: CART drops to 62.38%, Logistic Regression to 88.10%, while RST maintains 98.57% Top-1 (99.52% Top-3).
  - At **70% Missing**:
    - **CART Decision Tree:** Collapses to **36.67%** (-60.95% drop).
    - **Random Forest:** Drops to **63.33%** (-34.29% drop).
    - **Logistic Regression:** Drops to **64.76%** (-35.24% drop).
    - **Bernoulli Naive Bayes:** Drops to **75.71%** (-24.29% drop).
    - **Rough Set Theory (Top-1):** Sustains **85.24%** (-14.76% drop).
    - **Rough Set Theory (Top-3):** Sustains **94.76%** (-5.24% drop).
- **Talking Point:** *"Decision trees experience catastrophic pruning because imputing zeros forces traversal down incorrect subtrees. Rough Set Theory preserves 94.76% Top-3 recall even when 70% of symptom information is completely unobserved."*

---

## 3. Walkthrough of Theoretical Tabs

### 3.1 Rough Set & Reducts Explorer
- Navigate to **RST Theory & Reducts** tab.
- **Theory Cards:** Review Pawlak's 10 core concepts (Information Systems, Indiscernibility, Approximations, Dependency Degree $\gamma_C(D)=1.0$, etc.).
- **Empty Core Proof ($CORE(C) = \emptyset$):** Show Pawlak's indispensable attribute test ($\gamma_{C \setminus \{a\}} = 1.0$ for all 132 attributes) and Skowron's discernibility matrix test (0 singleton clauses across 45,023 object pairs).
- **Inclusion-Minimal Reducts:**
  - Select **Candidate 1 (Johnson Greedy Hitting Set — 38 Attributes)**.
  - Review the backward elimination proof: all 38 single-attribute removals strictly reduce $\gamma < 1.0$ (mean $\gamma = 0.9891$).
  - Review the **71.2% dimensionality reduction** from 132 to 38 attributes.
  - Highlight the explicit disclaimer: *Inclusion-minimal under Pawlak's criterion, NOT globally minimum-cardinality.*

### 3.2 Association Rules Miner
- Navigate to **Association Rules** tab.
- Show **831 disease-consequent rules** mined strictly from `Training.csv` ($N = 4,920$) via Apriori ($\text{min\_support} = 0.01$, $\text{min\_confidence} = 0.70$).
- Filter by disease (e.g., `Fungal infection` or `Allergy`) to show high-lift symptom antecedents (e.g., `nodal_skin_eruptions` $\implies$ `Fungal infection`, 100% confidence, 41.0x lift).

### 3.3 Faculty Benchmarks & System Metadata
- Navigate to **Faculty Benchmarks** tab.
- Show **Dataset Profile Card:** 4,920 training records, 42 held-out test records.
- Show **Evaluation Queries (882) vs Benchmark Queries (1,050)** explanation.
- Show **Computational Timings Card:**
  - Pure model/knowledge preparation: **7.59s**.
  - Offline benchmarking suite: **20.50s**.
  - In-memory inference: **0.657 ms**.
  - HTTP API latency: **6.82 ms**.
- Highlight the **Scientific Limitations Banner**.

---

## 4. Key Faculty Defense Q&A

1. **Q: Why is $CORE(C) = \emptyset$? Does that mean the symptoms are useless?**  
   *A:* "Not at all. In clinical datasets with 132 symptoms, diseases exhibit high diagnostic redundancy. Every pair of distinct diseases is separated by at least two symptoms (minimum clause size in Skowron's matrix is 2). Because no single symptom is irreplaceable across every disease distinction, no single attribute is indispensable. Thus, $CORE(C) = \emptyset$."

2. **Q: Why do you call the incomplete query relation a tolerance relation rather than Pawlak equivalence?**  
   *A:* "Classical Pawlak indiscernibility requires transitivity. When an incoming query has unknown symptoms ($?$), transitivity breaks down across partial observations. Therefore, the relation is mathematically a compatibility/tolerance relation, inducing tolerance neighborhoods $[q]_T$ rather than a partition of $U$."

3. **Q: Why use BernoulliNB instead of MultinomialNB?**  
   *A:* "Our features are binary indicators $\{0, 1\}$. BernoulliNB is the principled Bayesian model for binary data, explicitly modeling both presence ($x_i=1$) and absence ($x_i=0$). MultinomialNB is intended for multiset word counts where 0 represents absence of a count."

4. **Q: Is the 38-attribute reduct the global minimum reduct?**  
   *A:* "No. Finding the global minimum-cardinality reduct is proven to be NP-hard. Candidate 1 is an inclusion-minimal reduct discovered via Johnson's algorithm: every single attribute removal drops $\gamma < 1.0$, but we do not claim global minimum cardinality."

5. **Q: What is the Discriminative Power score? Is it a standard RST formula?**  
   *A:* "No, we explicitly document it as a project-specific heuristic, not a standard Pawlak metric. It calculates the empirical prevalence variance among top candidate diseases for unobserved symptoms, identifying questions with maximal distinguishing potential."

---

## 5. Known Limitations

> [!WARNING]
> **Mandatory Academic Evaluation Limitation Notice:**  
> *"The held-out test set contains only 42 records, so these results are empirical for this dataset and should not be interpreted as clinical generalization."*

1. **Only 42 Held-Out Test Records:** The official test dataset contains exactly 42 records across 41 disease classes (approximately 1 record per class).
2. **Dataset-Specific Empirical Results:** All reported accuracies, coverages, and degradations are empirical findings on this benchmark dataset. They should not be interpreted as generalizable clinical evidence.
3. **Selected Baseline Incomplete-Information Relation:** The compatibility/tolerance relation $T(q, x)$ comparing objects solely on known query attributes is the selected baseline; faculty may specify alternative generalized incomplete rough set formulations in future work.
4. **Inclusion-Minimal Reducts, Not Globally Minimum:** Reduct candidates (e.g., 38 attributes) are inclusion-minimal under Pawlak's dependency criterion, not proven to be the global minimum-cardinality reduct (which is NP-hard).
5. **Academic Decision-Support Prototype:** This system is an academic research demonstration of Rough Set Theory and Machine Learning, strictly NOT a medical diagnostic tool or clinical software.
