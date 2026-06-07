# Substituční šifra

Python projekt pro šifrování, dešifrování a kryptoanalýzu klasické monoalfabetické substituční šifry. Řešení používá abecedu `ABCDEFGHIJKLMNOPQRSTUVWXYZ_`, kde `_` představuje mezeru. Referenční jazykový model je vytvořen pouze z knihy **Válka s mloky**.

## Nejjednodušší spuštění

Ve Windows stačí dvojklik:

```text
install.bat
run.bat
```

Nebo z terminálu:

```powershell
.\install.bat
.\run.bat
```

`install.bat` vytvoří virtuální prostředí a nainstaluje projekt. `run.bat` připraví referenční text, vytvoří matici `models/TM_ref.npy`, spustí testy, zkontroluje soubory zadání, spustí dešifrování a vytvoří vyhodnocení.

## Struktura projektu

```text
src/substitution_cipher/     knihovní logika
scripts/                     spustitelné pomocné skripty
data/reference/              surový a vyčištěný text Války s mloky
data/ciphertexts/            ciphertexty ze zadání
data/teacher_example/        známý kontrolní příklad
models/                      referenční matice
outputs/                     vygenerované plaintexty a klíče
notebooks/                   demonstrační notebook a HTML export
reports/                     reporty a tabulkové souhrny
tests/                       automatické testy
```

V `data/` jsou pouze textová data. Vygenerovaná matice je v `models/TM_ref.npy`.

## Instalace knihovny

```powershell
python -m pip install -e ".[dev]"
```

Po instalaci lze importovat přímo balíček:

```python
from substitution_cipher import SubstitutionCipher
```

## Povinné funkční API

Zadání vyžaduje tyto veřejné funkce:

```python
substitute_encrypt(plaintext, key)
substitute_decrypt(ciphertext, key)
get_bigrams(text)
transition_matrix(bigrams)
plausibility(text, TM_ref)
prolom_substitute(text, TM_ref, iter, start_key=None)
```

Jsou dostupné přímo z balíčku:

```python
from substitution_cipher import (
    get_bigrams,
    plausibility,
    prolom_substitute,
    substitute_decrypt,
    substitute_encrypt,
    transition_matrix,
)
```

## Šifrování a dešifrování

Klíč je permutace celé abecedy o délce 27. Každý znak plaintextu se nahradí znakem na stejné pozici v klíči.

```python
from substitution_cipher import ALPHABET, substitute_decrypt, substitute_encrypt

key = ALPHABET[1:] + ALPHABET[:1]
plaintext = "AHOJ_SVETE"

ciphertext = substitute_encrypt(plaintext, key)
decrypted = substitute_decrypt(ciphertext, key)
```

Objektové API používá stejné funkce:

```python
from substitution_cipher import SubstitutionCipher

cipher = SubstitutionCipher()
ciphertext = cipher.encrypt("AHOJ_SVETE", key)
plaintext = cipher.decrypt(ciphertext, key)
```

## Příprava Války s mloky

Surový text se získává z českých Wikizdrojů přes MediaWiki API:

```text
https://cs.wikisource.org/w/api.php
```

Použitá stránka díla je `Válka_s_Mloky`. Stažení a čištění jsou oddělené kroky:

```powershell
python scripts\download_reference_text.py
python scripts\prepare_reference_text.py
python scripts\build_reference_matrix.py
```

`download_reference_text.py` stáhne vlastní obsah díla a uloží ho jako UTF-8. Bez `--force` nepřepisuje už existující lokální soubor.

`prepare_reference_text.py` odstraní diakritiku, převede text na velká písmena, oddělovače převede na `_` a ponechá pouze `A-Z_`.

`build_reference_matrix.py` vytvoří finální bigramovou matici `models/TM_ref.npy`.

Surový text je uložen zde:

```text
data/reference/valka_s_mloky_raw.txt
```

Vyčištěný text vznikne příkazem:

```powershell
python scripts\prepare_reference_text.py
```

Výstup:

```text
data/reference/valka_s_mloky_clean.txt
```

Pokud už soubor existuje, není potřeba knihu stahovat znovu.

## Referenční matice

Matici vytvoří:

```powershell
python scripts\build_reference_matrix.py
```

Výstup:

```text
models/TM_ref.npy
```

Postup odpovídá zadání: nejprve se spočítají absolutní bigramy, nulové buňky se nahradí hodnotou `1` a teprve potom se matice normalizuje na relativní pravděpodobnosti.

## Kryptoanalýza

Základní funkce:

