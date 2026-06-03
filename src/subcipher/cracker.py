"""Cryptanalysis based on a bigram language model."""

from __future__ import annotations

import math
import random

import pandas as pd

from .alphabet import ALPHABET, random_key
from .bigrams import get_bigrams, transition_matrix
from .cipher import substitute_decrypt, validate_key


def plausibility(text: str, TM_ref: pd.DataFrame) -> float:
    """Return log-plausibility of text according to a reference bigram matrix."""
    bigrams_obs = get_bigrams(text)
    TM_obs = transition_matrix(bigrams_obs)

    score = 0.0
    for first in ALPHABET:
        for second in ALPHABET:
            probability = float(TM_ref.loc[first, second])
            count = float(TM_obs.loc[first, second])
            score += math.log(probability) * count
    return score


def _swap_two_random_positions(key: str, rng: random.Random) -> str:
    chars = list(key)
    i, j = rng.sample(range(len(chars)), 2)
    chars[i], chars[j] = chars[j], chars[i]
    return "".join(chars)


def prolom_substitute(text: str, TM_ref: pd.DataFrame, iter: int, start_key: str | None = None):
    """Break a substitution cipher using a Metropolis-Hastings style search.

    Public function name and argument order follow the assignment.

    Returns:
        tuple: `(best_key, best_decrypted_text, best_score)`
    """
    if iter <= 0:
        raise ValueError("iter must be a positive integer.")

    rng = random.Random()
    current_key = start_key if start_key is not None else random_key()
    validate_key(current_key)

    decrypted_current = substitute_decrypt(text, current_key)
    current_score = plausibility(decrypted_current, TM_ref)

    best_key = current_key
    best_text = decrypted_current
    best_score = current_score

    for _ in range(iter):
        candidate_key = _swap_two_random_positions(current_key, rng)
        decrypted_candidate = substitute_decrypt(text, candidate_key)
        candidate_score = plausibility(decrypted_candidate, TM_ref)

        score_delta = candidate_score - current_score
        accept = score_delta >= 0 or rng.random() < min(1.0, math.exp(score_delta))

        if accept:
            current_key = candidate_key
            current_score = candidate_score
            decrypted_current = decrypted_candidate

        if current_score > best_score:
            best_key = current_key
            best_text = decrypted_current
            best_score = current_score

    return best_key, best_text, best_score
