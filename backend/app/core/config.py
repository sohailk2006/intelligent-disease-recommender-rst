"""Configuration settings for the Rough Set Disease Recommender System.
Academic decision-support prototype.
"""

from pathlib import Path
from typing import Union
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = (
        "An Intelligent Recommender System Using Machine Learning, "
        "Association Rules and Rough Set for Disease Prediction from Incomplete Symptom Set"
    )
    PROJECT_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    ENVIRONMENT: str = "production"

    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    TRAIN_DATA_PATH: Path = DATA_DIR / "Training.csv"
    TEST_DATA_PATH: Path = DATA_DIR / "Testing.csv"
    ARTIFACTS_DIR: Path = BASE_DIR / "backend" / "artifacts"

    # Reproducibility & Random Seeds
    RANDOM_SEED: int = 42

    # Rough Set & Reduct Parameters
    REDUCT_MAX_ATTRIBUTES: int = 60
    DEFAULT_REDUCT_ALGORITHM: str = "johnson"

    # Association Rule Mining Parameters
    ASSOCIATION_MIN_SUPPORT: float = 0.01
    ASSOCIATION_MIN_CONFIDENCE: float = 0.70
    ASSOCIATION_MAX_LEN: int = 3

    # Evaluation & Masking Benchmark Parameters
    BENCHMARK_MISSING_RATES: list[float] = [0.0, 0.1, 0.3, 0.5, 0.7]
    BENCHMARK_REPETITIONS: int = 5

    # Server Configuration (binds to 0.0.0.0 when deployed)
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: Union[list[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> list[str]:
        if isinstance(v, str) and not v.strip().startswith("["):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


settings = Settings()
