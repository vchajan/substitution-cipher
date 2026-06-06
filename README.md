# Substituční šifra

Python knihovna pro šifrování, dešifrování a automatickou kryptoanalýzu klasické substituční šifry. Jazykový model je postavený na bigramech a hledání klíče probíhá pomocí algoritmu Metropolis–Hastings.

Projekt umí pracovat s jedním textem i s celou sadou souborů. Součástí jsou také nástroje pro přípravu referenčního textu, tvorbu přechodové matice, export výsledků, validaci dat a vyhodnocení úspěšnosti.

## Hlavní možnosti

- šifrování a dešifrování substitučním klíčem,
- vytvoření bigramů a přechodové matice,
- výpočet věrohodnosti kandidátního plaintextu,
- automatické hledání klíče pomocí Metropolis–Hastings algoritmu,
- více nezávislých restartů a následné lokální doladění klíče,
- zpracování jednoho souboru nebo celého adresáře,
- export plaintextu a nalezeného klíče,
- validace vstupů, výstupů a referenčních matic.

Knihovna používá pevnou abecedu:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

Podtržítko `_` představuje mezeru. Texty určené ke zpracování musí obsahovat pouze znaky z této abecedy.

---

## Rychlé spuštění ve Windows

Pro běžné spuštění není potřeba zadávat žádné příkazy ručně:

1. spusťte `install.bat`,
2. po dokončení spusťte `run.bat`.

`install.bat` vytvoří virtuální prostředí a nainstaluje potřebné závislosti. `run.bat` následně zkontroluje data, spustí testy, dešifruje připravené ciphertexty a vytvoří souhrn výsledků.

Z PowerShellu lze oba soubory spustit také takto:

```powershell
.\install.bat
.\run.bat
```

---

## Instalace

### Běžné použití

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

### Vývoj, testy a Jupyter Notebook

```powershell
pip install -e ".[dev]"
```

Instalace s parametrem `-e` používá editovatelný režim. Změny ve zdrojovém kódu se tak projeví bez opakované instalace balíčku.

---

## Rychlý příklad

Nejjednodušší způsob použití nabízí třída `SubstitutionCipher`.

```python
from substitution_cipher import SubstitutionCipher

cipher = SubstitutionCipher.from_matrix_file(
    "data/processed/TM_ref_krakatit.npy"
)

ciphertext = "..."

result = cipher.crack(
    ciphertext,
    iterations=10_000,
    restarts=2,
)

print(result.plaintext)
print(result.key)
print(result.score)
```

Metoda `crack()` vrací objekt `CrackResult`:

- `plaintext` – nejlepší nalezený dešifrovaný text,
- `key` – nalezený substituční klíč,
- `score` – výsledné plausibility skóre,
- `restart` – číslo restartu, ve kterém byl nejlepší výsledek nalezen,
- `iterations` – počet iterací použitý v jednom restartu.

---

## Šifrování a dešifrování

```python
from substitution_cipher import SubstitutionCipher

cipher = SubstitutionCipher()

key = "DEFGHIJKLMNOPQRSTUVWXYZ_ABC"
plaintext = "BYL_POZDNI_VECER"

ciphertext = cipher.encrypt(plaintext, key)
decrypted = cipher.decrypt(ciphertext, key)

print(ciphertext)
print(decrypted)
```

Klíč musí být platnou permutací celé abecedy:

- má délku 27 znaků,
- obsahuje právě znaky `ABCDEFGHIJKLMNOPQRSTUVWXYZ_`,
- každý znak se v něm objeví právě jednou.

Při neplatném klíči nebo nepovolených znacích knihovna vyvolá `ValueError`.

---

## Práce s referenční maticí

Referenční matice popisuje, jak často po jednom znaku následuje jiný znak v českém textu. Lze ji načíst ze souboru nebo vytvořit přímo z připraveného textu.

### Načtení existující matice

```python
from substitution_cipher import SubstitutionCipher

cipher = SubstitutionCipher.from_matrix_file(
    "data/processed/TM_ref_krakatit.npy"
)
```

### Vytvoření nové matice

```python
from substitution_cipher import SubstitutionCipher

cipher = SubstitutionCipher()

reference_text = "TOTO_JE_DLOUHY_VYCISTENY_CESKY_TEXT"
matrix = cipher.build_reference_matrix(reference_text)

cipher.save_reference_matrix("data/processed/custom_matrix.npy")
```

