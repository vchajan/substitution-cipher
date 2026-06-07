"""Veřejné API projektu substituční šifry."""

from .api import CrackResult, SubstitutionCipher
from .batch import FileCrackSummary, crack_directory, crack_files
from .bigrams import (
    absolute_bigram_matrix,
    build_reference_matrix_from_text,
    get_bigrams,
    transition_matrix,
)
from .cipher import random_key, substitute_decrypt, substitute_encrypt, validate_key
from .constants import ALPHABET
from .cryptanalysis import plausibility, polish_key, prolom_substitute
from .io_utils import export_result
from .preprocessing import clean_text, validate_clean_text

__all__ = [
    "ALPHABET",
    "CrackResult",
    "FileCrackSummary",
    "SubstitutionCipher",
    "crack_directory",
    "crack_files",
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
    "validate_clean_text",
]
