"""Bigramy a přechodové matice."""

from __future__ import annotations

import numpy as np

from .constants import ALPHABET


def get_bigrams(text: str) -> list[str]:
    """Vrátí všechny dvojice sousedních znaků v textu."""
    return [text[index : index + 2] for index in range(max(0, len(text) - 1))]


def absolute_bigram_matrix(bigrams: list[str]) -> np.ndarray:
    """Spočítá absolutní četnosti bigramů bez vyhlazení nul."""
    alphabet_index = {char: index for index, char in enumerate(ALPHABET)}
    matrix = np.zeros((len(ALPHABET), len(ALPHABET)), dtype=float)

    for bigram in bigrams:
        if len(bigram) != 2:
            continue

        first, second = bigram
        if first not in alphabet_index or second not in alphabet_index:
            continue

        matrix[alphabet_index[first], alphabet_index[second]] += 1.0

    return matrix


def transition_matrix(bigrams: list[str]) -> np.ndarray:
    """Vrátí absolutní bigramovou matici s nulami nahrazenými jedničkou."""
    matrix = absolute_bigram_matrix(bigrams)
    # Nuly nahrazujeme jedničkou, aby později nevznikl logaritmus z nuly.
    matrix[matrix == 0.0] = 1.0
    return matrix


def build_reference_matrix_from_text(text: str) -> np.ndarray:
    """Vytvoří relativní referenční matici z čistého textu."""
    matrix = transition_matrix(get_bigrams(text))
    total = float(matrix.sum())
    if total <= 0.0:
        raise ValueError("Nelze normalizovat matici s nulovým součtem.")
    return matrix / total
