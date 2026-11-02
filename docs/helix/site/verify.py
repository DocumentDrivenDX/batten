#!/usr/bin/env python3
"""Check the generated, prefix-safe static publication without network access."""

import struct
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

from build import OUT, PAGES, PUBLIC_URL


class Page(HTMLParser):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[tuple[str, str]] = []
        self.headings = 0
        self.metadata: dict[str, str] = {}
        self.canonical = ""
        self.feed(text)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value for key, value in attrs if value is not None}
        if values.get("id"):
            if values["id"] in self.ids:
                raise ValueError(f"Duplicate element ID: {values['id']}")
            self.ids.add(values["id"])
        if tag == "h1":
            self.headings += 1
        if tag == "meta":
            key = values.get("property", values.get("name", ""))
            if key in self.metadata:
                raise ValueError(f"Duplicate metadata: {key}")
            self.metadata[key] = values.get("content", "")
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical = values.get("href", "")
        for key in ("href", "src"):
            if values.get(key):
                self.links.append((tag, values[key]))


def verify_links(name: str, page: Page, pages: dict[str, Page]) -> None:
    for tag, raw in page.links:
        url = urlsplit(raw)
        if url.scheme or url.netloc:
            if (tag != "a" and raw != page.canonical) or url.scheme != "https":
                raise ValueError(f"External runtime dependency: {raw}")
            continue
        if url.path.startswith("/"):
            raise ValueError(f"Project-prefix-unsafe path: {raw}")
        target = (OUT / unquote(url.path or name)).resolve()
        if not target.is_relative_to(OUT.resolve()) or not target.is_file():
            raise ValueError(f"Broken or escaping local reference in {name}: {raw}")
        if url.fragment and target.name in pages:
            if unquote(url.fragment) not in pages[target.name].ids:
                raise ValueError(f"Missing fragment in {name}: {raw}")


def verify_social(name: str, page: Page) -> None:
    expected = PUBLIC_URL + ("" if name == "index.html" else name)
    meta = page.metadata
    if page.canonical != expected or meta.get("og:url") != expected:
        raise ValueError(f"Incorrect canonical/social URL: {name}")
    for key in ("og:title", "og:description", "og:site_name", "og:image:alt"):
        if not meta.get(key):
            raise ValueError(f"Missing social metadata {key}: {name}")
    if (
        meta.get("og:type") != "website"
        or meta.get("twitter:card") != "summary_large_image"
    ):
        raise ValueError(f"Incorrect social card type: {name}")
    for suffix in ("title", "description", "image", "image:alt"):
        if meta.get(f"twitter:{suffix}") != meta.get(f"og:{suffix}"):
            raise ValueError(f"Inconsistent social metadata: {name}/{suffix}")
    image = meta.get("og:image", "")
    if image != PUBLIC_URL + "assets/social-preview.png":
        raise ValueError(f"Incorrect public preview image: {name}")
    data = (OUT / "assets/social-preview.png").read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or struct.unpack(">II", data[16:24]) != (
        1200,
        630,
    ):
        raise ValueError("Social preview must be a 1200 by 630 PNG")
    if (
        meta.get("og:image:width"),
        meta.get("og:image:height"),
        meta.get("og:image:type"),
    ) != ("1200", "630", "image/png"):
        raise ValueError("Incorrect preview image dimensions or media type")


def verify() -> None:
    pages = {
        f"{slug}.html": Page((OUT / f"{slug}.html").read_text()) for slug, _ in PAGES
    }
    for name, page in pages.items():
        if page.headings != 1 or "main" not in page.ids:
            raise ValueError(f"Missing primary landmark or unique heading: {name}")
        verify_links(name, page, pages)
        verify_social(name, page)
    if not (OUT / ".nojekyll").is_file():
        raise ValueError("Missing Pages static publication marker")
    if any(p.is_symlink() for p in OUT.rglob("*")):
        raise ValueError("Publication may not contain symlinks")
    print(
        f"Verified {len(pages)} pages: local links, anchors, assets and project-prefix safety."
    )


if __name__ == "__main__":
    verify()
