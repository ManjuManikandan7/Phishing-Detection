"""Train and save Bi-LSTM text classifier."""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Bidirectional, Dense, Dropout, Embedding, LSTM
from tensorflow.keras.models import Sequential

from config import settings
from ml.train_common import (
    MAX_LEN,
    VOCAB_SIZE,
    build_sequences,
    class_weights,
    load_split_csv,
    save_meta,
    set_seed,
)


def build_bilstm_model() -> tf.keras.Model:
    model = Sequential(
        [
            Embedding(input_dim=VOCAB_SIZE, output_dim=128, input_length=MAX_LEN),
            Bidirectional(LSTM(64, return_sequences=False)),
            Dropout(0.3),
            Dense(64, activation="relu"),
            Dropout(0.2),
            Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def main() -> None:
    set_seed()
    train_df = load_split_csv("train")
    val_df = load_split_csv("val")
    test_df = load_split_csv("test")

    x_train, x_val, _, word_index = build_sequences(
        train_df["message"].tolist(),
        val_df["message"].tolist(),
        test_df["message"].tolist(),
    )
    y_train = train_df["label"].to_numpy()
    y_val = val_df["label"].to_numpy()

    model = build_bilstm_model()
    cw = class_weights(y_train)
    settings.artifacts_dir.mkdir(parents=True, exist_ok=True)

    model.fit(
        x_train,
        y_train,
        validation_data=(x_val, y_val),
        epochs=8,
        batch_size=32,
        class_weight=cw,
        callbacks=[EarlyStopping(patience=2, restore_best_weights=True, monitor="val_loss")],
        verbose=1,
    )

    out_model = settings.artifacts_dir / "bilstm_model.keras"
    out_meta = settings.artifacts_dir / "bilstm_meta.json"
    model.save(out_model)
    save_meta(out_meta, word_index, MAX_LEN, "bilstm")
    print(f"Saved Bi-LSTM model to {out_model}")


if __name__ == "__main__":
    main()
