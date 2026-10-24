"""Shared text preprocessing for training and inference."""

import re
import unicodedata


def normalize_text(text: str) -> str:
    """Lowercase, normalize unicode, collapse whitespace."""
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def truncate_text(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len]
