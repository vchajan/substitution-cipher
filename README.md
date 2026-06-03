# Substitution Cipher

Python project for a school assignment: classical substitution cipher,
bigram transition matrix, and Metropolis-Hastings cryptanalysis.

The library uses exactly this alphabet:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

The `_` character represents a space.

## Project Structure

```text
data/
  raw/                 raw downloaded reference text
  processed/           clean_text.txt and TM_ref.npy
  ciphertexts/         ciphertext files from the teacher
notebooks/
  demo.ipynb           demonstration notebook
outputs/               exported plaintext/key files
reports/
  report.md            short project report
scripts/
  prepare_wikisource_text.py
  build_reference_matrix.py
  decrypt_samples.py
src/
  substitution_cipher/ main package for the assignment
tests/                 automated tests
```

The repository also contains the older `src/subcipher/` skeleton. The current
assignment-facing implementation is in `src/substitution_cipher/`.

## Installation

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Minimal dependencies are standard library plus NumPy for the core logic.
Matplotlib is used in the notebook for visualization.

## Prepare Reference Text

The reference text is downloaded from Czech Wikisource. The script uses only
Python standard library networking and HTML parsing.

```powershell
python scripts\prepare_wikisource_text.py
```

Outputs:

```text
data/raw/raw_text.txt
data/processed/clean_text.txt
```

The cleaned text contains only `A-Z` and `_`.

## Build Reference Matrix

```powershell
python scripts\build_reference_matrix.py
```

Output:

```text
data/processed/TM_ref.npy
```

The matrix is built from absolute bigram counts. Zero cells are replaced by
`1`, then the matrix is normalized so its total sum is `1`.

Current validated values:

```text
Text length: 434711
Bigram count: 434710
Matrix shape: (27, 27)
Matrix sum: 1.000000000000
```

## Run Tests

```powershell
pytest
```

If a local Windows installation still has a locked pytest temp directory, this
fallback also works:

```powershell
pytest --basetemp="$env:TEMP\substitution_cipher_pytest_tmp" -o cache_dir="$env:TEMP\substitution_cipher_pytest_cache"
```

The project tests themselves avoid pytest `tmp_path`, so ordinary `pytest`
should work in a clean environment.

## Run Notebook

```powershell
jupyter notebook notebooks\demo.ipynb
```

The notebook demonstrates:

- importing the library,
- the project alphabet,
- encryption and decryption,
- loading or building `TM_ref.npy`,
- checking matrix shape and sum,
- visualizing the bigram matrix with Matplotlib,
- a short cryptanalysis example,
- exporting plaintext and key files.

The notebook uses a small iteration count for speed. For final assignment
decryptions use 20,000 iterations per ciphertext.

## Decrypt Teacher Samples

Put ciphertext files into:

```text
data/ciphertexts/
```

Expected filename format:

```text
text_{length}_sample_{id}_ciphertext.txt
```

Run:

```powershell
python scripts\decrypt_samples.py
```

By default the script reads `data/processed/TM_ref.npy`, runs
`prolom_substitute(..., iter=20000)`, and writes exports to `outputs/`.

For a shorter test run:

```powershell
python scripts\decrypt_samples.py --iterations 200 --seed 42
```

If the input directory is missing or empty, the script prints a clear message
and exits without failing.

## Exported Files

Plaintext and key are written separately:

```text
text_{delka_textu}_sample_{id textu}_plaintext.txt
text_{delka_textu}_sample_{id textu}_key.txt
```

Each file contains only the plaintext or only the key.

## Basic Library Usage

```python
from substitution_cipher import ALPHABET, substitute_decrypt, substitute_encrypt

key = ALPHABET[3:] + ALPHABET[:3]
plaintext = "BYL_POZDNI_VECER"

ciphertext = substitute_encrypt(plaintext, key)
decrypted = substitute_decrypt(ciphertext, key)
```
