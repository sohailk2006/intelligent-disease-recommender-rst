"""Integration tests for FastAPI application endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)


def test_root_and_health():
    resp_root = client.get("/")
    assert resp_root.status_code == 200
    assert "Rough Set" in resp_root.json()["project"]

    resp_health = client.get("/api/health")
    assert resp_health.status_code == 200
    data = resp_health.json()
    assert data["status"] == "HEALTHY"
    assert data["artifacts_cached"] is True
    assert data["universe_size"] == 4920


def test_get_symptoms_and_diseases():
    resp_symptoms = client.get("/api/symptoms")
    assert resp_symptoms.status_code == 200
    s_data = resp_symptoms.json()
    assert s_data["total_symptoms"] == 132
    assert len(s_data["symptoms"]) == 132

    # Filter by category
    resp_cat = client.get("/api/symptoms?category=respiratory")
    assert resp_cat.status_code == 200
    assert len(resp_cat.json()["symptoms"]) > 0

    resp_diseases = client.get("/api/diseases")
    assert resp_diseases.status_code == 200
    d_data = resp_diseases.json()
    assert d_data["total_diseases"] == 41
    assert len(d_data["diseases"]) == 41


def test_get_metadata_reducts_benchmarks():
    resp_meta = client.get("/api/metadata")
    assert resp_meta.status_code == 200
    assert "timings" in resp_meta.json()
    assert "reduct_calculation_time_seconds" in resp_meta.json()["timings"]

    resp_reducts = client.get("/api/reducts")
    assert resp_reducts.status_code == 200
    r_data = resp_reducts.json()
    assert len(r_data["reducts"]) >= 3
    assert r_data["full_dependency_degree"] == 1.0

    resp_bench = client.get("/api/benchmarks")
    assert resp_bench.status_code == 200
    b_data = resp_bench.json()
    assert b_data["missing_rates"] == [0.0, 0.1, 0.3, 0.5, 0.7]
    assert len(b_data["comparison_summary"]) == 5


def test_recommendation_with_incomplete_symptoms():
    # Incomplete query with known and unknown symptoms
    payload = {
        "symptoms": {
            "itching": 1,
            "skin_rash": 1,
            "nodal_skin_eruptions": 1,
            "dischromic _patches": 1,
            "fatigue": "?",
            "high_fever": 0,
            "joint_pain": "?",
        },
        "top_k": 3,
    }
    resp = client.post("/api/recommend", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["primary_recommendation"] is not None
    assert "Fungal infection" in data["primary_recommendation"]["disease"]
    assert data["rough_set_reasoning"]["unknown_symptoms_count"] > 0
    assert data["rough_set_reasoning"]["tolerance_class_size"] > 0
    assert data["prediction_latency_ms"] >= 0.0


def test_model_comparison_endpoint():
    payload = {
        "symptoms": {
            "chills": 1,
            "vomiting": 1,
            "high_fever": 1,
            "sweating": 1,
            "headache": 1,
            "nausea": 1,
            "muscle_pain": 1,
            "cough": "?",
            "fatigue": "?",
        },
        "top_k": 3,
    }
    resp = client.post("/api/compare", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert "Malaria" in data["rst_prediction"]["primary_disease"]
    assert "RandomForest" in data["ml_predictions"]
    assert "BernoulliNB" in data["ml_predictions"]
    assert "LogisticRegression" in data["ml_predictions"]
    assert "DecisionTree" in data["ml_predictions"]


def test_presets_endpoint():
    resp = client.get("/api/presets")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_presets"] >= 15
    assert any("Dengue" in p["title"] for p in data["presets"])
