"""Input/output helpers for ciphertexts and decrypted outputs."""

from __future__ import annotations

import re
from pathlib import Path

_CIPHERTEXT_PATTERN = re.compile(r"text_(?P<length>\d+)_sample_(?P<sample_id>\d+)_ciphertext\.txt$")


def read_text_file(path: str | Path) -> str:
    """Read a UTF-8 text file."""
    return Path(path).read_text(encoding="utf-8").strip()


def parse_ciphertext_filename(filename: str | Path) -> tuple[int, int]:
    """Parse length and sample ID from a ciphertext filename."""
    name = Path(filename).name
    match = _CIPHERTEXT_PATTERN.match(name)
    if not match:
        raise ValueError(
            "Ciphertext filename must match text_{length}_sample_{id}_ciphertext.txt"
        )
    return int(match.group("length")), int(match.group("sample_id"))


def export_decryption_result(
    output_dir: str | Path,
    length: int,
    sample_id: int,
    plaintext: str,
    key: str,
) -> tuple[Path, Path]:
    """Export plaintext and key using the required filename format."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    plaintext_path = output_path / f"text_{length}_sample_{sample_id}_plaintext.txt"
    key_path = output_path / f"text_{length}_sample_{sample_id}_key.txt"

    plaintext_path.write_text(plaintext, encoding="utf-8")
    key_path.write_text(key, encoding="utf-8")

    return plaintext_path, key_path
