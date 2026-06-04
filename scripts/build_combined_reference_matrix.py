"""Build a reference bigram matrix from one or more cleaned Czech texts."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

for directory in (SRC_DIR, SCRIPTS_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from prepare_wikisource_text import validate_clean_text  # noqa: E402
from substitution_cipher.bigrams import get_bigrams, save_matrix, transition_matrix  # noqa: E402


CLEAN_TEXT_PATH = PROJECT_ROOT / "data" / "processed" / "clean_text.txt"
EXTRA_TEXT_PATH = PROJECT_ROOT / "data" / "reference_texts" / "valka_s_mloky_clean.txt"
COMBINED_TEXT_PATH = PROJECT_ROOT / "data" / "processed" / "combined_clean_text.txt"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "TM_ref.npy"


@dataclass(frozen=True)
class CombinedReferenceStats:
    """Summary of the combined reference matrix build."""

    reference_count: int
    text_lengths: tuple[int, ...]
    combined_text_length: int
    bigram_count: int
    matrix_shape: tuple[int, int]
    matrix_sum: float
    contains_zeros: bool


def _read_clean_text(path: Path) -> str:
    """Read and validate one cleaned reference text file."""
    text = path.read_text(encoding="utf-8").strip()
    validate_clean_text(text)
    return text.strip("_")


def build_combined_reference_matrix(
    clean_text_path: str | Path = CLEAN_TEXT_PATH,
    extra_text_path: str | Path = EXTRA_TEXT_PATH,
    combined_text_path: str | Path = COMBINED_TEXT_PATH,
    output_path: str | Path = OUTPUT_PATH,
) -> CombinedReferenceStats:
    """Create and save a reference matrix from the available cleaned texts."""
    primary_path = Path(clean_text_path)
    optional_extra_path = Path(extra_text_path)

    texts = [_read_clean_text(primary_path)]

    if optional_extra_path.exists():
        texts.append(_read_clean_text(optional_extra_path))

    combined_text = "_".join(text for text in texts if text)
    validate_clean_text(combined_text)

    combined_output = Path(combined_text_path)
    combined_output.parent.mkdir(parents=True, exist_ok=True)
    combined_output.write_text(combined_text, encoding="utf-8")

    bigrams = get_bigrams(combined_text)
    matrix = transition_matrix(bigrams, smooth_zeros=True, normalize=True)
    save_matrix(matrix, output_path)

    return CombinedReferenceStats(
        reference_count=len(texts),
        text_lengths=tuple(len(text) for text in texts),
        combined_text_length=len(combined_text),
        bigram_count=len(bigrams),
        matrix_shape=matrix.shape,
        matrix_sum=float(matrix.sum()),
        contains_zeros=bool((matrix == 0.0).any()),
    )


def main() -> None:
    """Run the combined reference matrix build with project default paths."""
    stats = build_combined_reference_matrix()

    print(f"Used reference texts: {stats.reference_count}")
    for index, text_length in enumerate(stats.text_lengths, start=1):
        print(f"Reference text {index} length: {text_length}")
    print(f"Combined text length: {stats.combined_text_length}")
    print(f"Bigram count: {stats.bigram_count}")
    print(f"Matrix shape: {stats.matrix_shape}")
    print(f"Matrix sum: {stats.matrix_sum:.12f}")
    print(f"Matrix contains zeros: {stats.contains_zeros}")
    print(f"Saved combined text to: {COMBINED_TEXT_PATH}")
    print(f"Saved matrix to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
