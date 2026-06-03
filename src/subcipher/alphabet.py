"""Alphabet and key helpers."""

from __future__ import annotations

import random

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ_"


def caesar_key(shift: int) -> str:
    """Return a Caesar-style permutation key for the project alphabet."""
    shift = shift % len(ALPHABET)
    return ALPHABET[shift:] + ALPHABET[:shift]


def random_key(seed: int | None = None) -> str:
    """Return a random permutation of the project alphabet."""
    rng = random.Random(seed)
    chars = list(ALPHABET)
    rng.shuffle(chars)
    return "".join(chars)
