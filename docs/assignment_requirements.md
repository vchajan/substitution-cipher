# Požiadavky zo zadania

## Cieľ

Vytvoriť Python knižnicu na:

1. šifrovanie textu klasickou substitučnou šifrou,
2. dešifrovanie textu pomocou známeho kľúča,
3. automatické prelomenie substitučnej šifry pomocou štatistických metód,
4. aplikáciu knižnice na zašifrované dáta.

## Abeceda

Používa sa iba táto abeceda:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

Podtržítko `_` nahrádza medzeru.

## Jazykový model

Treba vytvoriť referenčnú bigramovú maticu z dlhého českého textu.

Postup:

1. získať vhodný český text,
2. normalizovať text na povolenú abecedu,
3. vytvoriť zoznam bigramov,
4. zostaviť absolútnu maticu,
5. nahradiť nulové hodnoty hodnotou `1`,
6. vytvoriť relatívnu maticu so súčtom prvkov `1`.

## Kryptoanalýza

Použiť Metropolis-Hastings algoritmus:

1. zvoliť počiatočný kľúč,
2. dešifrovať text,
3. vypočítať vierohodnosť,
4. vytvoriť kandidátny kľúč prehodením dvoch znakov,
5. rozhodnúť o prijatí kandidáta,
6. opakovať daný počet iterácií,
7. uložiť najlepší kľúč a dešifrovaný text.

## Povinné výstupy

- zdrojový kód knižnice,
- dokumentácia funkcií,
- Jupyter Notebook exportovaný do PDF alebo HTML,
- stručný report,
- exportované kľúče a plaintexty.

## Formát exportu

```text
text_{dlzka_textu}_sample_{id}_plaintext.txt
text_{dlzka_textu}_sample_{id}_key.txt
```
