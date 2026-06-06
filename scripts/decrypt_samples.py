"""Dešifrování ciphertextů ze zadání pomocí projektové knihovny.

Skript očekává názvy ve tvaru ``text_1000_sample_20_ciphertext.txt`` a exportuje
plaintext/key soubory ve formátu požadovaném zadáním.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from substitution_cipher.api import (  # noqa: E402
    SubstitutionCipher,
    parse_ciphertext_filename as _api_parse_ciphertext_filename,
)


def parse_ciphertext_filename(path: str | Path) -> tuple[int, int]:
    """Získá délku textu a ID vzorku z názvu ciphertext souboru."""
    return _api_parse_ciphertext_filename(path)


def find_ciphertext_files(input_dir: str | Path) -> list[Path]:
    """Vrátí číselně seřazené ciphertext soubory ze složky ``input_dir``."""
    directory = Path(input_dir)
    if not directory.exists():
        return []
    return sorted(
        directory.glob("text_*_sample_*_ciphertext.txt"),
        key=parse_ciphertext_filename,
    )


def decrypt_file(
    ciphertext_path: str | Path,
    cipher: SubstitutionCipher,
    output_directory: str | Path,
    iterations: int,
    restarts: int = 1,
    seed: int | None = None,
    polish: bool = True,
):
    """Dešifruje jeden ciphertext soubor a exportuje plaintext/key soubory."""
    return cipher.crack_file(
        input_path=ciphertext_path,
        output_directory=output_directory,
        iterations=iterations,
        restarts=restarts,
        seed=seed,
        polish=polish,
    )


def main() -> None:
    """Spustí dávkové dešifrování všech ciphertextů ve vstupní složce."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix",
        default=PROJECT_ROOT / "data" / "processed" / "TM_ref_krakatit.npy",
        type=Path,
        help="Cesta k referenční bigramové matici ve formátu .npy.",
    )
    parser.add_argument(
        "--input-directory",
        "--input-dir",
        dest="input_directory",
        default=PROJECT_ROOT / "data" / "ciphertexts",
        type=Path,
        help="Složka se soubory text_{length}_sample_{id}_ciphertext.txt.",
    )
    parser.add_argument(
        "--output-directory",
        "--output-dir",
        dest="output_directory",
        default=PROJECT_ROOT / "outputs",
        type=Path,
        help="Složka pro export plaintext/key souborů.",
    )
    parser.add_argument(
        "--iterations",
        default=10_000,
        type=int,
        help="Počet iterací Metropolis-Hastingsova algoritmu na jeden ciphertext.",
    )
    parser.add_argument(
        "--restarts",
        default=2,
        type=int,
        help="Počet nezávislých restartů na jeden ciphertext.",
    )
    parser.add_argument("--seed", default=None, type=int, help="Volitelný náhodný seed.")
    parser.add_argument(
        "--no-polish",
        action="store_true",
        help="Vypne lokální dolaďování klíče po každém M-H běhu.",
    )
    args = parser.parse_args()

    input_directory = Path(args.input_directory)
    if not input_directory.exists() or not list(input_directory.glob("*.txt")):
        print(f"Nebyly nalezeny žádné ciphertext soubory v: {args.input_directory}")
        return

    cipher = SubstitutionCipher.from_matrix_file(args.matrix)
    results = cipher.crack_directory(
        input_directory=args.input_directory,
        output_directory=args.output_directory,
        iterations=args.iterations,
        restarts=args.restarts,
        seed=args.seed,
        polish=not args.no_polish,
    )
    print(f"Dešifrované soubory: {len(results)}")
    print(f"Výstupní složka: {args.output_directory}")


if __name__ == "__main__":
    main()
