# Rough Set Theory (RST) Mathematical Foundations & Methodology

**Project:** An Intelligent Recommender System Using Machine Learning, Association Rules and Rough Set for Disease Prediction from Incomplete Symptom Set  
**Document:** Mathematical Reference & Algorithmic Methodology  
**Audience:** Academic Committee, Faculty Evaluators, and AI/ML Research Engineers  

---

## 1. Information System & Decision Table

In Rough Set Theory (Pawlak, 1982), the foundation of knowledge representation is an **information system**:
$$\mathcal{S} = (U, A, V, f)$$
where:
- $U$ is a non-empty finite set of objects (the **universe of discourse**). In our clinical benchmark dataset, $U = \{x_1, x_2, \dots, x_{4920}\}$ representing $N = 4,920$ patient records from `Training.csv`.
- $A$ is a non-empty finite set of attributes partitioned into **condition attributes** $C$ and **decision attributes** $D$:
  $$A = C \cup D, \quad C \cap D = \emptyset$$
  - $C = \{a_1, a_2, \dots, a_{132}\}$: 132 binary symptom attributes (`itching`, `skin_rash`, `high_fever`, etc.).
  - $D = \{d\}$: a single decision attribute `prognosis` representing 41 distinct disease categories ($|V_d| = 41$, with 120 training cases per disease).
- $V = \bigcup_{a \in A} V_a$ where $V_a$ is the domain of values for attribute $a$.
  - For condition attributes: $V_a = \{0, 1\}$ for all $a \in C$ (0 = absent, 1 = present).
  - For decision attribute: $V_d = \{\text{Fungal infection}, \text{Allergy}, \dots, \text{Impetigo}\}$.
- $f: U \times A \to V$ is an information function such that $f(x, a) \in V_a$ for every $x \in U$ and $a \in A$.

When condition attributes and decision attributes are distinguished, the system is termed a **Decision Table**:
$$DT = (U, C \cup \{d\}, V, f)$$

---

## 2. Classical Pawlak Indiscernibility Relation on Complete Training Objects

For any non-empty subset of condition attributes $B \subseteq C$, Pawlak defined the **indiscernibility relation** $IND(B)$ on complete objects as:
$$IND(B) = \{ (x, y) \in U \times U \mid \forall a \in B, f(x, a) = f(y, a) \}$$

### Properties of $IND(B)$ on Complete Objects:
1. **Reflexivity:** $(x, x) \in IND(B)$ for all $x \in U$.
2. **Symmetry:** $(x, y) \in IND(B) \implies (y, x) \in IND(B)$.
3. **Transitivity:** $(x, y) \in IND(B) \land (y, z) \in IND(B) \implies (x, z) \in IND(B)$.

Because it is reflexive, symmetric, and transitive, $IND(B)$ is a **mathematical equivalence relation**. It partitions the complete universe $U$ into mutually disjoint **equivalence classes** (elementary sets):
$$[x]_B = \{ y \in U \mid (x, y) \in IND(B) \}$$
The quotient set is denoted $U / IND(B)$ or simply $U / B$:
$$U / B = \{ [x]_B \mid x \in U \}, \quad \bigcup_{[x]_B \in U/B} [x]_B = U, \quad [x]_B \cap [y]_B = \emptyset \text{ if } [x]_B \neq [y]_B$$

**Empirical Verification on `Training.csv`:**
- Evaluating the full set of condition attributes $C$ ($|C| = 132$) partitions $U$ ($N = 4,920$) into **304 distinct equivalence classes**.
- Each equivalence class represents an identical symptom profile observed in the training cohort.

---

## 3. Rough Approximations & Boundary Regions

Let $X \subseteq U$ be a target concept (e.g., the set of all patients diagnosed with a specific disease $d_k \in V_d$). If $X$ cannot be formed as a exact union of elementary equivalence classes in $U / B$, it is termed a **rough (vague) set**.

Pawlak defined the target concept through two crisp sets:

### 3.1 Lower Approximation ($B$-Lower)
The $B$-lower approximation of $X$, denoted $B_*(X)$ or $\underline{B}X$, consists of all objects that can certainly be classified as belonging to $X$ using attribute set $B$:
$$B_*(X) = \{ x \in U \mid [x]_B \subseteq X \} = \bigcup \{ [x]_B \in U/B \mid [x]_B \subseteq X \}$$

