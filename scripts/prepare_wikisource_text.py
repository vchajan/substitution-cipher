import json
import re
import time
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# =========================
# Nastavenia projektu
# =========================

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ_"
MIN_BIGRAM_COUNT = 300_000

MAIN_PAGE = "Krakatit"

# Koreň projektu = priečinok nad /scripts
PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_OUTPUT = PROJECT_ROOT / "data" / "raw" / "raw_text.txt"
CLEAN_OUTPUT = PROJECT_ROOT / "data" / "processed" / "clean_text.txt"

CACHE_DIR = PROJECT_ROOT / "data" / "cache_wikisource"

# Ak chceš všetko stiahnuť úplne nanovo, nastav na True.
# Bežne nechaj False, aby Wikisource nedávalo HTTP 429 Too Many Requests.
FORCE_DOWNLOAD = False


# =========================
# HTML -> čistý text
# =========================

class HTMLTextExtractor(HTMLParser):
    """
    Jednoduchý HTML parser, který z HTML stránky vytáhne text.
    Nepoužívá externí knihovny typu BeautifulSoup.
    """

    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip_depth = 0
        self.skip_tags = {
            "script",
            "style",
            "table",
            "sup",
            "math",
            "noscript",
        }

    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.skip_depth += 1

        if self.skip_depth == 0 and tag in {
            "p",
            "br",
            "div",
            "section",
            "h1",
            "h2",
            "h3",
            "li",
        }:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.skip_tags and self.skip_depth > 0:
            self.skip_depth -= 1

        if self.skip_depth == 0 and tag in {
            "p",
            "div",
            "section",
            "h1",
            "h2",
            "h3",
            "li",
        }:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip_depth == 0:
            self.parts.append(data)

    def get_text(self) -> str:
        text = "".join(self.parts)

        # zjednodušenie whitespace v raw texte
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)

        return text.strip()


def html_to_text(html: str) -> str:
    parser = HTMLTextExtractor()
    parser.feed(html)
    return parser.get_text()


# =========================
# Wikisource API
# =========================

def safe_filename(title: str) -> str:
    """
    Vytvorí bezpečný názov cache súboru.
    Napr. Krakatit/I. -> Krakatit_I.txt
    """
    filename = re.sub(r"[^A-Za-z0-9_]+", "_", title).strip("_")
    return f"{filename}.txt"


def call_wikisource_api(params: dict, retries: int = 8) -> dict:
    """
    Zavolá MediaWiki API pro český Wikisource.
    Pri HTTP 429 čaká a skúša znova.
    """
    base_url = "https://cs.wikisource.org/w/api.php"

    params = dict(params)
    params["format"] = "json"
    params["formatversion"] = "2"

    url = base_url + "?" + urlencode(params)

    request = Request(
        url,
        headers={
            "User-Agent": "substitution-cipher-school-project/1.0 "
                          "(school project; respectful download)"
        },
    )

    for attempt in range(1, retries + 1):
        try:
            with urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))

        except HTTPError as error:
            if error.code == 429:
                sleep_time = 10 * attempt
                print(
                    f"HTTP 429: Wikisource dočasně omezuje požadavky. "
                    f"Čekám {sleep_time} s a zkusím znovu..."
                )
                time.sleep(sleep_time)
            else:
                raise

        except URLError as error:
            sleep_time = 10 * attempt
            print(f"Chyba spojení: {error}. Čekám {sleep_time} s a zkusím znovu...")
            time.sleep(sleep_time)

    raise RuntimeError("Nepodařilo se stáhnout data z Wikisource ani po opakovaných pokusech.")


