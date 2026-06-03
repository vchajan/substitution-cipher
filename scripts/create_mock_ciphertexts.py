from pathlib import Path
import random
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from substitution_cipher import ALPHABET, substitute_encrypt


def random_key(seed: int) -> str:
    rng = random.Random(seed)
    chars = list(ALPHABET)
    rng.shuffle(chars)
    return "".join(chars)


def main() -> None:
    clean_text_path = PROJECT_ROOT / "data" / "processed" / "clean_text.txt"
    ciphertext_dir = PROJECT_ROOT / "data" / "ciphertexts"
    expected_dir = PROJECT_ROOT / "data" / "mock_expected"

    ciphertext_dir.mkdir(parents=True, exist_ok=True)
    expected_dir.mkdir(parents=True, exist_ok=True)

    clean_text = clean_text_path.read_text(encoding="utf-8")

    samples = [
        {"length": 300, "sample_id": 1, "start": 1000, "seed": 101},
        {"length": 500, "sample_id": 2, "start": 8000, "seed": 202},
        {"length": 1000, "sample_id": 3, "start": 20000, "seed": 303},
    ]

    for sample in samples:
        length = sample["length"]
        sample_id = sample["sample_id"]
        start = sample["start"]
        seed = sample["seed"]

        plaintext = clean_text[start:start + length]
        key = random_key(seed)
        ciphertext = substitute_encrypt(plaintext, key)

        ciphertext_path = ciphertext_dir / f"text_{length}_sample_{sample_id}_ciphertext.txt"
        expected_plaintext_path = expected_dir / f"text_{length}_sample_{sample_id}_plaintext.txt"
        expected_key_path = expected_dir / f"text_{length}_sample_{sample_id}_key.txt"

        ciphertext_path.write_text(ciphertext, encoding="utf-8")
        expected_plaintext_path.write_text(plaintext, encoding="utf-8")
        expected_key_path.write_text(key, encoding="utf-8")

        print(f"Created: {ciphertext_path}")
        print(f"Expected plaintext: {expected_plaintext_path}")
        print(f"Expected key: {expected_key_path}")
        print()

    print("Mock ciphertext files created.")
    print("Use files in data/ciphertexts/ for testing decrypt_samples.py.")
    print("Files in data/mock_expected/ are only for checking during development.")


if __name__ == "__main__":
    main()