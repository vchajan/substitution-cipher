# Tímové pravidlá

## Vetvy

Hlavná vetva:

```text
main
```

Vývojová vetva:

```text
dev
```

Každý člen tímu pracuje na vlastnej vetve:

```text
feature/nazov-ulohy
```

Príklad:

```bash
git checkout dev
git pull origin dev
git checkout -b feature/bigram-matrix
```

## Commit správy

Používajte krátke a jasné správy:

```text
Implement key validation
Add bigram matrix tests
Add batch cracking script
Update report results
```

## Pred Pull Requestom

Skontrolujte:

- kód sa spustí bez chyby,
- prejdú testy `pytest`,
- nepridali ste zbytočne veľké súbory,
- názvy verejných funkcií ostali nezmenené,
- dokumentácia zodpovedá implementácii.
