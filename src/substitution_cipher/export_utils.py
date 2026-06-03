"""Export helpers for decrypted plaintexts and keys."""

from __future__ import annotations

from pathlib import Path


def export_result(
    plaintext: str,
    key: str,
    text_length: int,
    sample_id: int,
    output_dir: str | Path = "outputs",
) -> tuple[Path, Path]:
    """Write plaintext and key files in the assignment filename format.

    Args:
        plaintext: Decrypted text to save.
        key: Substitution key to save.
        text_length: Original ciphertext length used in the filename.
        sample_id: Ciphertext sample identifier used in the filename.
        output_dir: Directory where output files are written.

    Returns:
        Tuple ``(plaintext_path, key_path)``.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    plaintext_path = output_path / f"text_{text_length}_sample_{sample_id}_plaintext.txt"
    key_path = output_path / f"text_{text_length}_sample_{sample_id}_key.txt"

    plaintext_path.write_text(plaintext, encoding="utf-8")
    key_path.write_text(key, encoding="utf-8")

    return plaintext_path, key_path
