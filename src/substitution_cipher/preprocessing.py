"""Čištění a validace textu pro abecedu zadání."""

from __future__ import annotations

import re
import unicodedata

from .constants import ALPHABET


def remove_diacritics(text: str) -> str:
    """Odstraní z textu diakritiku."""
    normalized = unicodedata.normalize("NFD", text)
    return "".join(
        char for char in normalized
        if unicodedata.category(char) != "Mn"
    )


def clean_text(text: str, alphabet: str = ALPHABET) -> str:
    """Převede text na tvar obsahující pouze znaky ``A-Z`` a ``_``."""
    text = remove_diacritics(text).upper()
    text = re.sub(r"[^A-Z\s]", " ", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    cleaned = text.strip("_")
    return "".join(char for char in cleaned if char in set(alphabet))


def validate_clean_text(text: str, alphabet: str = ALPHABET) -> None:
    """Ověří, že text obsahuje pouze povolené znaky."""
    invalid = sorted(set(text) - set(alphabet))
    if invalid:
        raise ValueError(f"Text obsahuje nepovolené znaky: {invalid}")
