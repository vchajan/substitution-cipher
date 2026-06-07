# Report

## Cíl práce

Cílem práce je implementovat klasickou monoalfabetickou substituční šifru a pokusit se ji prolomit pomocí bigramového jazykového modelu a Metropolis-Hastingsova algoritmu.

Řešení je vytvořené jako Python knihovna. Vedle povinných funkcí obsahuje také objektové API, dávkové zpracování souborů, volitelné lokální doladění klíče a paralelní zpracování více ciphertextů.

## Abeceda

Projekt používá pevnou abecedu:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

Znak `_` reprezentuje mezeru. Jiná abeceda se v základním řešení nepoužívá.

## Substituční šifra

Klíč je permutace celé abecedy o délce 27 znaků. Každý znak plaintextu se při šifrování nahradí znakem na stejné pozici v klíči.

Dešifrování používá opačné mapování. Před použitím se kontroluje, že klíč:

- má správnou délku,
- neobsahuje opakované znaky,
- obsahuje přesně všechny znaky projektové abecedy.

Povinné funkce jsou:

```python
substitute_encrypt(plaintext, key)
substitute_decrypt(ciphertext, key)
```

## Referenční text

Jediným referenčním textem je kniha **Válka s mloky** od Karla Čapka.

Surový text se získává z českých Wikizdrojů pomocí MediaWiki API:

```text
https://cs.wikisource.org/w/api.php
```

Použitá stránka díla je:

```text
Válka_s_Mloky
```

Stažení zajišťuje skript:

```text
scripts/download_reference_text.py
```

Skript vyhledá části díla, načte jejich vlastní obsah, odstraní HTML značky a spojí jednotlivé části do jednoho UTF-8 souboru:

```text
data/reference/valka_s_mloky_raw.txt
```

Pokud už lokální soubor existuje, bez parametru `--force` se znovu nestahuje. Aktuální surový text má přibližně 401 000 znaků, takže poskytuje dostatečně velký vzorek českého jazyka.

## Příprava textu

Skript:

```text
scripts/prepare_reference_text.py
```

načte surový text jako UTF-8 a převede ho do projektové abecedy.

Při čištění se:

1. odstraní diakritika,
2. text převede na velká písmena,
3. mezery a další oddělovače převedou na `_`,
4. odstraní číslice a interpunkce,
5. ponechají pouze znaky `A-Z_`.

Vyčištěný text se uloží do:

```text
data/reference/valka_s_mloky_clean.txt
```

Jeho délka je přibližně 382 000 znaků.

## Bigramy

Bigram je dvojice sousedních znaků. Například z textu:

```text
ABC
```

vzniknou bigramy:

```text
AB
BC
```

Povinná funkce:

```python
get_bigrams(text)
```

vrací všechny sousední dvojice znaků v textu.

## Absolutní bigramová matice

Bigramy se zapisují do matice o rozměru `27 × 27`.

- řádek určuje první znak bigramu,
- sloupec určuje druhý znak bigramu,
- hodnota buňky určuje počet výskytů dané dvojice.

Povinná funkce:

```python
transition_matrix(bigrams)
```

nejprve spočítá absolutní četnosti bigramů.

## Ošetření nul

Některé kombinace znaků se v referenčním textu nemusí objevit. Jejich četnost by byla nulová, což by při pozdějším výpočtu logaritmu způsobilo problém.

Proto se všechny nulové buňky nahradí hodnotou `1`. Jde o jednoduché vyhlazení požadované zadáním.

## Relativní referenční matice

Po ošetření nul se matice vydělí součtem všech buněk. Tím vznikne relativní referenční matice, jejíž hodnoty představují odhad pravděpodobností bigramů.

Matice se ukládá do:

```text
models/TM_ref.npy
```

Finální matice má tyto vlastnosti:

- rozměr `(27, 27)`,
- součet hodnot `1.0`,
- žádné nulové hodnoty,
- žádné hodnoty `NaN`,
- žádné nekonečné hodnoty.

## Věrohodnost textu

Funkce:

```python
plausibility(text, TM_ref)
```

ohodnotí kandidátní plaintext podle referenční matice.

Nejprve vytvoří bigramy kandidátního textu a jeho pozorovanou matici pomocí:

```python
transition_matrix(get_bigrams(text))
```

Skóre se vypočítá jako:

```text
součet(log(TM_ref[i, j]) × TM_obs[i, j])
```

Vyšší hodnota, tedy méně záporné číslo, obvykle znamená, že text lépe odpovídá českým bigramovým četnostem.

## Metropolis-Hastingsův algoritmus

Pro hledání klíče se používá Metropolis-Hastingsův algoritmus.

Postup jednoho běhu:

1. vytvoří se náhodný počáteční klíč, pokud nebyl zadaný,
2. ciphertext se dešifruje aktuálním klíčem,
3. spočítá se plausibility aktuálního plaintextu,
4. v každé iteraci se v klíči prohodí dva náhodné znaky,
5. kandidátní klíč se použije k dešifrování,
6. spočítá se nové skóre,
7. lepší kandidát se přijme vždy,
8. horší kandidát se přijme s pravděpodobností `0.01`,
9. nejlepší nalezený klíč se uchovává zvlášť.

Přijetí některých horších kandidátů pomáhá algoritmu uniknout z lokálního maxima.

Povinná funkce je:

```python
prolom_substitute(text, TM_ref, iter, start_key=None)
```

Vrací:

```text
(best_key, best_decrypted_text, best_score)
```

## Vlastní rozšíření

