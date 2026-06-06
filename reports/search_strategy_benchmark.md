# Benchmark strategií hledání

Benchmark používá učitelský plaintext a klíč pouze pro vyhodnocení hotového slepého běhu.

## Souhrn

- Nejlepší průměrná strategie: two_stage_4x5000_plus_15000
- Nejstabilnější strategie: two_stage_4x5000_plus_15000
- Nejrychlejší strategie: 2x10000
- Nejlepší matice: krakatit
- Počet přesných výsledků 1000/1000: 14
- Doporučená konfigurace pro všech 60 souborů: 2x10000 s maticí krakatit

## Výsledky podle strategie a matice

| Strategie | Matice | Průměr % | Minimum % | Maximum % | Přesné běhy | Průměrný čas [s] |
|---|---|---:|---:|---:|---:|---:|
| 1x20000 | combined | 94.80 | 92.20 | 100.00 | 1/3 | 15.80 |
| 1x20000 | krakatit | 93.60 | 90.00 | 100.00 | 1/3 | 14.61 |
| 2x10000 | combined | 93.03 | 92.20 | 94.70 | 0/3 | 15.94 |
| 2x10000 | krakatit | 100.00 | 100.00 | 100.00 | 3/3 | 14.22 |
| 4x5000 | combined | 92.20 | 92.20 | 92.20 | 0/3 | 17.40 |
| 4x5000 | krakatit | 94.80 | 92.20 | 100.00 | 1/3 | 14.00 |
| 5x4000 | combined | 92.20 | 92.20 | 92.20 | 0/3 | 15.59 |
| 5x4000 | krakatit | 100.00 | 100.00 | 100.00 | 3/3 | 14.57 |
| two_stage_4x5000_plus_15000 | combined | 100.00 | 100.00 | 100.00 | 3/3 | 32.65 |
| two_stage_4x5000_plus_15000 | krakatit | 97.40 | 92.20 | 100.00 | 2/3 | 25.09 |
