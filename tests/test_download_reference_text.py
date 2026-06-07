from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import scripts.download_reference_text as downloader


def _mock_api_factory(long_part: str):
    def fake_api(params):
        action = params["action"]
        if action == "query" and params.get("titles"):
            return {"query": {"pages": [{"title": "Válka s Mloky"}]}}
        if action == "parse" and params.get("prop") == "links":
            return {
                "parse": {
                    "links": [
                        {"title": "Válka s Mloky/1"},
                        {"title": "Válka s Mloky/2"},
                    ]
                }
            }
        if action == "parse" and params.get("prop") == "text":
            page = params["page"]
            return {"parse": {"text": f"<div><p>{page} {long_part}</p></div>"}}
        raise AssertionError(f"Neočekávané parametry API: {params}")

    return fake_api


def test_download_reference_text_uses_mediawiki_parts(monkeypatch):
    monkeypatch.setattr(downloader, "_api_get_json", _mock_api_factory("AHOJ " * 20))

    with TemporaryDirectory(prefix="download_reference_", dir="outputs") as directory:
        output_path = Path(directory) / "valka_s_mloky_raw.txt"
        path, part_count, text_length, downloaded = downloader.download_reference_text(
            output_path=output_path,
            force=False,
            min_length=10,
        )

        text = output_path.read_text(encoding="utf-8")

    assert path == output_path
    assert part_count == 2
    assert text_length == len(text)
    assert downloaded is True
    assert "Válka s Mloky/1" in text
    assert "Válka s Mloky/2" in text
    assert "<div>" not in text


def test_download_reference_text_skips_existing_without_force(monkeypatch):
    def forbidden_api(_params):
        raise AssertionError("Bez --force se nemá volat internet.")

    monkeypatch.setattr(downloader, "_api_get_json", forbidden_api)

    with TemporaryDirectory(prefix="download_skip_", dir="outputs") as directory:
        output_path = Path(directory) / "valka_s_mloky_raw.txt"
        output_path.write_text("ULOZENY_TEXT", encoding="utf-8")

        path, part_count, text_length, downloaded = downloader.download_reference_text(
            output_path=output_path,
            force=False,
        )

    assert path == output_path
    assert part_count == 0
    assert text_length == len("ULOZENY_TEXT")
    assert downloaded is False


def test_download_reference_text_force_overwrites_existing(monkeypatch):
    monkeypatch.setattr(downloader, "_api_get_json", _mock_api_factory("NOVY_TEXT " * 10))

    with TemporaryDirectory(prefix="download_force_", dir="outputs") as directory:
        output_path = Path(directory) / "valka_s_mloky_raw.txt"
        output_path.write_text("STARY_TEXT", encoding="utf-8")

        _path, _part_count, _text_length, downloaded = downloader.download_reference_text(
            output_path=output_path,
            force=True,
            min_length=10,
        )

        text = output_path.read_text(encoding="utf-8")

    assert downloaded is True
    assert "NOVY_TEXT" in text
    assert "STARY_TEXT" not in text


def test_download_reference_text_rejects_suspiciously_short_result(monkeypatch):
    monkeypatch.setattr(downloader, "_api_get_json", _mock_api_factory("KRATKY"))

    with TemporaryDirectory(prefix="download_short_", dir="outputs") as directory:
        output_path = Path(directory) / "valka_s_mloky_raw.txt"
        with pytest.raises(RuntimeError, match="podezřele krátký"):
            downloader.download_reference_text(
                output_path=output_path,
                force=True,
                min_length=1000,
            )
