"""Classical substitution cipher helpers."""

from __future__ import annotations

from .config import ALPHABET


def validate_key(key: str, alphabet: str = ALPHABET) -> None:
    """Validate that ``key`` is a permutation of ``alphabet``.

    The key must have the same length as the alphabet, contain exactly the
    alphabet characters, and use every character once.

    Args:
        key: Candidate substitution key.
        alphabet: Alphabet that the key must permute.

    Returns:
        None.

    Raises:
        ValueError: If the key is not a valid alphabet permutation.
    """
    if not isinstance(key, str):
        raise ValueError("Key must be a string.")

    if len(key) != len(alphabet):
        raise ValueError("Key must have the same length as the alphabet.")

    if len(set(key)) != len(key):
        raise ValueError("Key must not contain duplicate characters.")

    if set(key) != set(alphabet):
        raise ValueError("Key must contain exactly the same characters as the alphabet.")


def substitute_encrypt(plaintext: str, key: str) -> str:
    """Encrypt ``plaintext`` with a classical substitution key.

    Each character from the assignment alphabet is mapped to the character at
    the same position in ``key``. Characters outside the alphabet are copied
    unchanged.

    Args:
        plaintext: Text to encrypt.
        key: Permutation of ``ALPHABET`` used as the substitution key.

    Returns:
        Encrypted text.

    Raises:
        ValueError: If ``key`` is not a valid alphabet permutation.
    """
    validate_key(key)
    mapping = dict(zip(ALPHABET, key, strict=True))
    return "".join(mapping.get(char, char) for char in plaintext)


def substitute_decrypt(ciphertext: str, key: str) -> str:
    """Decrypt ``ciphertext`` with the inverse mapping of ``key``.

    Characters outside the assignment alphabet are copied unchanged.

    Args:
        ciphertext: Text to decrypt.
        key: Permutation of ``ALPHABET`` used for encryption.

    Returns:
        Decrypted text.

    Raises:
        ValueError: If ``key`` is not a valid alphabet permutation.
    """
    validate_key(key)
    reverse_mapping = dict(zip(key, ALPHABET, strict=True))
    return "".join(reverse_mapping.get(char, char) for char in ciphertext)
