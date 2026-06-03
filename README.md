# Substituční šifra

Python projekt pro školní zadání: klasická substituční šifra, bigramová
přechodová matice a kryptoanalýza pomocí Metropolis-Hastings algoritmu.

Knihovna používá přesně tuto abecedu:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

Znak `_` reprezentuje mezeru.

## Struktura projektu

```text
data/
  raw/                 stažený referenční text
  processed/           clean_text.txt a TM_ref.npy
  ciphertexts/         ciphertext soubory od vyučujícího
notebooks/
  demo.ipynb           demonstrační notebook
outputs/               exportované plaintext/key soubory
reports/
  report.md            stručný report k projektu
scripts/
  prepare_wikisource_text.py
  build_reference_matrix.py
  decrypt_samples.py
src/
  substitution_cipher/ hlavní balíček podle zadání
tests/                 automatické testy
```

V repozitáři zůstává i starší skeleton `src/subcipher/`. Aktuální implementace
pro zadání je v `src/substitution_cipher/`.

## Instalace

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Hlavní logika používá standardní knihovnu Pythonu a NumPy. Matplotlib se používá
v notebooku pro vizualizaci.

## Příprava referenčního textu

Referenční text se stahuje z české Wikisource. Skript používá pouze standardní
knihovny Pythonu pro síťové požadavky a jednoduché zpracování HTML.

```powershell
python scripts\prepare_wikisource_text.py
```

Výstupy:

```text
data/raw/raw_text.txt
data/processed/clean_text.txt
```

Vyčištěný text obsahuje pouze znaky `A-Z` a `_`.

## Vytvoření referenční matice

```powershell
python scripts\build_reference_matrix.py
```

Výstup:

```text
data/processed/TM_ref.npy
```

Matice se vytváří z absolutních četností bigramů. Nulové buňky se nahradí
hodnotou `1` a potom se matice normalizuje tak, aby její součet byl `1`.

Aktuálně ověřené hodnoty:

```text
Text length: 434711
Bigram count: 434710
Matrix shape: (27, 27)
Matrix sum: 1.000000000000
```

## Spuštění testů

```powershell
pytest
```

Pokud by konkrétní instalace Windows měla zamčený dočasný adresář pytestu, lze
použít i tento náhradní příkaz:

```powershell
pytest --basetemp="$env:TEMP\substitution_cipher_pytest_tmp" -o cache_dir="$env:TEMP\substitution_cipher_pytest_cache"
```

Testy projektu samy nepoužívají `tmp_path`, takže běžné `pytest` by mělo v
čistém prostředí fungovat.

## Spuštění notebooku

```powershell
jupyter notebook notebooks\demo.ipynb
```

Notebook ukazuje:

- import knihovny,
- použitou abecedu,
- šifrování a dešifrování,
- načtení nebo vytvoření `TM_ref.npy`,
- kontrolu tvaru a součtu matice,
- vizualizaci bigramové matice pomocí Matplotlib,
- krátkou ukázku kryptoanalýzy,
- export plaintextu a klíče.

V notebooku je kvůli rychlosti použito méně iterací. Pro finální dešifrování
souborů ze zadání se používá 20 000 iterací na jeden ciphertext.

Export notebooku do HTML:

```powershell
jupyter nbconvert --to html notebooks\demo.ipynb
```

Pokud `jupyter` nebo `nbconvert` nejsou nainstalované, export se provede až po
jejich instalaci.

## Dešifrování vzorků od vyučujícího

Ciphertext soubory vložte do:

```text
data/ciphertexts/
```

Očekávaný formát názvu:

```text
text_{length}_sample_{id}_ciphertext.txt
```

Spuštění:

```powershell
python scripts\decrypt_samples.py --iterations 20000
```

Skript implicitně načte `data/processed/TM_ref.npy`, pro každý ciphertext spustí
`prolom_substitute(..., iter=20000)` a uloží výstupy do `outputs/`.

Pro krátkou kontrolu bez reálného dešifrování lze použít:

```powershell
python scripts\decrypt_samples.py --iterations 1 --seed 1
```

Pokud vstupní složka chybí nebo je prázdná, skript pouze vypíše jasnou hlášku a
nespadne. Falešné plaintext/key výstupy nevytváří.

## Exportované soubory

Plaintext a klíč se ukládají samostatně:

```text
text_{délka_textu}_sample_{id textu}_plaintext.txt
text_{délka_textu}_sample_{id textu}_key.txt
```

Každý soubor obsahuje pouze samotný plaintext nebo samotný klíč.

## Základní použití knihovny

```python
from substitution_cipher import ALPHABET, substitute_decrypt, substitute_encrypt

key = ALPHABET[3:] + ALPHABET[:3]
plaintext = "BYL_POZDNI_VECER"

ciphertext = substitute_encrypt(plaintext, key)
decrypted = substitute_decrypt(ciphertext, key)
```

## Finální odevzdání

1. Připravit referenční text:

```powershell
python scripts\prepare_wikisource_text.py
```

2. Vytvořit referenční matici:

```powershell
python scripts\build_reference_matrix.py
```

3. Spustit testy:

```powershell
pytest
```

4. Exportovat notebook do HTML:

```powershell
jupyter nbconvert --to html notebooks\demo.ipynb
```

5. Po dodání ciphertextů od vyučujícího je vložit do:

```text
data/ciphertexts/
```

6. Spustit finální dešifrování:

```powershell
python scripts\decrypt_samples.py --iterations 20000
```

7. Výstupy budou v:

```text
outputs/
```

ve formátu:

```text
text_{délka_textu}_sample_{id textu}_plaintext.txt
text_{délka_textu}_sample_{id textu}_key.txt
```
