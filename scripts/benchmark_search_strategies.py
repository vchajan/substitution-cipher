"""Benchmark blind search strategies for one teacher ciphertext sample.

The benchmark never uses the known teacher plaintext or key while searching.
Teacher files are loaded only after a strategy finishes, so they are used only
for measuring the final accuracy of a blind result.
"""

from __future__ import annotations

import csv
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from substitution_cipher import ALPHABET, CrackResult, SubstitutionCipher, polish_key  # noqa: E402


CIPHERTEXT_PATH = (
    PROJECT_ROOT / "data" / "ciphertexts" / "text_1000_sample_1_ciphertext.txt"
)
TEACHER_PLAINTEXT_PATH = (
    PROJECT_ROOT / "data" / "teacher_example" / "text_1000_sample_1_plaintext.txt"
)
TEACHER_KEY_PATH = (
    PROJECT_ROOT / "data" / "teacher_example" / "text_1000_sample_1_key.txt"
)
MATRIX_PATHS = {
    "krakatit": PROJECT_ROOT / "data" / "processed" / "TM_ref_krakatit.npy",
    "valka_s_mloky": PROJECT_ROOT / "data" / "processed" / "TM_ref_valka_s_mloky.npy",
    "combined": PROJECT_ROOT / "data" / "processed" / "TM_ref_combined.npy",
}
REPORT_CSV_PATH = PROJECT_ROOT / "reports" / "search_strategy_benchmark.csv"
REPORT_MD_PATH = PROJECT_ROOT / "reports" / "search_strategy_benchmark.md"
DEFAULT_SEEDS = (1, 2, 3)

CSV_FIELDS = (
    "strategy",
    "matrix",
    "seed",
    "total_iterations",
    "number_of_starts",
    "plausibility",
    "matching_chars",
    "matching_percent",
    "plaintext_exact",
    "key_exact",
    "runtime_seconds",
)


@dataclass(frozen=True)
class SearchStrategy:
    """Definition of one blind search strategy."""

    name: str
    first_phase_starts: int
    first_phase_iterations: int
    continuation_iterations: int = 0

    @property
    def total_iterations(self) -> int:
        """Return the total number of M-H iterations spent by the strategy."""
        return (
            self.first_phase_starts * self.first_phase_iterations
            + self.continuation_iterations
        )

    @property
    def number_of_starts(self) -> int:
        """Return the number of independent random first-phase starts."""
        return self.first_phase_starts

    @property
    def is_two_stage(self) -> bool:
        """Return whether the strategy continues from the best first key."""
        return self.continuation_iterations > 0


STRATEGIES = (
    SearchStrategy("1x20000", first_phase_starts=1, first_phase_iterations=20_000),
    SearchStrategy("2x10000", first_phase_starts=2, first_phase_iterations=10_000),
    SearchStrategy("4x5000", first_phase_starts=4, first_phase_iterations=5_000),
    SearchStrategy("5x4000", first_phase_starts=5, first_phase_iterations=4_000),
    SearchStrategy(
        "two_stage_4x5000_plus_15000",
        first_phase_starts=4,
        first_phase_iterations=5_000,
        continuation_iterations=15_000,
    ),
)


def read_text(path: str | Path) -> str:
    """Read one UTF-8 text file and strip surrounding whitespace."""
    return Path(path).read_text(encoding="utf-8").strip()


def compare_with_teacher(
    plaintext: str,
    key: str,
    teacher_plaintext: str,
    teacher_key: str,
) -> dict[str, object]:
    """Measure result accuracy against teacher data after blind cracking."""
    matching_chars = sum(
        1 for found, expected in zip(plaintext, teacher_plaintext) if found == expected
    )
    teacher_length = len(teacher_plaintext)
    matching_percent = (
        100.0 * matching_chars / teacher_length if teacher_length else 0.0
    )

    return {
        "matching_chars": matching_chars,
        "matching_percent": matching_percent,
        "plaintext_exact": plaintext == teacher_plaintext,
        "key_exact": key == teacher_key,
    }


def _polish_result(
    cipher: SubstitutionCipher,
    ciphertext: str,
    result: CrackResult,
) -> CrackResult:
    """Polish the selected key once and return a fresh CrackResult."""
    assert cipher.reference_matrix is not None
    key, plaintext, score = polish_key(ciphertext, result.key, cipher.reference_matrix)
    return CrackResult(
        key=key,
        plaintext=plaintext,
        score=score,
        restart=result.restart,
        iterations=result.iterations,
    )


def _crack_one_start(
    cipher: SubstitutionCipher,
    ciphertext: str,
    iterations: int,
    seed: int,
    start_key: str | None = None,
) -> CrackResult:
    """Run one unpolished M-H search start."""
    return cipher.crack(
        ciphertext,
        iterations=iterations,
        start_key=start_key,
        restarts=1,
        seed=seed,
        polish=False,
        progress_every=0,
    )


