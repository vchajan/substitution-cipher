"""Relativní cesty používané skripty a objektovým API."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
REFERENCE_DIR = DATA_DIR / "reference"
CIPHERTEXT_DIR = DATA_DIR / "ciphertexts"
TEACHER_EXAMPLE_DIR = DATA_DIR / "teacher_example"
MODEL_DIR = PROJECT_ROOT / "models"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
REPORT_DIR = PROJECT_ROOT / "reports"
NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"

RAW_REFERENCE_TEXT_PATH = REFERENCE_DIR / "valka_s_mloky_raw.txt"
CLEAN_REFERENCE_TEXT_PATH = REFERENCE_DIR / "valka_s_mloky_clean.txt"
REFERENCE_MATRIX_PATH = MODEL_DIR / "TM_ref.npy"
