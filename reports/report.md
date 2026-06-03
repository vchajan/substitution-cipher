# Report: substituční šifra a kryptoanalýza

## Cíl práce

Cílem projektu je vytvořit Python knihovnu pro klasickou substituční šifru,
postavit referenční bigramovou matici z českého textu a použít ji při
automatickém prolomení substituční šifry pomocí Metropolis-Hastings algoritmu.

## Substituční šifra

Projekt používá abecedu:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

Znak `_` reprezentuje mezeru. Klíč je permutace celé abecedy, tedy každý znak
abecedy se v něm vyskytuje právě jednou. Šifrování mapuje znaky z abecedy na
odpovídající znaky klíče. Dešifrování používá inverzní mapování z klíče zpět na
abecedu.

## Příprava referenčního textu

Referenční text je získán z Wikisource, konkrétně z knihy Krakatit. Skript
`scripts/prepare_wikisource_text.py` používá standardní knihovny Pythonu,
`urllib` a `html.parser`, bez knihoven `requests` nebo BeautifulSoup.

Text se čistí takto:

- odstraní se diakritika,
- text se převede na velká písmena,
- interpunkce, čísla a nepovolené znaky se berou jako oddělovače,
- mezery a řádky se převedou na `_`,
- opakované `_` se sloučí.

Výsledný text obsahuje pouze znaky `A-Z` a `_`.

Aktuální referenční data:

- délka clean textu: `434711`,
- počet bigramů: `434710`.

## Bigramy a přechodová matice

Bigram je dvojice po sobě jdoucích znaků. Z čistého textu se nejprve vytvoří
seznam bigramů a poté absolutní matice četností o rozměru `27 x 27`.

Po spočítání absolutních četností se nulové buňky nahradí hodnotou `1`, aby
později nevznikal problém `log(0)`. Teprve potom se matice normalizuje na
relativní pravděpodobnosti.

Aktuální referenční matice:

- tvar matice: `(27, 27)`,
- součet matice: `1.000000000000`,
- formát uložení: `data/processed/TM_ref.npy`.

## Plausibility

Funkce `plausibility` počítá logaritmickou věrohodnost textu podle referenční
bigramové matice. Referenční matice je relativní a bez nul, pozorovaná matice
bigramů je absolutní.

Použitý výpočet odpovídá vzorci:

```python
likelihood += log(TM_ref[i, j]) * TM_obs[i, j]
```

Logaritmický prostor je důležitý, protože přímé násobení mnoha malých
pravděpodobností by vedlo k podtečení.

## Metropolis-Hastings algoritmus

Algoritmus začíná náhodným klíčem nebo uživatelem zadaným `start_key`. V každé
iteraci vznikne kandidát prohozením dvou náhodně vybraných znaků v klíči.
Kandidát se použije k dešifrování a vypočte se jeho plausibility.

Lepší kandidát se přijímá automaticky. Horší kandidát se podle pseudokódu z PDF
přijímá s pravděpodobností `0.01`. Během celého běhu se ukládá nejlepší
nalezený klíč, nejlepší plaintext a nejlepší score.

Pro finální dešifrování zadaných souborů je připraven skript
`scripts/decrypt_samples.py`, který implicitně používá `20 000` iterací na
každý ciphertext.

## Export výsledků

Plaintext a klíč se ukládají do samostatných souborů:

```text
text_{délka_textu}_sample_{id textu}_plaintext.txt
text_{délka_textu}_sample_{id textu}_key.txt
```

V souborech je pouze samotný plaintext nebo samotný klíč, bez dalšího popisu.

## Testování a validace

Testy ověřují:

- validaci klíče a round-trip šifrování/dešifrování,
- chování pro znaky mimo abecedu,
- čištění textu,
- tvorbu bigramů,
- absolutní, vyhlazenou i relativní přechodovou matici,
- logaritmickou plausibility,
- náhodný klíč,
- základní běh Metropolis-Hastings algoritmu,
- export plaintextu a klíče,
- bezpečné chování skriptu pro prázdnou složku ciphertextů.

Finální testovací běh:

- příkaz: `pytest`,
- výsledek: `20 passed`.

## Dosažené výsledky

Projekt má připravenou knihovnu, referenční text, referenční matici,
demonstrační notebook, report a skript pro zpracování reálných ciphertextů.
Reálné výsledky prolomení lze doplnit po přidání souborů od vyučujícího do
`data/ciphertexts/`.