def download_page_text(page_title: str) -> str:
    """
    Stáhne jednu stránku z Wikisource a vrátí její text.
    Používá cache, aby se stránky nemusely stahovat pořád dokola.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / safe_filename(page_title)

    if cache_file.exists() and not FORCE_DOWNLOAD:
        print(f"Načítám z cache: {page_title}")
        return cache_file.read_text(encoding="utf-8")

    data = call_wikisource_api({
        "action": "parse",
        "page": page_title,
        "prop": "text",
        "redirects": "1",
        "disabletoc": "1",
        "disableeditsection": "1",
    })

    if "error" in data:
        raise RuntimeError(f"Chyba při stahování stránky {page_title}: {data['error']}")

    html = data["parse"]["text"]
    text = html_to_text(html)

    cache_file.write_text(text, encoding="utf-8")

    return text


# =========================
# Kapitoly Krakatitu
# =========================

def int_to_roman(number: int) -> str:
    """
    Převede celé číslo na římské číslo.
    Napr. 1 -> I, 4 -> IV, 9 -> IX, 54 -> LIV.
    """
    values = [
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]

    result = ""

    for value, symbol in values:
        while number >= value:
            result += symbol
            number -= value

    return result


def get_krakatit_chapter_pages() -> list[str]:
    """
    Krakatit na Wikisource používá kapitoly I. až LIV.
    Tady je generujeme natvrdo, aby se nespoléhalo na náhodné pořadí odkazů.
    """
    return [f"Krakatit/{int_to_roman(i)}." for i in range(1, 55)]


# =========================
# Čistenie textu
# =========================

def remove_diacritics(text: str) -> str:
    """
    Odstraní diakritiku.
    Napr. á -> a, č -> c, ř -> r.
    """
    normalized = unicodedata.normalize("NFD", text)

    return "".join(
        char for char in normalized
        if unicodedata.category(char) != "Mn"
    )


def clean_text(text: str) -> str:
    """
    Vyčistí text tak, aby obsahoval pouze znaky A-Z a _.

    Postup:
    - odstranění diakritiky,
    - převod na velká písmena,
    - odstranění interpunkce, číslic a cizích znaků,
    - mezery a nové řádky se změní na podtržítko,
    - více podtržítek za sebou se zkrátí na jedno.
    """
    text = remove_diacritics(text)
    text = text.upper()

    # Všechno kromě písmen A-Z a whitespace nahradíme mezerou.
    # Tím se pomlčky, čárky, tečky, čísla atd. nestanou součástí abecedy.
    text = re.sub(r"[^A-Z\s]", " ", text)

    # Whitespace převedeme na podtržítko.
    text = re.sub(r"\s+", "_", text)

    # Více podtržítek za sebou zkrátíme na jedno.
    text = re.sub(r"_+", "_", text)

    return text.strip("_")


def validate_clean_text(text: str) -> None:
    """
    Skontroluje, že clean text obsahuje iba znaky zo zadanej abecedy
    a že má dostatok bigramov.
    """
    invalid_chars = sorted(set(text) - set(ALPHABET))
    bigram_count = max(0, len(text) - 1)

    print()
    print("===== KONTROLA CLEAN TEXTU =====")

    if invalid_chars:
        raise ValueError(f"Text obsahuje nepovolené znaky: {invalid_chars}")

    print("Kontrola znaků: OK")
    print(f"Délka vyčištěného textu: {len(text)} znaků")
    print(f"Počet bigramů: {bigram_count}")

    if bigram_count < MIN_BIGRAM_COUNT:
        print(f"UPOZORNĚNÍ: Text má méně než {MIN_BIGRAM_COUNT} bigramů.")
        print("To může být pro referenční bigramovou matici málo.")
    else:
        print("Počet bigramů je dostačující.")


def print_text_statistics(raw_text: str, cleaned_text: str) -> None:
    """
    Vypíše základní štatistiky, aby bolo vidieť, koľko znakov ubudlo čistením.
    """
    print()
    print("===== STATISTIKA =====")
    print(f"Délka raw textu: {len(raw_text)} znaků")
    print(f"Délka clean textu: {len(cleaned_text)} znaků")
    print(f"Počet bigramů v clean textu: {max(0, len(cleaned_text) - 1)}")

    if raw_text:
        ratio = len(cleaned_text) / len(raw_text)
        print(f"Poměr clean/raw: {ratio:.2%}")


# =========================
# Hlavný proces
# =========================

def main() -> None:
    print("===== PŘÍPRAVA TEXTU Z WIKISOURCE =====")
    print(f"Koreň projektu: {PROJECT_ROOT}")
    print(f"Výstup raw textu: {RAW_OUTPUT}")
    print(f"Výstup clean textu: {CLEAN_OUTPUT}")
    print()

    # Hlavní stránka je obvykle jen rozcestník, ale stáhneme ji pro kontrolu.
    print(f"Stahuji hlavní stránku: {MAIN_PAGE}")
    main_page_text = download_page_text(MAIN_PAGE)
    main_page_clean = clean_text(main_page_text)

    print(f"Délka hlavní stránky po vyčištění: {len(main_page_clean)} znaků")

    # Pre samotný referenčný text použijeme kapitoly I. až LIV.
    chapter_pages = get_krakatit_chapter_pages()

    print()
    print(f"Stahuji kapitoly knihy Krakatit: {len(chapter_pages)} kapitol")
    print("Poznámka: Ak už sú kapitoly v cache, načítajú sa lokálně.")
    print()

    chapter_texts = []

    for index, chapter_page in enumerate(chapter_pages, start=1):
        print(f"[{index:02d}/{len(chapter_pages)}] {chapter_page}")

        chapter_text = download_page_text(chapter_page)
        chapter_clean = clean_text(chapter_text)

        print(f"    raw: {len(chapter_text)} znaků, clean: {len(chapter_clean)} znaků")

        chapter_texts.append(chapter_text)

        # Ak sa stránka čítala z cache, pauza nevadí.
        # Ak sa sťahuje z webu, pauza pomáha vyhnúť sa HTTP 429.
        time.sleep(2.0)

    raw_text = "\n\n".join(chapter_texts)
    cleaned_text = clean_text(raw_text)

    RAW_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    CLEAN_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    RAW_OUTPUT.write_text(raw_text, encoding="utf-8")
    CLEAN_OUTPUT.write_text(cleaned_text, encoding="utf-8")

    print_text_statistics(raw_text, cleaned_text)
    validate_clean_text(cleaned_text)

    print()
    print("===== HOTOVO =====")
    print(f"Neupravený text uložen jako:")
    print(f"  {RAW_OUTPUT}")
    print(f"Vyčištěný text uložen jako:")
    print(f"  {CLEAN_OUTPUT}")
    print()
    print("Rychlá kontrola v PowerShellu:")
    print(
        "python -c \"from pathlib import Path; "
        "t=Path('data/processed/clean_text.txt').read_text(encoding='utf-8'); "
        "print(len(t), len(t)-1, set(t)-set('ABCDEFGHIJKLMNOPQRSTUVWXYZ_'))\""
    )


if __name__ == "__main__":
    main()