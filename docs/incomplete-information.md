# Incomplete-Information Reasoning & Tolerance Relations in Rough Set Theory

**Project:** An Intelligent Recommender System Using Machine Learning, Association Rules and Rough Set for Disease Prediction from Incomplete Symptom Set  
**Document:** Incomplete Information Formulation, Semantics, and Disambiguation Heuristic  
**Audience:** Academic Committee, Faculty Evaluators, and AI/ML Research Engineers  

---

## 1. Tri-State Symptom Representation

Real-world clinical intake is inherently incomplete: patients frequently report salient symptoms while leaving dozens of secondary symptoms unmentioned or unknown.

To address this without introducing unwarranted assumptions, the system enforces a strict **tri-state symptom alphabet**:
- **`1` (Present):** The symptom is explicitly confirmed to be present by the patient or clinician.
- **`0` (Absent):** The symptom is explicitly evaluated and confirmed to be absent.
- **`?` (Unknown / Missing / Unobserved):** The symptom was not queried, is unobserved, or the patient cannot provide information.

### Core Non-Interference Principle:
> **"Unknown symptom $\neq$ Absent symptom in the RST system ($? \neq 0$)."**

In conventional machine learning pipelines, estimators require dense real-valued feature vectors, forcing an imputation heuristic (typically setting missing features to 0). In medical decision-support, imputing $? \to 0$ asserts that a patient definitively lacks a symptom merely because it was unqueried. Rough Set Theory rejects this imputation: **unknown symptoms remain explicitly unobserved**, and the reasoning engine reasons over epistemic uncertainty.

---

## 2. Classical Equivalence vs Compatibility / Tolerance Relations

A crucial distinction in this system is the formal separation between the relation on the complete reference universe and the relation applied to incoming incomplete queries:

### 2.1 Complete Training Universe: Classical Pawlak Equivalence
On the complete training universe $U$ ($N = 4,920$, 132 condition symptoms $\{0, 1\}$):
- All condition attribute values are strictly known.
- The indiscernibility relation $IND(C)$ satisfies **reflexivity, symmetry, and transitivity**.
- $IND(C)$ forms a **classical Pawlak equivalence relation**, partitioning $U$ into 304 mutually disjoint equivalence classes $[x]_C$.

### 2.2 Incomplete Query Objects: Compatibility / Tolerance Relation
When an incomplete query $q \in \{0, 1, ?\}^{|C|}$ is submitted:
- Observations are partial ($Known(q) \subset C$).
- **Transitivity does NOT hold across partial observations.** For example:
  - Object $x$ has symptoms $(a=1, b=1)$.
  - Query $q$ has symptoms $(a=1, b=?)$.
  - Object $y$ has symptoms $(a=1, b=0)$.
  - Here, $x$ is compatible with $q$, and $y$ is compatible with $q$, but $x$ and $y$ are completely discernible on symptom $b$ ($x(b) \neq y(b)$).
- Therefore, the relation comparing an incomplete query with reference objects is formally a **compatibility / tolerance relation** $T(q, x)$, **NOT** a classical Pawlak equivalence relation.

---

## 3. Mathematical Definition of the Selected Baseline Tolerance Relation

Let $Known(q) = \{ a \in C \mid q(a) \in \{0, 1\} \}$ be the set of symptoms with known values in query $q$. The selected baseline tolerance relation $T$ between query $q$ and training instance $x \in U$ is defined as:
$$T(q, x) \iff \forall a \in Known(q), \quad q(a) = x(a)$$

Attributes where $q(a) = {?}$ are **completely excluded** from the compatibility check:
- If $q(a) = {?}$, the condition $q(a) = x(a)$ is trivially satisfied regardless of whether $x(a) = 0$ or $x(a) = 1$.
- No zero-penalty is applied to unobserved symptoms.

### Tolerance Neighborhood $[q]_T$:
Rather than partitioning the universe, the compatibility relation induces a **tolerance neighborhood** (compatibility set):
$$[q]_T = \{ x \in U \mid T(q, x) \} = \{ x \in U \mid \forall a \in Known(q), q(a) = x(a) \}$$
Unlike equivalence classes, tolerance neighborhoods:
1. Vary dynamically depending on which specific attributes are known in $q$.
2. May overlap across multiple decision classes.
3. Shrink monotonically as more symptoms are confirmed ($Known(q') \supseteq Known(q) \implies [q']_T \subseteq [q]_T$).

---

## 4. Approximations Under the Selected Tolerance Relation

Given a target disease class $X_d \subseteq U$ ($d \in D$), the approximations under the selected tolerance relation $T$ are defined as:

### 4.1 Lower Approximation ($T$-Lower)
$$T_*(X_d) = \{ q \mid [q]_T \subseteq X_d \}$$
- **Interpretation:** Every single training object compatible with query $q$ belongs exclusively to disease class $d$.
- **Semantics:** **Deterministic Certainty**. The patient's reported symptoms are sufficient to uniquely isolate disease $d$ with 100% confidence.

### 4.2 Upper Approximation ($T$-Upper)
$$T^*(X_d) = \{ q \mid [q]_T \cap X_d \neq \emptyset \}$$
- **Interpretation:** At least one training object compatible with query $q$ belongs to disease class $d$.
- **Semantics:** **Plausible Candidate**. Disease $d$ cannot be excluded based on the current partial evidence.

### 4.3 Boundary Region ($T$-Boundary)
$$BN_T(X_d) = T^*(X_d) \setminus T_*(X_d)$$
- **Interpretation:** The query is compatible with instances of disease $d$, but also with instances of at least one other disease.
- **Semantics:** **Incomplete Information Ambiguity**. This triggers the active recommendation engine to suggest clarifying follow-up symptoms.

