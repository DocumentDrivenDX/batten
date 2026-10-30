#!/usr/bin/env python3
"""Check the generated, prefix-safe static publication without network access."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from build import OUT, PAGES


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = set()
        self.links = []
        self.headings = 0
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            if attrs['id'] in self.ids:
                raise ValueError(f"Duplicate element ID: {attrs['id']}")
            self.ids.add(attrs['id'])
        if tag == 'h1':
            self.headings += 1
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append((tag, attrs[key]))


def verify():
    pages = {f'{slug}.html': Page((OUT / f'{slug}.html').read_text()) for slug, _ in PAGES}
    for name, page in pages.items():
        if page.headings != 1 or 'main' not in page.ids:
            raise ValueError(f'Missing primary landmark or unique heading: {name}')
        for tag, raw in page.links:
            url = urlsplit(raw)
            if url.scheme or url.netloc:
                if tag != 'a' or url.scheme != 'https':
                    raise ValueError(f'External runtime dependency: {raw}')
                continue
            if url.path.startswith('/'):
                raise ValueError(f'Project-prefix-unsafe path: {raw}')
            target = (OUT / unquote(url.path or name)).resolve()
            if not target.is_relative_to(OUT.resolve()) or not target.is_file():
                raise ValueError(f'Broken or escaping local reference in {name}: {raw}')
            if url.fragment and target.name in pages:
                if unquote(url.fragment) not in pages[target.name].ids:
                    raise ValueError(f'Missing fragment in {name}: {raw}')
    if not (OUT / '.nojekyll').is_file():
        raise ValueError('Missing Pages static publication marker')
    if any(p.is_symlink() for p in OUT.rglob('*')):
        raise ValueError('Publication may not contain symlinks')
    print(f'Verified {len(pages)} pages: local links, anchors, assets and project-prefix safety.')


if __name__ == '__main__':
    verify()
