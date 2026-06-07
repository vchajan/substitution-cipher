"""Kontrola vstupních souborů zadání a vytvořených výstupů."""

from __future__ import annotations

import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from substitution_cipher.cipher import validate_key  # noqa: E402
from substitution_cipher.constants import ALPHABET  # noqa: E402
from substitution_cipher.paths import CIPHERTEXT_DIR, OUTPUT_DIR, TEACHER_EXAMPLE_DIR  # noqa: E402


EXPECTED_LENGTHS = (250, 500, 1000)
EXPECTED_SAMPLE_IDS = tuple(range(1, 21))

CIPHERTEXT_PATTERN = re.compile(
    r"^text_(?P<length>\d+)_sample_(?P<sample_id>\d+)_ciphertext\.txt$"
)
PLAINTEXT_PATTERN = re.compile(
    r"^text_(?P<length>\d+)_sample_(?P<sample_id>\d+)_plaintext\.txt$"
)
KEY_PATTERN = re.compile(r"^text_(?P<length>\d+)_sample_(?P<sample_id>\d+)_key\.txt$")


def _read_stripped(path: Path) -> str:
    """Načte UTF-8 text a odstraní okolní bílé znaky."""
    return path.read_text(encoding="utf-8").strip()


def _invalid_characters(text: str) -> list[str]:
    """Vrátí znaky mimo projektovou abecedu."""
    return sorted(set(text) - set(ALPHABET))


def _expected_pairs() -> set[tuple[int, int]]:
    """Vrátí všechny očekávané dvojice délky a ID vzorku."""
    return {
        (length, sample_id)
        for length in EXPECTED_LENGTHS
        for sample_id in EXPECTED_SAMPLE_IDS
    }


def _parse_named_file(
    path: Path,
    pattern: re.Pattern[str],
    errors: list[str],
) -> tuple[int, int] | None:
    """Zpracuje název souboru a sjednotí formát chyb."""
    match = pattern.match(path.name)
    if not match:
        errors.append(f"Neplatný název souboru: {path}")
        return None
    return int(match.group("length")), int(match.group("sample_id"))


def validate_ciphertexts(
    ciphertext_dir: str | Path = CIPHERTEXT_DIR,
) -> tuple[list[str], list[str], dict[str, int]]:
    """Zkontroluje ciphertexty, jejich názvy, počty, délky a znaky."""
    directory = Path(ciphertext_dir)
    errors: list[str] = []
    warnings: list[str] = []
    counts = {"ciphertext_files": 0}

    if not directory.exists():
        errors.append(f"Složka s ciphertexty chybí: {directory}")
        return errors, warnings, counts

    txt_files = sorted(directory.glob("*.txt"))
    counts["ciphertext_files"] = len(txt_files)
    found: set[tuple[int, int]] = set()

    for path in txt_files:
        parsed = _parse_named_file(path, CIPHERTEXT_PATTERN, errors)
        if parsed is None:
            continue

        length, sample_id = parsed
        if length not in EXPECTED_LENGTHS:
            errors.append(f"Neočekávaná délka ciphertextu v názvu: {path.name}")
            continue
        if sample_id not in EXPECTED_SAMPLE_IDS:
            errors.append(f"Neočekávané ID vzorku v názvu: {path.name}")
            continue

        found.add((length, sample_id))
        text = _read_stripped(path)
        invalid_chars = _invalid_characters(text)
        if invalid_chars:
            errors.append(f"Ciphertext obsahuje nepovolené znaky {invalid_chars}: {path.name}")
        if len(text) != length:
            warnings.append(
                f"Nesedí délka ciphertextu {path.name}: "
                f"očekáváno {length}, nalezeno {len(text)}"
            )

    for length, sample_id in sorted(_expected_pairs() - found):
        errors.append(f"Chybí ciphertext: text_{length}_sample_{sample_id}_ciphertext.txt")

    if len(txt_files) != 60:
        errors.append(f"Očekáváno 60 ciphertext souborů, nalezeno {len(txt_files)}")

    return errors, warnings, counts


def validate_teacher_example(
    teacher_dir: str | Path = TEACHER_EXAMPLE_DIR,
) -> tuple[list[str], list[str], dict[str, int]]:
    """Zkontroluje známý učitelský plaintext a klíč."""
    directory = Path(teacher_dir)
    errors: list[str] = []
    warnings: list[str] = []
    counts = {"teacher_plaintext_files": 0, "teacher_key_files": 0}

    plaintext_path = directory / "text_1000_sample_1_plaintext.txt"
    key_path = directory / "text_1000_sample_1_key.txt"

    if plaintext_path.exists():
        counts["teacher_plaintext_files"] = 1
        plaintext = _read_stripped(plaintext_path)
        invalid_chars = _invalid_characters(plaintext)
        if invalid_chars:
            errors.append(f"Učitelský plaintext obsahuje nepovolené znaky {invalid_chars}")
        if len(plaintext) != 1000:
            warnings.append(
                f"Nesedí délka učitelského plaintextu: "
                f"očekáváno 1000, nalezeno {len(plaintext)}"
            )
    else:
        errors.append(f"Chybí učitelský plaintext: {plaintext_path}")

    if key_path.exists():
        counts["teacher_key_files"] = 1
        key = _read_stripped(key_path)
        try:
            validate_key(key)
        except ValueError as error:
            errors.append(f"Učitelský klíč není platný: {error}")
    else:
        errors.append(f"Chybí učitelský klíč: {key_path}")

    return errors, warnings, counts


