from pathlib import Path
from tempfile import TemporaryDirectory

from substitution_cipher.export_utils import export_result


def test_export_result_writes_plaintext_and_key():
    output_root = Path("outputs")
    output_root.mkdir(exist_ok=True)

    with TemporaryDirectory(prefix="test_export_", dir=output_root) as directory:
        plaintext_path, key_path = export_result(
            plaintext="AHOJ_SVETE",
            key="ABCDEFGHIJKLMNOPQRSTUVWXYZ_",
            text_length=1000,
            sample_id=20,
            output_dir=directory,
        )

        assert plaintext_path.name == "text_1000_sample_20_plaintext.txt"
        assert key_path.name == "text_1000_sample_20_key.txt"
        assert plaintext_path.read_text(encoding="utf-8") == "AHOJ_SVETE"
        assert key_path.read_text(encoding="utf-8") == "ABCDEFGHIJKLMNOPQRSTUVWXYZ_"
