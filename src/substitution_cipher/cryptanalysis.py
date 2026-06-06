"""Metropolis-Hastings cryptanalysis for a substitution cipher."""

from __future__ import annotations

import random

import numpy as np

from .bigrams import absolute_bigram_matrix, get_bigrams
from .cipher import substitute_decrypt, validate_key
from .config import ALPHABET


def random_key(seed: int | None = None) -> str:
    """Return a random permutation of the assignment alphabet.

    Args:
        seed: Optional seed for reproducible key generation.

    Returns:
        A string containing each alphabet character exactly once.
    """
    rng = random.Random(seed)
    chars = list(ALPHABET)
    rng.shuffle(chars)
    return "".join(chars)


def _validate_reference_matrix(TM_ref: np.ndarray) -> np.ndarray:
    """Return ``TM_ref`` as an array after validating its basic properties."""
    reference = np.asarray(TM_ref, dtype=float)
    expected_shape = (len(ALPHABET), len(ALPHABET))

    if reference.shape != expected_shape:
        raise ValueError(f"TM_ref must have shape {expected_shape}.")

    if not np.all(np.isfinite(reference)):
        raise ValueError("TM_ref must contain only finite values.")

    if np.any(reference <= 0.0):
        raise ValueError("TM_ref must not contain zero or negative values.")

    return reference


def plausibility(text: str, TM_ref: np.ndarray) -> float:
    """Compute log-likelihood of ``text`` under a reference bigram matrix.

    ``TM_ref`` must be a relative transition matrix without zero values.
    Observed bigrams are counted as absolute frequencies and evaluated as::

        sum(log(TM_ref[i, j]) * TM_obs[i, j])

    Args:
        text: Candidate plaintext.
        TM_ref: Smoothed relative reference bigram matrix.

    Returns:
        Log-likelihood score as a float.

    Raises:
        ValueError: If ``TM_ref`` has a wrong shape or contains non-positive
            values.
    """
    reference = _validate_reference_matrix(TM_ref)
    observed = absolute_bigram_matrix(get_bigrams(text))
    return float(np.sum(np.log(reference) * observed))


def _swap_two_random_characters(key: str, rng: random.Random) -> str:
    """Return a copy of ``key`` with two random positions swapped."""
    chars = list(key)
    first, second = rng.sample(range(len(chars)), 2)
    chars[first], chars[second] = chars[second], chars[first]
    return "".join(chars)


def polish_key(
    ciphertext: str,
    key: str,
    TM_ref: np.ndarray,
    max_passes: int = 5,
) -> tuple[str, str, float]:
    """Improve a substitution key by systematic local pair swaps.

    The function starts from an already found key and repeatedly tries every
    possible swap of two key positions. If at least one swap improves the
    plaintext plausibility, the best improving swap is accepted. The process
    stops after ``max_passes`` passes or when no swap improves the score.

    Args:
        ciphertext: Ciphertext to decrypt.
        key: Initial substitution key.
        TM_ref: Smoothed relative reference bigram matrix.
        max_passes: Maximum number of full pair-swap passes.

    Returns:
        Tuple ``(best_key, best_decrypted_text, best_score)``.

    Raises:
        ValueError: If ``key`` is invalid, ``max_passes`` is negative, or
            ``TM_ref`` is not a valid reference matrix.
    """
    if max_passes < 0:
        raise ValueError("max_passes must be non-negative.")

    validate_key(key)
    _validate_reference_matrix(TM_ref)

    best_key = key
    best_text = substitute_decrypt(ciphertext, best_key)
    best_score = plausibility(best_text, TM_ref)

    for _ in range(max_passes):
        pass_best_key = best_key
        pass_best_text = best_text
        pass_best_score = best_score

        for first in range(len(ALPHABET) - 1):
            for second in range(first + 1, len(ALPHABET)):
                candidate_chars = list(best_key)
                candidate_chars[first], candidate_chars[second] = (
                    candidate_chars[second],
                    candidate_chars[first],
                )
                candidate_key = "".join(candidate_chars)
                candidate_text = substitute_decrypt(ciphertext, candidate_key)
                candidate_score = plausibility(candidate_text, TM_ref)

                if candidate_score > pass_best_score:
                    pass_best_key = candidate_key
                    pass_best_text = candidate_text
                    pass_best_score = candidate_score

        if pass_best_score <= best_score:
            break

        best_key = pass_best_key
        best_text = pass_best_text
        best_score = pass_best_score

    return best_key, best_text, best_score


def _run_metropolis_hastings(
    text: str,
    TM_ref: np.ndarray,
    iterations: int,
    rng: random.Random,
    start_key: str | None = None,
    progress_every: int = 50,
) -> tuple[str, str, float]:
    """Run one Metropolis-Hastings key search."""
    if iterations < 0:
        raise ValueError("iterations must be non-negative.")

    _validate_reference_matrix(TM_ref)

    if start_key is None:
        current_chars = list(ALPHABET)
        rng.shuffle(current_chars)
        current_key = "".join(current_chars)
    else:
        current_key = start_key

    validate_key(current_key)

    current_text = substitute_decrypt(text, current_key)
    current_score = plausibility(current_text, TM_ref)

    best_key = current_key
    best_text = current_text
    best_score = current_score

    for iteration in range(1, iterations + 1):
        candidate_key = _swap_two_random_characters(current_key, rng)
        candidate_text = substitute_decrypt(text, candidate_key)
        candidate_score = plausibility(candidate_text, TM_ref)

        if candidate_score > current_score or rng.random() < 0.01:
            current_key = candidate_key
            current_text = candidate_text
            current_score = candidate_score

        if current_score > best_score:
            best_key = current_key
            best_text = current_text
            best_score = current_score

        if progress_every > 0 and iteration % progress_every == 0:
            print(
                f"Iteration {iteration} "
                f"current log plausibility: {current_score} "
                f"best log plausibility: {best_score}"
            )

    return best_key, best_text, best_score


def prolom_substitute(
    text: str,
    TM_ref: np.ndarray,
    iter: int,
    start_key: str | None = None,
) -> tuple[str, str, float]:
    """Break a substitution cipher with one Metropolis-Hastings run.

    A candidate key is generated by swapping two random characters in the
    current key. Better candidates are accepted automatically. Worse
    candidates are accepted with probability ``0.01``, matching the assignment
    pseudocode. The function returns the best key and plaintext seen during
    the whole run, not merely the last accepted state.

    Args:
        text: Ciphertext to decrypt.
        TM_ref: Smoothed relative reference bigram matrix.
        iter: Number of Metropolis-Hastings iterations.
        start_key: Optional starting key. If omitted, a random key is used.

    Returns:
        Tuple ``(best_key, best_decrypted_text, best_score)``.

    Raises:
        ValueError: If ``iter`` is negative, ``start_key`` is invalid, or
            ``TM_ref`` is not a valid reference matrix.
    """
    if iter < 0:
        raise ValueError("iter must be non-negative.")

    return _run_metropolis_hastings(
        text=text,
        TM_ref=TM_ref,
        iterations=iter,
        rng=random.Random(),
        start_key=start_key,
        progress_every=50,
    )
