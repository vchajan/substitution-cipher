"""Crack one ciphertext file and export plaintext/key result."""

from __future__ import annotations

import argparse

from subcipher.bigrams import load_matrix
from subcipher.cracker import prolom_substitute
from subcipher.io_utils import export_decryption_result, parse_ciphertext_filename, read_text_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ciphertext", help="Path to text_{length}_sample_{id}_ciphertext.txt")
    parser.add_argument("reference_matrix", help="Path to reference TM_ref.csv")
    parser.add_argument("output_dir", help="Output directory for plaintext/key files")
    parser.add_argument("--iterations", type=int, default=20_000)
    parser.add_argument("--start-key", default=None)
    args = parser.parse_args()

    length, sample_id = parse_ciphertext_filename(args.ciphertext)
    ciphertext = read_text_file(args.ciphertext)
    TM_ref = load_matrix(args.reference_matrix)

    best_key, plaintext, score = prolom_substitute(
        ciphertext,
        TM_ref,
        args.iterations,
        args.start_key,
    )

    plaintext_path, key_path = export_decryption_result(
        args.output_dir,
        length,
        sample_id,
        plaintext,
        best_key,
    )

    print(f"Score: {score}")
    print(f"Plaintext saved to: {plaintext_path}")
    print(f"Key saved to: {key_path}")


if __name__ == "__main__":
    main()
