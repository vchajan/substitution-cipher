import inspect

import numpy as np

from substitution_cipher import (
    ALPHABET,
    get_bigrams,
    plausibility,
    prolom_substitute,
    substitute_decrypt,
    substitute_encrypt,
    transition_matrix,
)
from substitution_cipher.bigrams import build_reference_matrix_from_text
from substitution_cipher.cipher import validate_key


def _parameter_names(function):
    return list(inspect.signature(function).parameters)


def test_required_function_signatures_match_assignment():
    assert _parameter_names(substitute_encrypt) == ["plaintext", "key"]
    assert _parameter_names(substitute_decrypt) == ["ciphertext", "key"]
    assert _parameter_names(get_bigrams) == ["text"]
    assert _parameter_names(transition_matrix) == ["bigrams"]
    assert _parameter_names(plausibility) == ["text", "TM_ref"]
    assert _parameter_names(prolom_substitute) == ["text", "TM_ref", "iter", "start_key"]
    assert inspect.signature(prolom_substitute).parameters["start_key"].default is None


def test_encrypt_decrypt_roundtrip():
    key = ALPHABET[1:] + ALPHABET[:1]
    plaintext = "AHOJ_SVETE"
    ciphertext = substitute_encrypt(plaintext, key)

    assert ciphertext != plaintext
    assert substitute_decrypt(ciphertext, key) == plaintext


def test_bigram_matrix_and_plausibility():
    bigrams = get_bigrams("ABC")
    matrix = transition_matrix(bigrams)

    assert bigrams == ["AB", "BC"]
    assert matrix.shape == (27, 27)
    assert np.all(matrix > 0)

    reference = build_reference_matrix_from_text("AHOJ_SVETE_AHOJ_SVETE")
    assert isinstance(plausibility("AHOJ_SVETE", reference), float)


def test_prolom_substitute_returns_required_tuple():
    key = ALPHABET[3:] + ALPHABET[:3]
    plaintext = "AHOJ_SVETE_AHOJ_SVETE"
    ciphertext = substitute_encrypt(plaintext, key)
    reference = build_reference_matrix_from_text(plaintext * 3)

    best_key, best_plaintext, score = prolom_substitute(
        ciphertext,
        reference,
        iter=0,
        start_key=ALPHABET,
    )

    validate_key(best_key)
    assert isinstance(best_plaintext, str)
    assert isinstance(score, float)
    assert len(best_plaintext) == len(ciphertext)