### 4.4 Rough Membership Degree
The degree of belonging of query $q$ to disease class $X_d$ is quantified by the rough membership function:
$$\mu_{X_d}(q) = \frac{|[q]_T \cap X_d|}{|[q]_T|}$$
where $\mu_{X_d}(q) \in [0, 1]$ and $\sum_{d \in D} \mu_{X_d}(q) = 1.0$.

---

## 5. System Behavior Across Query Scenarios

| Scenario | Query Input State | Tolerance Neighborhood $[q]_T$ | Approximation Status | System Action |
|---|---|---|:---:|---|
| **Complete Symptoms** | All 132 symptoms known | Coincides with exact equivalence class $[x]_C$ ($| [q]_T | \approx 16-120$) | Lower Approximation $T_*(X)$ | Returns deterministic primary disease recommendation ($100\%$ membership). |
| **Partial / Ambiguous** | $5-20$ symptoms known, rest unknown | Intersects multiple disease cohorts ($| [q]_T | \approx 50-300$) | Boundary Region $BN_T(X)$ | Ranks candidate diseases by $\mu_{X_d}(q)$ and computes Discriminative Power Heuristic for follow-up questions. |
| **Highly Sparse / 1 Symptom** | 1 symptom known (`vomiting=1`), 131 unknown | Expands across multiple conditions ($| [q]_T | = 1,914$) | Boundary Region $BN_T(X)$ | Identifies top 3 candidates (e.g., GERD, Hepatitis, Jaundice) and prompts high-variance follow-up symptoms. |
| **Zero Known Symptoms** | 132 unknown symptoms ($Known(q) = \emptyset$) | Spans entire universe: $[q]_T = U$ ($| [q]_T | = 4,920$) | None ($[q]_T = U$) | Returns graceful **"Insufficient Information"** status. Refuses to make arbitrary clinical guesses. |

---

## 6. Disambiguation-Score Audit: Discriminative Power Heuristic

When an incomplete query falls into the boundary region ($BN_T(X)$), the system must suggest follow-up questions to efficiently reduce ambiguity.

### 6.1 Mathematical Formulation
The engine computes the **Discriminative Power Heuristic** for each unobserved symptom $a \in Unknown(q)$:
$$\text{Var}(p(a)) = \frac{1}{K} \sum_{k=1}^K (p_k(a) - \bar{p}(a))^2$$
where:
- $K = \min(3, |\text{Candidate Diseases in } [q]_T|)$ is the number of top competing candidate diseases.
- $p_k(a) = \frac{1}{|U_{d_k}|} \sum_{x \in U_{d_k}} x(a)$ is the empirical prevalence of symptom $a$ among training instances of disease class $d_k$.
- $\bar{p}(a) = \frac{1}{K} \sum_{k=1}^K p_k(a)$ is the mean prevalence across the top candidate diseases.

### 6.2 Normalization and Bounding
- Because each $p_k(a) \in [0, 1]$ is a Bernoulli proportion, the variance is mathematically bounded:
  $$\text{Var}(p(a)) \in [0, 0.25]$$
  - Maximum variance ($0.25$) occurs when a symptom is present in 100% of cases for one disease ($p_1 = 1.0$) and 0% for another ($p_2 = 0.0$).
  - Minimum variance ($0.0$) occurs when a symptom has identical prevalence across all candidate diseases (e.g., present in 50% of both, or absent in both).
- The engine filters out uninformative questions by enforcing a threshold: $\text{Var}(p(a)) > 0.05$.

### 6.3 Metric Classification & Interpretation
- **Project-Specific Heuristic:** This metric is an empirical prevalence-variance heuristic developed for interactive clinical disambiguation; it is **NOT** a classical Pawlak Rough Set metric. It is explicitly labeled in UI and schemas as the **"Discriminative Power Heuristic"**.
- **Higher Score = More Useful:** Symptoms with higher discriminative power exhibit the greatest difference in presentation among the competing diseases. Confirming or ruling out a high-variance symptom provides maximal information gain to collapse the boundary region.

---

## 7. Modular Architecture & Future Extensions

To support academic extensibility, the tolerance relation is decoupled behind an abstract interface in `backend/app/rst/incomplete_strategy.py`:
```python
class IncompleteToleranceStrategy(ABC):
    @abstractmethod
    def compute_tolerance_neighborhood(
        self, query: Dict[str, Any], decision_table: DecisionTable
    ) -> List[int]:
        pass
```
The currently active implementation is `BaselineQueryToleranceStrategy`. If a faculty committee later specifies another formulation (such as Kryszkiewicz's 1999 generalized incomplete rough set model, Stefanowski & Tsoukias's 2001 valued tolerance relations, or Variable Precision Rough Sets), it can be plugged in without modifying core API schemas.

---

## 8. Known Limitations

1. **Only 42 Held-Out Test Records:** The official test dataset contains exactly 42 records across 41 disease classes (approximately 1 record per class).
2. **Dataset-Specific Empirical Results:** All reported accuracies, coverages, and degradations are empirical findings on this benchmark dataset. They should not be interpreted as generalizable clinical evidence.
3. **Selected Baseline Incomplete-Information Relation:** The compatibility/tolerance relation $T(q, x)$ comparing objects solely on known query attributes is the selected baseline; faculty may specify alternative generalized incomplete rough set formulations in future work.
4. **Inclusion-Minimal Reducts, Not Globally Minimum:** Reduct candidates (e.g., 38 attributes) are inclusion-minimal under Pawlak's dependency criterion, not proven to be the global minimum-cardinality reduct (which is NP-hard).
5. **Academic Decision-Support Prototype:** This system is an academic research demonstration of Rough Set Theory and Machine Learning, strictly NOT a medical diagnostic tool or clinical software.
