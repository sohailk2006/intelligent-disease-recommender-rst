# Dataset Specifications & Acquisition Guide

## 1. Governance & Version Control Policy
In compliance with project data governance and privacy policies:
- Raw medical training datasets (`Training.csv`) and held-out evaluation datasets (`Testing.csv`) are **intentionally excluded from Git version control** via `.gitignore`.
- All deterministically computed mathematical and diagnostic artifacts (including Johnson discernibility reducts, association rules, disease catalog, confusion matrices, and pre-trained baseline weights) are pre-packaged and verified under [`backend/artifacts/`](../backend/artifacts/).
- **The application runs fully out-of-the-box without requiring raw CSV files** for inference, evaluation display, and interactive reasoning.

---

## 2. Dataset Schema & Structure

If you are an authorized developer or researcher seeking to re-train the models or re-generate research artifacts from scratch, you must supply the dataset files directly into this directory (`data/`).

### A. `Training.csv`
- **Universe Size ($U$):** Exactly 4,920 records (or compatible row count).
- **Condition Attributes ($C$):** 132 binary symptom attributes with values in $\{0, 1\}$.
  - Format: Integer values `0` (symptom absent) or `1` (symptom present).
- **Decision Attribute ($D$):** 1 decision column named `prognosis`.
  - Values: 41 distinct categorical disease classes (e.g., `Fungal infection`, `Malaria`, `Dengue`, `Tuberculosis`, etc.).
- **Missing Values:** Complete training records (no NaN or null entries in the training baseline).

### B. `Testing.csv`
- **Test Sample Size:** 42 records (or custom held-out test distribution).
- **Schema:** Identical 132 condition attribute columns + 1 `prognosis` decision attribute column as `Training.csv`.

---

## 3. How to Supply Datasets & Run Pipeline

1. **Obtain Authorized Data:**
   Acquire the benchmark disease prediction dataset from the authorized research repository or academic supervisor.

2. **Place CSV Files:**
   Save the files into this directory:
   ```
   data/
   ├── .gitkeep
   ├── README.md
   ├── Training.csv   <- (Place here, not tracked by Git)
   └── Testing.csv    <- (Place here, not tracked by Git)
   ```

3. **Execute Deterministic Pipeline (Optional Retraining):**
   Run the training and caching script from the project root:
   ```bash
   python backend/app/pipeline/train_and_cache.py
   ```
   This will regenerate all artifacts in `backend/artifacts/`:
   - `reducts.json` (Johnson greedy discernibility reducts)
   - `association_rules.json` (Apriori mined rules)
   - `symptoms_catalog.json` (132 clinical condition attributes catalog)
   - `metadata.json` (universe statistics and decision classes)
   - `benchmarks.json` (masked missingness evaluations at 0%, 10%, 30%, 50%, 70%)
   - `confusion_matrix.json` (41x41 multiclass diagnostic matrix)
   - `ml_models.joblib` (baseline models: Naive Bayes, Logistic Regression, Random Forest, Decision Tree, SVM, KNN)

---

## 4. Security Reminder
Do **not** upload patient-identifiable healthcare records or unauthorized medical datasets. Do **not** commit raw CSV files to version control.
