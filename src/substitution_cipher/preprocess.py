"""Text cleaning helpers for the project alphabet."""

from __future__ import annotations

import re
import unicodedata

from .config import ALPHABET


def remove_diacritics(text: str) -> str:
    """Remove accents and combining marks from text.

    Args:
        text: Input Unicode text.

    Returns:
        Text with Czech accents and other combining marks stripped.
    """
    normalized = unicodedata.normalize("NFD", text)
    return "".join(
        char for char in normalized
        if unicodedata.category(char) != "Mn"
    )


def clean_text(text: str, alphabet: str = ALPHABET) -> str:
    """Clean text so it contains only ``A-Z`` and ``_``.

    Diacritics are removed, text is converted to uppercase, every run of
    whitespace is represented by one underscore, and unsupported characters
    are treated as separators.

    Args:
        text: Raw input text.
        alphabet: Allowed output alphabet. The assignment alphabet is used by
            default and should not be changed for project data.

    Returns:
        Cleaned text containing only characters from ``alphabet``.
    """
    text = remove_diacritics(text).upper()
    text = re.sub(r"[^A-Z\s]", " ", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    cleaned = text.strip("_")

    allowed = set(alphabet)
    return "".join(char for char in cleaned if char in allowed)
