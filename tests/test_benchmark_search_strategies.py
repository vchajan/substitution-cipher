import importlib.util
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "benchmark_search_strategies.py"
SPEC = importlib.util.spec_from_file_location("benchmark_search_strategies", SCRIPT_PATH)
benchmark = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = benchmark
SPEC.loader.exec_module(benchmark)


def _uniform_matrix() -> np.ndarray:
    matrix = np.ones((len(benchmark.ALPHABET), len(benchmark.ALPHABET)), dtype=float)
    return matrix / matrix.sum()


def _shift_key(offset: int) -> str:
    alphabet = benchmark.ALPHABET
    return alphabet[offset:] + alphabet[:offset]


def _write_basic_inputs(root: Path) -> tuple[Path, Path, Path, Path]:
    ciphertext_path = root / "ciphertext.txt"
    teacher_plaintext_path = root / "teacher_plaintext.txt"
    teacher_key_path = root / "teacher_key.txt"
    matrix_path = root / "matrix.npy"

    ciphertext_path.write_text("ABC_ABC", encoding="utf-8")
    teacher_plaintext_path.write_text("ABC_ABC", encoding="utf-8")
    teacher_key_path.write_text(benchmark.ALPHABET, encoding="utf-8")
    np.save(matrix_path, _uniform_matrix())

    return ciphertext_path, teacher_plaintext_path, teacher_key_path, matrix_path


def test_strategy_count_is_expected():
    assert len(benchmark.STRATEGIES) == 5
    assert [strategy.name for strategy in benchmark.STRATEGIES] == [
        "1x20000",
        "2x10000",
        "4x5000",
        "5x4000",
        "two_stage_4x5000_plus_15000",
    ]


def test_benchmark_does_not_write_to_main_outputs(monkeypatch):
    def fake_crack(
        self,
        ciphertext,
        iterations=20_000,
        start_key=None,
        restarts=1,
        seed=None,
        polish=True,
        progress_every=50,
    ):
        return benchmark.CrackResult(
            key=benchmark.ALPHABET,
            plaintext=ciphertext,
            score=-1.0,
            restart=1,
            iterations=iterations,
        )

    def fake_polish(ciphertext, key, TM_ref):
        return key, ciphertext, -0.5

    monkeypatch.setattr(benchmark.SubstitutionCipher, "crack", fake_crack)
    monkeypatch.setattr(benchmark, "polish_key", fake_polish)

    Path("outputs").mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="test_benchmark_no_outputs_", dir="outputs") as directory:
        root = Path(directory)
        ciphertext_path, teacher_plaintext_path, teacher_key_path, matrix_path = (
            _write_basic_inputs(root)
        )
        output_dir = root / "outputs"

        benchmark.run_benchmark(
            ciphertext_path=ciphertext_path,
            teacher_plaintext_path=teacher_plaintext_path,
            teacher_key_path=teacher_key_path,
            matrix_paths={"test": matrix_path},
            seeds=(1,),
            strategies=(benchmark.SearchStrategy("test", 1, 1),),
            csv_path=root / "reports" / "search_strategy_benchmark.csv",
            markdown_path=root / "reports" / "search_strategy_benchmark.md",
        )

        assert not output_dir.exists()


def test_teacher_plaintext_is_not_passed_to_crack(monkeypatch):
    teacher_plaintext = "SECRET_TEACHER_TEXT"
    seen_crack_calls = []

    def fake_crack(self, *args, **kwargs):
        seen_crack_calls.append((args, kwargs))
        assert teacher_plaintext not in args
        assert teacher_plaintext not in kwargs.values()
        ciphertext = args[0]
        return benchmark.CrackResult(
            key=benchmark.ALPHABET,
            plaintext=ciphertext,
            score=-1.0,
            restart=1,
            iterations=kwargs["iterations"],
        )

    def fake_polish(ciphertext, key, TM_ref):
        return key, ciphertext, -0.5

    monkeypatch.setattr(benchmark.SubstitutionCipher, "crack", fake_crack)
    monkeypatch.setattr(benchmark, "polish_key", fake_polish)

    Path("outputs").mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="test_benchmark_teacher_safe_", dir="outputs") as directory:
        root = Path(directory)
        ciphertext_path, teacher_plaintext_path, teacher_key_path, matrix_path = (
            _write_basic_inputs(root)
        )
        teacher_plaintext_path.write_text(teacher_plaintext, encoding="utf-8")

        benchmark.run_benchmark(
            ciphertext_path=ciphertext_path,
            teacher_plaintext_path=teacher_plaintext_path,
            teacher_key_path=teacher_key_path,
            matrix_paths={"test": matrix_path},
            seeds=(1,),
            strategies=(benchmark.SearchStrategy("test", 1, 1),),
            csv_path=root / "report.csv",
            markdown_path=root / "report.md",
        )

    assert len(seen_crack_calls) == 1


