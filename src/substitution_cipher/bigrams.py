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


def transition_matrix(
    bigrams: list[str],
    alphabet: str = ALPHABET,
    smooth_zeros: bool = True,
    normalize: bool = False,
) -> np.ndarray:
    """Build a bigram transition matrix.

    The matrix first stores absolute bigram counts. Bigrams containing
    characters outside ``alphabet`` are ignored. If ``smooth_zeros`` is true,
    all zero cells are replaced by 1. If ``normalize`` is true, the whole
    matrix is divided by its total sum so that the result sums to 1.

    Args:
        bigrams: List of two-character strings.
        alphabet: Alphabet defining matrix rows and columns.
        smooth_zeros: Replace zero cells with 1 after absolute counting.
        normalize: Convert the matrix to relative frequencies.

    Returns:
        A NumPy array with shape ``(len(alphabet), len(alphabet))``.

    Raises:
        ValueError: If normalization is requested for an empty zero matrix.
    """
    alphabet_index = {char: index for index, char in enumerate(alphabet)}
    matrix = np.zeros((len(alphabet), len(alphabet)), dtype=float)

    for bigram in bigrams:
        if len(bigram) != 2:
            continue

        first, second = bigram
        if first not in alphabet_index or second not in alphabet_index:
            continue

        matrix[alphabet_index[first], alphabet_index[second]] += 1.0

    if smooth_zeros:
        matrix[matrix == 0.0] = 1.0

    if normalize:
        total = float(matrix.sum())
        if total <= 0.0:
            raise ValueError("Cannot normalize a matrix with zero total count.")
        matrix = matrix / total

    return matrix


def build_reference_matrix_from_text(text: str, alphabet: str = ALPHABET) -> np.ndarray:
    """Build a smoothed relative reference matrix from plaintext ``text``.

    Args:
        text: Clean reference text.
        alphabet: Alphabet used for bigram counting.

    Returns:
        Relative bigram matrix with zero smoothing and total sum equal to 1.

    Raises:
        ValueError: If the matrix cannot be normalized.
    """
    return transition_matrix(
        get_bigrams(text),
        alphabet=alphabet,
        smooth_zeros=True,
        normalize=True,
    )


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
