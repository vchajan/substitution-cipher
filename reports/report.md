# Report: substituční šifra a kryptoanalýza

## Cíl práce

Cílem projektu je vytvořit Python knihovnu pro klasickou substituční šifru,
připravit českou bigramovou referenční matici a použít ji k automatickému
prolomení substituční šifry pomocí Metropolis-Hastings algoritmu.

Projekt používá pevnou abecedu:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

Znak `_` reprezentuje mezeru.

## Povinné části podle PDF zadání

Projekt zachovává povinné funkční API:

```python
substitute_encrypt(plaintext, key)
substitute_decrypt(ciphertext, key)
get_bigrams(text)
transition_matrix(bigrams)
plausibility(text, TM_ref)
prolom_substitute(text, TM_ref, iter, start_key=None)
```

Povinná část řešení zahrnuje substituční šifru, čištění textu na abecedu
`A-Z_`, výpočet bigramů, absolutní přechodovou matici s vyhlazením nul hodnotou
`1`, relativní referenční matici, plausibility skóre a jeden Metropolis-Hastings
běh.

Metropolis-Hastings algoritmus v každé iteraci prohodí dva náhodné znaky v
klíči. Lepší kandidát se přijme vždy, horší kandidát se přijme s
pravděpodobností `0.01`. Během běhu se uchovává nejlepší nalezený klíč,
plaintext a skóre.

## Vlastní rozšíření

Nad rámec povinného zadání projekt přidává:

- objektovou fasádu `SubstitutionCipher`,
- dávkové zpracování celého adresáře ciphertextů,
- volitelné opakované restarty,
- volitelný seed pro reprodukovatelnost,
- lokální doladění `polish_key`,
- validační a vyhodnocovací skripty,
- benchmark strategií hledání.

Tato rozšíření nemění povinné funkční API ani základní pravidla M-H algoritmu.
Více restartů pouze opakuje stejný algoritmus s různými počátečními klíči.
`polish_key` po skončení M-H běhu systematicky zkouší všechny výměny dvou znaků
v klíči a přijímá pouze zlepšení podle stejného plausibility skóre.

## Referenční texty a matice

Původní referenční text je vyčištěný román **Krakatit**:

```text
data/processed/clean_text.txt
```

Doplňkový referenční text je **Válka s mloky**:

```text
data/reference_texts/valka_s_mloky_clean.txt
```

Skript `scripts/build_combined_reference_matrix.py` vytváří:

```text
data/processed/TM_ref_krakatit.npy
data/processed/TM_ref_combined.npy
data/processed/TM_ref.npy
```

`TM_ref_krakatit.npy` je matice pouze z Krakatitu. `TM_ref_combined.npy` je
matice ze spojeného Krakatitu a Války s mloky. `TM_ref.npy` je kompatibilní
kopie vytvořená skriptem pro kombinovanou matici. Finální dešifrování explicitně
používá `TM_ref_krakatit.npy`.

## Bigramová matice

Bigram je dvojice po sobě jdoucích znaků. Z vyčištěného textu se vytvoří seznam
bigramů, spočítají se absolutní četnosti v matici `27 x 27`, nulové buňky se
nahradí hodnotou `1` a matice se normalizuje tak, aby její součet byl `1`.

Nulové hodnoty v absolutní matici znamenají, že se některé bigramy neboli
dvojice znaků v referenčním textu nemusí objevit. Neznamená to automaticky, že
chybí jednotlivé znaky.

## Finální konfigurace kryptoanalýzy

Benchmark na známém učitelském kontrolním vzorku `text_1000_sample_1` ukázal,
že nejstabilnější otestovaná konfigurace je:

```text
referenční matice: data/processed/TM_ref_krakatit.npy
iterace na jeden restart: 10000
počet restartů: 2
celkový počet iterací na jeden ciphertext: 20000
polish_key: zapnutý
```

Celkový počet iterací na jeden ciphertext tedy zůstává `20 000`.

