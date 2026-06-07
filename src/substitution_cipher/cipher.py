"""Pomocné funkce pro klasickou substituční šifru."""

from __future__ import annotations

import random

from .constants import ALPHABET


def validate_key(key: str, alphabet: str = ALPHABET) -> None:
    """Ověří, že klíč je permutací celé abecedy."""
    if not isinstance(key, str):
        raise ValueError("Klíč musí být řetězec.")

    if len(key) != len(alphabet):
        raise ValueError("Klíč musí mít stejnou délku jako abeceda.")

    if len(set(key)) != len(key):
        raise ValueError("Klíč nesmí obsahovat opakované znaky.")

    if set(key) != set(alphabet):
        raise ValueError("Klíč musí obsahovat přesně znaky abecedy.")


def random_key(seed: int | None = None) -> str:
    """Vytvoří náhodnou permutaci projektové abecedy."""
    rng = random.Random(seed)
    chars = list(ALPHABET)
    rng.shuffle(chars)
    return "".join(chars)


def substitute_encrypt(plaintext: str, key: str) -> str:
    """Zašifruje text zadaným substitučním klíčem."""
    validate_key(key)
    mapping = dict(zip(ALPHABET, key, strict=True))
    return "".join(mapping.get(char, char) for char in plaintext)


def substitute_decrypt(ciphertext: str, key: str) -> str:
    """Dešifruje text inverzním mapováním zadaného klíče."""
    validate_key(key)
    reverse_mapping = dict(zip(key, ALPHABET, strict=True))
    return "".join(reverse_mapping.get(char, char) for char in ciphertext)
