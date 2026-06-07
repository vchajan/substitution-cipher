"""Stáhne surový text Války s mloky z českých Wikizdrojů."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from substitution_cipher.paths import RAW_REFERENCE_TEXT_PATH  # noqa: E402


WIKISOURCE_API = "https://cs.wikisource.org/w/api.php"
WIKISOURCE_PAGE = "Válka_s_Mloky"
USER_AGENT = "substitution-cipher-school-project/1.0 (MediaWiki API downloader)"
MIN_REFERENCE_LENGTH = 200_000


class _VisibleTextParser(HTMLParser):
    """Jednoduchý převod renderovaného obsahu stránky na viditelný text."""

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        if tag in {"script", "style"}:
            self._skip_depth += 1
        elif tag in {"p", "br", "div", "section", "h1", "h2", "h3", "li"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1
        elif tag in {"p", "div", "section", "h1", "h2", "h3", "li"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        return "".join(self.parts)


def _api_get_json(params: dict[str, str | int]) -> dict:
    """Zavolá MediaWiki API a vrátí JSON odpověď."""
    query = urlencode({**params, "format": "json", "formatversion": "2"})
    request = Request(
        f"{WIKISOURCE_API}?{query}",
        headers={"User-Agent": USER_AGENT},
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(
            "Nepodařilo se stáhnout data z českých Wikizdrojů. "
            "Zkontrolujte připojení k internetu nebo použijte už uložený raw text."
        ) from exc


def _resolve_page_title(page: str) -> str:
    """Vrátí skutečný název stránky po případném přesměrování."""
    data = _api_get_json(
        {
            "action": "query",
            "titles": page.replace("_", " "),
            "redirects": "1",
        }
    )
    pages = data.get("query", {}).get("pages", [])
    if not pages or pages[0].get("missing"):
        raise RuntimeError(f"Stránka na Wikizdrojích nebyla nalezena: {page}")
    return str(pages[0]["title"])


def _parse_link_title(link: dict) -> str | None:
    title = link.get("title", link.get("*"))
    return str(title) if title else None


def _linked_subpages(page_title: str) -> list[str]:
    """Najde podstránky odkazované z hlavní stránky v pořadí obsahu."""
    data = _api_get_json(
        {
            "action": "parse",
            "page": page_title,
            "prop": "links",
            "redirects": "1",
        }
    )
    links = data.get("parse", {}).get("links", [])
    prefix = f"{page_title}/"
    titles: list[str] = []
    seen: set[str] = set()

    for link in links:
        title = _parse_link_title(link)
        if title and title.startswith(prefix) and title not in seen:
            seen.add(title)
            titles.append(title)

    return titles


def _natural_key(title: str) -> list[int | str]:
    suffix = title.rsplit("/", maxsplit=1)[-1]
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", suffix)]


def _all_subpages(page_title: str) -> list[str]:
    """Záložní seznam podstránek, pokud je hlavní stránka neodkazuje přímo."""
    titles: list[str] = []
    params: dict[str, str | int] = {
        "action": "query",
        "list": "allpages",
        "apnamespace": "0",
        "apprefix": f"{page_title}/",
        "aplimit": "max",
    }

    while True:
        data = _api_get_json(params)
        for page in data.get("query", {}).get("allpages", []):
            titles.append(str(page["title"]))
        continue_data = data.get("continue")
        if not continue_data:
            break
        params.update(continue_data)

    return sorted(titles, key=_natural_key)


def discover_content_pages(page: str = WIKISOURCE_PAGE) -> list[str]:
    """Vrátí stránky, které tvoří vlastní text díla."""
    page_title = _resolve_page_title(page)
    subpages = _linked_subpages(page_title) or _all_subpages(page_title)
    return subpages if subpages else [page_title]


def _page_html(page_title: str) -> str:
    data = _api_get_json(
        {
            "action": "parse",
            "page": page_title,
            "prop": "text",
            "redirects": "1",
            "disablelimitreport": "1",
            "disableeditsection": "1",
        }
    )
    try:
        return str(data["parse"]["text"])
    except KeyError as exc:
        raise RuntimeError(f"MediaWiki API nevrátilo text stránky: {page_title}") from exc


def html_to_plain_text(content_html: str) -> str:
    """Převede HTML obsahu z MediaWiki API na prostý text bez navigace webu."""
    parser = _VisibleTextParser()
    parser.feed(content_html)
    text = html.unescape(parser.text())
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    compact_lines = [line for line in lines if line]
    return "\n\n".join(compact_lines)


def download_book_text(page: str = WIKISOURCE_PAGE) -> tuple[str, int]:
    """Stáhne všechny části knihy a spojí je do jednoho surového textu."""
    page_titles = discover_content_pages(page)
    parts = [html_to_plain_text(_page_html(title)) for title in page_titles]
    text = "\n\n".join(part for part in parts if part.strip()).strip()
    return text, len(page_titles)


def download_reference_text(
    output_path: str | Path = RAW_REFERENCE_TEXT_PATH,
    force: bool = False,
    min_length: int = MIN_REFERENCE_LENGTH,
) -> tuple[Path, int, int, bool]:
    """Stáhne raw text, pokud už lokálně neexistuje nebo je použit ``--force``."""
    target = Path(output_path)
    if target.exists() and not force:
        text_length = len(target.read_text(encoding="utf-8"))
        return target, 0, text_length, False

    text, part_count = download_book_text()
    if len(text) < min_length:
        raise RuntimeError(
            f"Stažený text je podezřele krátký ({len(text)} znaků). "
            f"Očekává se alespoň {min_length} znaků."
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target, part_count, len(text), True


def main(argv: list[str] | None = None) -> int:
    """Spustí stažení referenčního textu z příkazové řádky."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Přepíše existující raw text novým stažením z Wikizdrojů.",
    )
    args = parser.parse_args(argv)

    try:
        output_path, part_count, text_length, downloaded = download_reference_text(
            force=args.force,
        )
    except RuntimeError as exc:
        print(f"Chyba: {exc}", file=sys.stderr)
        return 1

    print("===== STAŽENÍ REFERENČNÍHO TEXTU =====")
    print(f"Zdroj: {WIKISOURCE_API}")
    print(f"Stránka: {WIKISOURCE_PAGE}")
    if downloaded:
        print(f"Stažené části: {part_count}")
    else:
        print("Lokální soubor už existuje, stahování se přeskočilo.")
        print("Pro nové stažení použijte --force.")
    print(f"Délka textu: {text_length}")
    print(f"Cílová cesta: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