Tato konfigurace byla zvolena proto, že na kontrolním vzorku dosáhla 100 % ve
všech třech testovaných seedech, byla mírně rychlejší než strategie `5 x 4 000`,
každý restart má dostatek prostoru ke konvergenci a nastavení se snadno
vysvětluje.

Správná interpretace výsledku je omezená: jde o nejstabilnější otestovanou
konfiguraci na známém učitelském kontrolním vzorku. Nejde o garanci 100 %
přesnosti na všech neznámých textech.

## Výsledek benchmarku

Teacher plaintext a teacher key nebyly použity během hledání, jako startovní
klíč ani při výběru restartu. Použily se až po dokončení každého slepého běhu
pro změření přesnosti.

| Strategie | Matice | Průměr | Minimum | Přesné běhy |
|---|---|---:|---:|---:|
| 1 x 20 000 | combined | 94,80 % | 92,20 % | 1/3 |
| 1 x 20 000 | krakatit | 93,60 % | 90,00 % | 1/3 |
| 2 x 10 000 | krakatit | 100,00 % | 100,00 % | 3/3 |
| 5 x 4 000 | krakatit | 100,00 % | 100,00 % | 3/3 |

Podrobné výsledky jsou v:

```text
reports/search_strategy_benchmark.md
reports/search_strategy_benchmark.csv
```

## Zpracování učitelských ciphertextů

Učitelské ciphertexty jsou ve složce:

```text
data/ciphertexts/
```

Očekávaný formát názvu:

```text
text_{length}_sample_{sample_id}_ciphertext.txt
```

Výstupy se ukládají do:

```text
outputs/
```

Každý ciphertext vytvoří dva soubory:

```text
text_{délka_textu}_sample_{id textu}_plaintext.txt
text_{délka_textu}_sample_{id textu}_key.txt
```

Finální příkaz:

```powershell
python scripts\decrypt_samples.py `
  --matrix data\processed\TM_ref_krakatit.npy `
  --iterations 10000 `
  --restarts 2 `
  --seed 1
```

Při běžném dešifrování není známý plaintext ani správný key algoritmu dostupný.
Nejlepší restart se vybírá pouze podle plausibility skóre.

## Testování a validace

Projekt obsahuje testy pro validaci klíče, šifrování, dešifrování, bigramy,
přechodovou matici, plausibility, M-H algoritmus, `polish_key`, objektové API,
dávkový export, benchmark a validační skripty.

Základní testy:

```powershell
pytest
```

Validace souborů:

```powershell
python scripts\validate_assignment_files.py
```

Vyhodnocení výstupů:

```powershell
python scripts\evaluate_outputs.py
```

Očekávané strukturální výsledky po finálním běhu:

```text
60 ciphertextů
60 plaintextů
60 key souborů
validace OK
minimálně 44 úspěšných testů
```

Skutečný výsledek známého učitelského vzorku po finálním běhu se seedem `1`:

```text
text_1000_sample_1
shodné znaky plaintextu: 1000 / 1000
shoda plaintextu: 100.000000 %
plaintext přesně sedí: ano
nalezený key je validní: ano
key přesně sedí s učitelským key souborem: ne
```

Rozdíl v key souboru neznamená nutně chybu plaintextu. Pokud se některý znak v
ciphertextu nevyskytne, nemusí být celý substituční klíč z daného textu
jednoznačně určitelný.

## Omezení

M-H je náhodný algoritmus, takže stejný ciphertext může při různých seedech dát
různý výsledek. Kratší texty jsou obtížnější, protože obsahují méně bigramů.
Celý klíč nemusí být jednoznačně zjistitelný, pokud se některý znak v
ciphertextu nevyskytne. Bigramový model hodnotí jazykovou pravděpodobnost, ne
skutečnou znalost správného plaintextu.

## Závěr

Projekt je připraven jako knihovna i jako sada spustitelných skriptů. Povinné
API podle PDF zadání zůstává zachováno. Pro finální dešifrování je nastavena
konfigurace `2 x 10 000` s maticí z Krakatitu, protože byla v benchmarku na
známém kontrolním vzorku nejstabilnější z otestovaných variant.
