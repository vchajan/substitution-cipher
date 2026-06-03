# Architektúra projektu

## `src/subcipher/alphabet.py`

Zodpovednosť:

- definícia abecedy,
- kontrola veľkosti abecedy,
- generovanie Caesarovho kľúča,
- generovanie náhodného substitučného kľúča.

## `src/subcipher/cipher.py`

Zodpovednosť:

- validácia kľúča,
- šifrovanie,
- dešifrovanie.

## `src/subcipher/preprocess.py`

Zodpovednosť:

- prevod textu na veľké písmená,
- odstránenie diakritiky,
- nahradenie medzier podtržítkom,
- odstránenie nepovolených znakov.

## `src/subcipher/bigrams.py`

Zodpovednosť:

- vytvorenie bigramov,
- vytvorenie absolútnej prechodovej matice,
- prevod na relatívnu maticu,
- uloženie/načítanie matice.

## `src/subcipher/cracker.py`

Zodpovednosť:

- výpočet log-vierohodnosti textu,
- generovanie kandidátnych kľúčov,
- Metropolis-Hastings algoritmus.

## `src/subcipher/io_utils.py`

Zodpovednosť:

- čítanie textových súborov,
- parsovanie názvu ciphertext súboru,
- export plaintext/key výsledkov.
