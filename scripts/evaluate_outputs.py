"""Vyhodnocení výstupů proti známému učitelskému příkladu."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from substitution_cipher.cipher import validate_key  # noqa: E402
from substitution_cipher.cryptanalysis import plausibility  # noqa: E402
from substitution_cipher.io_utils import load_matrix  # noqa: E402
from substitution_cipher.paths import (  # noqa: E402
    OUTPUT_DIR,
    REFERENCE_MATRIX_PATH,
    REPORT_DIR,
    TEACHER_EXAMPLE_DIR,
)


REPORT_MD_PATH = REPORT_DIR / "evaluation_summary.md"
REPORT_CSV_PATH = REPORT_DIR / "evaluation_summary.csv"

PLAINTEXT_PATTERN = re.compile(
    r"^text_(?P<length>\d+)_sample_(?P<sample_id>\d+)_plaintext\.txt$"
)
CSV_FIELDS = [
    "length",
    "sample_id",
    "plaintext_file",
    "key_file",
    "plaintext_length",
    "key_valid",
    "plausibility",
    "matches_teacher_example",
    "matching_chars",
    "matching_percent",
    "key_matches_teacher_example",
]


def _read_optional(path: Path) -> str | None:
    """Načte textový soubor, pokud existuje."""
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip()


def _parse_plaintext_filename(path: Path) -> tuple[int, int] | None:
    """Získá délku a ID vzorku z názvu plaintext výstupu."""
    match = PLAINTEXT_PATTERN.match(path.name)
    if not match:
        return None
    return int(match.group("length")), int(match.group("sample_id"))


def _matching_characters(left: str, right: str) -> int:
    """Spočítá shodné znaky na stejných pozicích."""
    return sum(1 for first, second in zip(left, right, strict=False) if first == second)


def _key_is_valid(key: str | None) -> bool:
    """Vrátí, zda je klíč platnou permutací abecedy."""
    if key is None:
        return False
    try:
        validate_key(key)
    except ValueError:
        return False
    return True


def _format_optional(value: object) -> str:
    """Naformátuje volitelné hodnoty pro CSV a Markdown."""
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def collect_evaluation_rows(
    teacher_dir: str | Path = TEACHER_EXAMPLE_DIR,
    output_dir: str | Path = OUTPUT_DIR,
    matrix_path: str | Path = REFERENCE_MATRIX_PATH,
) -> list[dict[str, object]]:
    """Nasbírá vyhodnocovací řádky pro všechny plaintext výstupy."""
    teacher_path = Path(teacher_dir)
    outputs_path = Path(output_dir)
    matrix = load_matrix(matrix_path)

    teacher_plaintext = _read_optional(teacher_path / "text_1000_sample_1_plaintext.txt")
    teacher_key = _read_optional(teacher_path / "text_1000_sample_1_key.txt")

    rows: list[dict[str, object]] = []
    for plaintext_path in sorted(outputs_path.glob("text_*_sample_*_plaintext.txt")):
        parsed = _parse_plaintext_filename(plaintext_path)
        if parsed is None:
            continue

        length, sample_id = parsed
        key_path = outputs_path / f"text_{length}_sample_{sample_id}_key.txt"
        plaintext = plaintext_path.read_text(encoding="utf-8").strip()
        key = _read_optional(key_path)

        row: dict[str, object] = {
            "length": length,
            "sample_id": sample_id,
            "plaintext_file": plaintext_path.name,
            "key_file": key_path.name if key_path.exists() else "",
            "plaintext_length": len(plaintext),
            "key_valid": _key_is_valid(key),
            "plausibility": plausibility(plaintext, matrix),
            "matches_teacher_example": None,
            "matching_chars": None,
            "matching_percent": None,
            "key_matches_teacher_example": None,
        }

        if length == 1000 and sample_id == 1 and teacher_plaintext is not None:
            matching_chars = _matching_characters(plaintext, teacher_plaintext)
            row["matches_teacher_example"] = plaintext == teacher_plaintext
            row["matching_chars"] = matching_chars
            row["matching_percent"] = matching_chars / len(teacher_plaintext) * 100.0

            if teacher_key is not None and key is not None:
                row["key_matches_teacher_example"] = key == teacher_key

        rows.append(row)

    return rows


def write_csv(rows: list[dict[str, object]], path: str | Path = REPORT_CSV_PATH) -> Path:
    """Zapíše vyhodnocení do CSV."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _format_optional(row.get(field)) for field in CSV_FIELDS})
    return output_path


def write_markdown(rows: list[dict[str, object]], path: str | Path = REPORT_MD_PATH) -> Path:
    """Zapíše krátký Markdown souhrn vyhodnocení."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plaintext_count = len(rows)
    key_count = sum(1 for row in rows if row["key_file"])
    teacher_row = next(
        (row for row in rows if row["length"] == 1000 and row["sample_id"] == 1),
        None,
    )

    lines = [
        "# Vyhodnocení výstupů",
        "",
        "## Souhrn",
        "",
        f"- Počet plaintext souborů: {plaintext_count}",
        f"- Počet key souborů: {key_count}",
        "- Referenční matice: `models/TM_ref.npy`",
        "",
        "## Učitelský příklad text_1000_sample_1",
        "",
    ]

    if teacher_row is None:
        lines.append("- Výstup pro učitelský příklad nebyl nalezen.")
    else:
        lines.extend(
            [
                f"- Plaintext přesně sedí: {_format_optional(teacher_row['matches_teacher_example'])}",
                f"- Správné znaky: {_format_optional(teacher_row['matching_chars'])}",
                f"- Procento shody: {_format_optional(teacher_row['matching_percent'])}",
                f"- Key přesně sedí: {_format_optional(teacher_row['key_matches_teacher_example'])}",
            ]
        )

    lines.extend(
        [
            "",
            "## Tabulka",
            "",
            "| length | sample_id | plaintext_file | key_file | plaintext_length | key_valid | plausibility | matches_teacher_example | matching_chars | matching_percent | key_matches_teacher_example |",
            "|---:|---:|---|---|---:|---|---:|---|---:|---:|---|",
        ]
    )

    for row in rows:
        lines.append(
            "| "
            + " | ".join(_format_optional(row.get(field)) for field in CSV_FIELDS)
            + " |"
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def evaluate_outputs(
    teacher_dir: str | Path = TEACHER_EXAMPLE_DIR,
    output_dir: str | Path = OUTPUT_DIR,
    matrix_path: str | Path = REFERENCE_MATRIX_PATH,
    report_md_path: str | Path = REPORT_MD_PATH,
    report_csv_path: str | Path = REPORT_CSV_PATH,
) -> tuple[list[dict[str, object]], Path, Path]:
    """Vyhodnotí výstupy a uloží Markdown i CSV souhrn."""
    rows = collect_evaluation_rows(teacher_dir, output_dir, matrix_path)
    csv_path = write_csv(rows, report_csv_path)
    md_path = write_markdown(rows, report_md_path)
    return rows, md_path, csv_path


def main() -> None:
    """Spustí vyhodnocení s výchozími cestami projektu."""
    rows, md_path, csv_path = evaluate_outputs()
    print("===== VYHODNOCENÍ VÝSTUPŮ =====")
    print(f"Vyhodnocené plaintext soubory: {len(rows)}")
    print(f"Markdown souhrn uložen do: {md_path}")
    print(f"CSV souhrn uložen do: {csv_path}")


if __name__ == "__main__":
    main()
