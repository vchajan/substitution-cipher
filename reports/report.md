# Report – prolomení substituční šifry

## 1. Co bylo cílem

Cílem projektu bylo vytvořit jednoduchou Python knihovnu pro monoalfabetickou substituční šifru a potom zkusit stejnou šifru prolomit bez znalosti původního textu.

Použitá abeceda je:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

Podtržítko nahrazuje mezeru. Klíč je permutace všech 27 znaků této abecedy.

Projekt obsahuje povinné funkce ze zadání:

```python
substitute_encrypt(plaintext, key)
substitute_decrypt(ciphertext, key)
get_bigrams(text)
transition_matrix(bigrams)
plausibility(text, TM_ref)
prolom_substitute(text, TM_ref, iter, start_key=None)
```

Vedle toho jsem přidal objektové rozhraní `SubstitutionCipher`, dávkové zpracování více souborů a volitelné lokální doladění klíče po skončení hlavního hledání.

## 2. Referenční text a příprava matice

Pro odhad českých bigramových četností jsem použil pouze knihu **Válka s mloky** od Karla Čapka.

Text se dá stáhnout skriptem:

```powershell
python scripts\download_reference_text.py
```

Skript používá MediaWiki API českých Wikizdrojů a uloží surový text do:

```text
data/reference/valka_s_mloky_raw.txt
```

Surový text má přibližně 401 tisíc znaků. Následně se vyčistí skriptem:

```powershell
python scripts\prepare_reference_text.py
```

Při čištění se odstraní diakritika, text se převede na velká písmena a ponechají se jen znaky `A-Z_`. Vyčištěný text má přibližně 382 tisíc znaků.

Z vyčištěného textu se vytvoří všechny sousední dvojice znaků. Ty se zapíšou do matice `27 × 27`. Řádek znamená první znak bigramu a sloupec druhý znak.

Nulové buňky se nahradí jedničkou, aby později nevznikl problém s `log(0)`. Potom se matice vydělí součtem všech buněk a uloží se jako:

```text
models/TM_ref.npy
```

Finální matice má rozměr `(27, 27)`, součet `1.0` a neobsahuje nuly ani neplatné hodnoty.

## 3. Hodnocení kandidátního textu

Každý kandidátní plaintext se hodnotí funkcí `plausibility`.

Z textu se nejprve vytvoří bigramová matice:

```python
transition_matrix(get_bigrams(text))
```

Potom se spočítá součet:

```text
log(TM_ref[i, j]) * TM_obs[i, j]
```

přes všechny buňky matice.

Výsledek je záporné číslo. Vyšší hodnota, tedy méně záporné číslo, obvykle znamená, že text lépe odpovídá českému jazyku.

Tento model samozřejmě nepozná význam slov. Sleduje jen dvojice sousedních znaků, takže někdy může dát vysoké skóre i textu, který není úplně správně.

## 4. Hledání klíče

Klíč se hledá pomocí Metropolis-Hastingsova algoritmu.

Na začátku se použije náhodná permutace abecedy. V každé iteraci se prohodí dvě pozice v klíči a vzniklý kandidát se použije k dešifrování ciphertextu.

Lepší kandidát se přijme vždy. Horší kandidát se přijme s pravděpodobností `0.01`. Tím se hledání může dostat ven z lokálního maxima a nezůstane příliš brzy u prvního rozumného řešení.

Během běhu se zvlášť ukládá nejlepší klíč, nejlepší plaintext a jejich skóre.

Po skončení hlavního běhu lze zapnout `polish_key`. Tato funkce už není náhodná. Postupně zkusí všechny dvojice znaků v klíči a přijme jen takovou výměnu, která skóre zlepší.

Dávkové zpracování může běžet paralelně, protože každý ciphertext je nezávislý. Paralelizují se celé soubory, ne jednotlivé iterace jednoho běhu.

## 5. Spuštění a výsledky

Nejjednodušší spuštění ve Windows je:

```powershell
.\install.bat
.\run.bat
```

Finální dávkový běh používá pro každý ciphertext 20 000 iterací.

Celkem bylo zpracováno:

- 60 ciphertextů,
- 60 výstupních plaintextů,
- 60 výstupních klíčů,
- 0 chyb při dávkovém zpracování.

Pro kontrolu byl použit známý učitelský příklad `text_1000_sample_1`.

Správný plaintext ani správný klíč nebyly použity během hledání. Sloužily až k vyhodnocení hotového výsledku.

V uloženém finálním běhu bylo správně obnoveno:

```text
922 / 1000 znaků
```

tedy:

```text
92,2 %
```

Celý plaintext ani celý klíč se přesně neshodovaly s učitelským řešením.

Podrobné výsledky jsou v:

```text
reports/evaluation_summary.md
reports/evaluation_summary.csv
```

Automatické testy skončily výsledkem:

```text
32 passed
```

a validace souborů zadání skončila stavem:

```text
Status: OK
```

## 6. Závěr

Projekt splňuje hlavní části zadání: umí substituční šifrování a dešifrování, vytvoří referenční bigramovou matici, ohodnotí kandidátní plaintext a hledá klíč pomocí Metropolis-Hastingsova algoritmu.

Největší omezení je náhodnost hledání a jednoduchost bigramového modelu. Kratší texty obsahují méně informací a bývají výrazně těžší. Ani u delšího textu není jisté, že nejlepší nalezené skóre znamená přesně správný plaintext.

Výsledek 92,2 % na známém příkladu ukazuje, že metoda funguje, ale není stoprocentně spolehlivá. Lepší výsledek by mohl přinést vyšší počet restartů nebo složitější jazykový model, například trigramy. V tomto projektu jsem ale zachoval hlavní logiku zadanou v úloze.
