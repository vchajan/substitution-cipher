# Substituční šifra a kryptoanalýza

Tento projekt vznikl jako školní práce zaměřená na klasickou substituční šifru. Cílem bylo vytvořit vlastní Python knihovnu, která umí text zašifrovat, dešifrovat a následně se pokusit zašifrovaný text automaticky prolomit pomocí statistické analýzy jazyka.

Projekt pracuje s pevně danou abecedou:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

Znak `_` nahrazuje mezeru. Jiná abeceda se v projektu nepoužívá.

---

## Rychlé spuštění ve Windows

Nejjednodušší postup:

1. Dvojklik na `install.bat`.
2. Dvojklik na `run.bat`.

Nebo v příkazovém řádku Windows (`cmd`) z kořenové složky projektu:

```cmd
install
run
```

V PowerShellu lze případně použít `.\install.bat` a `.\run.bat`.

Soubor `install.bat` vytvoří virtuální prostředí `.venv`, aktualizuje `pip` a nainstaluje projekt včetně vývojových závislostí.

Soubor `run.bat` aktivuje `.venv`, vytvoří referenční matici, spustí testy a potom spustí finální dešifrování příkazem `python scripts\decrypt_samples.py --iterations 20000`. Pokud ve složce `data/ciphertexts/` zatím nejsou ciphertext soubory, je to v pořádku; skript jen vypíše informační hlášku.

Pokročilé technické příkazy jsou uvedené níže.

---

## Co projekt obsahuje

Projekt obsahuje tyto hlavní části:

```text
data/
  raw/                 původní stažený referenční text
  processed/           vyčištěný text a referenční matice
  ciphertexts/         zašifrované texty od vyučujícího

notebooks/
  demo.ipynb           demonstrační Jupyter Notebook

reports/
  report.md            stručný report k projektu

install.bat            rychlá instalace ve Windows
run.bat                rychlé spuštění ve Windows

scripts/
  prepare_wikisource_text.py
  build_reference_matrix.py
  decrypt_samples.py

src/
  substitution_cipher/ hlavní Python knihovna

tests/
  automatické testy
```

Hlavní implementace je ve složce:

```text
src/substitution_cipher/
```

Starší skeleton `src/subcipher/` může v repozitáři zůstat, ale aktuální řešení pro zadání je v `src/substitution_cipher/`.

---

## Pokročilá instalace

Nejprve je vhodné vytvořit virtuální prostředí:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Potom nainstalovat projekt:

```powershell
pip install -e ".[dev]"
```

Jádro projektu používá hlavně standardní knihovny Pythonu a knihovnu NumPy. Matplotlib se používá v notebooku pro jednoduchou vizualizaci.

---

## Příprava referenčního textu

Pro vytvoření jazykového modelu češtiny se používá český text z Wikisource. V tomto projektu je použit román **Krakatit**.

Text se stáhne a vyčistí pomocí skriptu:

```powershell
python scripts\prepare_wikisource_text.py
```

Skript vytvoří soubory:

```text
data/raw/raw_text.txt
data/processed/clean_text.txt
```

Vyčištěný text obsahuje pouze znaky:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

Při čištění se odstraní diakritika, interpunkce, čísla a nepovolené znaky. Mezery a konce řádků se převedou na `_`.

---

## Vytvoření referenční bigramové matice

Referenční matice se vytvoří z vyčištěného textu:

```powershell
python scripts\build_reference_matrix.py
```

Výstupem je soubor:

```text
data/processed/TM_ref.npy
```

Matice se vytváří tak, že se nejprve spočítají absolutní četnosti bigramů. Potom se nulové hodnoty nahradí hodnotou `1`, aby při výpočtu nevznikal problém s `log(0)`. Nakonec se matice převede na relativní pravděpodobnosti, takže součet všech hodnot v matici je `1`.

Aktuálně ověřené hodnoty:

```text
Text length: 434711
Bigram count: 434710
Matrix shape: (27, 27)
Matrix sum: 1.000000000000
```

---

## Spuštění testů

Testy se spustí příkazem:

```powershell
pytest
```

V otestovaném stavu projekt prošel s výsledkem:

```text
24 passed
```

Pokud by na Windows nastal problém se zamčenou dočasnou složkou pytestu, dá se použít i tento příkaz:

```powershell
pytest --basetemp="$env:TEMP\substitution_cipher_pytest_tmp" -o cache_dir="$env:TEMP\substitution_cipher_pytest_cache"
```

