"""Check which trained model artifacts exist on disk."""

from pathlib import Path

from config import settings
from schemas import ModelInfo

MODEL_DEFS = [
    {
        "id": "cnn",
        "name": "CNN Text Classifier",
        "artifact": "cnn_model.keras",
        "meta": "cnn_meta.json",
        "description": "1D convolution over embedded token sequences.",
    },
    {
        "id": "bilstm",
        "name": "Bi-LSTM Text Classifier",
        "artifact": "bilstm_model.keras",
        "meta": "bilstm_meta.json",
        "description": "Bidirectional LSTM over embedded sequences.",
    },
    {
        "id": "tinybert",
        "name": "TinyBERT (Hugging Face)",
        "artifact": "tinybert",
        "meta": None,
        "description": "Fine-tuned huawei-noah/TinyBERT_General_4L_312D for sequence classification.",
    },
    {
        "id": "baseline",
        "name": "Rule-Based Baseline",
        "artifact": None,
        "meta": None,
        "description": "Heuristic detector for smoke testing when ML models are not trained.",
    },
]


def artifact_path(model_id: str, filename: str | None) -> Path | None:
    if not filename:
        return None
    if model_id == "tinybert" and filename == "tinybert":
        return settings.artifacts_dir / "tinybert"
    return settings.artifacts_dir / filename


def model_status(model_id: str) -> str:
    if model_id == "baseline":
        return "available"
    definition = next((m for m in MODEL_DEFS if m["id"] == model_id), None)
    if not definition:
        return "error"
    art = definition.get("artifact")
    if not art:
        return "error"
    path = artifact_path(model_id, art)
    if path and path.exists():
        if model_id == "tinybert":
            return "available" if (path / "config.json").exists() else "not_trained"
        return "available"
    return "not_trained"


def list_models(default_model: str) -> list[ModelInfo]:
    items: list[ModelInfo] = []
    for m in MODEL_DEFS:
        items.append(
            ModelInfo(
                id=m["id"],
                name=m["name"],
                status=model_status(m["id"]),  # type: ignore[arg-type]
                description=m["description"],
            )
        )
    return items
