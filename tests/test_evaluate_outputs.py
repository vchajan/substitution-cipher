import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

from substitution_cipher import ALPHABET
from substitution_cipher.bigrams import save_matrix, transition_matrix


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "evaluate_outputs.py"
SPEC = importlib.util.spec_from_file_location("evaluate_outputs", SCRIPT_PATH)
evaluate_outputs = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(evaluate_outputs)


def test_evaluate_outputs_writes_markdown_and_csv():
    output_root = Path("outputs")
    output_root.mkdir(exist_ok=True)

    with TemporaryDirectory(prefix="test_evaluate_outputs_", dir=output_root) as directory:
        root = Path(directory)
        teacher_dir = root / "teacher_example"
        outputs_dir = root / "outputs"
        reports_dir = root / "reports"
        teacher_dir.mkdir()
        outputs_dir.mkdir()
        reports_dir.mkdir()

        plaintext = "A" * 1000
        absolute = transition_matrix(["AA"])
        matrix = absolute / absolute.sum()
        matrix_path = root / "TM_ref.npy"
        save_matrix(matrix, matrix_path)

        (teacher_dir / "text_1000_sample_1_plaintext.txt").write_text(
            plaintext,
            encoding="utf-8",
        )
        (teacher_dir / "text_1000_sample_1_key.txt").write_text(ALPHABET, encoding="utf-8")
        (outputs_dir / "text_1000_sample_1_plaintext.txt").write_text(
            plaintext,
            encoding="utf-8",
        )
        (outputs_dir / "text_1000_sample_1_key.txt").write_text(ALPHABET, encoding="utf-8")

        rows, md_path, csv_path = evaluate_outputs.evaluate_outputs(
            teacher_dir=teacher_dir,
            output_dir=outputs_dir,
            matrix_path=matrix_path,
            report_md_path=reports_dir / "evaluation_summary.md",
            report_csv_path=reports_dir / "evaluation_summary.csv",
        )

        assert len(rows) == 1
        assert rows[0]["matches_teacher_example"] is True
        assert rows[0]["matching_chars"] == 1000
        assert np.isclose(rows[0]["matching_percent"], 100.0)
        assert rows[0]["key_matches_teacher_example"] is True
        assert md_path.exists()
        assert csv_path.exists()
