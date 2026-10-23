"""Pydantic request/response models."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    model: str | None = Field(default=None, description="Optional model id: cnn, bilstm, tinybert, baseline")

    @field_validator("message")
    @classmethod
    def strip_message(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Message cannot be empty or whitespace only.")
        return stripped


class WarningSign(BaseModel):
    category: str
    description: str
    severity: Literal["low", "medium", "high"]


class AnalyzeResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    classification: Literal["Legitimate", "Suspicious", "Phishing"]
    label: int
    risk_score: float = Field(..., ge=0, le=100)
    risk_band: str
    warning_signs: list[WarningSign]
    recommended_action: str
    model_used: str
    model_type: Literal["trained", "baseline"]
    confidence_note: str


class ModelInfo(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    id: str
    name: str
    status: Literal["available", "not_trained", "error"]
    description: str


class ModelsResponse(BaseModel):
    models: list[ModelInfo]
    default_model: str


class HealthResponse(BaseModel):
    status: str
    version: str


class AppInfoResponse(BaseModel):
    name: str
    version: str
    description: str
    docs_url: str


class EvaluationMetricRow(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_id: str
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f1_score: float | None = None
    roc_auc: float | None = None
    avg_inference_ms: float | None = None
    confusion_matrix: list[list[int]] | None = None
    note: str | None = None


class EvaluationResponse(BaseModel):
    available: bool
    dataset_note: str
    test_split: str | None = None
    results: list[EvaluationMetricRow]
    best_by_f1: str | None = None
