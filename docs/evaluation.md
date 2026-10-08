# Empirical Research Evaluation, Comparative Benchmarks & Profiling

**Project:** An Intelligent Recommender System Using Machine Learning, Association Rules and Rough Set for Disease Prediction from Incomplete Symptom Set  
**Document:** Experimental Methodology, Comparative Evaluation Results, and Computational Profiling  
**Audience:** Academic Committee, Faculty Evaluators, and AI/ML Research Engineers  

---

## 1. Experimental Setup & Evaluation Protocol

### 1.1 Dataset Partitioning & Strict Isolation
- **Training Universe (`Training.csv`):** $N = 4,920$ records, 132 binary symptom attributes, 41 balanced disease classes (120 instances per disease).
  - Used strictly for: Rough Set equivalence classes, dependency degree calculation, discernibility matrix construction, reduct generation, association rule mining, and ML baseline training.
- **Held-Out Test Set (`Testing.csv`):** $N = 42$ records, 132 binary symptom attributes, 41 disease classes (approximately 1 record per disease; Fungal infection has 2).
  - Used **strictly and exclusively** for final evaluation of trained models.
  - Zero data leakage: never used for feature selection, rule generation, hyperparameter tuning, or threshold setting.

### 1.2 Evaluation Query Counts: 882 Evaluation Queries vs 1,050 Benchmark Queries
To ensure full transparency between the experimental figures reported across the project:
1. **Final Evaluation Queries (882 queries):**  
   Used for computing and validating the scientific evaluation metrics table:
   - **0% Missing (Complete):** Because mask rate 0.0 is the identity function, each of the 42 test cases was evaluated **once**:
     $$42 \times 1 = 42 \text{ evaluation queries}$$
   - **Incomplete Levels (10%, 30%, 50%, 70%):** Each level was evaluated with **5 deterministic masking repetitions** (seeds 42, 43, 44, 45, 46) across all 42 test cases:
     $$4 \times (5 \times 42) = 840 \text{ evaluation queries}$$
   - **Total:** $42 + 840 = \mathbf{882 \text{ evaluation queries}}$.
2. **Runtime Benchmark Queries (1,050 queries):**  
   Used in `IncompleteBenchmarkRunner.run_benchmark()` for profiling computational speed, variance, and latency:
   - Evaluated all five levels (0%, 10%, 30%, 50%, 70%) with **5 repetitions each**:
     $$5 \times 5 \times 42 = \mathbf{1,050 \text{ benchmark queries}}$$
   - Evaluated across Rough Set Theory + 4 ML baselines (totaling $5,250$ individual model predictions).

---

## 2. Rough Set Recommender: Incomplete Evaluation Results

All metrics below represent audited results evaluated over the 882 evaluation queries using the selected baseline tolerance relation $T$:

| Missing Rate | Test Cases | Masking Runs | Evaluation Queries | Top-1 Accuracy (Mean $\pm$ Std) | Top-3 Accuracy (Mean $\pm$ Std) | Weighted Precision | Weighted Recall | Weighted F1 | Lower Approx. Coverage | Avg Candidates in $[q]_T$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **0% Missing** | 42 | 1 | 42 | **1.0000 $\pm$ 0.0000** | **1.0000 $\pm$ 0.0000** | 1.0000 | 1.0000 | 1.0000 | 100.0% | 1.00 |
| **10% Missing** | 42 | 5 | 210 | **0.9952 $\pm$ 0.0095** | **1.0000 $\pm$ 0.0000** | 0.9976 | 0.9952 | 0.9952 | 99.05% | 1.01 |
| **30% Missing** | 42 | 5 | 210 | **0.9952 $\pm$ 0.0095** | **1.0000 $\pm$ 0.0000** | 0.9976 | 0.9952 | 0.9952 | 97.62% | 1.03 |
| **50% Missing** | 42 | 5 | 210 | **0.9857 $\pm$ 0.0117** | **0.9952 $\pm$ 0.0095** | 0.9929 | 0.9857 | 0.9857 | 93.81% | 1.09 |
| **70% Missing** | 42 | 5 | 210 | **0.8524 $\pm$ 0.0486** | **0.9476 $\pm$ 0.0278** | 0.8020 | 0.8524 | 0.8167 | 70.95% | 1.48 |

### Key Observations:
- **Resilience Under High Sparsity:** Even when 70% of symptoms are unknown, the Rough Set Recommender achieves **85.24% Top-1 accuracy** and **94.76% Top-3 accuracy**.
- **Controlled Candidate Expansion:** At 70% missing symptoms, the tolerance neighborhood $[q]_T$ expands gently, containing an average of only **1.48 candidate diseases** out of 41 total diseases.
- **Lower Approximation Coverage:** At 50% missing, **93.81%** of test queries still fall definitively into the lower approximation $T_*(X)$, providing deterministic certainty. At 70% missing, **70.95%** remain in the lower approximation.

---

## 3. Comparative Benchmark: RST vs Machine Learning Baselines

### 3.1 Comparative Accuracy Trajectory

| Model | 0% Missing | 10% Missing | 30% Missing | 50% Missing | 70% Missing | Absolute Degradation at 70% |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Rough Set Theory (Top-1)** | **100.0%** | **99.52%** | **99.52%** | **98.57%** | **85.24%** | **-14.76%** |
| **Rough Set Theory (Top-3)** | **100.0%** | **100.0%** | **100.0%** | **99.52%** | **94.76%** | **-5.24%** |
| **Bernoulli Naive Bayes** | 100.0% | 98.57% | 98.10% | 94.76% | 75.71% | -24.29% |
| **Logistic Regression** | 100.0% | 99.52% | 98.10% | 88.10% | 64.76% | -35.24% |
| **Random Forest (100 Trees)** | 97.62% | 96.67% | 94.76% | 90.00% | 63.33% | -34.29% |
| **CART Decision Tree** | 97.62% | 92.86% | 82.38% | 62.38% | **36.67%** | **-60.95%** |

