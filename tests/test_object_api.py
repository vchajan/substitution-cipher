from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

import substitution_cipher.api as api_module
from substitution_cipher import ALPHABET, CrackResult, SubstitutionCipher


def _uniform_matrix() -> np.ndarray:
    matrix = np.ones((len(ALPHABET), len(ALPHABET)), dtype=float)
    return matrix / matrix.sum()


def test_object_api_encrypt_decrypt_score_and_matrix_file():
    cipher = SubstitutionCipher()
    key = ALPHABET[2:] + ALPHABET[:2]
    plaintext = "TESTOVACI_TEXT"
    ciphertext = cipher.encrypt(plaintext, key)

    assert cipher.decrypt(ciphertext, key) == plaintext
    matrix = cipher.build_reference_matrix((plaintext + "_") * 3)
    assert matrix.shape == (27, 27)
    assert np.isclose(matrix.sum(), 1.0)
    assert isinstance(cipher.score(plaintext), float)

    with TemporaryDirectory(prefix="matrix_test_", dir="outputs") as directory:
        path = Path(directory) / "TM_ref.npy"
        cipher.save_reference_matrix(path)
        loaded = SubstitutionCipher.from_matrix_file(path)
        assert np.allclose(loaded.reference_matrix, matrix)


def test_crack_returns_crack_result(monkeypatch):
    def fake_run(text, TM_ref, iterations, rng, start_key=None, progress_every=50):
        return ALPHABET, text, -1.0

    monkeypatch.setattr(api_module, "_run_metropolis_hastings", fake_run)
    cipher = SubstitutionCipher(_uniform_matrix())

    result = cipher.crack("ABC", iterations=1, restarts=1, polish=False, progress_every=0)

    assert isinstance(result, CrackResult)
    assert result.key == ALPHABET
    assert result.plaintext == "ABC"
    assert result.score == -1.0


def test_crack_file_and_directory_export(monkeypatch):
    def fake_run(text, TM_ref, iterations, rng, start_key=None, progress_every=50):
        return ALPHABET, text, -1.0

    monkeypatch.setattr(api_module, "_run_metropolis_hastings", fake_run)
    cipher = SubstitutionCipher(_uniform_matrix())

    with TemporaryDirectory(prefix="crack_dir_", dir="outputs") as directory:
        root = Path(directory)
        input_dir = root / "in"
        output_dir = root / "out"
        input_dir.mkdir()
        (input_dir / "text_3_sample_2_ciphertext.txt").write_text("ABC", encoding="utf-8")

        results = cipher.crack_directory(input_dir, output_dir, iterations=1, polish=False)

        assert len(results) == 1
        assert (output_dir / "text_3_sample_2_plaintext.txt").read_text(encoding="utf-8") == "ABC"
        assert (output_dir / "text_3_sample_2_key.txt").read_text(encoding="utf-8") == ALPHABET
