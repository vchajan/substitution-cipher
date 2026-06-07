"""Objektové rozhraní nad povinnými funkcemi zadání."""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .bigrams import get_bigrams, transition_matrix
from .cipher import substitute_decrypt, substitute_encrypt, validate_key
from .constants import ALPHABET
from .cryptanalysis import (
    _run_metropolis_hastings,
    _validate_reference_matrix,
    plausibility,
    polish_key,
)
from .io_utils import export_result, load_matrix, parse_ciphertext_filename, save_matrix


@dataclass(frozen=True)
class CrackResult:
    """Výsledek jednoho pokusu o prolomení ciphertextu."""

    key: str
    plaintext: str
    score: float
    restart: int
    iterations: int


def _validate_alphabet_text(text: str, label: str) -> None:
    """Vyvolá chybu, pokud text obsahuje znaky mimo projektovou abecedu."""
    invalid = sorted(set(text) - set(ALPHABET))
    if invalid:
        raise ValueError(f"{label} obsahuje nepovolené znaky: {invalid}")


class SubstitutionCipher:
    """Pohodlná fasáda nad povinným funkčním API."""

    def __init__(self, reference_matrix: np.ndarray | None = None) -> None:
        """Vytvoří objekt s volitelně načtenou referenční maticí."""
        self.reference_matrix = (
            None
            if reference_matrix is None
            else _validate_reference_matrix(reference_matrix)
        )

    def encrypt(self, plaintext: str, key: str) -> str:
        """Zašifruje plaintext zadaným klíčem."""
        return substitute_encrypt(plaintext, key)

    def decrypt(self, ciphertext: str, key: str) -> str:
        """Dešifruje ciphertext zadaným klíčem."""
        return substitute_decrypt(ciphertext, key)

    def bigrams(self, text: str) -> list[str]:
        """Vrátí sousední bigramy z textu."""
        return get_bigrams(text)

    def build_reference_matrix(self, text: str) -> np.ndarray:
        """Vytvoří a uloží relativní referenční matici z čistého textu."""
        _validate_alphabet_text(text, "Reference text")
        absolute = transition_matrix(get_bigrams(text))
        total = float(absolute.sum())
        if total <= 0.0:
            raise ValueError("Nelze normalizovat matici s nulovým součtem.")
        self.reference_matrix = absolute / total
        return self.reference_matrix

    @classmethod
    def from_matrix_file(cls, path: str | Path) -> "SubstitutionCipher":
        """Vytvoří objekt z uložené NumPy matice."""
        return cls(load_matrix(path))

    def save_reference_matrix(self, path: str | Path) -> None:
        """Uloží aktuálně načtenou referenční matici."""
        if self.reference_matrix is None:
            raise ValueError("Referenční matice není načtená.")
        save_matrix(self.reference_matrix, path)

    def score(self, text: str) -> float:
        """Spočítá věrohodnost textu podle načtené matice."""
        if self.reference_matrix is None:
            raise ValueError("Referenční matice není načtená.")
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
        """Prolomí jeden ciphertext, volitelně s více restarty."""
        if self.reference_matrix is None:
            raise ValueError("Referenční matice není načtená.")
        if iterations < 1:
            raise ValueError("iterations musí být alespoň 1.")
        if restarts < 1:
            raise ValueError("restarts musí být alespoň 1.")

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
                f"nejlepší plausibility: {score}"
            )

            if best_result is None or result.score > best_result.score:
                best_result = result

        assert best_result is not None
        print(
            f"Celkově nejlepší restart: {best_result.restart}, "
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
        progress_every: int = 50,
    ) -> CrackResult:
        """Prolomí jeden soubor zadání a uloží plaintext i klíč."""
        path = Path(input_path)
        text_length, sample_id = parse_ciphertext_filename(path)
        ciphertext = path.read_text(encoding="utf-8").strip()
        _validate_alphabet_text(ciphertext, "Ciphertext")

        result = self.crack(
            ciphertext,
            iterations=iterations,
            restarts=restarts,
            seed=seed,
            polish=polish,
            progress_every=progress_every,
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
        """Prolomí všechny ciphertext soubory ve složce."""
        directory = Path(input_directory)
        if not directory.exists():
            print(f"Ve složce nejsou ciphertext soubory: {directory}")
            return []

        txt_files = sorted(directory.glob("*.txt"))
        files: list[Path] = []
        for path in txt_files:
            parse_ciphertext_filename(path)
            files.append(path)

        files = sorted(files, key=parse_ciphertext_filename)
        if not files:
            print(f"Ve složce nejsou ciphertext soubory: {directory}")
            return []

        results: list[CrackResult] = []
        for index, path in enumerate(files):
            file_seed = None if seed is None else seed + index * max(1, restarts)
            print(f"Dešifruji {path.name}")
            result = self.crack_file(
                input_path=path,
                output_directory=output_directory,
                iterations=iterations,
                restarts=restarts,
                seed=file_seed,
                polish=polish,
            )
            results.append(result)
            print(f"Výstupy uloženy pro {path.name}")

        return results
