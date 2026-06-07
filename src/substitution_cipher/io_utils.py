"""Načítání, ukládání a názvy souborů projektu."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np


CIPHERTEXT_PATTERN = re.compile(
    r"^text_(?P<length>\d+)_sample_(?P<sample_id>\d+)_ciphertext\.txt$"
)


def read_text(path: str | Path) -> str:
    """Načte textový soubor jako UTF-8."""
    return Path(path).read_text(encoding="utf-8")


def write_text(path: str | Path, text: str) -> Path:
    """Uloží textový soubor jako UTF-8."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    return output_path


def save_matrix(matrix: np.ndarray, path: str | Path) -> Path:
    """Uloží matici ve formátu NumPy ``.npy``."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_path, matrix)
    return output_path


def load_matrix(path: str | Path) -> np.ndarray:
    """Načte matici uloženou ve formátu NumPy ``.npy``."""
    return np.load(Path(path))


def parse_ciphertext_filename(path: str | Path) -> tuple[int, int]:
    """Vrátí délku textu a ID vzorku z názvu ciphertext souboru."""
    match = CIPHERTEXT_PATTERN.match(Path(path).name)
    if not match:
        raise ValueError(
            "Název ciphertextu musí odpovídat tvaru "
            "text_{length}_sample_{id}_ciphertext.txt"
        )
    return int(match.group("length")), int(match.group("sample_id"))


def export_result(
    plaintext: str,
    key: str,
    text_length: int,
    sample_id: int,
    output_dir: str | Path,
) -> tuple[Path, Path]:
    """Uloží plaintext a klíč ve formátu požadovaném zadáním."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    plaintext_path = output_path / f"text_{text_length}_sample_{sample_id}_plaintext.txt"
    key_path = output_path / f"text_{text_length}_sample_{sample_id}_key.txt"

    plaintext_path.write_text(plaintext, encoding="utf-8")
    key_path.write_text(key, encoding="utf-8")
    return plaintext_path, key_path
