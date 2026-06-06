"""Bigram extraction and transition-matrix utilities."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .config import ALPHABET


def get_bigrams(text: str) -> list[str]:
    """Return all consecutive two-character windows from ``text``.

    Args:
        text: Input text.

    Returns:
        List of adjacent character pairs. Text shorter than two characters
        returns an empty list.
    """
    return [text[index : index + 2] for index in range(max(0, len(text) - 1))]


def absolute_bigram_matrix(bigrams: list[str]) -> np.ndarray:
    """Build an unsmoothed absolute bigram count matrix.

    Bigrams containing characters outside ``ALPHABET`` are ignored. This helper
    is used for observed candidate plaintexts in the plausibility score.
    """
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
    """Build the smoothed absolute bigram transition matrix.

    The assignment requires this exact order: first count absolute bigrams,
    then replace all zero cells by ``1``. Normalization is deliberately not
    done here; scripts building a reference matrix divide the result by its
    total sum afterwards.
    """
    matrix = absolute_bigram_matrix(bigrams)
    matrix[matrix == 0.0] = 1.0
    return matrix


def build_reference_matrix_from_text(text: str) -> np.ndarray:
    """Build a smoothed relative reference matrix from plaintext ``text``.

    Args:
        text: Clean reference text.

    Returns:
        Relative bigram matrix with zero smoothing and total sum equal to 1.

    Raises:
        ValueError: If the matrix cannot be normalized.
    """
    matrix = transition_matrix(get_bigrams(text))
    total = float(matrix.sum())
    if total <= 0.0:
        raise ValueError("Cannot normalize a matrix with zero total count.")
    return matrix / total


def save_matrix(matrix: np.ndarray, path: str | Path) -> None:
    """Save ``matrix`` to ``path`` in NumPy ``.npy`` format.

    Args:
        matrix: Matrix to save.
        path: Output path, usually ending in ``.npy``.

    Returns:
        None.
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_path, matrix)


def load_matrix(path: str | Path) -> np.ndarray:
    """Load a NumPy ``.npy`` transition matrix from ``path``.

    Args:
        path: Path to a saved ``.npy`` matrix.

    Returns:
        Loaded NumPy array.
    """
    return np.load(Path(path))
