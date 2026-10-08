"""API Route for Comparative Model Analysis (RST vs Baselines)."""

import time
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
import pandas as pd
import joblib

from app.core.config import settings
from app.api.schemas import CompareRequest
from app.rst.decision_table import DecisionTable
from app.rst.engine import RoughSetRecommender
from app.ml.baseline_models import MLBaselines

router = APIRouter(prefix="/compare", tags=["Model Comparison"])

_table: Optional[DecisionTable] = None
_recommender: Optional[RoughSetRecommender] = None
_ml_baselines: Optional[MLBaselines] = None


def get_comparison_dependencies():
    global _table, _recommender, _ml_baselines
    if _table is None:
        df = pd.read_csv(settings.TRAIN_DATA_PATH)
        _table = DecisionTable(df, decision_col="prognosis", drop_columns=["Unnamed: 133"])
        _recommender = RoughSetRecommender(_table)
        _ml_baselines = MLBaselines(_table)

        # Load persisted ML models if available
        models_path = settings.ARTIFACTS_DIR / "ml_models.joblib"
        if models_path.exists():
            _ml_baselines.models = joblib.load(models_path)
            _ml_baselines.is_trained = True
        else:
            _ml_baselines.train_models()

    return _recommender, _ml_baselines


@router.post("")
def compare_models(
    request: CompareRequest,
    deps=Depends(get_comparison_dependencies),
):
    """Run RST and all 4 ML baselines on the same query to observe incomplete data handling."""
    recommender, ml_baselines = deps

    # 1. Rough Set Recommender (No imputation; ignores unknown symptoms)
    t0 = time.time()
    rst_res = recommender.recommend(request.symptoms, top_k=request.top_k)
    t_rst = round((time.time() - t0) * 1000.0, 3)

    # 2. ML Baselines (Traditional zero imputation for unknown symptoms)
    t0 = time.time()
    ml_res = ml_baselines.predict_query(request.symptoms, top_k=request.top_k)
    t_ml = round((time.time() - t0) * 1000.0, 3)

    return {
        "status": "SUCCESS",
        "rst_prediction": {
            "model_name": "Rough Set Theory (Selected Tolerance Relation)",
            "primary_disease": rst_res["primary_recommendation"]["disease"] if rst_res.get("primary_recommendation") else "Unknown",
            "confidence": rst_res["primary_recommendation"]["membership_degree"] if rst_res.get("primary_recommendation") else 0.0,
            "approximation_status": rst_res["primary_recommendation"]["approximation_status"] if rst_res.get("primary_recommendation") else "NONE",
            "top_candidates": rst_res.get("top_candidates", []),
            "tolerance_class_size": rst_res["rough_set_reasoning"]["tolerance_class_size"],
            "handling_of_unknowns": "Strictly ignored in tolerance relation (never imputed as 0)",
            "latency_ms": t_rst,
        },
        "ml_predictions": {
            model_name: {
                "model_name": model_name,
                "predicted_disease": pred["predicted_disease"],
                "confidence": pred["confidence"],
                "top_candidates": pred["top_candidates"],
                "handling_of_unknowns": "Imputed as 0 (assumed symptom absent)",
            }
            for model_name, pred in ml_res.items()
        },
        "total_latency_ms": round(t_rst + t_ml, 3),
    }
