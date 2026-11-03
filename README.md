# Intelligent Disease Recommender System
### An Intelligent Recommender System Using Machine Learning, Association Rules and Rough Set for Disease Prediction from Incomplete Symptom Set

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://diagnostic-recommender-web.onrender.com)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20TypeScript-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TailwindCSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

---

## 📌 Overview & Research Motivation

In clinical decision support, patients frequently present with **incomplete symptom profiles**—reporting only primary complaints while leaving dozens of secondary symptoms unqueried or unobserved. 

Conventional machine learning classifiers (Decision Trees, Random Forests, SVMs) require dense feature vectors, forcing an imputation assumption (typically asserting that unqueried symptoms are absent: $? \to 0$). Under severe symptom incompleteness (e.g., 70% missing symptoms), this imputation causes severe misclassification and greedy tree split degradation.

This project implements a **hybrid diagnostic recommendation engine** combining:
1. **Rough Set Theory (RST):** Utilizes tolerance relations $T(q, x)$ to preserve unknown symptoms as explicitly unknown rather than absent. Binds deterministic certainty through **Lower Approximations** $\underline{R}(X)$ and characterizes diagnostic ambiguity through **Boundary Regions** $BN(X)$.
2. **Johnson Greedy Reduct Reduction:** Computes minimal discernibility reducts to reduce clinical dimensionality from 132 symptoms down to **38 essential condition attributes** while maintaining full dependency ($\gamma_C(D) = 1.0$).
3. **Association Rule Mining:** Mines 831 clinical symptom co-occurrence patterns using the Apriori algorithm ($\text{min\_confidence} \ge 0.70, \text{min\_support} \ge 0.01$).
4. **Comparative Machine Learning Baselines:** Evaluates robustness against 6 standard algorithms (BernoulliNB, Logistic Regression, Random Forest, Decision Tree, Support Vector Machine, and K-Nearest Neighbors) across 5 controlled missingness levels ($0\%, 10\%, 30\%, 50\%, 70\%$).

---

## 🚀 Live Demonstration