Výsledná matice má rozměr `27 × 27`, neobsahuje nulové pravděpodobnosti a její součet je roven 1.

### Ohodnocení textu

```python
score = cipher.score("TOTO_JE_KANDIDATNI_TEXT")
print(score)
```

Vyšší skóre znamená, že se bigramová struktura textu více podobá referenční češtině.

---

## Kryptoanalýza jednoho souboru

```python
from substitution_cipher import SubstitutionCipher

cipher = SubstitutionCipher.from_matrix_file(
    "data/processed/TM_ref_krakatit.npy"
)

result = cipher.crack_file(
    "data/ciphertexts/text_1000_sample_1_ciphertext.txt",
    "outputs",
    iterations=10_000,
    restarts=2,
)
```

Pro uvedený vstup vzniknou soubory:

```text
outputs/text_1000_sample_1_plaintext.txt
outputs/text_1000_sample_1_key.txt
```

Název vstupního souboru musí odpovídat formátu:

```text
text_{délka}_sample_{id}_ciphertext.txt
```

---

## Zpracování celého adresáře

```python
results = cipher.crack_directory(
    "data/ciphertexts",
    "outputs",
    iterations=10_000,
    restarts=2,
)
```

Metoda automaticky:

1. najde všechny odpovídající ciphertext soubory,
2. seřadí je podle délky a ID vzorku,
3. každý text dešifruje,
4. uloží plaintext a klíč do výstupního adresáře,
5. vrátí seznam objektů `CrackResult`.

Pokud vstupní adresář neexistuje nebo neobsahuje žádné vhodné soubory, metoda vrátí prázdný seznam a vypíše informativní zprávu.

---

## Funkční API

Vedle objektového rozhraní zůstávají veřejně dostupné také samostatné funkce. Jsou vhodné pro jednodušší skripty, výuku nebo přímé testování jednotlivých částí algoritmu.

```python
import substitution_cipher as sc

ciphertext = sc.substitute_encrypt(plaintext, key)
plaintext = sc.substitute_decrypt(ciphertext, key)

bigrams = sc.get_bigrams(plaintext)
absolute_matrix = sc.transition_matrix(bigrams)
score = sc.plausibility(plaintext, reference_matrix)

key, plaintext, score = sc.prolom_substitute(
    encrypted_text,
    reference_matrix,
    20_000,
    None,
)
```

Veřejné funkce:

```python
substitute_encrypt(plaintext, key)
substitute_decrypt(ciphertext, key)
get_bigrams(text)
transition_matrix(bigrams)
plausibility(text, TM_ref)
prolom_substitute(text, TM_ref, iter, start_key=None)
```

Třída `SubstitutionCipher` tyto funkce pouze spojuje do pohodlnějšího rozhraní. Samotná šifrovací a kryptoanalytická logika není v projektu implementována dvakrát.

---

## Přehled objektového API

### `SubstitutionCipher(reference_matrix=None)`

Vytvoří instanci knihovny. Referenční matici lze dodat rovnou nebo ji načíst později.

### `SubstitutionCipher.from_matrix_file(path)`

Načte matici ve formátu `.npy` a vrátí připravenou instanci.

### `encrypt(plaintext, key)`

Zašifruje plaintext pomocí zadaného substitučního klíče.

### `decrypt(ciphertext, key)`

Dešifruje ciphertext pomocí inverzního mapování klíče.

### `bigrams(text)`

Vrátí všechny dvojice po sobě jdoucích znaků.

```python
cipher.bigrams("ABC")
# ["AB", "BC"]
```

### `build_reference_matrix(text)`

Vytvoří relativní bigramovou matici a uloží ji do instance.

### `save_reference_matrix(path)`

Uloží aktuální referenční matici do souboru `.npy`.

### `score(text)`

Vrátí plausibility skóre textu podle načtené matice.

### `crack(...)`

```python
crack(
    ciphertext,
    iterations=20_000,
    start_key=None,
    restarts=1,
    seed=None,
    polish=True,
    progress_every=50,
)
```

Parametry:

- `ciphertext` – text určený k prolomení,
- `iterations` – počet iterací jednoho restartu,
- `start_key` – volitelný počáteční klíč,
- `restarts` – počet nezávislých běhů,
- `seed` – seed pro reprodukovatelné výsledky,
- `polish` – zapnutí lokálního doladění klíče,
- `progress_every` – interval výpisu průběhu.

Vrací `CrackResult`.

### `crack_file(...)`

