import importlib.util
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "benchmark_reference_matrices.py"
)
SPEC = importlib.util.spec_from_file_location("benchmark_reference_matrices", SCRIPT_PATH)
benchmark = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = benchmark
SPEC.loader.exec_module(benchmark)


def _long_clean_text(offset: int = 0, repetitions: int = 320) -> str:
    alphabet = benchmark.ALPHABET
    rotated = alphabet[offset:] + alphabet[:offset]
    return (rotated * repetitions).strip("_")


def _write_reference_texts(root: Path) -> tuple[Path, Path]:
    krakatit_path = root / "clean_text.txt"
    valka_path = root / "valka_s_mloky_clean.txt"
    krakatit_path.write_text(_long_clean_text(offset=0), encoding="utf-8")
    valka_path.write_text(_long_clean_text(offset=7), encoding="utf-8")
    return krakatit_path, valka_path


def test_full_strategy_count_is_expected():
    assert [strategy.name for strategy in benchmark.FULL_STRATEGIES] == [
        "1x20000",
        "2x10000",
    ]
    assert benchmark.OPTIONAL_STRATEGY_5X4000.name == "5x4000"


def test_train_holdout_split_has_no_positional_overlap():
    text = _long_clean_text(repetitions=20)

    train, holdout = benchmark.split_train_holdout(text)

    assert train == text[: len(train)]
    assert holdout == text[len(train) :]
    assert train + holdout == text
    assert len(train) + len(holdout) == len(text)


def test_holdout_samples_have_required_lengths():
    holdouts = {
        "krakatit": _long_clean_text(offset=0, repetitions=120),
        "valka_s_mloky": _long_clean_text(offset=4, repetitions=120),
    }

    samples = benchmark.create_holdout_samples(
        holdouts,
        samples_per_length=2,
    )

    assert {sample.plaintext_length for sample in samples} == {250, 500, 1000}
    assert all(len(sample.plaintext) == sample.plaintext_length for sample in samples)
    assert all(len(sample.ciphertext) == sample.plaintext_length for sample in samples)
    assert len(samples) == 2 * 3 * 2


def test_holdout_reference_matrices_have_expected_properties():
    train_texts = {
        "krakatit": _long_clean_text(offset=0, repetitions=40),
        "valka_s_mloky": _long_clean_text(offset=5, repetitions=40),
    }

    matrices = benchmark.build_holdout_reference_matrices(train_texts)

    assert set(matrices) == {"krakatit", "valka_s_mloky", "combined"}
    for matrix in matrices.values():
        assert matrix.shape == (27, 27)
        assert np.isclose(matrix.sum(), 1.0)
        assert int((matrix == 0.0).sum()) == 0


def test_same_generated_samples_are_used_for_all_matrices(monkeypatch):
    seen_by_sample = {}

    def fake_crack_sample(matrix_name, cipher, sample, strategy, seed):
        del cipher
        sample_key = (
            sample.source_book,
            sample.plaintext_length,
            sample.sample_id,
            strategy.name,
            seed,
        )
        seen_by_sample.setdefault(sample_key, {})[matrix_name] = (
            sample.key,
            sample.ciphertext,
        )
        return benchmark.CrackResult(
            key=sample.key,
            plaintext=sample.plaintext,
            score=0.0,
            restart=1,
            iterations=strategy.iterations,
        )

    monkeypatch.setattr(benchmark, "crack_sample", fake_crack_sample)

    Path("outputs").mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="test_reference_same_samples_", dir="outputs") as directory:
        root = Path(directory)
        krakatit_path, valka_path = _write_reference_texts(root)

        benchmark.run_reference_matrix_benchmark(
            krakatit_path=krakatit_path,
            valka_path=valka_path,
            csv_path=root / "report.csv",
            markdown_path=root / "report.md",
            seeds=(1,),
            samples_per_length=1,
            strategies=(benchmark.BenchmarkStrategy("test", 1, 1),),
            quick=True,
        )

    assert seen_by_sample
    for matrix_values in seen_by_sample.values():
        assert set(matrix_values) == {"krakatit", "valka_s_mloky", "combined"}
        assert len(set(matrix_values.values())) == 1


def test_teacher_plaintext_is_not_passed_to_crack(monkeypatch):
    teacher_plaintext = "SECRET_TEACHER_TEXT"
    seen_calls = []

    def fake_crack_sample(matrix_name, cipher, sample, strategy, seed):
        del matrix_name, cipher, strategy, seed
        seen_calls.append(sample.ciphertext)
        assert teacher_plaintext not in sample.plaintext
        assert teacher_plaintext not in sample.ciphertext
        return benchmark.CrackResult(
            key=sample.key,
            plaintext=sample.plaintext,
            score=0.0,
            restart=1,
            iterations=1,
        )

    monkeypatch.setattr(benchmark, "crack_sample", fake_crack_sample)

    Path("outputs").mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="test_reference_teacher_safe_", dir="outputs") as directory:
        root = Path(directory)
        krakatit_path, valka_path = _write_reference_texts(root)

        benchmark.run_reference_matrix_benchmark(
            krakatit_path=krakatit_path,
            valka_path=valka_path,
            csv_path=root / "report.csv",
            markdown_path=root / "report.md",
            seeds=(1,),
            samples_per_length=1,
            strategies=(benchmark.BenchmarkStrategy("test", 1, 1),),
            quick=True,
        )

    assert seen_calls


def test_csv_and_markdown_reports_are_created_and_outputs_are_untouched(monkeypatch):
    def fake_crack_sample(matrix_name, cipher, sample, strategy, seed):
        del matrix_name, cipher, seed
        return benchmark.CrackResult(
            key=sample.key,
            plaintext=sample.plaintext,
            score=0.0,
            restart=1,
            iterations=strategy.iterations,
        )

    monkeypatch.setattr(benchmark, "crack_sample", fake_crack_sample)

    Path("outputs").mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="test_reference_reports_", dir="outputs") as directory:
        root = Path(directory)
        krakatit_path, valka_path = _write_reference_texts(root)
        csv_path = root / "reports" / "reference_matrix_benchmark.csv"
        markdown_path = root / "reports" / "reference_matrix_benchmark.md"
        forbidden_output_dir = root / "outputs"

        rows = benchmark.run_reference_matrix_benchmark(
            krakatit_path=krakatit_path,
            valka_path=valka_path,
            csv_path=csv_path,
            markdown_path=markdown_path,
            seeds=(1,),
            samples_per_length=1,
            strategies=(benchmark.BenchmarkStrategy("test", 1, 1),),
            quick=True,
        )

        assert rows
        assert csv_path.exists()
        assert markdown_path.exists()
        assert csv_path.read_text(encoding="utf-8").splitlines()[0] == ",".join(
            benchmark.CSV_FIELDS
        )
        assert "Benchmark referenčních matic" in markdown_path.read_text(
            encoding="utf-8"
        )
        assert not forbidden_output_dir.exists()
