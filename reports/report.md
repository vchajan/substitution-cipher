# Report

## Cíl práce

Cílem je implementovat klasickou monoalfabetickou substituční šifru a pokusit se ji prolomit pomocí bigramového jazykového modelu a Metropolis-Hastingsova algoritmu.

## Abeceda

Používá se pevná abeceda:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

Znak `_` reprezentuje mezeru. Jiná abeceda se v projektu nepoužívá.

## Substituční šifra

Klíč je permutace celé abecedy. Při šifrování se každý znak plaintextu nahradí znakem na stejné pozici v klíči. Dešifrování používá opačné mapování.

## Referenční text

Jediným referenčním textem je **Válka s mloky**. Surový text je uložen v:

```text
data/reference/valka_s_mloky_raw.txt
```

Vyčištěný text je uložen v:

```text
data/reference/valka_s_mloky_clean.txt
```

Tento text byl zvolen jako dostatečně dlouhý český text pro odhad četností bigramů.

## Příprava textu

Skript `scripts/prepare_reference_text.py` načte surový text jako UTF-8, odstraní diakritiku, převede písmena na velká, oddělovače sjednotí na `_` a ponechá pouze znaky `A-Z_`.

## Bigramy

Bigram je dvojice sousedních znaků. Z textu `ABC` vzniknou bigramy `AB` a `BC`. Bigramy zachycují jednoduché lokální vlastnosti češtiny a slouží jako základ skórování kandidátních plaintextů.

## Absolutní matice

Funkce `transition_matrix` nejprve spočítá absolutní četnosti bigramů do matice `27 × 27`. Řádek odpovídá prvnímu znaku bigramu, sloupec druhému znaku.

## Ošetření nul

Některé bigramy se v referenčním textu nemusí vyskytnout. Jejich buňky by měly hodnotu nula, což by při výpočtu logaritmu způsobilo problém. Proto se nulové buňky nahradí hodnotou `1`.

## Relativní matice

Po ošetření nul se matice vydělí celkovým součtem. Výsledkem je relativní referenční matice:

```text
models/TM_ref.npy
```

Matice má shape `(27, 27)`, součet přibližně `1.0`, neobsahuje nuly, `NaN` ani nekonečné hodnoty.

## Věrohodnost

Funkce `plausibility(text, TM_ref)` spočítá logaritmickou věrohodnost textu podle referenční bigramové matice. Vyšší hodnota, tedy méně záporné skóre, obvykle znamená jazykově pravděpodobnější český text.

## Metropolis-Hastingsův algoritmus

Algoritmus začíná náhodným klíčem. V každé iteraci prohodí dva náhodné znaky v klíči, dešifruje ciphertext a spočítá nové skóre. Lepší kandidát se přijme vždy. Horší kandidát se podle zadání přijme s pravděpodobností `0.01`. Během běhu se uchovává nejlepší nalezený klíč.

## Povinné API

Projekt zachovává požadované funkce:

```python
substitute_encrypt(plaintext, key)
substitute_decrypt(ciphertext, key)
get_bigrams(text)
transition_matrix(bigrams)
plausibility(text, TM_ref)
prolom_substitute(text, TM_ref, iter, start_key=None)
```

Funkce `prolom_substitute` vrací `(key, plaintext, score)`.

## Objektové API

Třída `SubstitutionCipher` je pohodlná fasáda nad stejnou implementací. Umí načíst matici, šifrovat, dešifrovat, skórovat text, zpracovat jeden soubor i celou složku ciphertextů.

## Vlastní rozšíření

Projekt obsahuje volitelné lokální dolaďování klíče `polish_key` a volitelné restarty v objektovém API. Tato rozšíření nenahrazují povinný M-H algoritmus, jen mohou zlepšit stabilitu výsledku.

## Zpracování ciphertextů

Ciphertexty se očekávají ve složce:

```text
data/ciphertexts/
```

Finální dávkové zpracování:

```powershell
python scripts\decrypt_samples.py `
  --matrix models\TM_ref.npy `
  --input-directory data\ciphertexts `
  --output-directory outputs `
  --iterations 20000 `
  --restarts 1
```

Výstupy se ukládají do `outputs/` jako samostatný plaintext a klíč pro každý vstupní soubor.

## Vyhodnocení

Známý učitelský plaintext a klíč se používají pouze pro následnou kontrolu souboru `text_1000_sample_1`. Nepoužívají se při hledání klíče ani při výběru kandidátů.

## Testování

Testy ověřují povinné podpisy funkcí, šifrování, dešifrování, bigramy, referenční matici, objektové API, skripty, strukturu složek a dokumentaci.

## Omezení

Metropolis-Hastingsův algoritmus je náhodný. Kratší texty jsou těžší, protože obsahují méně bigramů. Bigramový model nemusí vždy vybrat přesný plaintext. Pokud se některý znak v ciphertextu nevyskytne, část klíče nemusí být jednoznačně určitelná.

## Závěr

Projekt implementuje substituční šifru i její bigramovou kryptoanalýzu podle zadání. Referenční matice vzniká pouze z Války s mloky a ukládá se do `models/TM_ref.npy`. Výstupy dávkového dešifrování patří do složky `outputs/`.
