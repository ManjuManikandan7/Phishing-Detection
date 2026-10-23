"""API smoke tests (baseline — no trained ML required)."""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_analyze_baseline_phishing():
    r = client.post(
        "/analyze",
        json={
            "message": "URGENT! Claim free diamonds now at http://fake-game-reward.xyz/login verify your password",
            "model": "baseline",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["model_type"] == "baseline"
    assert data["risk_score"] >= 0
    assert len(data["warning_signs"]) >= 1


def test_analyze_empty_rejected():
    r = client.post("/analyze", json={"message": "   ", "model": "baseline"})
    assert r.status_code == 422


def test_trained_or_unavailable_model():
    status = client.get("/models").json()
    cnn = next(m for m in status["models"] if m["id"] == "cnn")
    r = client.post("/analyze", json={"message": "hello team meeting at 3pm", "model": "cnn"})
    if cnn["status"] == "available":
        assert r.status_code == 200
        assert r.json()["model_type"] == "trained"
    else:
        assert r.status_code == 503


def test_tinybert_unavailable_when_not_trained():
    status = client.get("/models").json()
    tb = next(m for m in status["models"] if m["id"] == "tinybert")
    if tb["status"] != "available":
        r = client.post("/analyze", json={"message": "verify account now", "model": "tinybert"})
        assert r.status_code == 503
