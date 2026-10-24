"""Shared Keras training utilities for CNN and Bi-LSTM."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

from config import settings
from ml.preprocessing import load_labeled_csv

MAX_LEN = 128
VOCAB_SIZE = 8000


def load_split_csv(name: str) -> pd.DataFrame:
    path = settings.data_dir / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run ml/data/prepare_dataset.py first.")
    return load_labeled_csv(path)


def build_sequences(train_texts, val_texts, test_texts):
    tokenizer = Tokenizer(num_words=VOCAB_SIZE, oov_token="<unk>")
    tokenizer.fit_on_texts(train_texts)
    word_index = {str(k): int(v) for k, v in tokenizer.word_index.items()}

    def to_pad(texts):
        seqs = tokenizer.texts_to_sequences(texts)
        return pad_sequences(seqs, maxlen=MAX_LEN, padding="post", truncating="post")

    return to_pad(train_texts), to_pad(val_texts), to_pad(test_texts), word_index


def class_weights(labels: np.ndarray) -> dict:
    classes = np.unique(labels)
    weights = compute_class_weight(class_weight="balanced", classes=classes, y=labels)
    return {int(c): float(w) for c, w in zip(classes, weights)}


def save_meta(path: Path, word_index: dict, max_len: int, model_type: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"word_index": word_index, "max_len": max_len, "model_type": model_type, "vocab_size": VOCAB_SIZE}
    path.write_text(json.dumps(payload), encoding="utf-8")


def set_seed(seed: int = 42) -> None:
    tf.random.set_seed(seed)
    np.random.seed(seed)