def run_strategy(
    strategy: SearchStrategy,
    cipher: SubstitutionCipher,
    ciphertext: str,
    seed: int,
) -> CrackResult:
    """Run one blind strategy and return its final polished result.

    Multiple-start strategies select the best restart only by plausibility.
    The two-stage strategy then continues from that selected key; it does not
    restart randomly in the continuation phase.
    """
    best_first_phase: CrackResult | None = None

    for start_index in range(strategy.first_phase_starts):
        start_seed = seed + start_index
        result = _crack_one_start(
            cipher=cipher,
            ciphertext=ciphertext,
            iterations=strategy.first_phase_iterations,
            seed=start_seed,
        )
        if best_first_phase is None or result.score > best_first_phase.score:
            best_first_phase = result

    assert best_first_phase is not None
    selected = best_first_phase

    if strategy.is_two_stage:
        selected = _crack_one_start(
            cipher=cipher,
            ciphertext=ciphertext,
            iterations=strategy.continuation_iterations,
            seed=seed + 10_000,
            start_key=best_first_phase.key,
        )

    return _polish_result(cipher, ciphertext, selected)


def make_result_row(
    strategy: SearchStrategy,
    matrix_name: str,
    seed: int,
    result: CrackResult,
    runtime_seconds: float,
    teacher_plaintext: str,
    teacher_key: str,
) -> dict[str, object]:
    """Create one CSV-ready benchmark result row."""
    metrics = compare_with_teacher(
        plaintext=result.plaintext,
        key=result.key,
        teacher_plaintext=teacher_plaintext,
        teacher_key=teacher_key,
    )
    row: dict[str, object] = {
        "strategy": strategy.name,
        "matrix": matrix_name,
        "seed": seed,
        "total_iterations": strategy.total_iterations,
        "number_of_starts": strategy.number_of_starts,
        "plausibility": result.score,
        "runtime_seconds": runtime_seconds,
    }
    row.update(metrics)
    return row


def run_benchmark(
    ciphertext_path: str | Path = CIPHERTEXT_PATH,
    teacher_plaintext_path: str | Path = TEACHER_PLAINTEXT_PATH,
    teacher_key_path: str | Path = TEACHER_KEY_PATH,
    matrix_paths: Mapping[str, str | Path] = MATRIX_PATHS,
    seeds: Iterable[int] = DEFAULT_SEEDS,
    strategies: Iterable[SearchStrategy] = STRATEGIES,
    csv_path: str | Path = REPORT_CSV_PATH,
    markdown_path: str | Path = REPORT_MD_PATH,
) -> list[dict[str, object]]:
    """Run the benchmark and write CSV plus Markdown reports."""
    ciphertext = read_text(ciphertext_path)
    teacher_plaintext = read_text(teacher_plaintext_path)
    teacher_key = read_text(teacher_key_path)

    rows: list[dict[str, object]] = []
    seed_values = tuple(seeds)
    strategy_values = tuple(strategies)

    for matrix_name, matrix_path in matrix_paths.items():
        print(f"Loading matrix: {matrix_name} ({matrix_path})")
        cipher = SubstitutionCipher.from_matrix_file(matrix_path)

        for strategy in strategy_values:
            for seed in seed_values:
                print(
                    f"Running strategy={strategy.name}, matrix={matrix_name}, "
                    f"seed={seed}"
                )
                started_at = time.perf_counter()
                result = run_strategy(strategy, cipher, ciphertext, seed)
                runtime_seconds = time.perf_counter() - started_at
                row = make_result_row(
                    strategy=strategy,
                    matrix_name=matrix_name,
                    seed=seed,
                    result=result,
                    runtime_seconds=runtime_seconds,
                    teacher_plaintext=teacher_plaintext,
                    teacher_key=teacher_key,
                )
                rows.append(row)
                print(
                    f"  {row['matching_chars']}/{len(teacher_plaintext)} "
                    f"({row['matching_percent']:.2f} %), "
                    f"plausibility={row['plausibility']:.3f}"
                )

    write_csv_report(rows, csv_path)
    write_markdown_report(rows, markdown_path)
    return rows


