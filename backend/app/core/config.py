"""Configuration settings for the Rough Set Disease Recommender System.
Academic decision-support prototype.
"""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = (
        "An Intelligent Recommender System Using Machine Learning, "
        "Association Rules and Rough Set for Disease Prediction from Incomplete Symptom Set"
    )
    PROJECT_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

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

    # Server Configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ]


settings = Settings()
