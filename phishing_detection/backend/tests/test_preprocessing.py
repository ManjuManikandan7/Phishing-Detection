from ml.preprocessing import load_labeled_csv, stratified_splits
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "ml" / "data" / "messages_labeled.csv"


def test_load_and_split():
    df = load_labeled_csv(DATA)
    assert set(df["label"].unique()).issubset({0, 1})
    train, val, test = stratified_splits(df, random_state=42)
    assert len(train) + len(val) + len(test) == len(df)
    # No message leakage across splits
    assert len(set(train["message"]) & set(test["message"])) == 0
