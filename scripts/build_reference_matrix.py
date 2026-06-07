"""Vytvoří referenční bigramovou matici z Války s mloky."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from substitution_cipher.bigrams import get_bigrams, transition_matrix  # noqa: E402
from substitution_cipher.io_utils import save_matrix  # noqa: E402
from substitution_cipher.paths import CLEAN_REFERENCE_TEXT_PATH, REFERENCE_MATRIX_PATH  # noqa: E402
from substitution_cipher.preprocessing import validate_clean_text  # noqa: E402


def build_reference_matrix(
    clean_text_path: str | Path = CLEAN_REFERENCE_TEXT_PATH,
    output_path: str | Path = REFERENCE_MATRIX_PATH,
) -> tuple[np.ndarray, int]:
    """Načte čistý text, vytvoří relativní matici a uloží ji."""
    source_path = Path(clean_text_path)
    text = source_path.read_text(encoding="utf-8").strip()
    validate_clean_text(text)

    bigrams = get_bigrams(text)
    absolute = transition_matrix(bigrams)
    total = float(absolute.sum())
    if total <= 0.0:
        raise ValueError("Nelze normalizovat matici s nulovým součtem.")

    matrix = absolute / total
    save_matrix(matrix, output_path)
    return matrix, len(bigrams)


def main() -> None:
    """Vytvoří a uloží výchozí referenční matici."""
    text = CLEAN_REFERENCE_TEXT_PATH.read_text(encoding="utf-8").strip()
    matrix, bigram_count = build_reference_matrix()

    print("===== REFERENČNÍ MATICE =====")
    print(f"Zdrojový text: {CLEAN_REFERENCE_TEXT_PATH}")
    print(f"Délka textu: {len(text)}")
    print(f"Počet bigramů: {bigram_count}")
    print(f"Shape matice: {matrix.shape}")
    print(f"Součet matice: {matrix.sum():.12f}")
    print(f"Počet nul: {int(np.sum(matrix == 0.0))}")
    print(f"Obsahuje NaN: {bool(np.isnan(matrix).any())}")
    print(f"Obsahuje nekonečné hodnoty: {bool(np.isinf(matrix).any())}")
    print(f"Výstupní soubor: {REFERENCE_MATRIX_PATH}")


if __name__ == "__main__":
    main()