```python
from substitution_cipher import prolom_substitute
from substitution_cipher.io_utils import load_matrix

TM_ref = load_matrix("models/TM_ref.npy")
key, plaintext, score = prolom_substitute(ciphertext, TM_ref, iter=20_000)
```

Metropolis-Hastingsův algoritmus v každém kroku prohodí dva náhodné znaky v klíči. Lepší kandidát se přijme vždy, horší kandidát se přijme s pravděpodobností `0.01`.

Volitelné rozšíření `polish_key` po M-H běhu systematicky zkouší všechny dvojice znaků a přijme jen zlepšující výměny.

## Objektové API

```python
from substitution_cipher import SubstitutionCipher

cipher = SubstitutionCipher.from_matrix_file("models/TM_ref.npy")
result = cipher.crack(ciphertext, iterations=20_000)

print(result.plaintext)
print(result.key)
print(result.score)
```

`CrackResult` obsahuje:

```text
plaintext
key
score
restart
iterations
```

## Dešifrování souborů

Jeden soubor lze zpracovat přes objektové API:

```python
from substitution_cipher import SubstitutionCipher

cipher = SubstitutionCipher.from_matrix_file("models/TM_ref.npy")
cipher.crack_file(
    "data/ciphertexts/text_1000_sample_1_ciphertext.txt",
    "outputs",
    iterations=20_000,
)
```

Celou složku zpracuje CLI:

```powershell
python scripts\decrypt_samples.py `
  --matrix models\TM_ref.npy `
  --input-directory data\ciphertexts `
  --output-directory outputs `
  --iterations 20000 `
  --restarts 1 `
  --workers 1
```

Výstupy mají tvar:

```text
text_{délka_textu}_sample_{id_textu}_plaintext.txt
text_{délka_textu}_sample_{id_textu}_key.txt
```

## CLI argumenty

`scripts/decrypt_samples.py` podporuje:

```text
--matrix
--input-directory
--output-directory
--iterations
--restarts
--seed
--no-polish
--workers
```

Výchozí nastavení používá `models/TM_ref.npy`, vstup `data/ciphertexts/`, výstup `outputs/`, `20000` iterací a jeden restart.

## Paralelní zpracování

Ciphertext soubory jsou na sobě nezávislé, proto je lze zpracovat více procesy. Paralelizují se pouze celé soubory, nikoli restarty ani jednotlivé iterace Metropolis-Hastingsova algoritmu.

```powershell
# Sekvenčně
python scripts\decrypt_samples.py --workers 1

# Automatický počet procesů
python scripts\decrypt_samples.py --workers 0

# Přesně čtyři procesy
python scripts\decrypt_samples.py --workers 4
```

Hodnota `--workers 0` použije bezpečný automatický režim `min(6, max(1, os.cpu_count() - 1))`. Vyšší počet procesů může zrychlit zpracování více souborů, ale zvýší zatížení procesoru a spotřebu paměti. Počet iterací, počet restartů, M-H algoritmus ani výstupní formát se tím nemění.

Finální paralelní běh například:

```powershell
python scripts\decrypt_samples.py `
  --matrix models\TM_ref.npy `
  --input-directory data\ciphertexts `
  --output-directory outputs `
  --iterations 20000 `
  --restarts 1 `
  --workers 6
```

## Testování

```powershell
pytest
```

Testy kontrolují povinné podpisy funkcí, matici, objektové API, strukturu složek, skripty i dokumentaci.

## Notebook a report

Demonstrační notebook:

```text
notebooks/demo.ipynb
```

Textový report:

```text
reports/report.md
```

Notebook je vysvětlující a nespouští dlouhé zpracování všech 60 ciphertextů.
HTML export se vytvoří po instalaci Jupyter příkazem:

```powershell
jupyter nbconvert --to html notebooks\demo.ipynb
```

Výsledný soubor bude `notebooks/demo.html`.

## Časté problémy

Pokud chybí `models/TM_ref.npy`, spusť:

```powershell
python scripts\prepare_reference_text.py
python scripts\build_reference_matrix.py
```

Pokud `data/ciphertexts/` neobsahuje soubory, `decrypt_samples.py` pouze vypíše hlášku a neskončí chybou.

Pokud není dostupný Jupyter, notebook lze stále otevřít jako `.ipynb`; HTML export vznikne po instalaci vývojových závislostí.

## Omezení

Kryptoanalýza je náhodná metoda. Kratší ciphertexty mají méně bigramů a bývají obtížnější. Bigramový model hodnotí jazykovou věrohodnost, nezná správný plaintext. Některé znaky se v ciphertextu nemusí objevit, takže celý klíč nemusí být jednoznačně určitelný.
