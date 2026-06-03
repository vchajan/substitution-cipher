import numpy as np

from substitution_cipher import ALPHABET, substitute_encrypt
from substitution_cipher.bigrams import build_reference_matrix_from_text
from substitution_cipher.cryptanalysis import plausibility, prolom_substitute, random_key
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
