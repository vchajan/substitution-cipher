"""Text normalisation for the project alphabet."""

from __future__ import annotations

import re
import unicodedata

from .alphabet import ALPHABET

_SPACE_RE = re.compile(r"\s+")


def remove_diacritics(text: str) -> str:
    """Remove accents and other combining marks from text."""
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def normalize_text(text: str) -> str:
    """Normalize text to the alphabet `ABCDEFGHIJKLMNOPQRSTUVWXYZ_`.

    Steps:
    1. remove diacritics,
    2. convert to uppercase,
    3. replace whitespace with `_`,
    4. remove unsupported characters,
    5. collapse repeated underscores.
    """
    text = remove_diacritics(text).upper()
    text = _SPACE_RE.sub("_", text)
    allowed = set(ALPHABET)
    cleaned = "".join(char for char in text if char in allowed)
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.strip("_")
