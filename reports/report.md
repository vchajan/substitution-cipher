# Report: substituční šifra a kryptoanalýza

## Cíl práce

Cílem projektu je vytvořit Python knihovnu pro klasickou substituční šifru,
připravit referenční bigramovou matici z českého textu a použít ji k
automatickému prolomení šifry pomocí Metropolis-Hastings algoritmu.

Projekt používá abecedu:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

Znak `_` reprezentuje mezeru.

## Princip substituční šifry

Klíč je permutace celé abecedy. Při šifrování se každý znak původní abecedy
mapuje na znak na stejné pozici v klíči. Při dešifrování se používá inverzní
mapování z klíče zpět na původní abecedu.

Hlavní funkce knihovny jsou `substitute_encrypt` a `substitute_decrypt`.

## Příprava referenčních textů

Původní referenční text je vyčištěný román **Krakatit**, uložený v:

```text
data/processed/clean_text.txt
```

Druhý referenční text je **Válka s mloky**, uložený ve složce:

```text
data/reference_texts/
```

Použité soubory:

```text
data/reference_texts/valka_s_mloky_raw.txt
data/reference_texts/valka_s_mloky_clean.txt
```

Čištění textu probíhá takto:

- odstranění diakritiky,
- převod na velká písmena,
- odstranění interpunkce, číslic a nepovolených znaků,
- převod mezer na `_`,
- sloučení opakovaných `_`.

Výsledný clean text obsahuje pouze znaky `A-Z` a `_`.

## Bigramy a přechodová matice

Bigram je dvojice po sobě jdoucích znaků. Z vyčištěného textu se nejprve vytvoří
seznam bigramů a z něj absolutní matice četností o rozměru `27 x 27`.

Postup vytvoření referenční matice:

- nejprve se počítají absolutní četnosti bigramů,
- nulové hodnoty se nahradí hodnotou `1`,
- matice se převede na relativní pravděpodobnosti.

Finální matice byla vytvořena skriptem:

```powershell
python scripts\build_combined_reference_matrix.py
```

Aktuální hodnoty:

- počet použitých referenčních textů: `2`,
- délka Krakatitu: `434711`,
- délka Války s mloky: `381660`,
- délka spojeného textu: `816372`,
- počet bigramů: `816371`,
- tvar matice: `(27, 27)`,
- součet matice: `1.000000000000`,
- matice obsahuje nuly: `False`.

## Plausibility

Funkce `plausibility` počítá logaritmickou věrohodnost kandidátního plaintextu
podle referenční bigramové matice. Pozorované bigramy plaintextu se počítají
jako absolutní četnosti a násobí se logaritmy pravděpodobností v referenční
matici.

## Metropolis-Hastings algoritmus

Algoritmus začíná náhodným klíčem nebo zadaným `start_key`. V každé iteraci
vznikne kandidát prohozením dvou náhodně vybraných znaků v klíči.

Pravidla přijetí:

- lepší kandidát se přijme vždy,
- horší kandidát se přijme s pravděpodobností `0.01`,
- během běhu se uchovává nejlepší nalezený klíč, plaintext a skóre.

Po skončení M-H běhu lze volitelně použít `polish_key`. Tato funkce bez znalosti
plaintextu systematicky vyzkouší všechny výměny dvou znaků v klíči a přijme jen
takovou výměnu, která zlepší stejnou funkci věrohodnosti.

## Zpracování učitelských souborů

Učitelské ciphertexty jsou uloženy v:

```text
data/ciphertexts/
```

Očekávaný formát názvů je:

```text
text_{length}_sample_{sample_id}_ciphertext.txt
```

Použité délky jsou `250`, `500` a `1000`, pro každou délku existují sample ID
`1` až `20`. Celkem tedy projekt zpracovává `60` ciphertextů.

Finální dešifrování bylo spuštěno příkazem:

```powershell
python scripts\decrypt_samples.py --iterations 20000
```

Výstupy jsou v:

```text
outputs/
```

Každý výstup má dva soubory:

```text
text_{délka_textu}_sample_{id textu}_plaintext.txt
text_{délka_textu}_sample_{id textu}_key.txt
```

## Výsledky

Aktuální validace souborů:

- počet vstupních ciphertextů: `60`,
- počet exportovaných plaintext souborů: `60`,
- počet exportovaných key souborů: `60`,
- učitelský plaintext/key příklad je přítomen: ano,
- validační skript skončil se stavem: `OK`.

Vyhodnocení vůči učitelskému příkladu `text_1000_sample_1`:

- plaintext přesně sedí: `True`,
- správné znaky: `1000`,
- procento shody plaintextu: `100.000000`,
- nalezený key je validní permutace: `True`,
- key přesně sedí s učitelským souborem: `False`.

Rozdíl key souboru nebrání dešifrování daného textu: nalezený klíč i učitelský
klíč dávají pro `text_1000_sample_1_ciphertext.txt` stejný plaintext. Rozdíl je
v několika znacích klíče, které se v tomto konkrétním ciphertextu nevyskytují,
proto nejsou z plaintextu jednoznačně určitelné.

Detailní tabulky jsou uloženy v:

```text
reports/evaluation_summary.md
reports/evaluation_summary.csv
```

## Testování a validace

Testy ověřují:

- validaci klíče,
- šifrování a dešifrování,
- bigramy a přechodovou matici,
- výpočet plausibility,
- běh Metropolis-Hastings algoritmu,
- lokální doladění `polish_key`,
- export výsledků,
- bezpečné chování skriptu `decrypt_samples.py`,
- kombinovanou referenční matici,
- validaci zadávacích souborů,
- vyhodnocení výstupů.

Finální testovací běh:

- příkaz: `pytest`,
- výsledek: `29 passed`.

Další kontroly:

- `python scripts\validate_assignment_files.py`: `OK`,
- `python scripts\build_combined_reference_matrix.py`: matice `(27, 27)`, součet `1.0`, bez nul,
- `python scripts\evaluate_outputs.py`: vytvořeno Markdown i CSV vyhodnocení.

## Závěr

Projekt obsahuje knihovnu pro substituční šifru, kombinovaný český referenční
korpus, referenční bigramovou matici, skripty pro validaci, dešifrování i
vyhodnocení, notebook, HTML export notebooku a report. Finální běh zpracoval
všech `60` učitelských ciphertextů s `20 000` iteracemi na soubor a vytvořil
požadované plaintext/key výstupy.
