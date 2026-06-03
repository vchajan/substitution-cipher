from pathlib import Path

from subcipher.io_utils import export_decryption_result, parse_ciphertext_filename


def test_parse_ciphertext_filename():
    length, sample_id = parse_ciphertext_filename("text_1000_sample_20_ciphertext.txt")
    assert length == 1000
    assert sample_id == 20


def test_export_decryption_result(tmp_path: Path):
    plaintext_path, key_path = export_decryption_result(tmp_path, 1000, 20, "ABC", "KEY")
    assert plaintext_path.name == "text_1000_sample_20_plaintext.txt"
    assert key_path.name == "text_1000_sample_20_key.txt"
    assert plaintext_path.read_text(encoding="utf-8") == "ABC"
    assert key_path.read_text(encoding="utf-8") == "KEY"
