"""Orchestrate prediction, risk scoring, and response building."""

from fastapi import HTTPException

from config import settings
from schemas import AnalyzeResponse
from services.baseline_detector import baseline_predict
from services.model_registry import model_status
from services.risk_scoring import (
    classification_from_score_and_label,
    phishing_probability_to_risk_score,
    recommended_action,
    risk_band_from_score,
)
from services.warning_signs import extract_warning_signs
from utils.text_utils import truncate_text


def resolve_model_id(requested: str | None) -> str:
    model_id = (requested or settings.default_model).lower().strip()
    valid = {"cnn", "bilstm", "tinybert", "baseline"}
    if model_id not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid model. Choose from: {sorted(valid)}")
    return model_id


def analyze_message(message: str, model_id: str) -> AnalyzeResponse:
    message = truncate_text(message.strip(), settings.max_message_length)
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    signs = extract_warning_signs(message)

    if model_id == "baseline":
        base = baseline_predict(message)
        phishing_prob = base.phishing_score
        label = base.label
        model_used = "Rule-Based Baseline"
        model_type = "baseline"
        confidence_note = (
            "Score from heuristic rules, not a trained CNN/Bi-LSTM/TinyBERT model. "
            "Use for smoke testing until ML artifacts are trained."
        )
    else:
        status = model_status(model_id)
        if status != "available":
            raise HTTPException(
                status_code=503,
                detail=f"Model '{model_id}' is not available ({status}). Train it or use baseline explicitly.",
            )
        try:
            from ml.predict import predict_with_model

            result = predict_with_model(model_id, message)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail="Model inference failed.") from exc

        phishing_prob = result.phishing_probability
        label = result.label
        model_used = {"cnn": "CNN", "bilstm": "Bi-LSTM", "tinybert": "TinyBERT"}[model_id]
        model_type = "trained"
        confidence_note = (
            "Risk score is phishing-class score × 100 from the model output (sigmoid/softmax). "
            "Threshold bands are initial project settings and should be validated on your data."
        )

    risk_score = phishing_probability_to_risk_score(phishing_prob)
    classification = classification_from_score_and_label(label, risk_score)
    band = risk_band_from_score(risk_score)

    return AnalyzeResponse(
        classification=classification,
        label=label,
        risk_score=risk_score,
        risk_band=band,
        warning_signs=signs,
        recommended_action=recommended_action(classification, len(signs)),
        model_used=model_used,
        model_type=model_type,
        confidence_note=confidence_note,
    )
