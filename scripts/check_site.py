#!/usr/bin/env python3
"""Small dependency-free checks for the static bilingual website."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PAGES = (ROOT / "index.html", ROOT / "fr" / "index.html")
PROJECT_PAGES = {"/bgobs/"}


class Document(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang: str | None = None
        self.links: list[str] = []
        self.images: list[tuple[str, str | None]] = []
        self.alternates: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.html_lang = values.get("lang")
        elif tag == "a" and values.get("href"):
            self.links.append(values["href"] or "")
        elif tag == "img" and values.get("src"):
            self.images.append((values["src"] or "", values.get("alt")))
        elif tag == "link" and values.get("rel") == "alternate":
            language = values.get("hreflang")
            href = values.get("href")
            if language and href:
                self.alternates[language] = href


def local_target(url: str) -> Path | None:
    if urlsplit(url).path in PROJECT_PAGES:
        return None
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    relative = unquote(parsed.path).lstrip("/")
    target = ROOT / relative
    if parsed.path.endswith("/"):
        target /= "index.html"
    return target


def main() -> None:
    expected_languages = {"index.html": "en", "fr/index.html": "fr"}

    for page in PAGES:
        relative = page.relative_to(ROOT).as_posix()
        source = page.read_text(encoding="utf-8")
        document = Document()
        document.feed(source)

        assert document.html_lang == expected_languages[relative], relative
        assert {"en", "fr", "x-default"} <= document.alternates.keys(), relative
        assert "/bgobs/" in document.links, relative
        assert "https://github.com/LeMegaGeek/bgobs" in document.links, relative
        assert "Proprietary" in source or "Propriétaire" in source, relative
        assert "GPL-3.0-or-later" in source, relative
        assert "assets/cacam-logo.png" not in source, relative
        assert any(src == "/assets/bgobs-logo-192.png" for src, _alt in document.images), relative

        for url in document.links + [src for src, _alt in document.images]:
            target = local_target(url)
            if target is not None:
                assert target.exists(), f"{relative}: missing {url}"

        for src, alt in document.images:
            assert alt is not None, f"{relative}: image {src} has no alt attribute"

    french = (ROOT / "fr" / "index.html").read_text(encoding="utf-8")
    for accented_word in ("téléphone", "caméra", "propriétaire", "arrière-plan", "confidentialité"):
        assert accented_word in french, f"French text lost accents: {accented_word}"

    checksums = ROOT / "downloads" / "cacam" / "0.9.15" / "SHA256SUMS-0.9.15.txt"
    listed = checksums.read_text(encoding="utf-8")
    assert "CaCam-0.9.15-release.apk" in listed
    assert "CaCam-0.9.15-release.aab" in listed

    print("Static site checks passed for English and French pages.")


if __name__ == "__main__":
    main()