Načte jeden ciphertext soubor, provede kryptoanalýzu a uloží plaintext i klíč.

### `crack_directory(...)`

Zpracuje všechny ciphertext soubory v adresáři a vrátí seznam výsledků.

---

## Použití z příkazové řádky

Skript `scripts/decrypt_samples.py` poskytuje stejné možnosti jako objektové API.

### Doporučené nastavení

```powershell
python scripts\decrypt_samples.py `
  --matrix data\processed\TM_ref_krakatit.npy `
  --iterations 10000 `
  --restarts 2
```

### Krátký test

```powershell
python scripts\decrypt_samples.py `
  --matrix data\processed\TM_ref_krakatit.npy `
  --iterations 100 `
  --restarts 1 `
  --seed 1
```

### Dostupné argumenty

```text
--matrix              cesta k referenční matici
--input-directory     adresář se vstupními soubory
--input-dir           zkrácený alias pro --input-directory
--output-directory    adresář pro uložení výsledků
--output-dir          zkrácený alias pro --output-directory
--iterations          počet iterací jednoho restartu
--restarts            počet nezávislých restartů
--seed                seed pro reprodukovatelnost
--no-polish           vypnutí lokálního doladění klíče
```

Bez dalších argumentů skript používá tuto konfiguraci:

```text
matice:               data/processed/TM_ref_krakatit.npy
iterace na restart:   10000
počet restartů:       2
celkem iterací:       20000 na jeden ciphertext
lokální doladění:     zapnuto
```

---

## Jak kryptoanalýza funguje

Knihovna používá bigramový jazykový model. Bigram je dvojice znaků, které v textu následují bezprostředně po sobě. Například text `ABC` obsahuje bigramy `AB` a `BC`.

Při tvorbě referenční matice se nejprve spočítají absolutní četnosti všech bigramů. Buňky s nulovou četností se nahradí hodnotou 1, aby při pozdějším výpočtu nevznikl `log(0)`. Poté se matice převede na relativní pravděpodobnosti.

Samotné hledání klíče probíhá takto:

1. vytvoří se počáteční klíč,
2. ciphertext se dešifruje a ohodnotí,
3. v klíči se prohodí dva náhodné znaky,
4. nový kandidát se znovu dešifruje a ohodnotí,
5. lepší kandidát se přijme vždy,
6. horší kandidát se přijme s pravděpodobností `0.01`,
7. během běhu se uchovává nejlepší nalezený výsledek.

Po skončení M-H běhu může metoda `polish_key` systematicky vyzkoušet všechny dvojice výměn a přijmout pouze ty, které skóre dále zlepší. Při použití více restartů se celý proces spustí z několika nezávislých počátečních klíčů a uloží se výsledek s nejvyšším skóre.

Správný plaintext ani správný klíč nejsou během hledání algoritmu dostupné.

---

## Referenční texty a matice

Projekt obsahuje dvě hlavní varianty jazykového modelu:

```text
data/processed/TM_ref_krakatit.npy
    Matice vytvořená pouze z románu Krakatit.

data/processed/TM_ref_combined.npy
    Matice vytvořená spojením Krakatitu a Války s mloky.

data/processed/TM_ref.npy
    Kompatibilní výchozí kopie vytvářená pomocným skriptem.