- **Web Application:** [https://diagnostic-recommender-web.onrender.com](https://diagnostic-recommender-web.onrender.com)
- **Backend API (Swagger Docs):** [https://diagnostic-recommender-api.onrender.com/docs](https://diagnostic-recommender-api.onrender.com/docs)
- **API Health Endpoint:** [https://diagnostic-recommender-api.onrender.com/health](https://diagnostic-recommender-api.onrender.com/health)

---

## 🔬 Triad Architecture

```mermaid
flowchart TD
    A[Patient Symptom Intake\nKnown Present: 1, Known Absent: 0, Unknown: ?] --> B{Incomplete Query Relation T}
    
    B -->|Tolerance Neighborhood [q]T| C[Rough Set Engine\nPawlak Approximations]
    B -->|Symptom Co-occurrence| D[Association Rule Mining\n831 Apriori Rules]
    B -->|Zero-Imputed Feature Vector| E[ML Baseline Models\nRF, DT, NB, LR, SVM, KNN]
    
    C --> F[Diagnostic Classification\n- Lower Approximation: Certain\n- Boundary Region: Ambiguous\n- Rough Membership Score]
    D --> G[Evidence & Clinical Support\nRule Confidence & Lift Analysis]
    E --> H[Empirical Degradation Comparison\n0%, 10%, 30%, 50%, 70% Missing]
    
    F --> I[Clinical Recommendation Dashboard\nWith Follow-up Disambiguation Queries]
    G --> I
    H --> I
```

---

## 📊 Dataset & Empirical Benchmark Summary

- **Universe Size ($U$):** 4,920 complete clinical patient records
- **Condition Attributes ($C$):** 132 binary symptom attributes
- **Decision Classes ($D$):** 41 mutually disjoint disease categories
- **Selected Reduct:** 38 essential condition attributes derived via Johnson Greedy Discernibility Reduct ($\gamma_{\text{reduct}}(D) = 1.0$)

### Performance under Controlled Symptom Incompleteness (42 Held-out Samples)

| Model / Approach | 0% Missing | 10% Missing | 30% Missing | 50% Missing | 70% Missing |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Rough Set Theory (Tolerance)** | **100.00%** | **100.00%** | **100.00%** | **100.00%** | **Deterministic Bounds** |
| **Bernoulli Naive Bayes** | 100.00% | 99.52% | 96.67% | 80.47% | 49.05% |
| **Random Forest (100 trees)** | 100.00% | 98.10% | 95.71% | 80.00% | 49.05% |
| **Decision Tree** | 97.62% | 93.33% | 79.52% | 61.43% | 48.10% |
| **Support Vector Machine (RBF)** | 100.00% | 97.62% | 95.24% | 76.67% | 47.14% |
| **K-Nearest Neighbors ($k=5$)** | 100.00% | 97.14% | 90.95% | 70.00% | 35.71% |

*Key finding: Statistical classifiers experience a steep drop from ~97-100% down to ~35-49% when 70% of symptom attributes are unknown. In contrast, Rough Set Theory identifies the exact compatible upper approximation candidate set and recommends follow-up clinical questions based on information-theoretic variance to resolve boundary ambiguity.*

---

## 📁 Repository Structure

```
.
├── backend/                         # FastAPI Application & RST Core
│   ├── app/
│   │   ├── api/                     # REST API routers & schemas
│   │   │   ├── routes/              # recommend, metadata, benchmarks, comparison, presets
│   │   │   └── main.py              # Application entrypoint & CORS middleware
│   │   ├── core/                    # Application settings (0.0.0.0, CORS, paths)
│   │   ├── evaluation/              # Masked missingness evaluation engine
│   │   ├── ml/                      # Baseline ML model implementations
│   │   ├── pipeline/                # Deterministic train & cache script
│   │   ├── rst/                     # Rough Set Theory mathematical engine
│   │   │   ├── approximations.py    # Lower, Upper, Boundary, Negative regions
│   │   │   ├── decision_table.py    # Information system decision table
│   │   │   ├── dependency.py        # Degree of dependency gamma_C(D)
│   │   │   ├── discernibility.py    # Discernibility matrix & modulo-D discernibility
│   │   │   ├── engine.py            # RoughSetRecommender core inference
│   │   │   ├── incomplete.py        # Tolerance relation T(q, x) for incomplete queries
│   │   │   ├── indiscernibility.py  # Classical Pawlak equivalence partitioning
│   │   │   └── reduct.py            # Johnson greedy discernibility reduct algorithm
│   │   └── rules/                   # Apriori association rule mining
│   ├── artifacts/                   # Precomputed research artifacts (JSON & Joblib)
│   ├── tests/                       # Automated pytest test suites (11/11 passing)
│   └── requirements.txt             # Pinned production Python dependencies
│
├── frontend/                        # React 18 + TypeScript + Vite Application
│   ├── src/
│   │   ├── api/client.ts            # API client with automatic URL resolution
│   │   ├── components/              # UI presentation components
│   │   │   ├── Header.tsx           # Responsive navigation bar with mobile drawer
│   │   │   ├── HomeView.tsx         # Research overview & triad architecture cards
│   │   │   ├── SymptomInputConsole.tsx # Interactive 132-symptom input console
│   │   │   ├── RecommendationView.tsx  # Diagnostic result, bounds & follow-up questions
│   │   │   ├── ComparisonLab.tsx    # Live multi-model comparison on active query
│   │   │   ├── RstTheoryExplorer.tsx # Mathematical formalism & 38 reduct attributes
│   │   │   ├── AssociationRulesExplorer.tsx # Filterable 831-rule explorer
│   │   │   └── BenchmarksDashboard.tsx # Comprehensive faculty benchmark tables
│   │   ├── types/index.ts           # Strict TypeScript interface contracts
│   │   └── App.tsx                  # Main single-page application router & state
│   ├── package.json                 # Pinned NPM dependencies
│   └── vite.config.ts               # Vite configuration & development proxy
│
├── data/                            # Dataset documentation & sample structures
│   ├── README.md                    # Data governance & schema specifications
│   ├── Training.csv                 # 4,920 training records (132 symptoms, 41 diseases)
│   └── Testing.csv                  # 42 evaluation records
│
├── docs/                            # Research & Methodology Documentation
│   ├── rst-methodology.md           # Formal mathematical proofs and definitions
│   ├── incomplete-information.md    # Tolerance relations and epistemic uncertainty
│   ├── evaluation.md                # Benchmark methodology and results
│   ├── backend-audit.md             # API contract audit
│   └── demo-flow.md                 # Guided presentation walkthrough
│
├── Dockerfile                       # Production container specification
├── render.yaml                      # Infrastructure-as-Code deployment blueprint
└── README.md                        # Project documentation (this file)
```

---

## 🛠️ Local Development Quickstart

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Clone the Repository
```bash
git clone https://github.com/sohailk2006/intelligent-disease-recommender-rst.git
cd intelligent-disease-recommender-rst
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv .venv
# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run test suite
python -m pytest backend/tests/ -o pythonpath=backend -q

# Start FastAPI development server
python -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Build check
npm run build

# Start Vite development server
npm run dev
```
Open [http://127.0.0.1:5173](http://127.0.0.1:5173) in your browser.

---

## 🐳 Docker Container Execution

You can run the complete backend application inside a container:

```bash
# Build the Docker image
docker build -t disease-recommender-api .

# Run the container
docker run -p 8000:8000 -e CORS_ORIGINS="*" disease-recommender-api
```
Check health at [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

---

## ⚖️ Academic Notice & Disclaimer

> **Important:** This system is an **Academic Decision-Support Prototype** engineered for computational evaluation and academic research. It is **not** certified as a clinical medical device and is **not** intended to replace clinical judgment, physical examination, or professional laboratory diagnostics.
