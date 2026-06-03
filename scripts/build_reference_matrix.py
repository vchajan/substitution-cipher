"""Build the reference bigram matrix from cleaned project text."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from substitution_cipher.bigrams import (  # noqa: E402
    build_reference_matrix_from_text,
    get_bigrams,
    save_matrix,
)


CLEAN_TEXT_PATH = PROJECT_ROOT / "data" / "processed" / "clean_text.txt"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "TM_ref.npy"


def main() -> None:
    """Create and save the smoothed relative bigram reference matrix."""
    text = CLEAN_TEXT_PATH.read_text(encoding="utf-8").strip()
    bigrams = get_bigrams(text)
    matrix = build_reference_matrix_from_text(text)

    save_matrix(matrix, OUTPUT_PATH)

    print(f"Text length: {len(text)}")
    print(f"Bigram count: {len(bigrams)}")
    print(f"Matrix shape: {matrix.shape}")
    print(f"Matrix sum: {matrix.sum():.12f}")
    print(f"Saved matrix to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
