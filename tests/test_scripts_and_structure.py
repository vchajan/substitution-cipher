from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.decrypt_samples import find_ciphertext_files
from scripts.prepare_reference_text import prepare_reference_text
from scripts.validate_assignment_files import validate_assignment_files


def test_prepare_reference_text_uses_library_cleaning():
    with TemporaryDirectory(prefix="prepare_text_", dir="outputs") as directory:
        root = Path(directory)
        raw_path = root / "raw.txt"
        clean_path = root / "clean.txt"
        raw_path.write_text("Příliš žluťoučký kůň 123!", encoding="utf-8")

        cleaned, output_path = prepare_reference_text(raw_path, clean_path)

        assert output_path == clean_path
        assert cleaned == "PRILIS_ZLUTOUCKY_KUN"
        assert clean_path.read_text(encoding="utf-8") == cleaned


def test_find_ciphertext_files_sorts_assignment_names():
    with TemporaryDirectory(prefix="ciphertexts_", dir="outputs") as directory:
        root = Path(directory)
        for name in (
            "text_500_sample_2_ciphertext.txt",
            "text_250_sample_10_ciphertext.txt",
            "text_250_sample_1_ciphertext.txt",
        ):
            (root / name).write_text("ABC", encoding="utf-8")

        files = find_ciphertext_files(root)

        assert [path.name for path in files] == [
            "text_250_sample_1_ciphertext.txt",
            "text_250_sample_10_ciphertext.txt",
            "text_500_sample_2_ciphertext.txt",
        ]


def test_data_directory_contains_only_text_data():
    allowed_suffixes = {".txt", ".gitkeep"}
    for path in Path("data").rglob("*"):
        if path.is_file():
            assert path.suffix in allowed_suffixes or path.name == ".gitkeep"


def test_validate_assignment_files_accepts_small_valid_fixture():
    with TemporaryDirectory(prefix="validate_files_", dir="outputs") as directory:
        root = Path(directory)
        ciphertext_dir = root / "ciphertexts"
        teacher_dir = root / "teacher"
        output_dir = root / "outputs"
        ciphertext_dir.mkdir()
        teacher_dir.mkdir()
        output_dir.mkdir()

        for length in (250, 500, 1000):
            for sample_id in range(1, 21):
                name = f"text_{length}_sample_{sample_id}_ciphertext.txt"
                (ciphertext_dir / name).write_text("A" * length, encoding="utf-8")

        (teacher_dir / "text_1000_sample_1_plaintext.txt").write_text("A" * 1000, encoding="utf-8")
        (teacher_dir / "text_1000_sample_1_key.txt").write_text(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ_",
            encoding="utf-8",
        )

        status, errors, _warnings, counts = validate_assignment_files(
            ciphertext_dir,
            teacher_dir,
            output_dir,
        )

        assert status == "OK"
        assert errors == []
        assert counts["ciphertext_files"] == 60
