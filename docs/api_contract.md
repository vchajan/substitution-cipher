# API contract

Názvy týchto funkcií nemeňte, aby ostali kompatibilné so zadaním a notebookom.

## `substitute_encrypt(plaintext, key)`

Zašifruje text substitučnou šifrou.

Argumenty:

- `plaintext`: vstupný text,
- `key`: permutácia abecedy `ABCDEFGHIJKLMNOPQRSTUVWXYZ_`.

Výstup:

- zašifrovaný text.

## `substitute_decrypt(ciphertext, key)`

Dešifruje text pomocou inverzného mapovania.

Argumenty:

- `ciphertext`: zašifrovaný text,
- `key`: použitý substitučný kľúč.

Výstup:

- dešifrovaný text.

## `get_bigrams(text)`

Vráti zoznam dvojíc po sebe idúcich znakov.

## `transition_matrix(bigrams)`

Vytvorí absolútnu bigramovú maticu s vyhladením nulových hodnôt.

## `plausibility(text, TM_ref)`

Vypočíta log-vierohodnosť textu podľa referenčnej relatívnej bigramovej matice.

## `prolom_substitute(text, TM_ref, iter, start_key)`

Spustí Metropolis-Hastings algoritmus.

Výstup:

```python
(best_key, best_decrypted_text, best_score)
```
