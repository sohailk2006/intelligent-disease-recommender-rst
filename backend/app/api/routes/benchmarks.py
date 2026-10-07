"""API Routes for Benchmarks & Evaluation Results."""

import json
from fastapi import APIRouter, HTTPException
from app.core.config import settings

router = APIRouter(prefix="/benchmarks", tags=["Benchmarks & Evaluation"])


def _load_json_artifact(filename: str):
    file_path = settings.ARTIFACTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Artifact {filename} not yet generated.",
        )
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("")
def get_benchmarks():
    """Retrieve complete missing-rate benchmark results (0%, 10%, 30%, 50%, 70% missing)."""
    return _load_json_artifact("benchmarks.json")


@router.get("/confusion-matrix")
def get_confusion_matrix():
    """Retrieve 0% missing Testing.csv confusion matrix and per-disease metrics."""
    return _load_json_artifact("confusion_matrix.json")
