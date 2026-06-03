"""Crack all ciphertext files in a directory."""

from __future__ import annotations

import argparse
from pathlib import Path

from subcipher.bigrams import load_matrix
from subcipher.cracker import prolom_substitute
from subcipher.io_utils import export_decryption_result, parse_ciphertext_filename, read_text_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ciphertext_dir", help="Directory with *_ciphertext.txt files")
    parser.add_argument("reference_matrix", help="Path to reference TM_ref.csv")
    parser.add_argument("output_dir", help="Output directory for plaintext/key files")
    parser.add_argument("--iterations", type=int, default=20_000)
    args = parser.parse_args()

    TM_ref = load_matrix(args.reference_matrix)
    ciphertext_paths = sorted(Path(args.ciphertext_dir).glob("*_ciphertext.txt"))

    if not ciphertext_paths:
        raise FileNotFoundError("No *_ciphertext.txt files found.")

    for ciphertext_path in ciphertext_paths:
        length, sample_id = parse_ciphertext_filename(ciphertext_path)
        ciphertext = read_text_file(ciphertext_path)
        best_key, plaintext, score = prolom_substitute(ciphertext, TM_ref, args.iterations)
        export_decryption_result(args.output_dir, length, sample_id, plaintext, best_key)
        print(f"{ciphertext_path.name}: score={score}")


if __name__ == "__main__":
    main()
