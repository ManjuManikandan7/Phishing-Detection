"""
Prepare labeled data for training.

Primary dev dataset: synthetic samples in messages_labeled.csv (smoke testing only).
Document external datasets in ml/data/DATASETS.md when you add them.
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from ml.preprocessing import load_labeled_csv, save_splits, stratified_splits
DATA_DIR = BACKEND_DIR / "ml" / "data"
RAW_CSV = DATA_DIR / "messages_labeled.csv"


def main() -> None:
    if not RAW_CSV.exists():
        raise FileNotFoundError(f"Missing dataset: {RAW_CSV}")
    df = load_labeled_csv(RAW_CSV)
    train_df, val_df, test_df = stratified_splits(df)
    save_splits(DATA_DIR, train_df, val_df, test_df)
    print(f"Rows — train: {len(train_df)}, val: {len(val_df)}, test: {len(test_df)}")
    print(f"Label balance (train):\\n{train_df['label'].value_counts().to_string()}")


if __name__ == "__main__":
    main()
