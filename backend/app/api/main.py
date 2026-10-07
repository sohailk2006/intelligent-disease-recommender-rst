"""FastAPI Application Entrypoint for Rough Set Recommender System."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import logger

from app.api.routes import recommend, metadata, benchmarks, comparison, presets

app = FastAPI(
    title="Intelligent Recommender System - Rough Set Theory",
    description=(
        "Academic decision-support prototype using Pawlak Rough Set Theory, "
        "Association Rules, and Machine Learning for Disease Prediction from Incomplete Symptom Sets."
    ),
    version=settings.PROJECT_VERSION,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api
app.include_router(recommend.router, prefix=settings.API_PREFIX)
app.include_router(metadata.router, prefix=settings.API_PREFIX)
app.include_router(benchmarks.router, prefix=settings.API_PREFIX)
app.include_router(comparison.router, prefix=settings.API_PREFIX)
app.include_router(presets.router, prefix=settings.API_PREFIX)


@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "academic_notice": "Academic decision-support / recommendation prototype, NOT a medical diagnostic system.",
        "docs_url": "/docs",
        "api_endpoints": {
            "recommend": f"{settings.API_PREFIX}/recommend",
            "symptoms": f"{settings.API_PREFIX}/symptoms",
            "diseases": f"{settings.API_PREFIX}/diseases",
            "metadata": f"{settings.API_PREFIX}/metadata",
            "reducts": f"{settings.API_PREFIX}/reducts",
            "association_rules": f"{settings.API_PREFIX}/association-rules",
            "benchmarks": f"{settings.API_PREFIX}/benchmarks",
            "compare": f"{settings.API_PREFIX}/compare",
            "presets": f"{settings.API_PREFIX}/presets",
        },
    }


@app.get(f"{settings.API_PREFIX}/health")
def health_check():
    artifacts_ready = (settings.ARTIFACTS_DIR / "metadata.json").exists()
    return {
        "status": "HEALTHY",
        "artifacts_cached": artifacts_ready,
        "universe_size": 4920,
        "condition_attributes": 132,
        "decision_classes": 41,
    }