### 3.2 Upper Approximation ($B$-Upper)
The $B$-upper approximation of $X$, denoted $B^*(X)$ or $\overline{B}X$, consists of all objects that possibly belong to $X$ using attribute set $B$:
$$B^*(X) = \{ x \in U \mid [x]_B \cap X \neq \emptyset \} = \bigcup \{ [x]_B \in U/B \mid [x]_B \cap X \neq \emptyset \}$$

### 3.3 Boundary Region
The $B$-boundary region of $X$ represents the region of doubt where objects cannot be definitively assigned to $X$ or its complement:
$$BN_B(X) = B^*(X) \setminus B_*(X)$$

### Mathematical Axioms Verified:
1. $B_*(X) \subseteq X \subseteq B^*(X)$
2. $B_*(\emptyset) = B^*(\emptyset) = \emptyset$
3. $B_*(U) = B^*(U) = U$
4. $B^*(X \cup Y) = B^*(X) \cup B^*(Y)$
5. $B_*(X \cap Y) = B_*(X) \cap B_*(Y)$
6. $X$ is crisp (exact) with respect to $B$ if and only if $BN_B(X) = \emptyset$ (i.e., $B_*(X) = B^*(X) = X$).

---

## 4. Positive Region & Degree of Dependency

Let $D = \{X_1, X_2, \dots, X_m\}$ be the partition of $U$ induced by the decision attribute $d$ (where $X_k = \{x \in U \mid f(x, d) = d_k\}$).

### 4.1 Positive Region
The $B$-positive region of decision partition $D$, denoted $POS_B(D)$, is the union of the $B$-lower approximations of all decision classes:
$$POS_B(D) = \bigcup_{k=1}^m B_*(X_k)$$
$POS_B(D)$ consists of all objects in $U$ that can be uniquely and consistently classified into one of the decision classes using the attributes in $B$.

### 4.2 Degree of Dependency ($\gamma$)
The degree of dependency of decision attribute $D$ on attribute set $B$, denoted $\gamma_B(D) \in [0, 1]$, is:
$$\gamma_B(D) = \frac{|POS_B(D)|}{|U|}$$
- $\gamma_B(D) = 1.0$: The decision attribute $D$ depends **totally (100%)** on $B$. The decision table is completely consistent with respect to $B$.
- $0 < \gamma_B(D) < 1.0$: $D$ partially depends on $B$.
- $\gamma_B(D) = 0.0$: $D$ is totally independent of $B$.

**Empirical Verification on `Training.csv`:**
$$\gamma_C(D) = \frac{|POS_C(D)|}{|U|} = \frac{4920}{4920} = \mathbf{1.0000}$$
This confirms that the 132 symptom attributes provide a totally consistent decision table with zero decision collisions across training records.

---

## 5. Skowron's Discernibility Matrix & Mathematical Core Proof

### 5.1 Skowron's Discernibility Matrix
Skowron & Rauszer (1992) formalized attribute reduction using a symmetric $|U| \times |U|$ discernibility matrix $M(C) = (c_{ij})$, where each entry $c_{ij} \subseteq C$ contains all condition attributes that distinguish object $x_i$ from object $x_j$:
$$c_{ij} = \begin{cases}
\{ a \in C \mid f(x_i, a) \neq f(x_j, a) \}, & \text{if } f(x_i, d) \neq f(x_j, d) \\
\emptyset, & \text{if } f(x_i, d) = f(x_j, d)
\end{cases}$$

For efficiency, discernibility is evaluated across distinct equivalence classes representing distinct diseases, yielding **45,023 pairwise disease comparisons**.

### 5.2 Mathematical Proof of $CORE(C) = \emptyset$

> **Theorem:** The Core of condition attributes $C$ is strictly empty: $CORE(C) = \emptyset$.

**Proof 1: Pawlak's Indispensable Attribute Theorem (Pawlak, 1982)**  
An attribute $a \in C$ is defined as indispensable with respect to decision $D$ if and only if:
$$\gamma_{C \setminus \{a\}}(D) < \gamma_C(D)$$
The Core is the set of all indispensable attributes:
$$CORE(C) = \{ a \in C \mid \gamma_{C \setminus \{a\}}(D) < \gamma_C(D) \}$$
We evaluated $\gamma_{C \setminus \{a\}}(D)$ for all 132 attributes $a \in C$:
- For every attribute $a \in C$:
  $$\gamma_{C \setminus \{a\}}(D) = 1.0000 = \gamma_C(D)$$