---

## Ukázkový notebook

Demonstrační notebook je v souboru:

```text
notebooks/demo.ipynb
```

Notebook ukazuje:

- použitou abecedu,
- šifrování a dešifrování,
- načtení referenčního textu,
- vytvoření nebo načtení bigramové matice,
- kontrolu tvaru a součtu matice,
- jednoduchou vizualizaci matice,
- ukázku kryptoanalýzy,
- export nalezeného plaintextu a klíče.

Notebook používá menší počet iterací, aby se ukázka dala spustit rychle. Pro finální dešifrování se podle zadání používá 20 000 iterací na každý ciphertext.

Notebook lze exportovat do HTML pomocí:

```powershell
jupyter nbconvert --to html notebooks\demo.ipynb
```

Pokud příkaz `jupyter` není dostupný, je potřeba nejdříve doinstalovat Jupyter/nbconvert.

---

## Kryptoanalýza

Prolomení šifry je řešeno pomocí algoritmu Metropolis-Hastings. Algoritmus začne s náhodným klíčem a v každé iteraci vytvoří nový kandidátní klíč prohozením dvou náhodných znaků.

Každý kandidátní klíč se použije k dešifrování textu. Výsledek se ohodnotí pomocí referenční bigramové matice. Pokud je nový výsledek lepší, algoritmus ho přijme. Pokud je horší, může ho přijmout s pravděpodobností `0.01`, aby se nezasekl v horším mezivýsledku.

Po skončení M-H běhu lze volitelně provést lokální dolaďování klíče pomocí systematického zkoušení všech prohození dvou znaků. Tento krok nepoužívá známý plaintext, jen stejnou funkci věrohodnosti jako hlavní algoritmus.

Hlavní funkce pro kryptoanalýzu je:

```python
prolom_substitute(text, TM_ref, iter=20000)
```

---

## Dešifrování textů od vyučujícího

Zašifrované texty od vyučujícího se vloží do složky:

```text
data/ciphertexts/
```

Očekávaný název souboru je:

```text
text_{length}_sample_{id}_ciphertext.txt
```

Finální dešifrování se spustí příkazem:

```powershell
python scripts\decrypt_samples.py --iterations 20000
```

Skript načte referenční matici z:

```text
data/processed/TM_ref.npy
```

a výsledky uloží do složky:

```text
outputs/
```

Pokud složka `data/ciphertexts/` zatím neobsahuje žádné soubory, skript pouze vypíše informaci a neskončí chybou.

---

## Export výsledků

Pro každý dešifrovaný text se uloží dva soubory:

```text
text_{délka_textu}_sample_{id textu}_plaintext.txt
text_{délka_textu}_sample_{id textu}_key.txt
```

Soubor s plaintextem obsahuje pouze dešifrovaný text. Soubor s klíčem obsahuje pouze nalezený klíč.

---

## Report

Stručný report k projektu je v souboru:

```text
reports/report.md
```

Report popisuje:

- cíl práce,
- princip substituční šifry,
- přípravu referenčního textu,
- čištění textu,
- bigramy,
- přechodovou matici,
- výpočet věrohodnosti,
- Metropolis-Hastings algoritmus,
- export výsledků,
- testování a dosažené výsledky.

---

## Základní použití knihovny

```python
from substitution_cipher import ALPHABET, substitute_encrypt, substitute_decrypt

key = ALPHABET[3:] + ALPHABET[:3]
plaintext = "BYL_POZDNI_VECER"

ciphertext = substitute_encrypt(plaintext, key)
decrypted = substitute_decrypt(ciphertext, key)

print(ciphertext)
print(decrypted)
```

---

## Finální odevzdání

Před odevzdáním je vhodné zkontrolovat tento postup:

```powershell
python scripts\prepare_wikisource_text.py
python scripts\build_reference_matrix.py
pytest
```

Notebook lze exportovat do HTML:

```powershell
jupyter nbconvert --to html notebooks\demo.ipynb
```

Po dodání reálných ciphertextů od vyučujícího:

```powershell
python scripts\decrypt_samples.py --iterations 20000
```

K odevzdání patří hlavně:

- zdrojový kód knihovny,
- demonstrační notebook nebo jeho HTML/PDF export,
- stručný report,
- exportované plaintexty a klíče, pokud už jsou dostupné vstupní ciphertexty.
