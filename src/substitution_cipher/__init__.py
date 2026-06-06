"""Public API for the substitution cipher project."""

from .api import CrackResult, SubstitutionCipher
from .bigrams import (
    absolute_bigram_matrix,
    build_reference_matrix_from_text,
    get_bigrams,
    transition_matrix,
)
from .cipher import substitute_decrypt, substitute_encrypt, validate_key
from .config import ALPHABET
from .cryptanalysis import plausibility, polish_key, prolom_substitute, random_key
from .export_utils import export_result
from .preprocess import clean_text

__all__ = [
    "ALPHABET",
    "CrackResult",
    "SubstitutionCipher",
    "substitute_encrypt",
    "substitute_decrypt",
    "validate_key",
    "get_bigrams",
    "absolute_bigram_matrix",
    "transition_matrix",
    "build_reference_matrix_from_text",
    "plausibility",
    "polish_key",
    "prolom_substitute",
    "random_key",
    "export_result",
    "clean_text",
]