def write_csv_report(rows: list[dict[str, object]], path: str | Path) -> None:
    """Write raw benchmark rows to a CSV file."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in CSV_FIELDS})


def _group_rows(rows: list[dict[str, object]], key: str) -> dict[str, list[dict[str, object]]]:
    """Group rows by a CSV column."""
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row[key]), []).append(row)
    return grouped


def _group_rows_pair(
    rows: list[dict[str, object]],
) -> dict[tuple[str, str], list[dict[str, object]]]:
    """Group rows by ``(strategy, matrix)``."""
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault((str(row["strategy"]), str(row["matrix"])), []).append(row)
    return grouped


def _mean_percent(rows: list[dict[str, object]]) -> float:
    return statistics.fmean(float(row["matching_percent"]) for row in rows)


def _min_percent(rows: list[dict[str, object]]) -> float:
    return min(float(row["matching_percent"]) for row in rows)


def _mean_runtime(rows: list[dict[str, object]]) -> float:
    return statistics.fmean(float(row["runtime_seconds"]) for row in rows)


def summarize_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    """Return aggregate benchmark conclusions."""
    if not rows:
        return {
            "best_average_strategy": "",
            "most_stable_strategy": "",
            "fastest_strategy": "",
            "best_matrix": "",
            "exact_count": 0,
            "recommended_strategy": "",
            "recommended_matrix": "",
        }

    strategy_groups = _group_rows(rows, "strategy")
    matrix_groups = _group_rows(rows, "matrix")
    pair_groups = _group_rows_pair(rows)

    best_average_strategy = max(
        strategy_groups,
        key=lambda name: (_mean_percent(strategy_groups[name]), _min_percent(strategy_groups[name])),
    )
    most_stable_strategy = max(
        strategy_groups,
        key=lambda name: (_min_percent(strategy_groups[name]), _mean_percent(strategy_groups[name])),
    )
    fastest_strategy = min(strategy_groups, key=lambda name: _mean_runtime(strategy_groups[name]))
    best_matrix = max(
        matrix_groups,
        key=lambda name: (_mean_percent(matrix_groups[name]), _min_percent(matrix_groups[name])),
    )
    recommended_strategy, recommended_matrix = max(
        pair_groups,
        key=lambda pair: (
            _mean_percent(pair_groups[pair]),
            _min_percent(pair_groups[pair]),
            -_mean_runtime(pair_groups[pair]),
        ),
    )
    exact_count = sum(1 for row in rows if bool(row["plaintext_exact"]))

    return {
        "best_average_strategy": best_average_strategy,
        "most_stable_strategy": most_stable_strategy,
        "fastest_strategy": fastest_strategy,
        "best_matrix": best_matrix,
        "exact_count": exact_count,
        "recommended_strategy": recommended_strategy,
        "recommended_matrix": recommended_matrix,
    }


def write_markdown_report(rows: list[dict[str, object]], path: str | Path) -> None:
    """Write a Markdown summary report for the benchmark."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = summarize_rows(rows)

    pair_groups = _group_rows_pair(rows)
    lines = [
        "# Benchmark strategií hledání",
        "",
        "Benchmark používá učitelský plaintext a klíč pouze pro vyhodnocení "
        "hotového slepého běhu.",
        "",
        "## Souhrn",
        "",
        f"- Nejlepší průměrná strategie: {summary['best_average_strategy']}",
        f"- Nejstabilnější strategie: {summary['most_stable_strategy']}",
        f"- Nejrychlejší strategie: {summary['fastest_strategy']}",
        f"- Nejlepší matice: {summary['best_matrix']}",
        f"- Počet přesných výsledků 1000/1000: {summary['exact_count']}",
        "- Doporučená konfigurace pro všech 60 souborů: "
        f"{summary['recommended_strategy']} s maticí {summary['recommended_matrix']}",
        "",
        "## Výsledky podle strategie a matice",
        "",
        "| Strategie | Matice | Průměr % | Minimum % | Maximum % | Přesné běhy | Průměrný čas [s] |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]

    for (strategy, matrix), group in sorted(pair_groups.items()):
        percents = [float(row["matching_percent"]) for row in group]
        exact_count = sum(1 for row in group if bool(row["plaintext_exact"]))
        lines.append(
            f"| {strategy} | {matrix} | "
            f"{statistics.fmean(percents):.2f} | "
            f"{min(percents):.2f} | "
            f"{max(percents):.2f} | "
            f"{exact_count}/{len(group)} | "
            f"{_mean_runtime(group):.2f} |"
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Run the full benchmark with default assignment paths."""
    rows = run_benchmark()
    summary = summarize_rows(rows)
    print("\nBenchmark finished.")
    print(f"CSV report: {REPORT_CSV_PATH}")
    print(f"Markdown report: {REPORT_MD_PATH}")
    print(f"Best average strategy: {summary['best_average_strategy']}")
    print(f"Most stable strategy: {summary['most_stable_strategy']}")
    print(f"Fastest strategy: {summary['fastest_strategy']}")
    print(f"Best matrix: {summary['best_matrix']}")
    print(f"Exact 1000/1000 results: {summary['exact_count']}")
    print(
        "Recommended configuration for all 60 files: "
        f"{summary['recommended_strategy']} with matrix "
        f"{summary['recommended_matrix']}"
    )


if __name__ == "__main__":
    main()
