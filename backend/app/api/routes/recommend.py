"""API Route for Rough Set Disease Recommendation."""

import json
import time
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
import pandas as pd

from app.core.config import settings
from app.api.schemas import RecommendRequest, RecommendResponse
from app.rst.decision_table import DecisionTable
from app.rst.engine import RoughSetRecommender
from app.rules.association_mining import AssociationRuleMiner

router = APIRouter(prefix="/recommend", tags=["Recommendation"])

# Cached singleton references loaded on startup
_table: Optional[DecisionTable] = None
_recommender: Optional[RoughSetRecommender] = None
_rule_miner: Optional[AssociationRuleMiner] = None
_active_reducts: Optional[Dict[str, Any]] = None


def get_dependencies():
    global _table, _recommender, _rule_miner, _active_reducts
    if _table is None:
        df = pd.read_csv(settings.TRAIN_DATA_PATH)
        _table = DecisionTable(df, decision_col="prognosis", drop_columns=["Unnamed: 133"])

        # Load precomputed reducts
        reducts_path = settings.ARTIFACTS_DIR / "reducts.json"
        if reducts_path.exists():
            with open(reducts_path, "r", encoding="utf-8") as f:
                _active_reducts = json.load(f)
            primary_reduct = _active_reducts["reducts"][0]["attributes"]
        else:
            primary_reduct = None

        _recommender = RoughSetRecommender(_table, active_reduct=primary_reduct)

        # Load precomputed association rules
        rules_path = settings.ARTIFACTS_DIR / "association_rules.json"
        _rule_miner = AssociationRuleMiner(_table)
        if rules_path.exists():
            with open(rules_path, "r", encoding="utf-8") as f:
                _rule_miner.disease_rules = json.load(f)

    return _recommender, _rule_miner, _active_reducts


@router.post("", response_model=RecommendResponse)
def get_recommendation(
    request: RecommendRequest,
    deps=Depends(get_dependencies),
):
    recommender, rule_miner, active_reducts = deps

    # Select aligned reduct if requested
    if request.reduct_id and active_reducts:
        for r in active_reducts.get("reducts", []):
            if r["id"] == request.reduct_id:
                recommender.active_reduct = r["attributes"]
                break

    t0 = time.time()
    result = recommender.recommend(request.symptoms, top_k=request.top_k)
    latency_ms = round((time.time() - t0) * 1000.0, 3)

    if result.get("status") != "SUCCESS":
        raise HTTPException(status_code=400, detail=result.get("message", "Prediction failed."))

    # Match association rules
    matched_rules = rule_miner.find_matching_rules(request.symptoms, limit=5)

    return {
        "status": "SUCCESS",
        "primary_recommendation": result["primary_recommendation"],
        "top_candidates": result["top_candidates"],
        "rough_set_reasoning": result["rough_set_reasoning"],
        "matched_association_rules": matched_rules,
        "prediction_latency_ms": latency_ms,
    }
