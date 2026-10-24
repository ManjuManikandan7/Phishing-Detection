"""Application configuration from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Phishing Detection API"
    app_version: str = "1.0.0"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    max_message_length: int = 5000
    default_model: str = "baseline"
    backend_dir: Path = Path(__file__).resolve().parent
    ml_dir: Path = backend_dir / "ml"
    artifacts_dir: Path = ml_dir / "artifacts"
    data_dir: Path = ml_dir / "data"
    evaluation_file: Path = artifacts_dir / "evaluation_results.json"

    # Risk band thresholds (initial project settings — validate on your data)
    risk_low_max: int = 30
    risk_suspicious_max: int = 60
    risk_high_max: int = 80


settings = Settings()
