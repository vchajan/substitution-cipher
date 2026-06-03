# Plán práce pre skupinu

## Odporúčané rozdelenie

### Člen 1 – šifra a predspracovanie

Súbory:

```text
src/subcipher/alphabet.py
src/subcipher/cipher.py
src/subcipher/preprocess.py
tests/test_cipher.py
```

Úlohy:

- validácia kľúča,
- šifrovanie,
- dešifrovanie,
- normalizácia textu.

### Člen 2 – bigramová matica

Súbory:

```text
src/subcipher/bigrams.py
scripts/build_reference.py
tests/test_bigrams.py
```

Úlohy:

- bigramy,
- absolútna matica,
- vyhladenie nulových hodnôt,
- relatívna matica,
- uloženie referenčnej matice.

### Člen 3 – kryptoanalýza

Súbory:

```text
src/subcipher/cracker.py
scripts/crack_file.py
scripts/crack_batch.py
tests/test_cracker.py
```

Úlohy:

- výpočet vierohodnosti,
- generovanie kandidátnych kľúčov,
- Metropolis-Hastings algoritmus,
- export výsledkov.

### Člen 4 – notebook, report, validácia

Súbory:

```text
notebooks/demo.ipynb
docs/report_template.md
docs/assignment_requirements.md
```

Úlohy:

- demonštračný notebook,
- grafy/tabuľky,
- finálny report,
- kontrola výstupov.

Ak ste traja, spojte úlohy člena 4 s členom 2 alebo 3.
