"""Dávkové zpracování ciphertext souborů."""

from __future__ import annotations

import contextlib
import io
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from .api import SubstitutionCipher
from .io_utils import parse_ciphertext_filename


@dataclass(frozen=True)
class FileCrackSummary:
    """Stručný výsledek zpracování jednoho ciphertext souboru."""

    input_path: Path
    plaintext_path: Path | None
    key_path: Path | None
    score: float | None
    success: bool
    error: str | None = None


@dataclass(frozen=True)
class FileCrackTask:
    """Vstupní parametry pro jeden worker proces."""

    input_path: Path
    matrix_path: Path
    output_directory: Path
    iterations: int
    restarts: int
    seed: int | None
    polish: bool
    quiet: bool


def find_ciphertext_files(input_directory: str | Path) -> list[Path]:
    """Vrátí ciphertext soubory seřazené deterministicky podle délky a ID."""
    directory = Path(input_directory)
    if not directory.exists():
        return []

    return sorted(
        directory.glob("text_*_sample_*_ciphertext.txt"),
        key=parse_ciphertext_filename,
    )


def resolve_worker_count(workers: int, file_count: int | None = None) -> int:
    """Převede hodnotu CLI argumentu ``--workers`` na skutečný počet procesů."""
    if workers < 0:
        raise ValueError("workers nesmí být záporné číslo.")

    if workers == 0:
        requested = min(6, max(1, (os.cpu_count() or 1) - 1))
    else:
        requested = workers

    if file_count is not None and file_count > 0:
        return min(requested, file_count)
    return requested


def derive_file_seed(base_seed: int | None, file_index: int) -> int | None:
    """Odvodí stabilní seed pro soubor podle jeho pořadí."""
    if base_seed is None:
        return None
    # Nepoužíváme hash(), protože jeho výsledek nemusí být stabilní mezi běhy Pythonu.
    return base_seed + file_index


def expected_output_paths(input_path: str | Path, output_directory: str | Path) -> tuple[Path, Path]:
    """Vrátí očekávané cesty plaintext/key výstupů pro daný ciphertext."""
    text_length, sample_id = parse_ciphertext_filename(input_path)
    output_dir = Path(output_directory)
    return (
        output_dir / f"text_{text_length}_sample_{sample_id}_plaintext.txt",
        output_dir / f"text_{text_length}_sample_{sample_id}_key.txt",
    )


def build_file_tasks(
    files: list[Path],
    matrix_path: str | Path,
    output_directory: str | Path,
    iterations: int,
    restarts: int,
    seed: int | None,
    polish: bool,
    quiet: bool,
) -> list[FileCrackTask]:
    """Sestaví úlohy pro dávkové zpracování souborů."""
    matrix = Path(matrix_path)
    output_dir = Path(output_directory)

    return [
        FileCrackTask(
            input_path=Path(path),
            matrix_path=matrix,
            output_directory=output_dir,
            iterations=iterations,
            restarts=restarts,
            seed=derive_file_seed(seed, index),
            polish=polish,
            quiet=quiet,
        )
        for index, path in enumerate(files)
    ]


def _validate_unique_output_paths(tasks: list[FileCrackTask]) -> None:
    """Ověří, že dvě úlohy nezapisují do stejných výstupních souborů."""
    seen: set[Path] = set()
    for task in tasks:
        for path in expected_output_paths(task.input_path, task.output_directory):
            if path in seen:
                raise ValueError(f"Více ciphertextů by zapisovalo do stejného souboru: {path}")
            seen.add(path)


