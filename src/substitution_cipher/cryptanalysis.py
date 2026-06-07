"""Kryptoanalýza substituční šifry pomocí Metropolis-Hastingsova algoritmu."""

from __future__ import annotations

import random

import numpy as np

from .bigrams import absolute_bigram_matrix, get_bigrams
from .cipher import random_key, substitute_decrypt, validate_key
from .constants import ALPHABET


def _validate_reference_matrix(TM_ref: np.ndarray) -> np.ndarray:
    """Ověří základní vlastnosti referenční matice."""
    reference = np.asarray(TM_ref, dtype=float)
    expected_shape = (len(ALPHABET), len(ALPHABET))

    if reference.shape != expected_shape:
        raise ValueError(f"TM_ref musí mít shape {expected_shape}.")

    if not np.all(np.isfinite(reference)):
        raise ValueError("TM_ref smí obsahovat jen konečné hodnoty.")

    if np.any(reference <= 0.0):
        raise ValueError("TM_ref nesmí obsahovat nuly ani záporné hodnoty.")

    return reference


def plausibility(text: str, TM_ref: np.ndarray) -> float:
    """Ohodnotí text podle referenčních četností bigramů."""
    reference = _validate_reference_matrix(TM_ref)
    observed = absolute_bigram_matrix(get_bigrams(text))
    return float(np.sum(np.log(reference) * observed))


def _swap_two_random_characters(key: str, rng: random.Random) -> str:
    """Vrátí klíč s prohozenými dvěma náhodnými pozicemi."""
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
    """Doladí nalezený klíč systematickým zkoušením všech dvojic znaků."""
    if max_passes < 0:
        raise ValueError("max_passes nesmí být záporné.")

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
    """Spustí jeden běh hledání klíče."""
    if iterations < 0:
        raise ValueError("iterations nesmí být záporné.")

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
                f"Iterace {iteration} "
                f"aktuální log plausibility: {current_score} "
                f"nejlepší log plausibility: {best_score}"
            )

    return best_key, best_text, best_score


def prolom_substitute(
    text: str,
    TM_ref: np.ndarray,
    iter: int,
    start_key: str | None = None,
) -> tuple[str, str, float]:
    """Prolomí substituční šifru jedním během Metropolis-Hastingsova algoritmu."""
    if iter < 0:
        raise ValueError("iter nesmí být záporné.")

    return _run_metropolis_hastings(
        text=text,
        TM_ref=TM_ref,
        iterations=iter,
        rng=random.Random(),
        start_key=start_key,
        progress_every=50,
    )
