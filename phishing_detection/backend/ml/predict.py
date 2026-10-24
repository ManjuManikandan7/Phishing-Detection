"""Load trained models and run inference with training-consistent preprocessing."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from config import settings
from utils.text_utils import normalize_text

MAX_LEN = 128
TINYBERT_MAX_LEN = 128


@dataclass
class PredictionResult:
    label: int
    phishing_probability: float
    model_id: str
    inference_ms: float


def _load_keras_meta(meta_path: Path) -> dict:
    return json.loads(meta_path.read_text(encoding="utf-8"))


def predict_cnn(message: str) -> PredictionResult:
    import tensorflow as tf
    from tensorflow.keras.preprocessing.sequence import pad_sequences

    art = settings.artifacts_dir
    model_path = art / "cnn_model.keras"
    meta_path = art / "cnn_meta.json"
    if not model_path.exists() or not meta_path.exists():
        raise FileNotFoundError("CNN model artifacts not found. Run ml/train_cnn.py first.")

    meta = _load_keras_meta(meta_path)
    word_index = {k: int(v) for k, v in meta["word_index"].items()}
    max_len = int(meta.get("max_len", MAX_LEN))

    tokens = normalize_text(message).split()
    seq = [[word_index.get(w, 0) for w in tokens]]
    padded = pad_sequences(seq, maxlen=max_len, padding="post", truncating="post")

    t0 = time.perf_counter()
    model = tf.keras.models.load_model(model_path)
    proba = float(model.predict(padded, verbose=0)[0][0])
    ms = (time.perf_counter() - t0) * 1000
    label = 1 if proba >= 0.5 else 0
    return PredictionResult(label=label, phishing_probability=proba, model_id="cnn", inference_ms=ms)


def predict_bilstm(message: str) -> PredictionResult:
    import tensorflow as tf
    from tensorflow.keras.preprocessing.sequence import pad_sequences

    art = settings.artifacts_dir
    model_path = art / "bilstm_model.keras"
    meta_path = art / "bilstm_meta.json"
    if not model_path.exists() or not meta_path.exists():
        raise FileNotFoundError("Bi-LSTM model artifacts not found. Run ml/train_bilstm.py first.")

    meta = _load_keras_meta(meta_path)
    word_index = {k: int(v) for k, v in meta["word_index"].items()}
    max_len = int(meta.get("max_len", MAX_LEN))

    tokens = normalize_text(message).split()
    seq = [[word_index.get(w, 0) for w in tokens]]
    padded = pad_sequences(seq, maxlen=max_len, padding="post", truncating="post")

    t0 = time.perf_counter()
    model = tf.keras.models.load_model(model_path)
    proba = float(model.predict(padded, verbose=0)[0][0])
    ms = (time.perf_counter() - t0) * 1000
    label = 1 if proba >= 0.5 else 0
    return PredictionResult(label=label, phishing_probability=proba, model_id="bilstm", inference_ms=ms)


def predict_tinybert(message: str) -> PredictionResult:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    model_dir = settings.artifacts_dir / "tinybert"
    if not (model_dir / "config.json").exists():
        raise FileNotFoundError("TinyBERT artifacts not found. Run ml/train_tinybert.py first.")

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.eval()

    encoded = tokenizer(
        normalize_text(message),
        truncation=True,
        padding="max_length",
        max_length=TINYBERT_MAX_LEN,
        return_tensors="pt",
    )
    t0 = time.perf_counter()
    with torch.no_grad():
        outputs = model(**encoded)
        logits = outputs.logits[0].numpy()
    ms = (time.perf_counter() - t0) * 1000
    exp = np.exp(logits - np.max(logits))
    probs = exp / exp.sum()
    phishing_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
    label = 1 if phishing_prob >= 0.5 else 0
    return PredictionResult(label=label, phishing_probability=phishing_prob, model_id="tinybert", inference_ms=ms)


def predict_with_model(model_id: str, message: str) -> PredictionResult:
    if model_id == "cnn":
        return predict_cnn(message)
    if model_id == "bilstm":
        return predict_bilstm(message)
    if model_id == "tinybert":
        return predict_tinybert(message)
    raise ValueError(f"Unknown trained model: {model_id}")
