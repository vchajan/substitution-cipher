# Report: substitucni sifra a kryptoanalyza

## Cil prace

Cilem projektu je vytvorit Python knihovnu pro klasickou substitucni sifru,
postavit referencni bigramovou matici z ceskeho textu a pouzit ji pri
automatickem prolomeni substitucni sifry pomoci Metropolis-Hastings algoritmu.

## Substitucni sifra

Projekt pouziva abecedu:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

Znak `_` reprezentuje mezeru. Klic je permutace cele abecedy, tedy kazdy znak
abecedy se v nem vyskytuje prave jednou. Sifrovani mapuje znaky z abecedy na
odpovidajici znaky klice. Desifrovani pouziva inverzni mapovani z klice zpet na
abecedu.

## Priprava referencniho textu

Referencni text je ziskan z Wikisource, konkretne z knihy Krakatit. Skript
`scripts/prepare_wikisource_text.py` pouziva standardni knihovny Pythonu,
`urllib` a `html.parser`, bez knihoven `requests` nebo BeautifulSoup.

Text se cisti takto:

- odstrani se diakritika,
- text se prevede na velka pismena,
- interpunkce, cisla a nepovolene znaky se berou jako oddelovace,
- mezery a radky se prevedou na `_`,
- opakovane `_` se slouci.

Vysledny text obsahuje pouze znaky `A-Z` a `_`.

Aktualni referencni data:

- delka clean textu: `434711`,
- pocet bigramu: `434710`.

## Bigramy a prechodova matice

Bigram je dvojice po sobe jdoucich znaku. Z cisteho textu se nejprve vytvori
seznam bigramu a pote absolutni matice cetnosti o rozmeru `27 x 27`.

Po spocitani absolutnich cetnosti se nulove bunky nahradi hodnotou `1`, aby
později nevznikal problem `log(0)`. Teprve potom se matice normalizuje na
relativni pravdepodobnosti.

Aktualni referencni matice:

- tvar matice: `(27, 27)`,
- soucet matice: `1.000000000000`,
- format ulozeni: `data/processed/TM_ref.npy`.

## Plausibility

Funkce `plausibility` pocita logaritmickou verohodnost textu podle referencni
bigramove matice. Referencni matice je relativni a bez nul, pozorovana matice
bigramu je absolutni.

Pouzity vypocet odpovida vzorci:

```python
likelihood += log(TM_ref[i, j]) * TM_obs[i, j]
```

Logaritmicky prostor je dulezity, protoze prime nasobeni mnoha malych
pravdepodobnosti by vedlo k podteceni.

## Metropolis-Hastings algoritmus

Algoritmus zacina nahodnym klicem nebo uzivatelem zadanym `start_key`. V kazde
iteraci vznikne kandidat prohozenim dvou nahodne vybranych znaku v klici.
Kandidat se pouzije k desifrovani a vypocte se jeho plausibility.

Lepsi kandidat se prijima automaticky. Horsi kandidat se podle pseudokodu z PDF
prijima s pravdepodobnosti `0.01`. Behem celeho behu se uklada nejlepsi
nalezeny klic, nejlepsi plaintext a nejlepsi score.

Pro finalni desifrovani zadanych souboru je pripraven skript
`scripts/decrypt_samples.py`, ktery implicitne pouziva `20 000` iteraci na
kazdy ciphertext.

## Export vysledku

Plaintext a klic se ukladaji do samostatnych souboru:

```text
text_{delka_textu}_sample_{id textu}_plaintext.txt
text_{delka_textu}_sample_{id textu}_key.txt
```

V souborech je pouze samotny plaintext nebo samotny klic, bez dalsiho popisu.

## Testovani a validace

Testy overuji:

- validaci klice a round-trip sifrovani/desifrovani,
- chovani pro znaky mimo abecedu,
- cisteni textu,
- tvorbu bigramu,
- absolutni, vyhlazenou i relativni prechodovou matici,
- logaritmickou plausibility,
- nahodny klic,
- zakladni beh Metropolis-Hastings algoritmu,
- export plaintextu a klice,
- bezpecne chovani skriptu pro prazdnou slozku ciphertextu.

Finalni testovaci beh:

- prikaz: `pytest`,
- vysledek: `20 passed`.

## Dosazene vysledky

Projekt ma pripravenou knihovnu, referencni text, referencni matici,
demonstracni notebook, report a skript pro zpracovani realnych ciphertextu.
Realne vysledky prolomeni lze doplnit po pridani souboru od vyucujiciho do
`data/ciphertexts/`.
