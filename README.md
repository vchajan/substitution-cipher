# Substitution Cipher Cryptanalysis

Tímový skeleton pre školský projekt: Python knižnica na šifrovanie, dešifrovanie a kryptoanalýzu klasickej substitučnej šifry.

Projekt používa presne túto abecedu:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

Podtržítko `_` reprezentuje medzeru. Iná abeceda sa v projekte nepoužíva.

---

## Rýchly štart

Vytvorenie virtuálneho prostredia:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

Inštalácia projektu:

```bash
pip install -e ".[dev]"
```

Spustenie testov:

```bash
pytest
```

---

## Štruktúra projektu

```text
.
├── src/subcipher/          # zdrojový kód knižnice
├── tests/                  # automatické testy
├── scripts/                # spúšťacie skripty pre maticu a lúštenie
├── notebooks/              # Jupyter Notebook pre finálnu demonštráciu
├── docs/                   # dokumentácia, tímový plán a report
├── data/                   # vstupné dáta
├── outputs/                # exportované výsledky
└── .github/                # GitHub workflow, issue a PR šablóny
```

---

## Kde čo dopĺňať

### Knižnica

Zdrojový kód je v:

```text
src/subcipher/
```

Najdôležitejšie súbory:

```text
alphabet.py      # definícia abecedy a generovanie kľúčov
cipher.py        # šifrovanie, dešifrovanie, validácia kľúča
preprocess.py    # normalizácia textu
bigrams.py       # bigramy a prechodové matice
cracker.py       # Metropolis-Hastings algoritmus
io_utils.py      # export plaintext/key súborov
```

### Dáta

```text
data/raw/          # referenčný český text, napr. kniha z Wikisource
data/reference/    # uložená referenčná bigramová matica
data/ciphertexts/  # zašifrované texty od vyučujúceho
```

### Výstupy

Dešifrované texty a kľúče ukladajte do:

```text
outputs/decrypted/
```

Povinný názov exportu:

```text
text_{dlzka_textu}_sample_{id}_plaintext.txt
text_{dlzka_textu}_sample_{id}_key.txt
```

Príklad:

```text
text_1000_sample_20_plaintext.txt
text_1000_sample_20_key.txt
```

### Dokumentácia

Dokumentácia je v:

```text
docs/
```

Odporúčané súbory:

```text
docs/assignment_requirements.md  # stručný prepis požiadaviek
docs/architecture.md             # architektúra projektu
docs/api_contract.md             # verejné funkcie a ich vstupy/výstupy
docs/team_plan.md                # rozdelenie práce v skupine
docs/report_template.md          # šablóna finálneho reportu
```

### Notebook

Finálnu demonštráciu pripravujte v:

```text
notebooks/demo.ipynb
```

Notebook má ukázať:

1. šifrovanie,
2. dešifrovanie,
3. vytvorenie bigramovej matice,
4. kryptoanalýzu,
5. export výsledkov,
6. stručné vyhodnotenie úspešnosti.

---

## Základné spustenie

Vytvorenie referenčnej bigramovej matice:

```bash
python scripts/build_reference.py data/raw/krakatit.txt data/reference/TM_ref.csv
```

Lúštenie jedného súboru:

```bash
python scripts/crack_file.py data/ciphertexts/text_1000_sample_20_ciphertext.txt data/reference/TM_ref.csv outputs/decrypted --iterations 20000
```

Lúštenie všetkých `*_ciphertext.txt` súborov v priečinku:

```bash
python scripts/crack_batch.py data/ciphertexts data/reference/TM_ref.csv outputs/decrypted --iterations 20000
```
