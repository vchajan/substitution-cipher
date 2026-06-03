import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "decrypt_samples.py"
SPEC = importlib.util.spec_from_file_location("decrypt_samples", SCRIPT_PATH)
decrypt_samples = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(decrypt_samples)


def test_empty_ciphertext_directory_is_safe():
    output_root = Path("outputs")
    output_root.mkdir(exist_ok=True)

    with TemporaryDirectory(prefix="test_empty_ciphertexts_", dir=output_root) as directory:
        assert decrypt_samples.find_ciphertext_files(directory) == []


def test_ciphertext_filename_is_parsed():
    length, sample_id = decrypt_samples.parse_ciphertext_filename(
        "text_1000_sample_20_ciphertext.txt"
    )

    assert length == 1000
    assert sample_id == 20
