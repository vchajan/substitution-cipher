from __future__ import annotations

from concurrent.futures import Future
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

import substitution_cipher.batch as batch_module
from substitution_cipher import ALPHABET
from substitution_cipher.batch import (
    FileCrackSummary,
    build_file_tasks,
    crack_files,
    derive_file_seed,
    expected_output_paths,
    find_ciphertext_files,
    resolve_worker_count,
)


def _matrix_file(path: Path) -> Path:
    matrix = np.ones((len(ALPHABET), len(ALPHABET)), dtype=float)
    matrix /= matrix.sum()
    np.save(path, matrix)
    return path


def _write_ciphertext(directory: Path, length: int, sample_id: int, text: str = "ABC") -> Path:
    path = directory / f"text_{length}_sample_{sample_id}_ciphertext.txt"
    path.write_text(text, encoding="utf-8")
    return path


def _summary_for(task) -> FileCrackSummary:
    plaintext_path, key_path = expected_output_paths(task.input_path, task.output_directory)
    plaintext_path.parent.mkdir(parents=True, exist_ok=True)
    plaintext_path.write_text("ABC", encoding="utf-8")
    key_path.write_text(ALPHABET, encoding="utf-8")
    return FileCrackSummary(
        input_path=task.input_path,
        plaintext_path=plaintext_path,
        key_path=key_path,
        score=-1.0,
        success=True,
    )


def test_workers_one_processes_files_sequentially(monkeypatch):
    calls: list[str] = []

    def fake_worker(task):
        calls.append(task.input_path.name)
        return _summary_for(task)

    def forbidden_executor(*_args, **_kwargs):
        raise AssertionError("ProcessPoolExecutor se nemá použít pro workers=1.")

    monkeypatch.setattr(batch_module, "_crack_file_worker", fake_worker)
    monkeypatch.setattr(batch_module, "ProcessPoolExecutor", forbidden_executor)

    with TemporaryDirectory(prefix="workers_one_", dir="outputs") as directory:
        root = Path(directory)
        input_dir = root / "in"
        output_dir = root / "out"
        input_dir.mkdir()
        files = [
            _write_ciphertext(input_dir, 3, 1),
            _write_ciphertext(input_dir, 3, 2),
        ]

        summaries = crack_files(
            files=files,
            matrix_path=root / "TM_ref.npy",
            output_directory=output_dir,
            iterations=1,
            workers=1,
            show_progress=False,
        )

    assert [summary.success for summary in summaries] == [True, True]
    assert calls == [
        "text_3_sample_1_ciphertext.txt",
        "text_3_sample_2_ciphertext.txt",
    ]


def test_workers_two_uses_parallel_branch(monkeypatch):
    created_executors: list[int] = []

    class FakeExecutor:
        def __init__(self, max_workers):
            created_executors.append(max_workers)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def submit(self, function, task):
            future: Future = Future()
            future.set_result(function(task))
            return future

    monkeypatch.setattr(batch_module, "ProcessPoolExecutor", FakeExecutor)
    monkeypatch.setattr(batch_module, "_crack_file_worker", _summary_for)

    with TemporaryDirectory(prefix="workers_two_", dir="outputs") as directory:
        root = Path(directory)
        input_dir = root / "in"
        output_dir = root / "out"
        input_dir.mkdir()
        files = [
            _write_ciphertext(input_dir, 3, 1),
            _write_ciphertext(input_dir, 3, 2),
        ]

        summaries = crack_files(
            files=files,
            matrix_path=root / "TM_ref.npy",
            output_directory=output_dir,
            iterations=1,
            workers=2,
            show_progress=False,
        )

    assert created_executors == [2]
    assert len(summaries) == 2
    assert all(summary.success for summary in summaries)


def test_output_names_remain_in_assignment_format():
    plaintext_path, key_path = expected_output_paths(
        "text_250_sample_17_ciphertext.txt",
        "outputs",
    )

    assert plaintext_path.name == "text_250_sample_17_plaintext.txt"
    assert key_path.name == "text_250_sample_17_key.txt"


