"""Map model outputs to 0–100 risk score and display bands."""

from config import settings


def phishing_probability_to_risk_score(phishing_prob: float) -> float:
    """
    Convert model phishing class probability to 0–100 score.
    This is a linear scale from predicted phishing probability, not a calibrated real-world probability.
    """
    return round(max(0.0, min(1.0, phishing_prob)) * 100.0, 1)


def risk_band_from_score(score: float) -> str:
    if score <= settings.risk_low_max:
        return "Low Risk"
    if score <= settings.risk_suspicious_max:
        return "Suspicious"
    if score <= settings.risk_high_max:
        return "High Risk"
    return "Critical Risk"


def classification_from_score_and_label(label: int, score: float) -> str:
    if label == 1:
        if score >= 61:
            return "Phishing"
        return "Suspicious"
    if score >= 31:
        return "Suspicious"
    return "Legitimate"


def recommended_action(classification: str, signs_count: int) -> str:
    if classification == "Phishing":
        return (
            "Do not click links or reply. Delete the message and report it through the official app or email provider. "
            "If you already shared credentials, change passwords immediately using official sites only."
        )
    if classification == "Suspicious":
        return (
            "Treat as unverified. Confirm through official channels (in-app support or typed official URL). "
            "Do not enter passwords or OTPs from this message."
        )
    if signs_count > 0:
        return "Message looks mostly safe, but review the warning signs and stay cautious with links."
    return "No strong phishing indicators detected. Still avoid clicking unknown links."
