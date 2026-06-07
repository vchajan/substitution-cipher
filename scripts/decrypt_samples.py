"""Dávkové dešifrování ciphertextů ze zadání."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from substitution_cipher.batch import (  # noqa: E402
    crack_files,
    find_ciphertext_files as _find_ciphertext_files,
    resolve_worker_count,
)
from substitution_cipher.paths import CIPHERTEXT_DIR, OUTPUT_DIR, REFERENCE_MATRIX_PATH  # noqa: E402


def find_ciphertext_files(input_dir: str | Path) -> list[Path]:
    """Vrátí číselně seřazené ciphertext soubory ze složky."""
    return _find_ciphertext_files(input_dir)


def decrypt_file(
    ciphertext_path: str | Path,
    matrix_path: str | Path,
    output_directory: str | Path,
    iterations: int,
    restarts: int = 1,
    seed: int | None = None,
    polish: bool = True,
):
    """Dešifruje jeden soubor přes dávkové knihovní API."""
    summaries = crack_files(
        files=[Path(ciphertext_path)],
        matrix_path=matrix_path,
        output_directory=output_directory,
        iterations=iterations,
        restarts=restarts,
        seed=seed,
        polish=polish,
        workers=1,
    )
    return summaries[0]


def build_parser() -> argparse.ArgumentParser:
    """Sestaví parser argumentů příkazové řádky."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix",
        default=REFERENCE_MATRIX_PATH,
        type=Path,
        help="Cesta k referenční bigramové matici ve formátu .npy.",
    )
    parser.add_argument(
        "--input-directory",
        "--input-dir",
        dest="input_directory",
        default=CIPHERTEXT_DIR,
        type=Path,
        help="Složka se soubory text_{length}_sample_{id}_ciphertext.txt.",
    )
    parser.add_argument(
        "--output-directory",
        "--output-dir",
        dest="output_directory",
        default=OUTPUT_DIR,
        type=Path,
        help="Složka pro export plaintext/key souborů.",
    )
    parser.add_argument(
        "--iterations",
        default=20_000,
        type=int,
        help="Počet iterací Metropolis-Hastingsova algoritmu na jeden ciphertext.",
    )
    parser.add_argument(
        "--restarts",
        default=1,
        type=int,
        help="Počet nezávislých restartů na jeden ciphertext.",
    )
    parser.add_argument("--seed", default=None, type=int, help="Volitelný náhodný seed.")
    parser.add_argument(
        "--no-polish",
        action="store_true",
        help="Vypne lokální dolaďování klíče po každém M-H běhu.",
    )
    parser.add_argument(
        "--workers",
        default=1,
        type=int,
        help=(
            "Počet procesů pro paralelní zpracování souborů. "
            "1 = sekvenčně, 0 = automaticky, N = nejvýše N procesů."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Spustí dávkové dešifrování všech dostupných ciphertextů."""
    parser = build_parser()
    args = parser.parse_args(argv)

    files = find_ciphertext_files(args.input_directory)
    if not files:
        print(f"Ciphertext soubory zatím nejsou k dispozici v: {args.input_directory}")
        return 0

    try:
        worker_count = resolve_worker_count(args.workers, file_count=len(files))
    except ValueError as exc:
        parser.error(str(exc))

    print("===== DÁVKOVÉ DEŠIFROVÁNÍ =====")
    print("Referenční text: Válka s mloky")
    print(f"Referenční matice: {args.matrix}")
    print(f"Počet iterací na ciphertext: {args.iterations}")
    print(f"Počet restartů: {args.restarts}")
    print(f"Použité procesy: {worker_count}")

    start = time.perf_counter()
    # Skript jen dešifruje soubory; vyhodnocovací report se spouští až po dokončení dávky.
    summaries = crack_files(
        files=files,
        matrix_path=args.matrix,
        output_directory=args.output_directory,
        iterations=args.iterations,
        restarts=args.restarts,
        seed=args.seed,
        polish=not args.no_polish,
        workers=args.workers,
    )
    elapsed = time.perf_counter() - start

    successful = sum(summary.success for summary in summaries)
    failed = len(summaries) - successful

    print(f"Zpracované soubory: {len(summaries)}")
    print(f"Úspěšné: {successful}")
    print(f"Chyby: {failed}")
    print(f"Použité procesy: {worker_count}")
    print(f"Celkový čas: {elapsed:.2f} s")
    print(f"Výstupní složka: {args.output_directory}")

    if failed:
        print("Přehled chyb:")
        for summary in summaries:
            if not summary.success:
                print(f"- {summary.input_path.name}: {summary.error}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
