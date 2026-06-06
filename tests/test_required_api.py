import inspect

from substitution_cipher import (
    SubstitutionCipher,
    get_bigrams,
    plausibility,
    prolom_substitute,
    substitute_decrypt,
    substitute_encrypt,
    transition_matrix,
)


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


def test_object_api_method_signatures_are_stable():
    assert _parameter_names(SubstitutionCipher.encrypt) == ["self", "plaintext", "key"]
    assert _parameter_names(SubstitutionCipher.decrypt) == ["self", "ciphertext", "key"]
    assert _parameter_names(SubstitutionCipher.bigrams) == ["self", "text"]
    assert _parameter_names(SubstitutionCipher.build_reference_matrix) == ["self", "text"]
    assert _parameter_names(SubstitutionCipher.score) == ["self", "text"]
    assert _parameter_names(SubstitutionCipher.crack) == [
        "self",
        "ciphertext",
        "iterations",
        "start_key",
        "restarts",
        "seed",
        "polish",
        "progress_every",
    ]
    assert _parameter_names(SubstitutionCipher.crack_file) == [
        "self",
        "input_path",
        "output_directory",
        "iterations",
        "restarts",
        "seed",
        "polish",
    ]
    assert _parameter_names(SubstitutionCipher.crack_directory) == [
        "self",
        "input_directory",
        "output_directory",
        "iterations",
        "restarts",
        "seed",
        "polish",
    ]
