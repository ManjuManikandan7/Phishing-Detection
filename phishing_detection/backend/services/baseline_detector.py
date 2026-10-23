"""Explicit rule-based baseline — not a trained deep learning model."""

from dataclasses import dataclass

from services.warning_signs import extract_warning_signs


@dataclass
class BaselineResult:
    label: int
    phishing_score: float  # 0–1 heuristic, not ML probability


def baseline_predict(message: str) -> BaselineResult:
    signs = extract_warning_signs(message)
    score = 0.0
    weights = {"high": 0.35, "medium": 0.2, "low": 0.1}
    for s in signs:
        score += weights.get(s.severity, 0.1)
    score = min(1.0, score)
    if score >= 0.45:
        label = 1
    elif score >= 0.2:
        label = 1 if any(s.severity == "high" for s in signs) else 0
    else:
        label = 0
    return BaselineResult(label=label, phishing_score=score)
