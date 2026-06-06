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
KRAKATIT_MATRIX_PATH = PROJECT_ROOT / "data" / "processed" / "TM_ref_krakatit.npy"
VALKA_MATRIX_PATH = PROJECT_ROOT / "data" / "processed" / "TM_ref_valka_s_mloky.npy"
COMBINED_MATRIX_PATH = PROJECT_ROOT / "data" / "processed" / "TM_ref_combined.npy"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "TM_ref.npy"


@dataclass(frozen=True)
class ReferenceMatrixStats:
    """Summary of one standalone reference matrix build."""

    text_length: int
    bigram_count: int
    matrix_shape: tuple[int, int]
    matrix_sum: float
    zero_count: int
    output_path: Path

    @property
    def contains_zeros(self) -> bool:
        """Return whether the matrix contains at least one zero."""
        return self.zero_count > 0


@dataclass(frozen=True)
class CombinedReferenceStats:
    """Summary of the combined reference matrix build."""

    reference_count: int
    text_lengths: tuple[int, ...]
    combined_text_length: int
    bigram_count: int
    matrix_shape: tuple[int, int]
    matrix_sum: float
    zero_count: int
    krakatit_matrix_path: Path
    combined_matrix_path: Path
    final_matrix_path: Path
    krakatit_matrix_stats: ReferenceMatrixStats
    valka_matrix_path: Path | None = None
    valka_matrix_stats: ReferenceMatrixStats | None = None

    @property
    def contains_zeros(self) -> bool:
        """Return whether the final matrix contains at least one zero."""
        return self.zero_count > 0


def _read_clean_text(path: Path) -> str:
    """Read and validate one cleaned reference text file."""
    text = path.read_text(encoding="utf-8").strip()
    validate_clean_text(text)
    return text.strip("_")


def build_reference_matrix_from_clean_text(
    text: str,
    output_path: str | Path,
) -> ReferenceMatrixStats:
    """Build and save one reference matrix from already cleaned text."""
    cleaned_text = text.strip("_")
    validate_clean_text(cleaned_text)

    bigrams = get_bigrams(cleaned_text)
    absolute_matrix = transition_matrix(bigrams)
    matrix = absolute_matrix / float(absolute_matrix.sum())
    matrix_output_path = Path(output_path)
    save_matrix(matrix, matrix_output_path)

    return ReferenceMatrixStats(
        text_length=len(cleaned_text),
        bigram_count=len(bigrams),
        matrix_shape=matrix.shape,
        matrix_sum=float(matrix.sum()),
        zero_count=int((matrix == 0.0).sum()),
        output_path=matrix_output_path,
    )


def build_single_reference_matrix(
    clean_text_path: str | Path,
    output_path: str | Path,
) -> ReferenceMatrixStats:
    """Read one clean text file and save its reference matrix."""
    return build_reference_matrix_from_clean_text(
        text=_read_clean_text(Path(clean_text_path)),
        output_path=output_path,
    )


def build_combined_reference_matrix(
    clean_text_path: str | Path = CLEAN_TEXT_PATH,
    extra_text_path: str | Path = EXTRA_TEXT_PATH,
    combined_text_path: str | Path = COMBINED_TEXT_PATH,
    output_path: str | Path | None = None,
    krakatit_matrix_path: str | Path | None = None,
    valka_matrix_path: str | Path | None = None,
    combined_matrix_path: str | Path | None = None,
) -> CombinedReferenceStats:
    """Create and save a reference matrix from the available cleaned texts."""
    primary_path = Path(clean_text_path)
    optional_extra_path = Path(extra_text_path)
    final_matrix_path = Path(output_path) if output_path is not None else OUTPUT_PATH
    krakatit_path = (
        Path(krakatit_matrix_path)
        if krakatit_matrix_path is not None
        else (
            KRAKATIT_MATRIX_PATH
            if output_path is None
            else final_matrix_path.with_name("TM_ref_krakatit.npy")
        )
    )
    valka_path = (
        Path(valka_matrix_path)
        if valka_matrix_path is not None
        else (
            VALKA_MATRIX_PATH
            if output_path is None
            else final_matrix_path.with_name("TM_ref_valka_s_mloky.npy")
        )
    )
    combined_matrix_output_path = (
        Path(combined_matrix_path)
        if combined_matrix_path is not None
        else (
            COMBINED_MATRIX_PATH
            if output_path is None
            else final_matrix_path.with_name("TM_ref_combined.npy")
        )
    )

    texts = [_read_clean_text(primary_path)]
    valka_stats: ReferenceMatrixStats | None = None

    if optional_extra_path.exists():
        extra_text = _read_clean_text(optional_extra_path)
        texts.append(extra_text)
        valka_stats = build_reference_matrix_from_clean_text(extra_text, valka_path)

    combined_text = "_".join(text for text in texts if text)
    validate_clean_text(combined_text)

    combined_output = Path(combined_text_path)
    combined_output.parent.mkdir(parents=True, exist_ok=True)
    combined_output.write_text(combined_text, encoding="utf-8")

    krakatit_stats = build_reference_matrix_from_clean_text(texts[0], krakatit_path)

    bigrams = get_bigrams(combined_text)
    absolute_matrix = transition_matrix(bigrams)
    matrix = absolute_matrix / float(absolute_matrix.sum())
    save_matrix(matrix, combined_matrix_output_path)
    save_matrix(matrix, final_matrix_path)

    return CombinedReferenceStats(
        reference_count=len(texts),
        text_lengths=tuple(len(text) for text in texts),
        combined_text_length=len(combined_text),
        bigram_count=len(bigrams),
        matrix_shape=matrix.shape,
        matrix_sum=float(matrix.sum()),
        zero_count=int((matrix == 0.0).sum()),
        krakatit_matrix_path=krakatit_path,
        combined_matrix_path=combined_matrix_output_path,
        final_matrix_path=final_matrix_path,
        krakatit_matrix_stats=krakatit_stats,
        valka_matrix_path=valka_path if valka_stats is not None else None,
        valka_matrix_stats=valka_stats,
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
    print(f"Matrix zero count: {stats.zero_count}")
    print(f"Saved combined text to: {COMBINED_TEXT_PATH}")
    print(f"Saved Krakatit matrix to: {stats.krakatit_matrix_path}")
    if stats.valka_matrix_stats is not None and stats.valka_matrix_path is not None:
        print("Valka s mloky standalone matrix:")
        print(f"  Text length: {stats.valka_matrix_stats.text_length}")
        print(f"  Bigram count: {stats.valka_matrix_stats.bigram_count}")
        print(f"  Matrix shape: {stats.valka_matrix_stats.matrix_shape}")
        print(f"  Matrix sum: {stats.valka_matrix_stats.matrix_sum:.12f}")
        print(f"  Matrix zero count: {stats.valka_matrix_stats.zero_count}")
        print(f"  Saved to: {stats.valka_matrix_path}")
    print(f"Saved combined matrix to: {stats.combined_matrix_path}")
    print(f"Saved final matrix to: {stats.final_matrix_path}")


if __name__ == "__main__":
    main()
