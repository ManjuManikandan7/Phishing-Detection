"""FastAPI entrypoint for phishing detection."""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    AppInfoResponse,
    EvaluationMetricRow,
    EvaluationResponse,
    HealthResponse,
    ModelsResponse,
)
from services.analyze_service import analyze_message, resolve_model_id
from services.model_registry import list_models

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/", response_model=AppInfoResponse)
def root() -> AppInfoResponse:
    return AppInfoResponse(
        name=settings.app_name,
        version=settings.app_version,
        description=(
            "Analyzes user-submitted text for phishing indicators using trained models or an explicit baseline. "
            "Does not intercept game chats; integration would require authorized APIs."
        ),
        docs_url="/docs",
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=settings.app_version)


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(body: AnalyzeRequest) -> AnalyzeResponse:
    model_id = resolve_model_id(body.model)
    return analyze_message(body.message, model_id)


@app.get("/models", response_model=ModelsResponse)
def models() -> ModelsResponse:
    return ModelsResponse(models=list_models(settings.default_model), default_model=settings.default_model)


@app.get("/evaluation", response_model=EvaluationResponse)
def evaluation() -> EvaluationResponse:
    path: Path = settings.evaluation_file
    if not path.exists():
        return EvaluationResponse(
            available=False,
            dataset_note="No evaluation file yet. Train models and run ml/evaluate.py.",
            results=[],
            best_by_f1=None,
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Evaluation file is corrupted.") from exc

    rows = [EvaluationMetricRow(**row) for row in data.get("results", [])]
    return EvaluationResponse(
        available=bool(data.get("available")),
        dataset_note=data.get("dataset_note", ""),
        test_split=data.get("test_split"),
        results=rows,
        best_by_f1=data.get("best_by_f1"),
    )
