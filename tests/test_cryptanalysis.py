import numpy as np

from substitution_cipher import ALPHABET, substitute_decrypt, substitute_encrypt
from substitution_cipher.bigrams import build_reference_matrix_from_text
from substitution_cipher.cryptanalysis import (
    plausibility,
    polish_key,
    prolom_substitute,
    random_key,
)
from substitution_cipher.cipher import validate_key


def test_random_key_is_valid_permutation():
    key = random_key(seed=123)

    assert len(key) == len(ALPHABET)
    assert set(key) == set(ALPHABET)
    assert len(set(key)) == len(ALPHABET)
    validate_key(key)


def test_plausibility_returns_float_for_regular_and_short_text():
    TM_ref = build_reference_matrix_from_text("AHOJ_SVETE_AHOJ_SVETE")

    regular_score = plausibility("AHOJ_SVETE", TM_ref)
    short_score = plausibility("A", TM_ref)

    assert isinstance(regular_score, float)
    assert isinstance(short_score, float)


def test_plausibility_prefers_reference_like_text():
    TM_ref = build_reference_matrix_from_text("AHOJ_SVETE_AHOJ_SVETE_AHOJ_SVETE")

    czech_like = plausibility("AHOJ_SVETE_AHOJ", TM_ref)
    random_like = plausibility("QZX_QZX_QZX_QZX", TM_ref)

    assert czech_like > random_like


def test_plausibility_rejects_zero_reference_values():
    TM_ref = np.ones((27, 27), dtype=float)
    TM_ref[0, 0] = 0.0

    try:
        plausibility("AA", TM_ref)
    except ValueError as error:
        assert "zero" in str(error) or "non-positive" in str(error)
    else:
        raise AssertionError("plausibility should reject zero probabilities")


def test_prolom_substitute_runs_and_is_reproducible_with_seed():
    key = ALPHABET[3:] + ALPHABET[:3]
    plaintext = "AHOJ_SVETE_AHOJ_SVETE"
    ciphertext = substitute_encrypt(plaintext, key)
    TM_ref = build_reference_matrix_from_text(plaintext * 3)

    result_1 = prolom_substitute(
        ciphertext,
        TM_ref,
        iter=10,
        seed=7,
        progress_every=0,
    )
    result_2 = prolom_substitute(
        ciphertext,
        TM_ref,
        iter=10,
        seed=7,
        progress_every=0,
    )

    best_key, best_text, best_score = result_1
    validate_key(best_key)
    assert len(best_text) == len(ciphertext)
    assert isinstance(best_score, float)
    assert result_1 == result_2


def test_polish_key_returns_valid_key():
    key = ALPHABET[3:] + ALPHABET[:3]
    plaintext = "AHOJ_SVETE_AHOJ_SVETE"
    ciphertext = substitute_encrypt(plaintext, key)
    TM_ref = build_reference_matrix_from_text(plaintext * 3)

    polished_key, _polished_text, _polished_score = polish_key(
        ciphertext,
        random_key(seed=11),
        TM_ref,
    )

    validate_key(polished_key)


def test_polish_key_returns_plaintext_with_ciphertext_length():
    key = ALPHABET[5:] + ALPHABET[:5]
    plaintext = "SUBSTITUCNI_SIFRA"
    ciphertext = substitute_encrypt(plaintext, key)
    TM_ref = build_reference_matrix_from_text(plaintext * 3)

    _polished_key, polished_text, _polished_score = polish_key(
        ciphertext,
        random_key(seed=13),
        TM_ref,
    )

    assert len(polished_text) == len(ciphertext)


def test_polish_key_never_worsens_score():
    key = ALPHABET[7:] + ALPHABET[:7]
    plaintext = "AHOJ_SVETE_AHOJ_SVETE"
    ciphertext = substitute_encrypt(plaintext, key)
    TM_ref = build_reference_matrix_from_text(plaintext * 3)
    start_key = random_key(seed=17)
    start_text = substitute_decrypt(ciphertext, start_key)
    start_score = plausibility(start_text, TM_ref)

    _polished_key, _polished_text, polished_score = polish_key(
        ciphertext,
        start_key,
        TM_ref,
    )

    assert polished_score >= start_score


def test_prolom_substitute_with_polish_returns_expected_types():
    key = ALPHABET[3:] + ALPHABET[:3]
    plaintext = "AHOJ_SVETE_AHOJ_SVETE"
    ciphertext = substitute_encrypt(plaintext, key)
    TM_ref = build_reference_matrix_from_text(plaintext * 3)

    best_key, best_text, best_score = prolom_substitute(
        ciphertext,
        TM_ref,
        iter=3,
        seed=19,
        progress_every=0,
        polish=True,
    )

    validate_key(best_key)
    assert isinstance(best_key, str)
    assert isinstance(best_text, str)
    assert isinstance(best_score, float)
