from pathlib import Path
from tempfile import TemporaryDirectory

from substitution_cipher import ALPHABET
from substitution_cipher.io_utils import export_result, parse_ciphertext_filename


def test_parse_ciphertext_filename():
    assert parse_ciphertext_filename("text_500_sample_12_ciphertext.txt") == (500, 12)


def test_export_result_creates_assignment_files():
    with TemporaryDirectory(prefix="export_result_", dir="outputs") as directory:
        plaintext_path, key_path = export_result("ABC", ALPHABET, 3, 2, directory)

        assert Path(plaintext_path).name == "text_3_sample_2_plaintext.txt"
        assert Path(key_path).name == "text_3_sample_2_key.txt"
        assert Path(plaintext_path).read_text(encoding="utf-8") == "ABC"
        assert Path(key_path).read_text(encoding="utf-8") == ALPHABET
