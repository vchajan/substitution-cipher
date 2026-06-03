"""Bigram and transition-matrix utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .alphabet import ALPHABET


def get_bigrams(text: str) -> list[str]:
    """Return all consecutive character pairs from text."""
    return [text[i : i + 2] for i in range(len(text) - 1)]


def transition_matrix(bigrams: list[str]) -> pd.DataFrame:
    """Create an absolute bigram transition matrix with zero-value smoothing.

    First, observed bigrams are counted. Then every still-zero cell is replaced
    by 1 to avoid log(0) in later likelihood calculations.
    """
    matrix = pd.DataFrame(0, index=list(ALPHABET), columns=list(ALPHABET), dtype=float)

    for bigram in bigrams:
        if len(bigram) != 2:
            continue
        first, second = bigram[0], bigram[1]
        if first in ALPHABET and second in ALPHABET:
            matrix.loc[first, second] += 1

    matrix = matrix.mask(matrix == 0, 1)
    return matrix


def to_relative_matrix(matrix: pd.DataFrame) -> pd.DataFrame:
    """Convert an absolute transition matrix to a relative matrix."""
    total = float(matrix.to_numpy().sum())
    if total <= 0:
        raise ValueError("Matrix sum must be positive.")
    return matrix / total


def save_matrix(matrix: pd.DataFrame, path: str | Path) -> None:
    """Save a transition matrix to CSV."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    matrix.to_csv(path)


def load_matrix(path: str | Path) -> pd.DataFrame:
    """Load a transition matrix from CSV."""
    return pd.read_csv(path, index_col=0)
