# Substituční šifra a kryptoanalýza

Školní projekt pro klasickou substituční šifru, bigramovou referenční matici a
kryptoanalýzu pomocí Metropolis-Hastings algoritmu.

Projekt používá abecedu:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

Znak `_` reprezentuje mezeru.

## Rychlé spuštění ve Windows

Nejjednodušší postup:

1. Dvojklik na `install.bat`.
2. Dvojklik na `run.bat`.

Soubor `install.bat` vytvoří virtuální prostředí `.venv`, aktualizuje `pip` a
nainstaluje projekt včetně vývojových závislostí.

Soubor `run.bat` aktivuje `.venv`, zkontroluje zadávací soubory, vytvoří
kombinovanou referenční matici, spustí testy, dešifruje ciphertexty ze složky
`data/ciphertexts/` a vytvoří vyhodnocení.

V příkazovém řádku Windows (`cmd`) lze použít:

```cmd
install
run
```

V PowerShellu lze případně použít:

```powershell
.\install.bat
.\run.bat
```

## Kde jsou data a výsledky

```text
data/ciphertexts/                  60 učitelských ciphertextů
data/teacher_example/              učitelský příklad plaintext/key pro text_1000_sample_1
data/reference_texts/              druhý referenční text: Válka s mloky
data/processed/clean_text.txt      původní vyčištěný Krakatit
data/processed/combined_clean_text.txt
data/processed/TM_ref.npy          finální referenční bigramová matice
outputs/                           exportované plaintexty a key soubory
notebooks/demo.ipynb               demonstrační notebook
notebooks/demo.html                HTML export notebooku
reports/report.md                  finální report
reports/evaluation_summary.md      vyhodnocení výstupů
reports/evaluation_summary.csv     tabulka vyhodnocení výstupů
```

Učitelské ciphertexty mají názvy:

```text
text_{length}_sample_{sample_id}_ciphertext.txt
```

Použité délky jsou `250`, `500` a `1000`, pro každou délku sample ID `1` až
`20`.

Výstupy mají formát:

```text
text_{délka_textu}_sample_{id textu}_plaintext.txt
text_{délka_textu}_sample_{id textu}_key.txt
```

## Technické spuštění

Po instalaci lze celý finální postup spustit ručně:

```powershell
python scripts\validate_assignment_files.py
python scripts\build_combined_reference_matrix.py
pytest
python scripts\decrypt_samples.py --iterations 20000
python scripts\evaluate_outputs.py
python -m jupyter nbconvert --to html notebooks\demo.ipynb
```

Pokud není dostupný Jupyter/nbconvert, poslední příkaz se provede až po jeho
instalaci.

## Referenční texty

Základní referenční text je vyčištěný **Krakatit**:

```text
data/processed/clean_text.txt
```

Druhý referenční text je vyčištěná **Válka s mloky**:

```text
data/reference_texts/valka_s_mloky_clean.txt
```

Pro finální bigramovou matici se používá spojený referenční text. Skript
`scripts/build_combined_reference_matrix.py` načte Krakatit, připojí Válku s
mloky, pokud je dostupná, spojí texty přes jeden znak `_`, uloží
`data/processed/combined_clean_text.txt` a vytvoří `data/processed/TM_ref.npy`.

Aktuální hodnoty:

```text
Used reference texts: 2
Reference text 1 length: 434711
Reference text 2 length: 381660
Combined text length: 816372
Bigram count: 816371
Matrix shape: (27, 27)
Matrix sum: 1.000000000000
Matrix contains zeros: False
```

## Kryptoanalýza

Prolomení šifry řeší funkce:

```python
prolom_substitute(text, TM_ref, iter=20000)
```

Algoritmus používá Metropolis-Hastings:

- začne s náhodným klíčem,
- v každé iteraci prohodí dva náhodné znaky v klíči,
- lepší kandidát přijme vždy,
- horší kandidát přijme s pravděpodobností `0.01`,
- uchovává nejlepší nalezený klíč a plaintext.

Po M-H běhu lze použít `polish_key`, které bez znalosti plaintextu systematicky
zkouší všechny výměny dvou znaků a přijímá jen zlepšení podle stejné
věrohodnosti.

## Ověření výsledků

Validace vstupů a výstupů:

```powershell
python scripts\validate_assignment_files.py
```

Aktuální stav:

```text
Status: OK
ciphertext_files: 60
output_plaintext_files: 60
output_key_files: 60
```

Vyhodnocení výstupů:

```powershell
python scripts\evaluate_outputs.py
```

Pro učitelský příklad `text_1000_sample_1`:

```text
Plaintext přesně sedí: True
Správné znaky: 1000
Procento shody: 100.000000
Key přesně sedí: False
```

Nalezený klíč i učitelský klíč dešifrují daný ciphertext na stejný plaintext.
Rozdíl je v několika znacích, které se v tomto konkrétním ciphertextu
nevyskytují.

## Testy

```powershell
pytest
```

Aktuální výsledek:

```text
29 passed
```

## Notebook a report

Notebook:

```text
notebooks/demo.ipynb
notebooks/demo.html
```

Report:

```text
reports/report.md
reports/evaluation_summary.md
reports/evaluation_summary.csv
```

## Struktura projektu

```text
data/
  ciphertexts/
  processed/
  raw/
  reference_texts/
  teacher_example/
notebooks/
outputs/
reports/
scripts/
src/substitution_cipher/
tests/
install.bat
run.bat
```

Starší skeleton `src/subcipher/` může v repozitáři zůstat, ale aktuální řešení
pro zadání je ve složce `src/substitution_cipher/`.
