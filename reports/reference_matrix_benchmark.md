# Benchmark referenčních matic

## Učitelský benchmark

Benchmark učitelského vzorku je samostatný a zapisuje se do `reports/search_strategy_benchmark.csv` a `reports/search_strategy_benchmark.md`.

## Holdout benchmark

Režim: rychlý kontrolní běh.
Počet vzorků na délku a knihu: 1.
Seedy: 1.
Strategie: 1x50, 2x25.

## Příkazy

Vytvoření referenčních matic včetně samostatné matice pro Válku s mloky:

```powershell
python scripts\build_combined_reference_matrix.py
```

Rychlý kontrolní benchmark:

```powershell
python scripts\benchmark_reference_matrices.py --quick
```

Plný benchmark s výchozími strategiemi a seedy:

```powershell
python scripts\benchmark_reference_matrices.py
```

Holdout vzorky vznikly z posledních 20 % každé knihy. Matice v tomto benchmarku vznikly pouze z prvních 80 % knih.

## Doporučení podle holdoutu

- Nejlepší matice: valka_s_mloky
- Doporučená konfigurace: 1x50 s maticí valka_s_mloky
- Nejrychlejší měřená konfigurace: 1x50 s maticí combined
- Přesné plaintexty: 0/36

## Souhrn podle matice a strategie

| Matice | Strategie | Počet | Průměr % | Medián % | Minimum % | Maximum % | Přesné plaintexty | Průměrný čas [s] |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| combined | 1x50 | 6 | 22.37 | 23.60 | 1.80 | 37.00 | 0 | 0.75 |
| combined | 2x25 | 6 | 27.35 | 29.35 | 21.60 | 31.20 | 0 | 1.53 |
| krakatit | 1x50 | 6 | 23.50 | 21.40 | 15.90 | 31.50 | 0 | 0.81 |
| krakatit | 2x25 | 6 | 27.73 | 30.50 | 15.90 | 36.50 | 0 | 1.52 |
| valka_s_mloky | 1x50 | 6 | 27.78 | 32.30 | 1.80 | 39.90 | 0 | 0.75 |
| valka_s_mloky | 2x25 | 6 | 27.43 | 27.40 | 24.40 | 30.20 | 0 | 1.51 |

## Detail podle délky a zdrojové knihy

