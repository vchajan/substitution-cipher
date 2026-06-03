from subcipher.bigrams import get_bigrams, to_relative_matrix, transition_matrix


def test_get_bigrams():
    assert get_bigrams("KRYPT") == ["KR", "RY", "YP", "PT"]


def test_transition_matrix_has_smoothing_and_shape():
    matrix = transition_matrix(["AB", "AB", "BC"])
    assert matrix.shape == (27, 27)
    assert matrix.loc["A", "B"] == 2
    assert matrix.loc["A", "A"] == 1


def test_relative_matrix_sums_to_one():
    matrix = transition_matrix(["AB", "BC"])
    relative = to_relative_matrix(matrix)
    assert abs(float(relative.to_numpy().sum()) - 1.0) < 1e-12
