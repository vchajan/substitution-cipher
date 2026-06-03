import pytest

from subcipher import ALPHABET, caesar_key, random_key, substitute_decrypt, substitute_encrypt
from subcipher.cipher import validate_key


def test_caesar_encrypt_decrypt_roundtrip():
    key = caesar_key(3)
    plaintext = "BYL_POZDNI_VECER"
    ciphertext = substitute_encrypt(plaintext, key)
    assert ciphertext == "EAOCSRBGQLCYHFHU"
    assert substitute_decrypt(ciphertext, key) == plaintext


def test_random_key_roundtrip():
    key = random_key(seed=42)
    plaintext = "AHOJ_SVETE"
    ciphertext = substitute_encrypt(plaintext, key)
    assert substitute_decrypt(ciphertext, key) == plaintext


def test_invalid_key_rejected():
    with pytest.raises(ValueError):
        validate_key(ALPHABET[:-1])
