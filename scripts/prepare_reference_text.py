"""Připraví čistý referenční text z knihy Válka s mloky."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from substitution_cipher.paths import (  # noqa: E402
    CLEAN_REFERENCE_TEXT_PATH,
    RAW_REFERENCE_TEXT_PATH,
)
from substitution_cipher.preprocessing import clean_text, validate_clean_text  # noqa: E402


def prepare_reference_text(
    input_path: str | Path = RAW_REFERENCE_TEXT_PATH,
    output_path: str | Path = CLEAN_REFERENCE_TEXT_PATH,
) -> tuple[str, Path]:
    """Vyčistí surový text a uloží výsledek pro stavbu matice."""
    raw_path = Path(input_path)
    clean_path = Path(output_path)

    raw_text = raw_path.read_text(encoding="utf-8")
    # Čištění držíme odděleně od downloadu, aby šel stejný raw text opakovaně zpracovat.
    cleaned = clean_text(raw_text)
    validate_clean_text(cleaned)

    clean_path.parent.mkdir(parents=True, exist_ok=True)
    clean_path.write_text(cleaned, encoding="utf-8")
    return cleaned, clean_path


def main() -> None:
    """Spustí přípravu referenčního textu z výchozích cest."""
    raw_text = RAW_REFERENCE_TEXT_PATH.read_text(encoding="utf-8")
    cleaned, clean_path = prepare_reference_text()

    print("===== PŘÍPRAVA REFERENČNÍHO TEXTU =====")
    print(f"Vstupní soubor: {RAW_REFERENCE_TEXT_PATH}")
    print(f"Původní délka: {len(raw_text)}")
    print(f"Výsledná délka: {len(cleaned)}")
    print(f"Odstraněno nebo sloučeno znaků: {max(0, len(raw_text) - len(cleaned))}")
    print("Výsledek obsahuje pouze znaky A-Z a _.")
    print(f"Výstupní soubor: {clean_path}")


if __name__ == "__main__":
    main()
