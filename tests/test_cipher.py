import pytest

from substitution_cipher import ALPHABET, substitute_decrypt, substitute_encrypt
from substitution_cipher.cipher import validate_key


def test_valid_key_passes():
    validate_key(ALPHABET)


def test_invalid_key_raises_value_error():
    with pytest.raises(ValueError):
        validate_key(ALPHABET[:-1])

    with pytest.raises(ValueError):
        validate_key("A" * len(ALPHABET))


def test_encrypt_decrypt_roundtrip():
    key = ALPHABET[3:] + ALPHABET[:3]
    plaintext = "BYL_POZDNI_VECER_PRVNI_MAJ"
    ciphertext = substitute_encrypt(plaintext, key)

    assert ciphertext == "EAOCSRBGQLCYHFHUCSUYQLCPDM"
    assert substitute_decrypt(ciphertext, key) == plaintext


def test_characters_outside_alphabet_are_left_unchanged():
    key = ALPHABET[1:] + ALPHABET[:1]

    assert substitute_encrypt("AHOJ!", key).endswith("!")
    assert substitute_decrypt("BIPK!", key).endswith("!")
