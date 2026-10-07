"""Preset clinical test scenarios loaded from Testing.csv for interactive experimentation."""

from typing import List, Dict, Any
from fastapi import APIRouter
import pandas as pd
import numpy as np

from app.core.config import settings

router = APIRouter(prefix="/presets", tags=["Test Scenarios"])


@router.get("")
def get_presets():
    """Retrieve pre-built interactive test cases from Testing.csv with varying missing rates."""
    test_df = pd.read_csv(settings.TEST_DATA_PATH)
    test_df = test_df.loc[:, ~test_df.columns.str.contains("^Unnamed")]
    cond_cols = [c for c in test_df.columns if c != "prognosis"]

    scenarios = []

    # Curate key diseases from test set
    target_diseases = [
        ("Dengue", "High fever, chills, joint & muscle pain, skin rash"),
        ("Malaria", "Chills, vomiting, high fever, sweating, headache"),
        ("Diabetes ", "Fatigue, weight loss, increased appetite, polyuria"),
        ("Allergy", "Continuous sneezing, shivering, chills, watering eyes"),
        ("Psoriasis", "Skin rash, joint pain, skin peeling, silver-like dusting"),
        ("Jaundice", "Itching, vomiting, fatigue, weight loss, yellowish skin"),
        ("Fungal infection", "Itching, skin rash, nodal eruptions, dischromic patches"),
    ]

    for disease_name, clinical_desc in target_diseases:
        rows = test_df[test_df["prognosis"] == disease_name]
        if len(rows) == 0:
            continue
        row = rows.iloc[0]

        full_symptoms = {c: int(row[c]) for c in cond_cols}
        positive_symptoms = [c for c in cond_cols if int(row[c]) == 1]

        # Scenario 1: Complete 100% known
        scenarios.append({
            "id": f"{disease_name.strip().lower()}_complete",
            "title": f"{disease_name.strip()} (Complete - 0% Missing)",
            "disease_ground_truth": disease_name,
            "missing_rate_label": "0% Missing",
            "missing_rate": 0.0,
            "description": f"Ground-truth test sample from Testing.csv with all 132 symptoms explicitly documented.",
            "present_symptoms": positive_symptoms,
            "symptoms": full_symptoms,
        })

        # Scenario 2: Moderate Missing (50% missing)
        rng_50 = np.random.default_rng(42)
        masked_50 = dict(full_symptoms)
        mask_cols_50 = rng_50.choice(cond_cols, size=int(len(cond_cols) * 0.5), replace=False)
        for col in mask_cols_50:
            masked_50[col] = "?"

        scenarios.append({
            "id": f"{disease_name.strip().lower()}_50_missing",
            "title": f"{disease_name.strip()} (Moderate Incomplete - 50% Missing)",
            "disease_ground_truth": disease_name,
            "missing_rate_label": "50% Missing",
            "missing_rate": 0.5,
            "description": f"Simulated clinical scenario where 66 out of 132 symptoms are unknown ('?').",
            "present_symptoms": [s for s in positive_symptoms if masked_50.get(s) == 1],
            "symptoms": masked_50,
        })

        # Scenario 3: Highly Incomplete (70% missing)
        rng_70 = np.random.default_rng(1042)
        masked_70 = dict(full_symptoms)
        mask_cols_70 = rng_70.choice(cond_cols, size=int(len(cond_cols) * 0.7), replace=False)
        for col in mask_cols_70:
            masked_70[col] = "?"

        scenarios.append({
            "id": f"{disease_name.strip().lower()}_70_missing",
            "title": f"{disease_name.strip()} (Severe Incomplete - 70% Missing)",
            "disease_ground_truth": disease_name,
            "missing_rate_label": "70% Missing",
            "missing_rate": 0.7,
            "description": f"Sparse clinical report where 92 out of 132 symptoms are unknown ('?').",
            "present_symptoms": [s for s in positive_symptoms if masked_70.get(s) == 1],
            "symptoms": masked_70,
        })

    return {
        "total_presets": len(scenarios),
        "presets": scenarios,
    }
