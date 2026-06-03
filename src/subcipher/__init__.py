"""Substitution cipher library."""

from .alphabet import ALPHABET, caesar_key, random_key
from .bigrams import get_bigrams, load_matrix, save_matrix, to_relative_matrix, transition_matrix
from .cipher import substitute_decrypt, substitute_encrypt, validate_key
from .cracker import plausibility, prolom_substitute
from .preprocess import normalize_text

__all__ = [
    "ALPHABET",
    "caesar_key",
    "random_key",
    "validate_key",
    "substitute_encrypt",
    "substitute_decrypt",
    "normalize_text",
    "get_bigrams",
    "transition_matrix",
    "to_relative_matrix",
    "save_matrix",
    "load_matrix",
    "plausibility",
    "prolom_substitute",
]
