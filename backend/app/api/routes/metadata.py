"""API Routes for System Metadata, Symptoms, Diseases, Reducts, and Rules."""

import json
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Query, HTTPException
from app.core.config import settings

router = APIRouter(tags=["Knowledge & Metadata"])


def _load_json_artifact(filename: str) -> Any:
    file_path = settings.ARTIFACTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Artifact {filename} not yet generated. Please execute offline pipeline.",
        )
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/symptoms")
def get_symptoms(category: Optional[str] = None):
    """Retrieve full catalog of 132 symptoms with medical categories and frequencies."""
    catalog = _load_json_artifact("symptoms_catalog.json")
    if category:
        catalog = [s for s in catalog if s["category"].lower() == category.lower()]
    return {
        "total_symptoms": len(catalog),
        "categories": [
            "constitutional",
            "skin_mucosa",
            "gastrointestinal",
            "respiratory",
            "neurological_sensory",
            "musculoskeletal",
            "urinary_hepatic",
            "general_clinical",
        ],
        "symptoms": catalog,
    }


@router.get("/diseases")
def get_diseases():
    """Retrieve the 41 disease classes and class distribution."""
    meta = _load_json_artifact("metadata.json")
    dataset_summary = meta["dataset_summary"]
    return {
        "total_diseases": dataset_summary["num_decision_classes"],
        "diseases": dataset_summary["decision_classes"],
        "distribution": dataset_summary["decision_distribution"],
    }


@router.get("/metadata")
def get_metadata():
    """Retrieve research metadata, measured execution runtimes, and reproducibility settings."""
    return _load_json_artifact("metadata.json")


@router.get("/reducts")
def get_reducts():
    """Retrieve Rough Set minimal reduct candidates and Core attributes analysis."""
    return _load_json_artifact("reducts.json")


@router.get("/association-rules")
def get_association_rules(
    disease: Optional[str] = None,
    min_confidence: float = Query(default=0.7, ge=0.5, le=1.0),
    min_lift: float = Query(default=1.0, ge=1.0),
    limit: int = Query(default=50, ge=1, le=200),
):
    """Retrieve mined association rules connecting symptom itemsets to disease prognosis."""
    rules = _load_json_artifact("association_rules.json")
    filtered = rules
    if disease:
        filtered = [r for r in filtered if r["consequent"].lower() == disease.lower()]
    filtered = [
        r for r in filtered
        if r["confidence"] >= min_confidence and r["lift"] >= min_lift
    ]
    return {
        "total_mined_rules": len(rules),
        "matching_rules_count": len(filtered),
        "rules": filtered[:limit],
    }