def test_two_stage_continues_from_best_first_phase_key(monkeypatch):
    calls = []
    best_first_key = _shift_key(1)
    results = iter(
        [
            benchmark.CrackResult(_shift_key(0), "AAAA", -30.0, 1, 5),
            benchmark.CrackResult(best_first_key, "BBBB", -10.0, 1, 5),
            benchmark.CrackResult(_shift_key(2), "CCCC", -40.0, 1, 5),
            benchmark.CrackResult(_shift_key(3), "DDDD", -20.0, 1, 5),
            benchmark.CrackResult(_shift_key(4), "EEEE", -5.0, 1, 15),
        ]
    )

    def fake_crack(
        self,
        ciphertext,
        iterations=20_000,
        start_key=None,
        restarts=1,
        seed=None,
        polish=True,
        progress_every=50,
    ):
        calls.append(
            {
                "iterations": iterations,
                "start_key": start_key,
                "seed": seed,
                "polish": polish,
            }
        )
        return next(results)

    def fake_polish(ciphertext, key, TM_ref):
        return key, ciphertext, -4.0

    monkeypatch.setattr(benchmark.SubstitutionCipher, "crack", fake_crack)
    monkeypatch.setattr(benchmark, "polish_key", fake_polish)

    cipher = benchmark.SubstitutionCipher(_uniform_matrix())
    strategy = benchmark.SearchStrategy(
        "two_stage_test",
        first_phase_starts=4,
        first_phase_iterations=5,
        continuation_iterations=15,
    )

    result = benchmark.run_strategy(strategy, cipher, "ABCD", seed=100)

    assert [call["start_key"] for call in calls[:4]] == [None, None, None, None]
    assert calls[4]["start_key"] == best_first_key
    assert calls[4]["iterations"] == 15
    assert calls[4]["polish"] is False
    assert result.score == -4.0


def test_csv_and_markdown_reports_are_created(monkeypatch):
    def fake_crack(
        self,
        ciphertext,
        iterations=20_000,
        start_key=None,
        restarts=1,
        seed=None,
        polish=True,
        progress_every=50,
    ):
        return benchmark.CrackResult(
            key=benchmark.ALPHABET,
            plaintext=ciphertext,
            score=-1.0,
            restart=1,
            iterations=iterations,
        )

    def fake_polish(ciphertext, key, TM_ref):
        return key, ciphertext, -0.5

    monkeypatch.setattr(benchmark.SubstitutionCipher, "crack", fake_crack)
    monkeypatch.setattr(benchmark, "polish_key", fake_polish)

    Path("outputs").mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="test_benchmark_reports_", dir="outputs") as directory:
        root = Path(directory)
        ciphertext_path, teacher_plaintext_path, teacher_key_path, matrix_path = (
            _write_basic_inputs(root)
        )
        csv_path = root / "reports" / "search_strategy_benchmark.csv"
        markdown_path = root / "reports" / "search_strategy_benchmark.md"

        rows = benchmark.run_benchmark(
            ciphertext_path=ciphertext_path,
            teacher_plaintext_path=teacher_plaintext_path,
            teacher_key_path=teacher_key_path,
            matrix_paths={"test": matrix_path},
            seeds=(1,),
            strategies=(benchmark.SearchStrategy("test", 1, 1),),
            csv_path=csv_path,
            markdown_path=markdown_path,
        )

        assert len(rows) == 1
        assert csv_path.exists()
        assert markdown_path.exists()
        assert csv_path.read_text(encoding="utf-8").splitlines()[0] == ",".join(
            benchmark.CSV_FIELDS
        )
        assert "Doporučená konfigurace" in markdown_path.read_text(encoding="utf-8")
