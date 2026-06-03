"""Decrypt assignment ciphertext samples with the project library.

The script is intentionally small and ready for the real files supplied by the
teacher. It expects ciphertext names like ``text_1000_sample_20_ciphertext.txt``
and exports plaintext/key files using the required assignment format.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from substitution_cipher.bigrams import load_matrix  # noqa: E402
from substitution_cipher.cryptanalysis import prolom_substitute  # noqa: E402
from substitution_cipher.export_utils import export_result  # noqa: E402


_CIPHERTEXT_PATTERN = re.compile(
    r"text_(?P<length>\d+)_sample_(?P<sample_id>\d+)_ciphertext\.txt$"
)


def parse_ciphertext_filename(path: str | Path) -> tuple[int, int]:
    """Parse text length and sample id from an assignment ciphertext filename."""
    match = _CIPHERTEXT_PATTERN.match(Path(path).name)
    if not match:
        raise ValueError(
            "Ciphertext filename must match "
            "text_{length}_sample_{id}_ciphertext.txt"
        )
    return int(match.group("length")), int(match.group("sample_id"))


def find_ciphertext_files(input_dir: str | Path) -> list[Path]:
    """Return sorted ciphertext files from ``input_dir``.

    Missing or empty directories are represented by an empty list so the caller
    can print a friendly message instead of failing.
    """
    directory = Path(input_dir)
    if not directory.exists():
        return []
    return sorted(directory.glob("text_*_sample_*_ciphertext.txt"))


def decrypt_file(
    ciphertext_path: str | Path,
    TM_ref,
    output_dir: str | Path,
    iterations: int,
    seed: int | None = None,
) -> tuple[Path, Path]:
    """Decrypt one ciphertext file and export plaintext/key files."""
    path = Path(ciphertext_path)
    text_length, sample_id = parse_ciphertext_filename(path)
    ciphertext = path.read_text(encoding="utf-8").strip()

    key, plaintext, _score = prolom_substitute(
        ciphertext,
        TM_ref,
        iter=iterations,
        seed=seed,
    )
    return export_result(plaintext, key, text_length, sample_id, output_dir)


def main() -> None:
    """Run batch decryption for all ciphertext files in an input directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix",
        default=PROJECT_ROOT / "data" / "processed" / "TM_ref.npy",
        type=Path,
        help="Path to the reference .npy bigram matrix.",
    )
    parser.add_argument(
        "--input-dir",
        default=PROJECT_ROOT / "data" / "ciphertexts",
        type=Path,
        help="Directory with text_{length}_sample_{id}_ciphertext.txt files.",
    )
    parser.add_argument(
        "--output-dir",
        default=PROJECT_ROOT / "outputs",
        type=Path,
        help="Directory for plaintext/key exports.",
    )
    parser.add_argument(
        "--iterations",
        default=20_000,
        type=int,
        help="Metropolis-Hastings iterations per ciphertext.",
    )
    parser.add_argument("--seed", default=None, type=int, help="Optional random seed.")
    args = parser.parse_args()

    files = find_ciphertext_files(args.input_dir)
    if not files:
        print(f"No ciphertext files found in: {args.input_dir}")
        return

    TM_ref = load_matrix(args.matrix)

    for ciphertext_path in files:
        plaintext_path, key_path = decrypt_file(
            ciphertext_path,
            TM_ref,
            args.output_dir,
            args.iterations,
            seed=args.seed,
        )
        print(f"Decrypted {ciphertext_path.name}")
        print(f"  plaintext: {plaintext_path}")
        print(f"  key: {key_path}")


if __name__ == "__main__":
    main()