def test_ciphertext_file_order_is_deterministic():
    with TemporaryDirectory(prefix="order_", dir="outputs") as directory:
        root = Path(directory)
        _write_ciphertext(root, 500, 2)
        _write_ciphertext(root, 250, 10)
        _write_ciphertext(root, 250, 1)

        files = find_ciphertext_files(root)

    assert [path.name for path in files] == [
        "text_250_sample_1_ciphertext.txt",
        "text_250_sample_10_ciphertext.txt",
        "text_500_sample_2_ciphertext.txt",
    ]


def test_file_seeds_are_stable():
    assert [derive_file_seed(100, index) for index in range(4)] == [100, 101, 102, 103]
    assert derive_file_seed(None, 7) is None

    files = [Path("text_3_sample_1_ciphertext.txt"), Path("text_3_sample_2_ciphertext.txt")]
    tasks = build_file_tasks(
        files=files,
        matrix_path="models/TM_ref.npy",
        output_directory="outputs",
        iterations=1,
        restarts=1,
        seed=10,
        polish=False,
        quiet=True,
    )
    assert [task.seed for task in tasks] == [10, 11]


def test_one_file_failure_does_not_stop_other_files(monkeypatch):
    def fake_worker(task):
        if "sample_2" in task.input_path.name:
            plaintext_path, key_path = expected_output_paths(task.input_path, task.output_directory)
            return FileCrackSummary(
                input_path=task.input_path,
                plaintext_path=plaintext_path,
                key_path=key_path,
                score=None,
                success=False,
                error="test error",
            )
        return _summary_for(task)

    monkeypatch.setattr(batch_module, "_crack_file_worker", fake_worker)

    with TemporaryDirectory(prefix="failure_", dir="outputs") as directory:
        root = Path(directory)
        input_dir = root / "in"
        output_dir = root / "out"
        input_dir.mkdir()
        files = [
            _write_ciphertext(input_dir, 3, 1),
            _write_ciphertext(input_dir, 3, 2),
            _write_ciphertext(input_dir, 3, 3),
        ]

        summaries = crack_files(
            files=files,
            matrix_path=root / "TM_ref.npy",
            output_directory=output_dir,
            iterations=1,
            workers=1,
            show_progress=False,
        )

    assert [summary.success for summary in summaries] == [True, False, True]
    assert summaries[1].error == "test error"


def test_empty_file_list_returns_empty_result():
    assert crack_files(
        files=[],
        matrix_path="models/TM_ref.npy",
        output_directory="outputs",
        iterations=1,
        workers=2,
        show_progress=False,
    ) == []


def test_worker_count_resolution(monkeypatch):
    monkeypatch.setattr(batch_module.os, "cpu_count", lambda: 8)
    assert resolve_worker_count(1, file_count=10) == 1
    assert resolve_worker_count(2, file_count=10) == 2
    assert resolve_worker_count(0, file_count=10) == 6
    assert resolve_worker_count(0, file_count=2) == 2


def test_small_parallel_integration_creates_outputs():
    with TemporaryDirectory(prefix="parallel_integration_", dir="outputs") as directory:
        root = Path(directory)
        input_dir = root / "in"
        output_dir = root / "out"
        input_dir.mkdir()
        matrix_path = _matrix_file(root / "TM_ref.npy")
        files = [
            _write_ciphertext(input_dir, 3, 1),
            _write_ciphertext(input_dir, 3, 2),
        ]

        summaries = crack_files(
            files=files,
            matrix_path=matrix_path,
            output_directory=output_dir,
            iterations=1,
            restarts=1,
            seed=1,
            polish=False,
            workers=2,
            show_progress=False,
        )

        assert len(summaries) == 2
        assert all(summary.success for summary in summaries)
        assert (output_dir / "text_3_sample_1_plaintext.txt").exists()
        assert (output_dir / "text_3_sample_2_key.txt").exists()