- Dropping any single symptom never introduces a decision inconsistency.
- Therefore:
  $$|CORE(C)| = 0 \implies CORE(C) = \emptyset$$

**Proof 2: Skowron's Singleton Clause Theorem (Skowron & Rauszer, 1992)**  
An attribute $a$ belongs to $CORE(C)$ if and only if it appears as a singleton clause in the discernibility matrix $M(C)$:
$$a \in CORE(C) \iff \exists (i, j) \text{ such that } c_{ij} = \{a\}$$
Across all 45,023 object pairs between distinct disease profiles in our matrix:
- Minimum discernibility clause size: $\min_{i, j} |c_{ij}| = 2$.
- Number of singleton clauses ($|c_{ij}| = 1$): **0**.
- Because every distinguishing pair differs by at least two symptoms, no single symptom is irreplaceable across all discerning pairs.
- Therefore:
  $$CORE(C) = \emptyset$$

Both theorems independently establish that $CORE(C) = \emptyset$ with complete mathematical rigor.

---

## 6. Inclusion-Minimal Reducts (The 38-Attribute Candidate Result)

### 6.1 Definition of a Pawlak Reduct
A subset of condition attributes $R \subseteq C$ is a **reduct** of $C$ with respect to decision $D$ if and only if it satisfies two conditions:
1. **Dependency Preservation:** $\gamma_R(D) = \gamma_C(D) = 1.0000$ (jointly preserves full discernibility).
2. **Inclusion-Minimality:** For every attribute $a \in R$, $\gamma_{R \setminus \{a\}}(D) < \gamma_R(D)$ (no attribute in $R$ is redundant).

### 6.2 Discovery Algorithms & Results

| Candidate | Algorithm | Reduct Size | $\gamma_C(D)$ | $\gamma_R(D)$ | Inclusion-Minimal? | Compute Time |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **Candidate 1** | Johnson Greedy Discernibility Hitting Set | **38** | 1.0000 | 1.0000 | **YES** | 0.4359s |
| **Candidate 2** | QuickReduct Dependency Forward Selection | **45** | 1.0000 | 1.0000 | **YES** | 3.9419s |
| **Candidate 3** | Alternative Frequency Covering | **46** | 1.0000 | 1.0000 | **YES** | 0.5348s |

### 6.3 Exhaustive Verification of Candidate 1 ($|R_{38}| = 38$)
To prove inclusion-minimality under Pawlak's criterion, an exhaustive backward single-attribute deletion test was executed:
- For every $a \in R_{38}$, we evaluated $\gamma_{R_{38} \setminus \{a\}}(D)$:
  - **All 38 / 38 single-attribute removals strictly decrease dependency:** $\gamma < 1.0000$.
  - Minimum dependency observed upon removal: $0.9427$.
  - Maximum dependency observed upon removal: $0.9976$.
  - Mean dependency upon removal: $0.9891$.
- **Conclusion:** Candidate 1 is strictly **inclusion-minimal** under Pawlak's criterion.
- **Dimensionality Reduction:** Reduces feature space from 132 symptoms down to 38 symptoms (**71.2% reduction**).

### 6.4 Explicit Disclaimer of Global Minimum Reduct
Finding the global minimum-cardinality reduct ($\arg\min_{R} |R|$) is an **NP-hard** problem (Skowron & Rauszer, 1992). Candidate 1 is an **inclusion-minimal reduct candidate** discovered via Johnson's greedy heuristic; **it is NOT claimed to be the globally minimum-cardinality reduct**.

---

## 7. Known Limitations

1. **Only 42 Held-Out Test Records:** The official test dataset contains exactly 42 records across 41 disease classes (approximately 1 record per class).
2. **Dataset-Specific Empirical Results:** All reported accuracies, coverages, and degradations are empirical findings on this benchmark dataset. They should not be interpreted as generalizable clinical evidence.
3. **Selected Baseline Incomplete-Information Relation:** The compatibility/tolerance relation $T(q, x)$ comparing objects solely on known query attributes is the selected baseline; faculty may specify alternative generalized incomplete rough set formulations in future work.
4. **Inclusion-Minimal Reducts, Not Globally Minimum:** Reduct candidates (e.g., 38 attributes) are inclusion-minimal under Pawlak's dependency criterion, not proven to be the global minimum-cardinality reduct (which is NP-hard).
5. **Academic Decision-Support Prototype:** This system is an academic research demonstration of Rough Set Theory and Machine Learning, strictly NOT a medical diagnostic tool or clinical software.
