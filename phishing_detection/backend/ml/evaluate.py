"""Evaluate all trained models on the held-out test set."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import json
import time

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from config import settings
from ml.predict import predict_bilstm, predict_cnn, predict_tinybert
from ml.preprocessing import load_labeled_csv
from services.baseline_detector import baseline_predict


def _metrics(y_true, y_pred, y_prob) -> dict:
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist()
    out = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
        "confusion_matrix": cm,
    }
    try:
        out["roc_auc"] = float(roc_auc_score(y_true, y_prob))
    except ValueError:
        out["roc_auc"] = None
    return out


def evaluate_model(model_id: str, messages: list[str], labels: list[int]) -> dict | None:
    y_true = np.array(labels)
    y_pred = []
    y_prob = []
    times = []

    for msg in messages:
        try:
            if model_id == "baseline":
                t0 = time.perf_counter()
                r = baseline_predict(msg)
                times.append((time.perf_counter() - t0) * 1000)
                y_pred.append(r.label)
                y_prob.append(r.phishing_score)
            elif model_id == "cnn":
                r = predict_cnn(msg)
                times.append(r.inference_ms)
                y_pred.append(r.label)
                y_prob.append(r.phishing_probability)
            elif model_id == "bilstm":
                r = predict_bilstm(msg)
                times.append(r.inference_ms)
                y_pred.append(r.label)
                y_prob.append(r.phishing_probability)
            elif model_id == "tinybert":
                r = predict_tinybert(msg)
                times.append(r.inference_ms)
                y_pred.append(r.label)
                y_prob.append(r.phishing_probability)
            else:
                return None
        except (FileNotFoundError, ModuleNotFoundError, RuntimeError):
            return None

    m = _metrics(y_true, np.array(y_pred), np.array(y_prob))
    m["avg_inference_ms"] = float(np.mean(times)) if times else None
    m["model_id"] = model_id
    return m


def main() -> None:
    test_path = settings.data_dir / "test.csv"
    if not test_path.exists():
        raise FileNotFoundError("Run prepare_dataset.py before evaluate.py")

    df = load_labeled_csv(test_path)
    messages = df["message"].tolist()
    labels = df["label"].tolist()

    results = []
    for mid in ("baseline", "cnn", "bilstm", "tinybert"):
        row = evaluate_model(mid, messages, labels)
        if row:
            results.append(row)
            print(f"{mid}: acc={row['accuracy']:.3f} f1={row['f1_score']:.3f}")

    if not results:
        print("No models available to evaluate.")
        return

    best = max(results, key=lambda r: r.get("f1_score") or 0)
    payload = {
        "available": True,
        "dataset_note": "Metrics computed on held-out test split. Synthetic dev data — not real-world performance.",
        "test_split": str(test_path),
        "results": results,
        "best_by_f1": best["model_id"],
    }
    settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
    out = settings.evaluation_file
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
