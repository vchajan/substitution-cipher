"""Build a relative bigram reference matrix from a raw Czech text file."""

from __future__ import annotations

import argparse
from pathlib import Path

from subcipher.bigrams import get_bigrams, save_matrix, to_relative_matrix, transition_matrix
from subcipher.preprocess import normalize_text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to raw reference text file.")
    parser.add_argument("output", help="Path where the reference matrix CSV will be saved.")
    args = parser.parse_args()

    raw_text = Path(args.input).read_text(encoding="utf-8")
    normalized = normalize_text(raw_text)
    bigrams = get_bigrams(normalized)
    matrix = transition_matrix(bigrams)
    relative = to_relative_matrix(matrix)
    save_matrix(relative, args.output)

    print(f"Normalized characters: {len(normalized)}")
    print(f"Bigrams: {len(bigrams)}")
    print(f"Saved reference matrix to: {args.output}")


if __name__ == "__main__":
    main()