### 3.2 Analysis of Algorithmic Degradation
1. **CART Decision Tree Catastrophic Failure (-60.95%):** Decision trees evaluate single-attribute threshold splits sequentially from the root. When missing symptoms are imputed to 0, branches associated with unobserved positive symptoms are systematically pruned, causing accuracy to collapse to **36.67%** at 70% missing.
2. **Random Forest & Logistic Regression (-34% to -35%):** Ensembles and linear models exhibit moderate degradation down to ~63-64%, because imputing dozens of zeros shifts the decision hyperplane away from the true disease centroid.
3. **Bernoulli Naive Bayes (-24.29%):** Outperforms other ML baselines at 75.71% because of independent conditional probability multiplication, but still suffers because imputing 0 evaluates $P(x_i=0 \mid d)$ instead of acknowledging unknown evidence.
4. **Rough Set Theory Superiority (-14.76% Top-1, -5.24% Top-3):** Rough Set Theory maintains **85.24% Top-1** and **94.76% Top-3** because it forms a tolerance neighborhood without zero-assumptions, effectively comparing only the evidence actually present.

---

## 4. Machine Learning Baseline Methodology

### 4.1 Principle Behind Model Selection: BernoulliNB vs MultinomialNB
- **Why BernoulliNB:** The dataset consists of binary $\{0, 1\}$ symptom indicators. `BernoulliNB` is the principled Bayesian model for multivariate Bernoulli distributions. It models both the presence of symptoms ($P(x_i=1 \mid d)$) and the absence of symptoms ($P(x_i=0 \mid d)$).
- In contrast, `MultinomialNB` assumes multiset count data (e.g., word frequencies), where a 0 represents the absence of a word count rather than an explicit negative condition.

### 4.2 Explicit ML Baseline Imputation Assumption
- Conventional ML algorithms in scikit-learn require dense real-valued arrays without missing values.
- In all ML baselines, missing symptoms are imputed as 0 ($? \to 0$).
- **Strict Isolation:** This is an explicit ML baseline assumption. It **never** influences the Rough Set reasoning engine, where unknown symptoms remain explicitly unobserved ($? \neq 0$).

---

## 5. Computational Runtimes & Latency Profiling

### 5.1 Clear Separation: Preparation vs Offline Benchmarking
Line-by-line microsecond profiling (`time.perf_counter()`) reveals the exact structure of system runtime:

```
Total Preparation Pipeline
├── 1. Pure Model & Knowledge Artifact Generation (7.59s)
│   ├── Dataset Ingestion & Validation:        0.059s
│   ├── Decision Table & Indiscernibility:     0.013s
│   ├── Dependency Degree Computation:         0.576s
│   ├── Discernibility Matrix (45,023 pairs):  0.626s
│   ├── Inclusion-Minimal Reduct Discovery:    4.913s
│   ├── Association Rule Mining (Apriori):     0.619s
│   └── ML Baseline Fitting (4 models):        0.783s
│
└── 2. Offline Research Benchmarking Suite (20.50s - 32.26s)
    └── 1,050 multi-model queries across 5 missing rates and 5 repetitions
```

**Key Takeaway:** The initial preparation of all RST knowledge structures, reducts, association rules, and ML models requires only **7.59 seconds**. The remaining time is entirely spent executing the offline research benchmarking suite ($1,050$ queries $\times 5$ models = $5,250$ inferences).

### 5.2 Real-Time Online Latencies
- **In-Memory Python Inference (500 test queries):**
  - Mean Latency: **0.657 ms**
  - Median (p50): **0.609 ms**
  - 95th Percentile (p95): **0.981 ms**
- **Full FastAPI HTTP API Latency (via Starlette TestClient / live network):**
  - Mean Request Latency: **6.82 ms**
  - Median (p50): **5.57 ms**
  - 95th Percentile (p95): **10.44 ms**

Both inference modes provide sub-millisecond to sub-10ms response times, ensuring instantaneous interaction in clinical decision-support workflows.

---

## 6. Known Limitations

> [!WARNING]
> **Mandatory Academic Evaluation Limitation Notice:**  
> *"The held-out test set contains only 42 records, so these results are empirical for this dataset and should not be interpreted as clinical generalization."*

1. **Only 42 Held-Out Test Records:** The official test dataset contains exactly 42 records across 41 disease classes (approximately 1 record per class).
2. **Dataset-Specific Empirical Results:** All reported accuracies, coverages, and degradations are empirical findings on this benchmark dataset. They should not be interpreted as generalizable clinical evidence.
3. **Selected Baseline Incomplete-Information Relation:** The compatibility/tolerance relation $T(q, x)$ comparing objects solely on known query attributes is the selected baseline; faculty may specify alternative generalized incomplete rough set formulations in future work.
4. **Inclusion-Minimal Reducts, Not Globally Minimum:** Reduct candidates (e.g., 38 attributes) are inclusion-minimal under Pawlak's dependency criterion, not proven to be the global minimum-cardinality reduct (which is NP-hard).
5. **Academic Decision-Support Prototype:** This system is an academic research demonstration of Rough Set Theory and Machine Learning, strictly NOT a medical diagnostic tool or clinical software.
