import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory

from substitution_cipher import ALPHABET


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_assignment_files.py"
SPEC = importlib.util.spec_from_file_location("validate_assignment_files", SCRIPT_PATH)
validate_assignment_files = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(validate_assignment_files)


def test_validate_assignment_files_accepts_complete_structure():
    output_root = Path("outputs")
    output_root.mkdir(exist_ok=True)

    with TemporaryDirectory(prefix="test_validate_assignment_", dir=output_root) as directory:
        root = Path(directory)
        ciphertext_dir = root / "ciphertexts"
        teacher_dir = root / "teacher_example"
        outputs_dir = root / "outputs"
        ciphertext_dir.mkdir()
        teacher_dir.mkdir()
        outputs_dir.mkdir()

        for length in (250, 500, 1000):
            for sample_id in range(1, 21):
                path = ciphertext_dir / f"text_{length}_sample_{sample_id}_ciphertext.txt"
                path.write_text("A" * length, encoding="utf-8")

        (teacher_dir / "text_1000_sample_1_plaintext.txt").write_text(
            "A" * 1000,
            encoding="utf-8",
        )
        (teacher_dir / "text_1000_sample_1_key.txt").write_text(ALPHABET, encoding="utf-8")

        status, errors, warnings, counts = validate_assignment_files.validate_assignment_files(
            ciphertext_dir=ciphertext_dir,
            teacher_dir=teacher_dir,
            output_dir=outputs_dir,
        )

        assert status == "OK"
        assert errors == []
        assert warnings == []
        assert counts["ciphertext_files"] == 60
        assert counts["teacher_plaintext_files"] == 1
        assert counts["teacher_key_files"] == 1


def test_validate_assignment_files_reports_missing_ciphertexts():
    output_root = Path("outputs")
    output_root.mkdir(exist_ok=True)

    with TemporaryDirectory(prefix="test_validate_missing_", dir=output_root) as directory:
        root = Path(directory)
        ciphertext_dir = root / "ciphertexts"
        teacher_dir = root / "teacher_example"
        outputs_dir = root / "outputs"
        ciphertext_dir.mkdir()
        teacher_dir.mkdir()
        outputs_dir.mkdir()

        (teacher_dir / "text_1000_sample_1_plaintext.txt").write_text(
            "A" * 1000,
            encoding="utf-8",
        )
        (teacher_dir / "text_1000_sample_1_key.txt").write_text(ALPHABET, encoding="utf-8")

        status, errors, _warnings, counts = validate_assignment_files.validate_assignment_files(
            ciphertext_dir=ciphertext_dir,
            teacher_dir=teacher_dir,
            output_dir=outputs_dir,
        )

        assert status == "ERROR"
        assert counts["ciphertext_files"] == 0
        assert any("Missing ciphertext" in error for error in errors)