```

Nové matice lze vytvořit příkazem:

```powershell
python scripts\build_combined_reference_matrix.py
```

Pro finální zpracování je použita matice `TM_ref_krakatit.npy`. V benchmarku poskytla s konfigurací `2 × 10 000` nejlepší poměr přesnosti, stability a výpočetního času.

---

## Benchmark

Několik strategií bylo porovnáno na kontrolním vzorku `text_1000_sample_1`. Správný plaintext a klíč byly použity až po dokončení každého slepého běhu, pouze pro vyhodnocení výsledku.

| Strategie    | Matice   | Průměrná shoda |  Minimum | Přesné běhy |
| ------------ | -------- | -------------: | -------: | ----------: |
| `1 × 20 000` | combined |        94,80 % |  92,20 % |         1/3 |
| `1 × 20 000` | krakatit |        93,60 % |  90,00 % |         1/3 |
| `2 × 10 000` | krakatit |       100,00 % | 100,00 % |         3/3 |
| `5 × 4 000`  | krakatit |       100,00 % | 100,00 % |         3/3 |

Jako výchozí byla zvolena varianta `2 × 10 000`. Dosáhla stejné přesnosti jako `5 × 4 000`, ale byla mírně rychlejší a každý jednotlivý běh měl více času ke konvergenci.

Tento výsledek platí pro kontrolní vzorek a nepředstavuje záruku stoprocentní přesnosti u každého neznámého textu.

Podrobné výsledky jsou uložené v:

```text
reports/search_strategy_benchmark.md
reports/search_strategy_benchmark.csv
```

---

## Výstupní soubory

Výsledky se ukládají do adresáře `outputs/` ve formátu:

```text
text_{délka}_sample_{id}_plaintext.txt
text_{délka}_sample_{id}_key.txt
```

Například:

```text
text_1000_sample_20_plaintext.txt
text_1000_sample_20_key.txt
```

Soubor s plaintextem obsahuje pouze dešifrovaný text. Soubor s klíčem obsahuje pouze nalezenou permutaci abecedy.

---

## Testování a validace

### Automatické testy

```powershell
pytest
```

Aktuální verze projektu obsahuje 44 automatických testů pro šifrování, dešifrování, bigramy, kryptoanalýzu, objektové API, exporty, validaci souborů a benchmarkovací logiku.

### Kontrola vstupů a výstupů

```powershell
python scripts\validate_assignment_files.py
```

Skript kontroluje zejména:

- názvy a počty vstupních souborů,
- délku a povolené znaky ciphertextů,
- počet exportovaných plaintextů a klíčů,
- platnost nalezených klíčů,
- přítomnost kontrolního vzorku.

### Vyhodnocení výsledků

```powershell
python scripts\evaluate_outputs.py
```

Výstupem jsou soubory:

```text
reports/evaluation_summary.md
reports/evaluation_summary.csv
```

U známého kontrolního vzorku lze vypočítat přesnou shodu plaintextu. U ostatních souborů se kontroluje délka, validita klíče a plausibility skóre.

---

## Notebook a reporty

```text
notebooks/demo.ipynb
notebooks/demo.html
reports/report.md
reports/evaluation_summary.md
reports/search_strategy_benchmark.md
```

Notebook obsahuje ukázku veřejného API, přípravu matice, vizualizaci, krátkou kryptoanalýzu a načtení hotových výsledků. Report popisuje návrh řešení, algoritmus, benchmark a dosažené výsledky.

HTML verzi notebooku lze vytvořit příkazem:

```powershell
python -m jupyter nbconvert --to html notebooks\demo.ipynb
```

---

## Struktura projektu

```text
src/substitution_cipher/     zdrojový kód knihovny
scripts/                     příkazové a pomocné skripty
tests/                       automatické testy
data/ciphertexts/            vstupní ciphertexty
data/processed/              vyčištěné texty a referenční matice
data/reference_texts/        doplňkové referenční texty
data/teacher_example/        kontrolní plaintext a klíč
outputs/                     exportované výsledky
notebooks/                   demonstrační notebook a HTML export
reports/                     reporty, benchmarky a vyhodnocení
```

---

## Omezení

- Metropolis–Hastings je náhodný algoritmus, takže různé seedy mohou vést k různým výsledkům.
- Kratší ciphertexty obsahují méně bigramů a obvykle se luští obtížněji.
- Vyšší počet restartů zvyšuje šanci na dobrý výsledek, ale prodlužuje výpočet.
- Bigramový model hodnotí jazykovou pravděpodobnost, nikoli skutečný význam textu.
- Pokud se některý znak v ciphertextu nevyskytne, jeho část klíče nemusí být možné jednoznačně určit. Plaintext proto může být správný, i když nalezený celý klíč není totožný s referenčním klíčem.
- Stoprocentní výsledek na kontrolním vzorku není zárukou stejné přesnosti na všech neznámých textech.

---

## Řešení častých problémů

### Balíček nelze importovat

```powershell
pip install -e .
```

### Chybí referenční matice

```powershell
python scripts\build_combined_reference_matrix.py
```

### Skript nenašel žádné ciphertexty

Zkontrolujte, že soubory jsou v adresáři:

```text
data/ciphertexts/
```

a odpovídají názvu:

```text
text_{délka}_sample_{id}_ciphertext.txt
```

### Jupyter není dostupný

```powershell
pip install -e ".[dev]"
```

### Výpočet trvá příliš dlouho

Nejprve ověřte funkčnost krátkým během:

```powershell
python scripts\decrypt_samples.py --iterations 100 --restarts 1 --seed 1
```

Pro finální výsledky následně použijte doporučenou konfiguraci `10 000` iterací a `2` restarty.