def validate_outputs(
    output_dir: str | Path = OUTPUT_DIR,
) -> tuple[list[str], list[str], dict[str, int]]:
    """Zkontroluje existující exportované plaintexty a klíče."""
    directory = Path(output_dir)
    errors: list[str] = []
    warnings: list[str] = []
    counts = {"output_plaintext_files": 0, "output_key_files": 0}

    if not directory.exists():
        warnings.append(f"Výstupní složka chybí: {directory}")
        return errors, warnings, counts

    plaintext_files = sorted(directory.glob("text_*_sample_*_plaintext.txt"))
    key_files = sorted(directory.glob("text_*_sample_*_key.txt"))
    recognized_files = set(plaintext_files) | set(key_files)
    counts["output_plaintext_files"] = len(plaintext_files)
    counts["output_key_files"] = len(key_files)

    for path in sorted(directory.glob("*.txt")):
        if path not in recognized_files:
            errors.append(f"Neplatný název výstupního souboru: {path}")

    plaintext_pairs: set[tuple[int, int]] = set()
    key_pairs: set[tuple[int, int]] = set()

    for path in plaintext_files:
        parsed = _parse_named_file(path, PLAINTEXT_PATTERN, errors)
        if parsed is None:
            continue
        length, sample_id = parsed
        plaintext_pairs.add((length, sample_id))
        text = _read_stripped(path)
        invalid_chars = _invalid_characters(text)
        if invalid_chars:
            errors.append(f"Plaintext obsahuje nepovolené znaky {invalid_chars}: {path.name}")
        if len(text) != length:
            warnings.append(
                f"Nesedí délka plaintextu {path.name}: "
                f"očekáváno {length}, nalezeno {len(text)}"
            )

    for path in key_files:
        parsed = _parse_named_file(path, KEY_PATTERN, errors)
        if parsed is None:
            continue
        key_pairs.add(parsed)
        key = _read_stripped(path)
        try:
            validate_key(key)
        except ValueError as error:
            errors.append(f"Výstupní klíč není platný v {path.name}: {error}")

    for pair in sorted(plaintext_pairs - key_pairs):
        warnings.append(f"Chybí key výstup pro délku/vzorek: {pair[0]}/{pair[1]}")
    for pair in sorted(key_pairs - plaintext_pairs):
        warnings.append(f"Chybí plaintext výstup pro délku/vzorek: {pair[0]}/{pair[1]}")

    if plaintext_files or key_files:
        if len(plaintext_files) != 60:
            warnings.append(f"Očekáváno 60 plaintext výstupů, nalezeno {len(plaintext_files)}")
        if len(key_files) != 60:
            warnings.append(f"Očekáváno 60 key výstupů, nalezeno {len(key_files)}")

    return errors, warnings, counts


def validate_assignment_files(
    ciphertext_dir: str | Path = CIPHERTEXT_DIR,
    teacher_dir: str | Path = TEACHER_EXAMPLE_DIR,
    output_dir: str | Path = OUTPUT_DIR,
) -> tuple[str, list[str], list[str], dict[str, int]]:
    """Spustí všechny kontroly souborů zadání."""
    errors: list[str] = []
    warnings: list[str] = []
    counts: dict[str, int] = {}

    for section_errors, section_warnings, section_counts in (
        validate_ciphertexts(ciphertext_dir),
        validate_teacher_example(teacher_dir),
        validate_outputs(output_dir),
    ):
        errors.extend(section_errors)
        warnings.extend(section_warnings)
        counts.update(section_counts)

    status = "ERROR" if errors else "WARNING" if warnings else "OK"
    return status, errors, warnings, counts


def print_summary(status: str, errors: list[str], warnings: list[str], counts: dict[str, int]) -> None:
    """Vypíše přehledný souhrn validace."""
    print("===== KONTROLA SOUBORŮ ZADÁNÍ =====")
    print(f"Status: {status}")
    print()
    print("Počty:")
    for key in sorted(counts):
        print(f"  {key}: {counts[key]}")

    if warnings:
        print()
        print("Varování:")
        for warning in warnings:
            print(f"  VAROVÁNÍ: {warning}")

    if errors:
        print()
        print("Chyby:")
        for error in errors:
            print(f"  CHYBA: {error}")


def main() -> None:
    """Zkontroluje vstupy a výstupy projektu."""
    status, errors, warnings, counts = validate_assignment_files()
    print_summary(status, errors, warnings, counts)
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
