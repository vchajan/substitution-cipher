from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

from scripts.build_reference_matrix import build_reference_matrix
from substitution_cipher.paths import CLEAN_REFERENCE_TEXT_PATH, REFERENCE_MATRIX_PATH
from substitution_cipher.preprocessing import validate_clean_text


def test_clean_reference_text_path_is_valka_s_mloky():
    assert CLEAN_REFERENCE_TEXT_PATH.as_posix().endswith("data/reference/valka_s_mloky_clean.txt")
    text = CLEAN_REFERENCE_TEXT_PATH.read_text(encoding="utf-8").strip()
    validate_clean_text(text)
    assert len(text) > 1000


def test_build_reference_matrix_properties_on_temp_file():
    with TemporaryDirectory(prefix="matrix_build_", dir="outputs") as directory:
        root = Path(directory)
        clean_text_path = root / "valka_s_mloky_clean.txt"
        matrix_path = root / "TM_ref.npy"
        clean_text_path.write_text("AHOJ_SVETE_AHOJ_SVETE_AHOJ_SVETE", encoding="utf-8")

        matrix, bigram_count = build_reference_matrix(clean_text_path, matrix_path)

        assert bigram_count == len(clean_text_path.read_text(encoding="utf-8")) - 1
        assert matrix_path.exists()
        assert matrix.shape == (27, 27)
        assert np.isclose(matrix.sum(), 1.0)
        assert int(np.sum(matrix == 0.0)) == 0
        assert not np.isnan(matrix).any()
        assert not np.isinf(matrix).any()


def test_final_matrix_path_is_models_directory():
    assert REFERENCE_MATRIX_PATH.as_posix().endswith("models/TM_ref.npy")
