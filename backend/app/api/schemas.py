"""Pydantic schemas for the FastAPI endpoints."""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    """Request payload for disease recommendation."""
    symptoms: Dict[str, Union[int, str, None]] = Field(
        ...,
        description="Dictionary mapping symptom names to 1 (present), 0 (absent), or '?' (unknown).",
        example={"itching": 1, "skin_rash": 1, "fatigue": "?", "high_fever": 0},
    )
    top_k: int = Field(default=5, ge=1, le=20, description="Number of top candidates to return.")
    reduct_id: Optional[str] = Field(default="reduct_johnson", description="Reduct candidate ID to align with.")


class CompareRequest(BaseModel):
    """Request payload to compare RST with ML baselines."""
    symptoms: Dict[str, Union[int, str, None]] = Field(
        ...,
        description="Symptom dictionary for comparative multi-model execution.",
    )
    top_k: int = Field(default=3, ge=1, le=10)


class DisambiguationSuggestion(BaseModel):
    symptom: str
    discriminative_power: float = Field(
        ...,
        description="Project-specific discriminative power heuristic: prevalence variance across top candidate diseases (higher = more distinguishing).",
    )
    rates_per_disease: Dict[str, float]


class CandidateDisease(BaseModel):
    disease: str
    membership_degree: float
    confidence_percentage: float
    support_count: int
    approximation_status: str
    approximation_code: str
    aligned_symptoms: List[str]
    conflicting_symptoms: List[str]


class RoughSetReasoning(BaseModel):
    tolerance_class_size: int
    is_exact_match: bool
    known_symptoms_count: int
    unknown_symptoms_count: int
    strategy: Dict[str, Any]
    reduct_alignment: Dict[str, Any]
    boundary_uncertainty: bool
    suggested_disambiguation_symptoms: List[DisambiguationSuggestion]


class RecommendResponse(BaseModel):
    status: str
    primary_recommendation: Optional[CandidateDisease]
    top_candidates: List[CandidateDisease]
    rough_set_reasoning: RoughSetReasoning
    matched_association_rules: List[Dict[str, Any]]
    prediction_latency_ms: float
