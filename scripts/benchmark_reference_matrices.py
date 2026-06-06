"""Benchmark referenčních matic na deterministických holdout ciphertextech.

Skript nepoužívá učitelskou sadu ciphertextů. Vytvoří vlastní plaintexty
z holdout částí dostupných referenčních knih, zašifruje je deterministickými
substitučními klíči a porovná, jak dobře jednotlivé referenční matice vedou
existující slepou kryptoanalýzu.
"""

from __future__ import annotations

import argparse
import csv
import random
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

for directory in (SRC_DIR, SCRIPTS_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from prepare_wikisource_text import validate_clean_text  # noqa: E402
from substitution_cipher import (  # noqa: E402
    ALPHABET,
    CrackResult,
    SubstitutionCipher,
    build_reference_matrix_from_text,
    substitute_encrypt,
)


KRAKATIT_TEXT_PATH = PROJECT_ROOT / "data" / "processed" / "clean_text.txt"
VALKA_TEXT_PATH = PROJECT_ROOT / "data" / "reference_texts" / "valka_s_mloky_clean.txt"
REPORT_CSV_PATH = PROJECT_ROOT / "reports" / "reference_matrix_benchmark.csv"
REPORT_MD_PATH = PROJECT_ROOT / "reports" / "reference_matrix_benchmark.md"

TEXT_LENGTHS = (250, 500, 1000)
DEFAULT_SAMPLES_PER_LENGTH = 10
DEFAULT_SEEDS = (1, 2, 3)
TRAIN_FRACTION = 0.8


@dataclass(frozen=True)
class BenchmarkStrategy:
    """Definice jedné strategie restartů pro holdout benchmark."""

    name: str
    iterations: int
    restarts: int

    @property
    def total_iterations(self) -> int:
        """Vrátí celkový počet M-H iterací pro danou strategii."""
        return self.iterations * self.restarts


@dataclass(frozen=True)
class HoldoutSample:
    """Jeden deterministický plaintext/ciphertext vzorek pro benchmark."""

    source_book: str
    plaintext_length: int
    sample_id: int
    plaintext: str
    key: str
    ciphertext: str


CSV_FIELDS = (
    "source_book",
    "plaintext_length",
    "sample_id",
    "matrix",
    "strategy",
    "seed",
    "matching_chars",
    "matching_percent",
    "plaintext_exact",
    "key_exact",
    "plausibility",
    "runtime_seconds",
)

FULL_STRATEGIES = (
    BenchmarkStrategy("1x20000", iterations=20_000, restarts=1),
    BenchmarkStrategy("2x10000", iterations=10_000, restarts=2),
)
QUICK_STRATEGIES = (
    BenchmarkStrategy("1x50", iterations=50, restarts=1),
    BenchmarkStrategy("2x25", iterations=25, restarts=2),
)
OPTIONAL_STRATEGY_5X4000 = BenchmarkStrategy("5x4000", iterations=4_000, restarts=5)


def parse_seeds(raw: str) -> tuple[int, ...]:
    """Zpracuje čárkou oddělený seznam seedů z příkazové řádky."""
    seeds = tuple(int(part.strip()) for part in raw.split(",") if part.strip())
    if not seeds:
        raise ValueError("Musí být zadán alespoň jeden seed.")
    return seeds


def read_clean_text(path: str | Path) -> str:
    """Načte a zkontroluje jeden vyčištěný referenční text."""
    text = Path(path).read_text(encoding="utf-8").strip().strip("_")
    validate_clean_text(text)
    return text


def split_train_holdout(
    text: str,
    train_fraction: float = TRAIN_FRACTION,
) -> tuple[str, str]:
    """Deterministicky rozdělí text na nepřekrývající se train a holdout část."""
    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train_fraction musí být mezi 0 a 1.")

    split_index = int(len(text) * train_fraction)
    train = text[:split_index]
    holdout = text[split_index:]
    if not train or not holdout:
        raise ValueError("Train i holdout část musí být neprázdná.")
    return train, holdout


def load_reference_splits(
    krakatit_path: str | Path = KRAKATIT_TEXT_PATH,
    valka_path: str | Path = VALKA_TEXT_PATH,
) -> tuple[dict[str, str], dict[str, str]]:
    """Načte obě knihy a vrátí slovníky s train a holdout texty."""
    texts = {
        "krakatit": read_clean_text(krakatit_path),
        "valka_s_mloky": read_clean_text(valka_path),
    }

    train_texts: dict[str, str] = {}
    holdout_texts: dict[str, str] = {}
    for name, text in texts.items():
        train, holdout = split_train_holdout(text)
        train_texts[name] = train
        holdout_texts[name] = holdout

    return train_texts, holdout_texts


def build_holdout_reference_matrices(train_texts: Mapping[str, str]) -> dict[str, np.ndarray]:
    """Vytvoří paměťové matice pouze z train částí textů."""
    krakatit_text = train_texts["krakatit"]
    valka_text = train_texts["valka_s_mloky"]
    combined_text = f"{krakatit_text}_{valka_text}"

    return {
        "krakatit": build_reference_matrix_from_text(krakatit_text),
        "valka_s_mloky": build_reference_matrix_from_text(valka_text),
        "combined": build_reference_matrix_from_text(combined_text),
    }


def deterministic_key(seed: int, alphabet: str = ALPHABET) -> str:
    """Vytvoří ze seedu jeden deterministický substituční klíč."""
    characters = list(alphabet)
    random.Random(seed).shuffle(characters)
    return "".join(characters)


def _sample_start_indices(
    holdout_length: int,
    plaintext_length: int,
    sample_count: int,
) -> list[int]:
    """Vrátí deterministické začátky vzorků v holdout textu."""
    if holdout_length < plaintext_length:
        raise ValueError(
            f"Holdout text je příliš krátký pro délku {plaintext_length}: "
            f"{holdout_length} znaků."
        )
    if sample_count < 1:
        raise ValueError("sample_count musí být alespoň 1.")

    available = holdout_length - plaintext_length
    if sample_count == 1 or available == 0:
        return [0] * sample_count

    step = available / float(sample_count - 1)
    return [round(index * step) for index in range(sample_count)]


def create_holdout_samples(
    holdout_texts: Mapping[str, str],
    lengths: Sequence[int] = TEXT_LENGTHS,
    samples_per_length: int = DEFAULT_SAMPLES_PER_LENGTH,
    key_seed_base: int = 100_000,
) -> list[HoldoutSample]:
    """Vytvoří deterministické plaintexty, klíče a ciphertexty pro benchmark."""
    samples: list[HoldoutSample] = []

    for source_book, holdout_text in holdout_texts.items():
        for plaintext_length in lengths:
            starts = _sample_start_indices(
                holdout_length=len(holdout_text),
                plaintext_length=plaintext_length,
                sample_count=samples_per_length,
            )
            for sample_index, start in enumerate(starts, start=1):
                plaintext = holdout_text[start : start + plaintext_length]
                key_seed = key_seed_base + plaintext_length * 100 + sample_index
                key = deterministic_key(key_seed)
                ciphertext = substitute_encrypt(plaintext, key)
                samples.append(
                    HoldoutSample(
                        source_book=source_book,
                        plaintext_length=plaintext_length,
                        sample_id=sample_index,
                        plaintext=plaintext,
                        key=key,
                        ciphertext=ciphertext,
                    )
                )

    return samples


def compare_plaintext_and_key(
    found_plaintext: str,
    found_key: str,
    sample: HoldoutSample,
) -> dict[str, object]:
    """Porovná slepě nalezený výsledek se známým vygenerovaným vzorkem."""
    matching_chars = sum(
        1
        for found_char, expected_char in zip(found_plaintext, sample.plaintext)
        if found_char == expected_char
    )
    matching_percent = 100.0 * matching_chars / sample.plaintext_length
    return {
        "matching_chars": matching_chars,
        "matching_percent": matching_percent,
        "plaintext_exact": found_plaintext == sample.plaintext,
        "key_exact": found_key == sample.key,
    }


def crack_sample(
    matrix_name: str,
    cipher: SubstitutionCipher,
    sample: HoldoutSample,
    strategy: BenchmarkStrategy,
    seed: int,
) -> CrackResult:
    """Prolomí jeden vygenerovaný ciphertext přes existující objektové API."""
    del matrix_name
    return cipher.crack(
        sample.ciphertext,
        iterations=strategy.iterations,
        restarts=strategy.restarts,
        seed=seed,
        polish=True,
        progress_every=0,
    )


def make_result_row(
    sample: HoldoutSample,
    matrix_name: str,
    strategy: BenchmarkStrategy,
    seed: int,
    result: CrackResult,
    runtime_seconds: float,
) -> dict[str, object]:
    """Vytvoří jeden řádek benchmarku připravený pro CSV."""
    metrics = compare_plaintext_and_key(result.plaintext, result.key, sample)
    row: dict[str, object] = {
        "source_book": sample.source_book,
        "plaintext_length": sample.plaintext_length,
        "sample_id": sample.sample_id,
        "matrix": matrix_name,
        "strategy": strategy.name,
        "seed": seed,
        "plausibility": result.score,
        "runtime_seconds": runtime_seconds,
    }
    row.update(metrics)
    return row


def run_reference_matrix_benchmark(
    krakatit_path: str | Path = KRAKATIT_TEXT_PATH,
    valka_path: str | Path = VALKA_TEXT_PATH,
    csv_path: str | Path = REPORT_CSV_PATH,
    markdown_path: str | Path = REPORT_MD_PATH,
    seeds: Iterable[int] = DEFAULT_SEEDS,
    samples_per_length: int = DEFAULT_SAMPLES_PER_LENGTH,
    strategies: Sequence[BenchmarkStrategy] = FULL_STRATEGIES,
    quick: bool = False,
) -> list[dict[str, object]]:
    """Spustí holdout benchmark a zapíše CSV i Markdown report."""
    train_texts, holdout_texts = load_reference_splits(krakatit_path, valka_path)
    matrices = build_holdout_reference_matrices(train_texts)
    samples = create_holdout_samples(
        holdout_texts,
        samples_per_length=samples_per_length,
    )

    rows: list[dict[str, object]] = []
    seed_values = tuple(seeds)

    for matrix_name, matrix in matrices.items():
        print(f"Načítám paměťovou matici: {matrix_name}")
        cipher = SubstitutionCipher(matrix)

        for strategy in strategies:
            for seed in seed_values:
                for sample in samples:
                    print(
                        "Spouštím "
                        f"kniha={sample.source_book}, délka={sample.plaintext_length}, "
                        f"vzorek={sample.sample_id}, matice={matrix_name}, "
                        f"strategie={strategy.name}, seed={seed}"
                    )
                    started_at = time.perf_counter()
                    result = crack_sample(matrix_name, cipher, sample, strategy, seed)
                    runtime_seconds = time.perf_counter() - started_at
                    row = make_result_row(
                        sample=sample,
                        matrix_name=matrix_name,
                        strategy=strategy,
                        seed=seed,
                        result=result,
                        runtime_seconds=runtime_seconds,
                    )
                    rows.append(row)
                    print(
                        f"  {row['matching_chars']}/{sample.plaintext_length} "
                        f"({row['matching_percent']:.2f} %), "
                        f"plausibility={row['plausibility']:.3f}"
                    )

    write_csv_report(rows, csv_path)
    write_markdown_report(
        rows=rows,
        path=markdown_path,
        quick=quick,
        samples_per_length=samples_per_length,
        seeds=seed_values,
        strategies=strategies,
    )
    return rows


def write_csv_report(rows: list[dict[str, object]], path: str | Path) -> None:
    """Zapíše nezpracované řádky benchmarku do CSV."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in CSV_FIELDS})


def _group_rows(
    rows: Iterable[dict[str, object]],
    keys: Sequence[str],
) -> dict[tuple[object, ...], list[dict[str, object]]]:
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row[key] for key in keys), []).append(row)
    return grouped


def summarize_group(rows: list[dict[str, object]]) -> dict[str, object]:
    """Shrne procenta shody a čas běhu pro jednu skupinu."""
    percents = [float(row["matching_percent"]) for row in rows]
    return {
        "sample_count": len(rows),
        "mean": statistics.fmean(percents),
        "median": statistics.median(percents),
        "min": min(percents),
        "max": max(percents),
        "exact_plaintext_count": sum(1 for row in rows if bool(row["plaintext_exact"])),
        "avg_time": statistics.fmean(float(row["runtime_seconds"]) for row in rows),
    }


def summarize_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    """Vrátí souhrnné metriky pro doporučení podle holdoutu."""
    if not rows:
        return {
            "best_matrix": "",
            "best_strategy": "",
            "best_pair": ("", ""),
            "exact_count": 0,
            "fastest_pair": ("", ""),
        }

    matrix_groups = _group_rows(rows, ("matrix",))
    pair_groups = _group_rows(rows, ("matrix", "strategy"))

    best_matrix_tuple = max(
        matrix_groups,
        key=lambda key: (
            summarize_group(matrix_groups[key])["mean"],
            summarize_group(matrix_groups[key])["min"],
            summarize_group(matrix_groups[key])["exact_plaintext_count"],
        ),
    )
    best_pair = max(
        pair_groups,
        key=lambda key: (
            summarize_group(pair_groups[key])["mean"],
            summarize_group(pair_groups[key])["min"],
            summarize_group(pair_groups[key])["exact_plaintext_count"],
            -summarize_group(pair_groups[key])["avg_time"],
        ),
    )
    fastest_pair = min(
        pair_groups,
        key=lambda key: summarize_group(pair_groups[key])["avg_time"],
    )

    return {
        "best_matrix": best_matrix_tuple[0],
        "best_strategy": best_pair[1],
        "best_pair": best_pair,
        "exact_count": sum(1 for row in rows if bool(row["plaintext_exact"])),
        "fastest_pair": fastest_pair,
    }


def write_markdown_report(
    rows: list[dict[str, object]],
    path: str | Path,
    quick: bool,
    samples_per_length: int,
    seeds: Sequence[int],
    strategies: Sequence[BenchmarkStrategy],
) -> None:
    """Zapíše benchmarkový report ve formátu Markdown."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    summary = summarize_rows(rows)
    grouped = _group_rows(
        rows,
        ("matrix", "strategy", "plaintext_length", "source_book"),
    )
    pair_groups = _group_rows(rows, ("matrix", "strategy"))

    mode = "rychlý kontrolní běh" if quick else "plný benchmark"
    lines = [
        "# Benchmark referenčních matic",
        "",
        "## Učitelský benchmark",
        "",
        "Benchmark učitelského vzorku je samostatný a zapisuje se do "
        "`reports/search_strategy_benchmark.csv` a "
        "`reports/search_strategy_benchmark.md`.",
        "",
        "## Holdout benchmark",
        "",
        f"Režim: {mode}.",
        f"Počet vzorků na délku a knihu: {samples_per_length}.",
        f"Seedy: {', '.join(str(seed) for seed in seeds)}.",
        "Strategie: "
        + ", ".join(strategy.name for strategy in strategies)
        + ".",
        "",
        "## Příkazy",
        "",
        "Vytvoření referenčních matic včetně samostatné matice pro "
        "Válku s mloky:",
        "",
        "```powershell",
        "python scripts\\build_combined_reference_matrix.py",
        "```",
        "",
        "Rychlý kontrolní benchmark:",
        "",
        "```powershell",
        "python scripts\\benchmark_reference_matrices.py --quick",
        "```",
        "",
        "Plný benchmark s výchozími strategiemi a seedy:",
        "",
        "```powershell",
        "python scripts\\benchmark_reference_matrices.py",
        "```",
        "",
        "Holdout vzorky vznikly z posledních 20 % každé knihy. Matice "
        "v tomto benchmarku vznikly pouze z prvních 80 % knih.",
        "",
        "## Doporučení podle holdoutu",
        "",
        f"- Nejlepší matice: {summary['best_matrix']}",
        "- Doporučená konfigurace: "
        f"{summary['best_pair'][1]} s maticí {summary['best_pair'][0]}",
        "- Nejrychlejší měřená konfigurace: "
        f"{summary['fastest_pair'][1]} s maticí {summary['fastest_pair'][0]}",
        f"- Přesné plaintexty: {summary['exact_count']}/{len(rows)}",
        "",
        "## Souhrn podle matice a strategie",
        "",
        "| Matice | Strategie | Počet | Průměr % | Medián % | Minimum % | Maximum % | Přesné plaintexty | Průměrný čas [s] |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for (matrix_name, strategy_name), group in sorted(pair_groups.items()):
        stats = summarize_group(group)
        lines.append(
            f"| {matrix_name} | {strategy_name} | "
            f"{stats['sample_count']} | "
            f"{stats['mean']:.2f} | "
            f"{stats['median']:.2f} | "
            f"{stats['min']:.2f} | "
            f"{stats['max']:.2f} | "
            f"{stats['exact_plaintext_count']} | "
            f"{stats['avg_time']:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Detail podle délky a zdrojové knihy",
            "",
            "| Matice | Strategie | Délka | Zdroj | Počet | Průměr % | Medián % | Minimum % | Maximum % | Přesné plaintexty | Průměrný čas [s] |",
            "|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )

    for key, group in sorted(grouped.items()):
        matrix_name, strategy_name, plaintext_length, source_book = key
        stats = summarize_group(group)
        lines.append(
            f"| {matrix_name} | {strategy_name} | {plaintext_length} | "
            f"{source_book} | "
            f"{stats['sample_count']} | "
            f"{stats['mean']:.2f} | "
            f"{stats['median']:.2f} | "
            f"{stats['min']:.2f} | "
            f"{stats['max']:.2f} | "
            f"{stats['exact_plaintext_count']} | "
            f"{stats['avg_time']:.2f} |"
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    """Vytvoří parser příkazové řádky."""
    parser = argparse.ArgumentParser(
        description="Benchmark referenčních matic na vygenerovaných holdout ciphertextech."
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Spustí krátký kontrolní benchmark s málo vzorky a krátkým hledáním.",
    )
    parser.add_argument(
        "--samples-per-length",
        type=int,
        default=None,
        help="Počet holdout vzorků pro každou délku a zdrojovou knihu.",
    )
    parser.add_argument(
        "--seeds",
        default=None,
        help="Seedy oddělené čárkou, například 1,2,3.",
    )
    parser.add_argument(
        "--include-5x4000",
        action="store_true",
        help="Přidá také volitelnou plnou strategii 5x4000.",
    )
    return parser


def main() -> None:
    """Spustí benchmark z příkazové řádky."""
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.quick:
        samples_per_length = (
            args.samples_per_length if args.samples_per_length is not None else 1
        )
        seeds = parse_seeds(args.seeds) if args.seeds is not None else (1,)
        strategies: tuple[BenchmarkStrategy, ...] = QUICK_STRATEGIES
    else:
        samples_per_length = (
            args.samples_per_length
            if args.samples_per_length is not None
            else DEFAULT_SAMPLES_PER_LENGTH
        )
        seeds = parse_seeds(args.seeds) if args.seeds is not None else DEFAULT_SEEDS
        strategies = FULL_STRATEGIES
        if args.include_5x4000:
            strategies = (*strategies, OPTIONAL_STRATEGY_5X4000)

    rows = run_reference_matrix_benchmark(
        seeds=seeds,
        samples_per_length=samples_per_length,
        strategies=strategies,
        quick=args.quick,
    )
    summary = summarize_rows(rows)

    print("\nBenchmark referenčních matic je hotový.")
    print(f"CSV report: {REPORT_CSV_PATH}")
    print(f"Markdown report: {REPORT_MD_PATH}")
    print(f"Nejlepší matice: {summary['best_matrix']}")
    print(
        "Doporučená konfigurace podle holdoutu: "
        f"{summary['best_pair'][1]} s maticí {summary['best_pair'][0]}"
    )
    print(f"Přesné plaintexty: {summary['exact_count']}/{len(rows)}")


if __name__ == "__main__":
    main()
