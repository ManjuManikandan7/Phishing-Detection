"""Dataset loading, cleaning, and train/val/test splits."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from utils.text_utils import normalize_text

LABEL_MAP = {0: "Legitimate", 1: "Phishing"}
REVERSE_LABEL_MAP = {"legitimate": 0, "safe": 0, "ham": 0, "phishing": 1, "spam": 1, "smishing": 1}


def load_labeled_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"message", "label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")
    df = df.copy()
    df["message"] = df["message"].astype(str).map(normalize_text)
    df = df[df["message"].str.len() > 0]
    df["label"] = df["label"].apply(_coerce_label)
    df = df.dropna(subset=["label"])
    df["label"] = df["label"].astype(int)
    df = df.drop_duplicates(subset=["message"], keep="first")
    return df.reset_index(drop=True)


def _coerce_label(value) -> int | None:
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        iv = int(value)
        return iv if iv in (0, 1) else None
    s = str(value).strip().lower()
    return REVERSE_LABEL_MAP.get(s)


def stratified_splits(
    df: pd.DataFrame,
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split without duplicate messages crossing splits (dedupe already applied)."""
    train_df, test_df = train_test_split(
        df, test_size=test_size, random_state=random_state, stratify=df["label"]
    )
    relative_val = val_size / (1.0 - test_size)
    train_df, val_df = train_test_split(
        train_df, test_size=relative_val, random_state=random_state, stratify=train_df["label"]
    )
    return train_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)


def save_splits(data_dir: Path, train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(data_dir / "train.csv", index=False)
    val_df.to_csv(data_dir / "val.csv", index=False)
    test_df.to_csv(data_dir / "test.csv", index=False)
    meta = {
        "label_map": LABEL_MAP,
        "columns": ["message", "label", "source"],
        "note": "0=Legitimate, 1=Phishing. Splits are stratified after deduplication.",
    }
    (data_dir / "dataset_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
