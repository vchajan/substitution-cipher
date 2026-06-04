import importlib.util
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_combined_reference_matrix.py"
SPEC = importlib.util.spec_from_file_location("build_combined_reference_matrix", SCRIPT_PATH)
build_combined_reference_matrix = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = build_combined_reference_matrix
SPEC.loader.exec_module(build_combined_reference_matrix)


def test_combined_reference_matrix_works_without_extra_text():
    output_root = Path("outputs")
    output_root.mkdir(exist_ok=True)

    with TemporaryDirectory(prefix="test_combined_without_extra_", dir=output_root) as directory:
        root = Path(directory)
        clean_text_path = root / "clean_text.txt"
        extra_text_path = root / "missing_valka_s_mloky_clean.txt"
        combined_text_path = root / "combined_clean_text.txt"
        matrix_path = root / "TM_ref.npy"

        clean_text_path.write_text("AB_AB", encoding="utf-8")

        stats = build_combined_reference_matrix.build_combined_reference_matrix(
            clean_text_path=clean_text_path,
            extra_text_path=extra_text_path,
            combined_text_path=combined_text_path,
            output_path=matrix_path,
        )

        matrix = np.load(matrix_path)

        assert stats.reference_count == 1
        assert stats.text_lengths == (5,)
        assert combined_text_path.read_text(encoding="utf-8") == "AB_AB"
        assert stats.bigram_count == 4
        assert matrix.shape == (27, 27)
        assert np.isclose(matrix.sum(), 1.0)
        assert not stats.contains_zeros


def test_combined_reference_matrix_works_with_extra_text():
    output_root = Path("outputs")
    output_root.mkdir(exist_ok=True)

    with TemporaryDirectory(prefix="test_combined_with_extra_", dir=output_root) as directory:
        root = Path(directory)
        clean_text_path = root / "clean_text.txt"
        extra_text_path = root / "valka_s_mloky_clean.txt"
        combined_text_path = root / "combined_clean_text.txt"
        matrix_path = root / "TM_ref.npy"

        clean_text_path.write_text("AB_AB", encoding="utf-8")
        extra_text_path.write_text("CD_CD", encoding="utf-8")

        stats = build_combined_reference_matrix.build_combined_reference_matrix(
            clean_text_path=clean_text_path,
            extra_text_path=extra_text_path,
            combined_text_path=combined_text_path,
            output_path=matrix_path,
        )

        matrix = np.load(matrix_path)

        assert stats.reference_count == 2
        assert stats.text_lengths == (5, 5)
        assert combined_text_path.read_text(encoding="utf-8") == "AB_AB_CD_CD"
        assert stats.bigram_count == 10
        assert matrix.shape == (27, 27)
        assert np.isclose(matrix.sum(), 1.0)
        assert not stats.contains_zeros
