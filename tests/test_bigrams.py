import numpy as np

from substitution_cipher import ALPHABET
from substitution_cipher.bigrams import (
    absolute_bigram_matrix,
    build_reference_matrix_from_text,
    get_bigrams,
    transition_matrix,
)


def test_get_bigrams():
    assert get_bigrams("KRAKATIT") == ["KR", "RA", "AK", "KA", "AT", "TI", "IT"]


def test_transition_matrix_shape_and_counts():
    matrix = transition_matrix(["AB", "AB", "BC"])
    assert matrix.shape == (27, 27)
    assert matrix[0, 1] == 2
    assert matrix[1, 2] == 1
    assert matrix[0, 0] == 1


def test_absolute_bigram_matrix_keeps_zeros():
    matrix = absolute_bigram_matrix(["AB", "AB", "BC"])
    assert matrix.shape == (27, 27)
    assert matrix[0, 1] == 2
    assert matrix[1, 2] == 1
    assert matrix[0, 0] == 0


def test_transition_matrix_smoothing_removes_zeros():
    matrix = transition_matrix(["AB"])
    assert matrix.shape == (len(ALPHABET), len(ALPHABET))
    assert np.all(matrix > 0)


def test_relative_matrix_sums_to_one():
    matrix = build_reference_matrix_from_text("ABC")
    assert np.isclose(matrix.sum(), 1.0)


def test_reference_matrix_from_text_is_relative_and_nonzero():
    matrix = build_reference_matrix_from_text("ABR_KADABRA")
    assert matrix.shape == (27, 27)
    assert np.isclose(matrix.sum(), 1.0)
    assert np.all(matrix > 0)
