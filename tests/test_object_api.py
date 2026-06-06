from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

import substitution_cipher.api as api_module
from substitution_cipher import ALPHABET, CrackResult, SubstitutionCipher


def _uniform_matrix() -> np.ndarray:
    matrix = np.ones((len(ALPHABET), len(ALPHABET)), dtype=float)
    return matrix / matrix.sum()


def test_object_api_encrypt_decrypt_and_matrix_roundtrip():
    cipher = SubstitutionCipher()
    key = ALPHABET[1:] + ALPHABET[:1]
    plaintext = "AHOJ_SVETE"
    ciphertext = cipher.encrypt(plaintext, key)

    assert cipher.decrypt(ciphertext, key) == plaintext
    assert cipher.bigrams("ABC") == ["AB", "BC"]

    matrix = cipher.build_reference_matrix("AHOJ_SVETE_AHOJ")
    assert matrix.shape == (27, 27)
    assert np.isclose(matrix.sum(), 1.0)

    with TemporaryDirectory(prefix="test_object_api_", dir="outputs") as directory:
        path = Path(directory) / "matrix.npy"
        cipher.save_reference_matrix(path)
        loaded = SubstitutionCipher.from_matrix_file(path)
        assert np.allclose(loaded.reference_matrix, matrix)


def test_score_without_matrix_raises_clear_error():
    cipher = SubstitutionCipher()

    try:
        cipher.score("ABC")
    except ValueError as error:
        assert str(error) == "Reference matrix is not loaded."
    else:
        raise AssertionError("score should fail without a reference matrix")


def test_object_crack_with_polish_returns_crack_result():
    key = ALPHABET[3:] + ALPHABET[:3]
    plaintext = "AHOJ_SVETE_AHOJ_SVETE"
    ciphertext = SubstitutionCipher().encrypt(plaintext, key)
    cipher = SubstitutionCipher()
    cipher.build_reference_matrix(plaintext * 3)

    result = cipher.crack(
        ciphertext,
        iterations=1,
        restarts=1,
        seed=1,
        polish=True,
        progress_every=0,
        start_key=ALPHABET,
    )

    assert isinstance(result, CrackResult)
    assert isinstance(result.key, str)
    assert isinstance(result.plaintext, str)
    assert isinstance(result.score, float)
    assert len(result.plaintext) == len(ciphertext)


def test_object_crack_restarts_keep_best_result(monkeypatch):
    scores = iter([-20.0, -10.0])

    def fake_run(text, TM_ref, iterations, rng, start_key=None, progress_every=50):
        score = next(scores)
        return ALPHABET, text, score

    monkeypatch.setattr(api_module, "_run_metropolis_hastings", fake_run)
    cipher = SubstitutionCipher(_uniform_matrix())

    result = cipher.crack(
        "ABC",
        iterations=7,
        restarts=2,
        seed=10,
        polish=False,
        progress_every=0,
    )

    assert result.restart == 2
    assert result.iterations == 7
    assert result.score == -10.0


def test_crack_file_exports_plaintext_and_key(monkeypatch):
    def fake_run(text, TM_ref, iterations, rng, start_key=None, progress_every=50):
        return ALPHABET, text, -1.0

    monkeypatch.setattr(api_module, "_run_metropolis_hastings", fake_run)
    cipher = SubstitutionCipher(_uniform_matrix())

    with TemporaryDirectory(prefix="test_crack_file_", dir="outputs") as directory:
        root = Path(directory)
        ciphertext_path = root / "text_3_sample_2_ciphertext.txt"
        output_dir = root / "out"
        ciphertext_path.write_text("ABC", encoding="utf-8")

        result = cipher.crack_file(
            input_path=ciphertext_path,
            output_directory=output_dir,
            iterations=1,
            restarts=1,
            seed=1,
            polish=False,
        )

        assert result.plaintext == "ABC"
        assert (output_dir / "text_3_sample_2_plaintext.txt").read_text(
            encoding="utf-8"
        ) == "ABC"
        assert (output_dir / "text_3_sample_2_key.txt").read_text(
            encoding="utf-8"
        ) == ALPHABET


def test_crack_directory_empty_is_safe(capsys):
    cipher = SubstitutionCipher(_uniform_matrix())

    with TemporaryDirectory(prefix="test_crack_directory_empty_", dir="outputs") as directory:
        results = cipher.crack_directory(
            input_directory=directory,
            output_directory=Path(directory) / "out",
            iterations=1,
        )

    captured = capsys.readouterr()
    assert results == []
    assert "No ciphertext files found" in captured.out


def test_crack_directory_sorts_by_length_and_sample(monkeypatch):
    seen: list[str] = []

    def fake_crack_file(self, input_path, *args, **kwargs):
        seen.append(Path(input_path).name)
        return CrackResult(ALPHABET, "ABC", -1.0, 1, kwargs["iterations"])

    monkeypatch.setattr(SubstitutionCipher, "crack_file", fake_crack_file)
    cipher = SubstitutionCipher(_uniform_matrix())

    with TemporaryDirectory(prefix="test_crack_directory_sort_", dir="outputs") as directory:
        root = Path(directory)
        for name in (
            "text_500_sample_2_ciphertext.txt",
            "text_250_sample_10_ciphertext.txt",
            "text_250_sample_1_ciphertext.txt",
        ):
            (root / name).write_text("ABC", encoding="utf-8")

        results = cipher.crack_directory(
            input_directory=root,
            output_directory=root / "out",
            iterations=3,
        )

    assert [result.iterations for result in results] == [3, 3, 3]
    assert seen == [
        "text_250_sample_1_ciphertext.txt",
        "text_250_sample_10_ciphertext.txt",
        "text_500_sample_2_ciphertext.txt",
    ]