| Matice | Strategie | Délka | Zdroj | Počet | Průměr % | Medián % | Minimum % | Maximum % | Přesné plaintexty | Průměrný čas [s] |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| combined | 1x50 | 250 | krakatit | 1 | 20.80 | 20.80 | 20.80 | 20.80 | 0 | 0.35 |
| combined | 1x50 | 250 | valka_s_mloky | 1 | 16.80 | 16.80 | 16.80 | 16.80 | 0 | 0.35 |
| combined | 1x50 | 500 | krakatit | 1 | 26.40 | 26.40 | 26.40 | 26.40 | 0 | 0.66 |
| combined | 1x50 | 500 | valka_s_mloky | 1 | 1.80 | 1.80 | 1.80 | 1.80 | 0 | 0.66 |
| combined | 1x50 | 1000 | krakatit | 1 | 37.00 | 37.00 | 37.00 | 37.00 | 0 | 1.24 |
| combined | 1x50 | 1000 | valka_s_mloky | 1 | 31.40 | 31.40 | 31.40 | 31.40 | 0 | 1.23 |
| combined | 2x25 | 250 | krakatit | 1 | 29.60 | 29.60 | 29.60 | 29.60 | 0 | 0.71 |
| combined | 2x25 | 250 | valka_s_mloky | 1 | 31.20 | 31.20 | 31.20 | 31.20 | 0 | 0.76 |
| combined | 2x25 | 500 | krakatit | 1 | 21.60 | 21.60 | 21.60 | 21.60 | 0 | 1.32 |
| combined | 2x25 | 500 | valka_s_mloky | 1 | 31.00 | 31.00 | 31.00 | 31.00 | 0 | 1.30 |
| combined | 2x25 | 1000 | krakatit | 1 | 21.60 | 21.60 | 21.60 | 21.60 | 0 | 2.54 |
| combined | 2x25 | 1000 | valka_s_mloky | 1 | 29.10 | 29.10 | 29.10 | 29.10 | 0 | 2.53 |
| krakatit | 1x50 | 250 | krakatit | 1 | 20.80 | 20.80 | 20.80 | 20.80 | 0 | 0.42 |
| krakatit | 1x50 | 250 | valka_s_mloky | 1 | 22.00 | 22.00 | 22.00 | 22.00 | 0 | 0.56 |
| krakatit | 1x50 | 500 | krakatit | 1 | 30.20 | 30.20 | 30.20 | 30.20 | 0 | 0.66 |
| krakatit | 1x50 | 500 | valka_s_mloky | 1 | 20.60 | 20.60 | 20.60 | 20.60 | 0 | 0.68 |
| krakatit | 1x50 | 1000 | krakatit | 1 | 31.50 | 31.50 | 31.50 | 31.50 | 0 | 1.28 |
| krakatit | 1x50 | 1000 | valka_s_mloky | 1 | 15.90 | 15.90 | 15.90 | 15.90 | 0 | 1.24 |
| krakatit | 2x25 | 250 | krakatit | 1 | 20.80 | 20.80 | 20.80 | 20.80 | 0 | 0.71 |
| krakatit | 2x25 | 250 | valka_s_mloky | 1 | 31.20 | 31.20 | 31.20 | 31.20 | 0 | 0.70 |
| krakatit | 2x25 | 500 | krakatit | 1 | 32.20 | 32.20 | 32.20 | 32.20 | 0 | 1.30 |
| krakatit | 2x25 | 500 | valka_s_mloky | 1 | 29.80 | 29.80 | 29.80 | 29.80 | 0 | 1.29 |
| krakatit | 2x25 | 1000 | krakatit | 1 | 36.50 | 36.50 | 36.50 | 36.50 | 0 | 2.64 |
| krakatit | 2x25 | 1000 | valka_s_mloky | 1 | 15.90 | 15.90 | 15.90 | 15.90 | 0 | 2.49 |
| valka_s_mloky | 1x50 | 250 | krakatit | 1 | 33.20 | 33.20 | 33.20 | 33.20 | 0 | 0.36 |
| valka_s_mloky | 1x50 | 250 | valka_s_mloky | 1 | 22.00 | 22.00 | 22.00 | 22.00 | 0 | 0.36 |
| valka_s_mloky | 1x50 | 500 | krakatit | 1 | 38.40 | 38.40 | 38.40 | 38.40 | 0 | 0.65 |
| valka_s_mloky | 1x50 | 500 | valka_s_mloky | 1 | 1.80 | 1.80 | 1.80 | 1.80 | 0 | 0.66 |
| valka_s_mloky | 1x50 | 1000 | krakatit | 1 | 39.90 | 39.90 | 39.90 | 39.90 | 0 | 1.24 |
| valka_s_mloky | 1x50 | 1000 | valka_s_mloky | 1 | 31.40 | 31.40 | 31.40 | 31.40 | 0 | 1.25 |
| valka_s_mloky | 2x25 | 250 | krakatit | 1 | 24.40 | 24.40 | 24.40 | 24.40 | 0 | 0.71 |
| valka_s_mloky | 2x25 | 250 | valka_s_mloky | 1 | 27.20 | 27.20 | 27.20 | 27.20 | 0 | 0.76 |
| valka_s_mloky | 2x25 | 500 | krakatit | 1 | 30.20 | 30.20 | 30.20 | 30.20 | 0 | 1.30 |
| valka_s_mloky | 2x25 | 500 | valka_s_mloky | 1 | 27.60 | 27.60 | 27.60 | 27.60 | 0 | 1.36 |
| valka_s_mloky | 2x25 | 1000 | krakatit | 1 | 26.10 | 26.10 | 26.10 | 26.10 | 0 | 2.46 |
| valka_s_mloky | 2x25 | 1000 | valka_s_mloky | 1 | 29.10 | 29.10 | 29.10 | 29.10 | 0 | 2.45 |
