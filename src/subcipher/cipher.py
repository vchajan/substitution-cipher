"""Encryption and decryption for a classical substitution cipher."""

from __future__ import annotations

from .alphabet import ALPHABET


def validate_key(key: str) -> None:
    """Validate that key is a permutation of the project alphabet."""
    if not isinstance(key, str):
        raise TypeError("Key must be a string.")
    if len(key) != len(ALPHABET):
        raise ValueError(f"Key must contain exactly {len(ALPHABET)} characters.")
    if set(key) != set(ALPHABET):
        raise ValueError("Key must be a permutation of the project alphabet.")


def substitute_encrypt(plaintext: str, key: str) -> str:
    """Encrypt plaintext with a substitution key.

    Characters outside the project alphabet are copied unchanged.
    """
    validate_key(key)
    mapping = dict(zip(ALPHABET, key, strict=True))
    return "".join(mapping.get(char, char) for char in plaintext)


def substitute_decrypt(ciphertext: str, key: str) -> str:
    """Decrypt ciphertext with the inverse of a substitution key.

    Characters outside the project alphabet are copied unchanged.
    """
    validate_key(key)
    reverse_mapping = dict(zip(key, ALPHABET, strict=True))
    return "".join(reverse_mapping.get(char, char) for char in ciphertext)