Projekt obsahuje několik volitelných rozšíření, která nemění povinnou logiku zadání.

### Lokální doladění klíče

Funkce `polish_key` po skončení M-H algoritmu systematicky vyzkouší všechny možné výměny dvou pozic v klíči.

Pokud některá výměna zlepší skóre, přijme se nejlepší zlepšení. Postup se opakuje, dokud se skóre zlepšuje nebo dokud se nedosáhne maximálního počtu průchodů.

### Restarty

Objektové API může spustit více nezávislých M-H běhů a vybrat výsledek s nejvyšší plausibility.

### Paralelní zpracování

Jednotlivé ciphertext soubory jsou na sobě nezávislé. Dávkový skript je proto může zpracovat více procesy současně.

Paralelizují se celé soubory, ne jednotlivé iterace jednoho M-H běhu.

## Povinné API

Projekt zachovává požadované veřejné funkce:

```python
substitute_encrypt(plaintext, key)
substitute_decrypt(ciphertext, key)
get_bigrams(text)
transition_matrix(bigrams)
plausibility(text, TM_ref)
prolom_substitute(text, TM_ref, iter, start_key=None)
```

Vedle nich je dostupná třída:

```python
SubstitutionCipher
```

Ta poskytuje pohodlné objektové rozhraní nad stejnou implementací.

## Zpracování ciphertextů

Vstupní ciphertexty jsou ve složce:

```text
data/ciphertexts/
```

Dávkové zpracování spouští:

```powershell
python scripts\decrypt_samples.py `
  --matrix models\TM_ref.npy `
  --input-directory data\ciphertexts `
  --output-directory outputs `
  --iterations 20000 `
  --restarts 1 `
  --workers 4
```

Pro každý vstup vzniknou dva soubory:

```text
text_{délka}_sample_{id}_plaintext.txt
text_{délka}_sample_{id}_key.txt
```

## Dosažené výsledky

Bylo zpracováno všech 60 ciphertext souborů ze zadání.

Vzniklo:

- 60 plaintext souborů,
- 60 souborů s nalezeným klíčem,
- 0 chyb při dávkovém zpracování.

Všechny exportované klíče jsou platnými permutacemi projektové abecedy a délky plaintextů odpovídají délkám uvedeným v názvech vstupních souborů.

Pro objektivní kontrolu byl použit známý učitelský příklad:

```text
text_1000_sample_1
```

Známý plaintext ani učitelský klíč nebyly použity během hledání. Sloužily pouze k následnému vyhodnocení hotového slepého běhu.

Výsledek známého příkladu:

- správné znaky: `922 / 1000`,
- procento shody: `92,2 %`,
- přesná shoda celého plaintextu: ne,
- přesná shoda celého klíče: ne.

Výsledek je platný, protože zadání nevyžaduje stoprocentní úspěšnost. Metropolis-Hastingsův algoritmus je náhodný a bigramový model hodnotí pouze dvojice sousedních znaků. Nejlépe hodnocený text proto nemusí být vždy přesně totožný s původním plaintextem.

Kratší ciphertexty jsou obvykle obtížnější, protože obsahují méně bigramů a poskytují méně informací o vlastnostech původního jazyka.

Podrobný přehled všech výstupů je uložen v:

```text
reports/evaluation_summary.md
reports/evaluation_summary.csv
```

## Testování

Automatické testy ověřují zejména:

- povinné podpisy funkcí,
- správné šifrování a dešifrování,
- tvorbu bigramů,
- vlastnosti přechodové matice,
- vytvoření referenční matice,
- objektové API,
- paralelní dávkové zpracování,
- názvy a počty výstupních souborů,
- downloader referenčního textu bez skutečného připojení k internetu,
- strukturu projektu,
- platnost notebooku a dokumentace.

Poslední kontrola proběhla úspěšně:

```text
32 passed
```

Validace souborů zadání skončila stavem:

```text
Status: OK
```

## Omezení

Použité řešení má několik omezení:

- Metropolis-Hastingsův algoritmus je náhodný, takže se výsledky jednotlivých běhů mohou lišit.
- Kratší ciphertexty poskytují méně bigramů a hůře se vyhodnocují.
- Bigramový model nezná význam slov ani celých vět.
- Nejvyšší plausibility nemusí vždy odpovídat přesnému původnímu plaintextu.
- Pokud se některý znak v ciphertextu nevyskytne, jeho část klíče nemusí být jednoznačně určitelná.
- Více iterací nebo restartů může výsledek zlepšit, ale prodlužuje výpočet.

## Závěr

Projekt implementuje šifrování, dešifrování a kryptoanalýzu klasické monoalfabetické substituční šifry podle zadání.

Referenční jazykový model vzniká pouze z knihy Válka s mloky. Text se získává z českých Wikizdrojů, převede se do projektové abecedy a následně se z něj vytvoří relativní bigramová matice `models/TM_ref.npy`.

Kryptoanalýza používá Metropolis-Hastingsův algoritmus s výměnou dvou náhodných znaků a pravděpodobností `0.01` pro přijetí horšího kandidáta.

Bylo úspěšně zpracováno všech 60 ciphertextů a pro každý vznikl plaintext i nalezený klíč. U známého učitelského příkladu bylo správně obnoveno 922 z 1000 znaků, tedy 92,2 % textu.

Výsledky ukazují, že jednoduchý bigramový model dokáže substituční šifru prolomit s vysokou úspěšností, ale kvůli náhodnosti hledání a omezením bigramového modelu není při každém běhu zaručeno přesné obnovení celého plaintextu a klíče.
