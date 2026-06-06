"""Object-oriented convenience API for the substitution cipher project."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .bigrams import get_bigrams, load_matrix, save_matrix, transition_matrix
from .cipher import substitute_decrypt, substitute_encrypt, validate_key
from .config import ALPHABET
from .cryptanalysis import (
    _run_metropolis_hastings,
    _validate_reference_matrix,
    plausibility,
    polish_key,
)
from .export_utils import export_result


_CIPHERTEXT_PATTERN = re.compile(
    r"^text_(?P<length>\d+)_sample_(?P<sample_id>\d+)_ciphertext\.txt$"
)


@dataclass(frozen=True)
class CrackResult:
    """Result of one ciphertext cracking run."""

    key: str
    plaintext: str
    score: float
    restart: int
    iterations: int


def _validate_alphabet_text(text: str, label: str) -> None:
    """Raise ``ValueError`` if ``text`` contains characters outside ``ALPHABET``."""
    invalid = sorted(set(text) - set(ALPHABET))
    if invalid:
        raise ValueError(f"{label} contains invalid characters: {invalid}")


def _parse_ciphertext_filename(path: str | Path) -> tuple[int, int]:
    """Parse text length and sample id from an assignment ciphertext filename."""
    match = _CIPHERTEXT_PATTERN.match(Path(path).name)
    if not match:
        raise ValueError(
            "Ciphertext filename must match "
            "text_{length}_sample_{id}_ciphertext.txt"
        )
    return int(match.group("length")), int(match.group("sample_id"))


class SubstitutionCipher:
    """Convenience wrapper around the assignment functions and matrix files."""

    def __init__(self, reference_matrix: np.ndarray | None = None) -> None:
        """Create an API object with an optional reference matrix."""
        self.reference_matrix = (
            None
            if reference_matrix is None
            else _validate_reference_matrix(reference_matrix)
        )

    def encrypt(self, plaintext: str, key: str) -> str:
        """Encrypt ``plaintext`` with ``key``."""
        return substitute_encrypt(plaintext, key)

    def decrypt(self, ciphertext: str, key: str) -> str:
        """Decrypt ``ciphertext`` with ``key``."""
        return substitute_decrypt(ciphertext, key)

    def bigrams(self, text: str) -> list[str]:
        """Return adjacent bigrams from ``text``."""
        return get_bigrams(text)

    def build_reference_matrix(self, text: str) -> np.ndarray:
        """Build and store a smoothed relative reference matrix from clean text."""
        _validate_alphabet_text(text, "Reference text")
        absolute = transition_matrix(get_bigrams(text))
        total = float(absolute.sum())
        if total <= 0.0:
            raise ValueError("Cannot normalize a matrix with zero total count.")
        self.reference_matrix = absolute / total
        return self.reference_matrix

    @classmethod
    def from_matrix_file(cls, path: str | Path) -> "SubstitutionCipher":
        """Create an API object from a saved NumPy reference matrix."""
        return cls(load_matrix(path))

    def save_reference_matrix(self, path: str | Path) -> None:
        """Save the currently loaded reference matrix."""
        if self.reference_matrix is None:
            raise ValueError("Reference matrix is not loaded.")
        save_matrix(self.reference_matrix, path)

    def score(self, text: str) -> float:
        """Return plausibility score for ``text`` using the stored matrix."""
        if self.reference_matrix is None:
            raise ValueError("Reference matrix is not loaded.")
        return plausibility(text, self.reference_matrix)

    def crack(
        self,
        ciphertext: str,
        iterations: int = 20_000,
        start_key: str | None = None,
        restarts: int = 1,
        seed: int | None = None,
        polish: bool = True,
        progress_every: int = 50,
    ) -> CrackResult:
        """Crack one ciphertext, optionally using repeated M-H restarts."""
        if self.reference_matrix is None:
            raise ValueError("Reference matrix is not loaded.")
        if iterations < 1:
            raise ValueError("iterations must be at least 1.")
        if restarts < 1:
            raise ValueError("restarts must be at least 1.")

        _validate_alphabet_text(ciphertext, "Ciphertext")
        if start_key is not None:
            validate_key(start_key)

        best_result: CrackResult | None = None

        for restart_index in range(restarts):
            restart_seed = None if seed is None else seed + restart_index
            rng = random.Random(restart_seed)
            key, plaintext, score = _run_metropolis_hastings(
                text=ciphertext,
                TM_ref=self.reference_matrix,
                iterations=iterations,
                rng=rng,
                start_key=start_key,
                progress_every=progress_every,
            )

            if polish:
                key, plaintext, score = polish_key(ciphertext, key, self.reference_matrix)

            result = CrackResult(
                key=key,
                plaintext=plaintext,
                score=score,
                restart=restart_index + 1,
                iterations=iterations,
            )

            print(
                f"Restart {restart_index + 1}/{restarts} "
                f"best plausibility: {score}"
            )

            if best_result is None or result.score > best_result.score:
                best_result = result

        assert best_result is not None
        print(
            f"Overall best restart: {best_result.restart}, "
            f"plausibility: {best_result.score}"
        )
        return best_result

    def crack_file(
        self,
        input_path: str | Path,
        output_directory: str | Path,
        iterations: int = 20_000,
        restarts: int = 1,
        seed: int | None = None,
        polish: bool = True,
    ) -> CrackResult:
        """Crack one assignment ciphertext file and export plaintext/key files."""
        path = Path(input_path)
        text_length, sample_id = _parse_ciphertext_filename(path)
        ciphertext = path.read_text(encoding="utf-8").strip()
        _validate_alphabet_text(ciphertext, "Ciphertext")

        result = self.crack(
            ciphertext,
            iterations=iterations,
            restarts=restarts,
            seed=seed,
            polish=polish,
        )
        export_result(result.plaintext, result.key, text_length, sample_id, output_directory)
        return result

    def crack_directory(
        self,
        input_directory: str | Path,
        output_directory: str | Path,
        iterations: int = 20_000,
        restarts: int = 1,
        seed: int | None = None,
        polish: bool = True,
    ) -> list[CrackResult]:
        """Crack all assignment ciphertext files in a directory."""
        directory = Path(input_directory)
        if not directory.exists():
            print(f"No ciphertext files found in: {directory}")
            return []

        txt_files = sorted(directory.glob("*.txt"))
        files: list[Path] = []
        for path in txt_files:
            _parse_ciphertext_filename(path)
            files.append(path)

        files = sorted(files, key=_parse_ciphertext_filename)
        if not files:
            print(f"No ciphertext files found in: {directory}")
            return []

        results: list[CrackResult] = []
        for index, path in enumerate(files):
            file_seed = None if seed is None else seed + index * max(1, restarts)
            print(f"Decrypting {path.name}")
            result = self.crack_file(
                input_path=path,
                output_directory=output_directory,
                iterations=iterations,
                restarts=restarts,
                seed=file_seed,
                polish=polish,
            )
            results.append(result)
            print(f"Saved outputs for {path.name}")

        return results


parse_ciphertext_filename = _parse_ciphertext_filename