def _crack_file_worker(task: FileCrackTask) -> FileCrackSummary:
    """Zpracuje jeden ciphertext soubor; funkce musí být serializovatelná pro Windows."""
    plaintext_path, key_path = expected_output_paths(task.input_path, task.output_directory)
    try:
        cipher = SubstitutionCipher.from_matrix_file(task.matrix_path)
        if task.quiet:
            with contextlib.redirect_stdout(io.StringIO()):
                result = cipher.crack_file(
                    input_path=task.input_path,
                    output_directory=task.output_directory,
                    iterations=task.iterations,
                    restarts=task.restarts,
                    seed=task.seed,
                    polish=task.polish,
                    progress_every=0,
                )
        else:
            result = cipher.crack_file(
                input_path=task.input_path,
                output_directory=task.output_directory,
                iterations=task.iterations,
                restarts=task.restarts,
                seed=task.seed,
                polish=task.polish,
            )
        return FileCrackSummary(
            input_path=task.input_path,
            plaintext_path=plaintext_path,
            key_path=key_path,
            score=result.score,
            success=True,
        )
    except Exception as exc:  # noqa: BLE001 - chyba jednoho souboru nesmí zastavit dávku.
        # Worker chybu vrátí hlavnímu procesu; ostatní soubory tak mohou doběhnout.
        return FileCrackSummary(
            input_path=task.input_path,
            plaintext_path=plaintext_path,
            key_path=key_path,
            score=None,
            success=False,
            error=f"{type(exc).__name__}: {exc}",
        )


def _print_progress(done: int, total: int, summary: FileCrackSummary) -> None:
    status = "Hotovo" if summary.success else "Chyba"
    print(f"[{done}/{total}] {status}: {summary.input_path.name}")


def crack_files(
    files: list[Path],
    matrix_path: str | Path,
    output_directory: str | Path,
    iterations: int,
    restarts: int = 1,
    seed: int | None = None,
    polish: bool = True,
    workers: int = 1,
    show_progress: bool = True,
) -> list[FileCrackSummary]:
    """Zpracuje seznam ciphertextů sekvenčně nebo paralelně po celých souborech."""
    if not files:
        return []

    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Paralelizujeme celé soubory, protože M-H iterace uvnitř jednoho běhu na sebe navazují.
    worker_count = resolve_worker_count(workers, file_count=len(files))
    quiet = worker_count > 1
    tasks = build_file_tasks(
        files=files,
        matrix_path=matrix_path,
        output_directory=output_dir,
        iterations=iterations,
        restarts=restarts,
        seed=seed,
        polish=polish,
        quiet=quiet,
    )
    _validate_unique_output_paths(tasks)

    ordered_results: list[FileCrackSummary | None] = [None] * len(tasks)

    if worker_count == 1:
        for index, task in enumerate(tasks):
            summary = _crack_file_worker(task)
            ordered_results[index] = summary
            if show_progress:
                _print_progress(index + 1, len(tasks), summary)
    else:
        with ProcessPoolExecutor(max_workers=worker_count) as executor:
            futures = {
                executor.submit(_crack_file_worker, task): index
                for index, task in enumerate(tasks)
            }
            for done, future in enumerate(as_completed(futures), start=1):
                index = futures[future]
                try:
                    summary = future.result()
                except Exception as exc:  # noqa: BLE001 - ostatní future musí doběhnout.
                    task = tasks[index]
                    plaintext_path, key_path = expected_output_paths(
                        task.input_path,
                        task.output_directory,
                    )
                    summary = FileCrackSummary(
                        input_path=task.input_path,
                        plaintext_path=plaintext_path,
                        key_path=key_path,
                        score=None,
                        success=False,
                        error=f"{type(exc).__name__}: {exc}",
                    )
                ordered_results[index] = summary
                if show_progress:
                    _print_progress(done, len(tasks), summary)

    return [summary for summary in ordered_results if summary is not None]


def crack_directory(
    input_directory: str | Path,
    matrix_path: str | Path,
    output_directory: str | Path,
    iterations: int,
    restarts: int = 1,
    seed: int | None = None,
    polish: bool = True,
    workers: int = 1,
    show_progress: bool = True,
) -> list[FileCrackSummary]:
    """Najde a zpracuje všechny ciphertext soubory ve složce."""
    files = find_ciphertext_files(input_directory)
    return crack_files(
        files=files,
        matrix_path=matrix_path,
        output_directory=output_directory,
        iterations=iterations,
        restarts=restarts,
        seed=seed,
        polish=polish,
        workers=workers,
        show_progress=show_progress,
    )
