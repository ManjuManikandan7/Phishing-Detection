"""Fine-tune TinyBERT for binary phishing classification."""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import numpy as np
import torch
from sklearn.metrics import accuracy_score
from torch.utils.data import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

from config import settings
from ml.train_common import load_split_csv, set_seed

PRETRAINED = "huawei-noah/TinyBERT_General_4L_312D"
MAX_LEN = 128


class TextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.encodings = tokenizer(
            list(texts),
            truncation=True,
            padding="max_length",
            max_length=MAX_LEN,
            return_tensors="pt",
        )
        self.labels = torch.tensor(list(labels), dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item["labels"] = self.labels[idx]
        return item


def compute_metrics(eval_pred):
    from sklearn.metrics import f1_score

    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "f1": f1_score(labels, preds, zero_division=0),
    }


def main() -> None:
    set_seed()
    train_df = load_split_csv("train")
    val_df = load_split_csv("val")

    try:
        tokenizer = AutoTokenizer.from_pretrained(PRETRAINED)
        model = AutoModelForSequenceClassification.from_pretrained(PRETRAINED, num_labels=2)
    except Exception as exc:
        raise RuntimeError(
            f"Could not download/load {PRETRAINED}. Check internet/Hugging Face access. Details: {exc}"
        ) from exc

    train_ds = TextDataset(train_df["message"], train_df["label"], tokenizer)
    val_ds = TextDataset(val_df["message"], val_df["label"], tokenizer)

    out_dir = settings.artifacts_dir / "tinybert"
    out_dir.mkdir(parents=True, exist_ok=True)

    args = TrainingArguments(
        output_dir=str(out_dir / "checkpoints"),
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_steps=20,
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
    )
    trainer.train()
    trainer.save_model(str(out_dir))
    tokenizer.save_pretrained(str(out_dir))
    print(f"Saved TinyBERT to {out_dir}")


if __name__ == "__main__":
    main()
