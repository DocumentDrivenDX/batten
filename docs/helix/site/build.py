#!/usr/bin/env python3
"""Build the Batten design microsite from source-stamped guide pages. Stdlib only."""

import hashlib
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SITE = Path(__file__).resolve().parent
GUIDE = ROOT / "docs/helix/guide/developer"
OUT = SITE / "dist"
REPO = "https://github.com/DocumentDrivenDX/batten"
PUBLIC_URL = "https://documentdrivendx.github.io/batten/"
DESCRIPTION = "Batten: declarative AI applications with explicit platform choices. Try the local approval desk preview, or explore the architecture for governed fleets."
PAGES = [
    ("index", "Overview"),
    ("composition", "Compose"),
    ("hosting", "Hosting"),
    ("integrations", "Platform"),
    ("architecture", "Architecture"),
    ("examples", "Examples"),
    ("about", "About this guide"),
]
PAGES.extend([
    (f"example-{app['slug']}", app["slug"].replace("-", " ").title())
    for app in json.loads(
        (ROOT / "docs/helix/reference-apps/catalog.json").read_text()
    )["apps"]
])
MARK = '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M5 6h22M5 16h22M5 26h22M10 3v26M22 3v26"/></svg>'


def inline(text: str) -> str:
    """Render this guide's intentionally small, escaped Markdown subset."""

    def link(match: re.Match[str]) -> str:
        label, url = match.groups()
        if url.endswith(".md") and not url.startswith("http"):
            url = url[:-3] + ".html"
        if not (url.startswith("https://") or re.fullmatch(r"[a-z-]+\.html", url)):
            raise ValueError(f"Unsupported guide link: {url}")
        return f'<a href="{html.escape(url, quote=True)}">{html.escape(label)}</a>'

    escaped = html.escape(text)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, escaped)


def markdown(text: str) -> tuple[str, list[tuple[str, str]]]:
    body = re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()
    chunks: list[str] = []
    toc: list[tuple[str, str]] = []
    for block in body.split("\n\n"):
        block = block.strip()
        if not block or block.startswith("# "):
            continue
        if block.startswith("## "):
            title = block[3:].strip()
            anchor = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            toc.append((anchor, title))
            chunks.append(f'<h2 id="{anchor}">{html.escape(title)}</h2>')
        else:
            chunks.append("<p>" + inline(" ".join(block.splitlines())) + "</p>")
    return "\n".join(chunks), toc


def sources(text: str) -> str:
    refs = re.findall(r"<!-- helix:source ([^ ]+) sha256:([a-f0-9]+) -->", text)
    rows: list[str] = []
    for path, expected in refs:
        value = (ROOT / path).read_text()
        digest = hashlib.sha256(
            "\n".join(x.rstrip() for x in value.splitlines()).encode()
        ).hexdigest()[:16]
        if digest != expected:
            raise ValueError(f"Stale guide source: {path}")
        label = Path(path).stem.replace("-", " ")
        rows.append(
            f'<li><a href="{REPO}/blob/main/{path}">{html.escape(label)}</a><code>{digest}</code></li>'
        )
    return (
        '<details class="sources"><summary>Read the design sources <span>↗</span></summary><ul>'
        + "".join(rows)
        + "</ul></details>"
    )


def header(slug: str) -> str:
    links = "".join(
        f'<a href="{key}.html"'
        + (' aria-current="page"' if key == slug else "")
        + f">{label}</a>"
        for key, label in PAGES
        if key != "about" and not key.startswith("example-")
    )
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><a class="brand" href="index.html">{MARK}<span>batten<span class="brand-dot">.</span></span></a>
<button class="menu-toggle" aria-expanded="false" aria-controls="site-nav">Menu <span>☰</span></button>
<nav id="site-nav" aria-label="Main navigation">{links}</nav>
<div class="header-tools"><button class="theme-toggle" aria-label="Switch color theme" title="Switch color theme">◐</button><a class="repo-link" href="{REPO}">GitHub <span>↗</span></a></div></header>
<div class="design-banner"><span class="status-dot"></span> Local runtime preview <span class="banner-detail">— Approval desk and app registry available. Broader fleet capabilities remain in design.</span></div>'''


def explorer() -> str:
    options = [
        (
            "tables",
            "01",
            "Tables",
            "UMF + Weft",
            "Native models and typed data access.",
        ),
        ("agents", "02", "Agents", "Tether", "Sessions and declared operation tools."),
        (
            "ontology",
            "03",
            "Ontology",
            "Arras",
            "Entities, relationships and native actions.",
        ),
        (
            "ui",
            "04",
            "Interface",
            "ux-builder",
            "Design artifacts and public client bindings.",
        ),
        (
            "sagas",
            "05",
            "Sagas",
            "UMF",
            "Upstream recovery semantics and executor binding.",
        ),
    ]
    choices = "".join(
        f'''<button class="module-choice" data-module="{key}" aria-pressed="{"true" if key in ("tables", "agents", "ui") else "false"}"><span class="module-number">{num}</span><span class="module-label"><strong>{label}</strong><span>{desc}</span></span><span class="module-provider">{provider}</span><span class="module-check" aria-hidden="true"></span></button>'''
        for key, num, label, provider, desc in options
    )
    return f"""<section class="explorer section-wrap" id="explore" aria-labelledby="explorer-title">
<div class="section-heading"><div><p class="eyebrow">COMPOSE / BIND / ASSESS</p><h2 id="explorer-title">Your application.<br>Your platform choices.</h2></div><p>Select capabilities and change the host.<br>The application’s meaning stays with it.</p></div>
<noscript><p class="explorer-note">Enable JavaScript to explore these choices, or read the composition guide below.</p></noscript><div class="explorer-grid"><div class="selection-panel"><div class="panel-top"><h3>Application capabilities</h3><span>Choose what you need</span></div>
<div class="core-choice"><span class="core-symbol">▥</span><span><strong>Batten core</strong><small>Contracts · permissions · lifecycle</small></span><span class="always">Always included</span></div>
<div role="group" aria-label="Optional application capabilities">{choices}</div>
<div class="host-controls"><h3>Hosting environment</h3><div class="host-switch" role="group" aria-label="Hosting environment"><button data-host="local" aria-pressed="true">Local</button><button data-host="standalone" aria-pressed="false">Standalone</button><button data-host="embedded" aria-pressed="false">Embedded</button></div>
<label class="placement-label" for="placement">Execution placement <select id="placement"><option value="in-process">In process</option><option value="child-process" selected>Child process</option><option value="remote-worker">Remote worker</option></select></label></div></div>
<div class="composition-panel"><div class="composition-top"><span class="eyebrow">ILLUSTRATIVE COMPOSITION</span><span class="preview-pill">Design explorer</span></div>
<div class="composition-app"><span class="app-icon">↗</span><div><span>APPLICATION INTENT</span><h3>AI review queue</h3><p>One declaration. Explicit bindings.</p></div></div>
<div class="connecting-line" aria-hidden="true"></div><div class="capability-chips" id="capability-chips"></div>
<div class="connecting-line" aria-hidden="true"></div><div class="host-preview"><span class="host-glyph" aria-hidden="true">▤</span><div><span id="host-label">LOCAL HOST</span><strong id="host-description">Develop with explicit local resources.</strong><p id="ownership-description">Fabricated identity · owned resources</p></div></div>
<div class="composition-summary" role="status" aria-live="polite" aria-atomic="true"><span class="status-dot"></span><p id="composition-summary"></p></div>
<p class="explorer-note" id="explorer-note">An architecture illustration, not a running application or a compatibility check.</p>
<a class="text-link" href="composition.html">Understand composition <span>↗</span></a></div></div></section>"""


def home(body: str, provenance: str) -> str:
    platforms = [
        ("UMF", "Models, actions & saga semantics", "01"),
        ("Weft", "Query compilation", "02"),
        ("Arras", "Ontology capabilities", "03"),
        ("Tether", "Agent execution", "04"),
        ("ux-builder", "UI design & tooling", "05"),
    ]
    strip = "".join(
        f'<a href="integrations.html"><span>{num} /</span><strong>{name}</strong><small>{desc}</small></a>'
        for name, desc, num in platforms
    )
    return f"""<main id="main"><section class="hero section-wrap"><div class="hero-copy"><p class="eyebrow"><span class="tiny-cross">+</span> A NOVIRHYZA APPLICATION SDK</p>
<h1>Declare the app.<br><em>Govern the fleet.</em></h1><p class="hero-description">Compose data, actions, agents and interfaces.<br>Batten’s design packages deep declarative services into a qualified runtime, built for shared operation and governed upgrades.</p>
<div class="hero-actions"><a class="button primary" href="#explore">Explore the architecture <span>↓</span></a><a class="button secondary" href="architecture.html">Read the design <span>↗</span></a></div>
<div class="hero-footnote"><span class="footnote-rule"></span>Declarative by default. Typed code where it counts.</div></div>
<div class="hero-visual" aria-label="Application declarations connect through Batten to a chosen host"><div class="visual-meta"><span>THE APPLICATION, AS INTENT</span><span>01—03</span></div>
<div class="intent-card"><span class="intent-kind">UMF / APPLICATION</span><h2>review_queue</h2><div class="intent-row"><span>models</span><strong>Review</strong></div><div class="intent-row"><span>actions</span><strong>ApproveReview</strong></div><div class="intent-row"><span>agents</span><strong>RecommendReview</strong></div><div class="intent-row"><span>interface</span><strong>Review screen</strong></div></div>
<div class="visual-connector"><span></span><span class="connector-label">explicit capability bindings</span><span></span></div><div class="batten-bar">{MARK}<strong>batten core</strong><span>+ selected modules</span></div><div class="host-branch"><span></span><span></span><span></span></div><div class="host-trio"><span>Local</span><span>Standalone</span><span>Embedded</span></div><p class="visual-caption">Same application intent. Different host bindings.</p></div></section>
<section class="platform-strip" aria-label="Platform responsibilities">{strip}</section>
<section class="section-wrap reading" aria-labelledby="release-title"><p class="eyebrow">AVAILABLE NOW / 0.1.0a1</p><h2 id="release-title">Run the local approval desk.</h2><p>Submit, revise and independently approve requests through native UMF and Weft on PostgreSQL 18. Open the visual app registry and follow decisions through durable receipts and local telemetry.</p><p>Python 3.11 · Local development identities · Fabricated data. This preview qualifies the recorded local cohort; production identity and the complete fleet remain separate work.</p><div class="hero-actions"><a class="button primary" href="{REPO}/releases/tag/runtime-v0.1.0a1">Get the runtime preview ↗</a><a class="button secondary" href="{REPO}/blob/main/examples/approval-desk/README.md">Run instructions ↗</a></div></section>
<section class="section-wrap reading" aria-labelledby="examples-title"><p class="eyebrow">BUSINESS JOURNEYS / EXPLICIT BOUNDARIES</p><h2 id="examples-title">See the platform through its apps.</h2><p>Follow twelve walkthroughs covering approvals, intake, case work, evidence, assisted review, entity graphs, grounded answers, triage, reconciliation, digests, access review and service handoff.</p><p>Start with the runnable approval desk. The remaining specification walkthroughs explain intended behavior and the failure boundaries each app must qualify.</p><a class="button secondary" href="examples.html">Explore the example apps ↗</a></section>
<section class="principles section-wrap"><div><p class="eyebrow">A DELIBERATE FOUNDATION</p><h2>A small core.<br>Room to compose.</h2></div><div class="principle-grid"><article><span class="principle-index">01 / NATIVE MEANING</span><h3>Build on the platform.</h3><p>Use UMF models and actions, Weft queries, Arras ontology and Tether agents through their public boundaries.</p></article><article><span class="principle-index">02 / EXPLICIT CAPABILITIES</span><h3>Bring what the app needs.</h3><p>Select modules independently. Keep optional platform dependencies out of applications that do not use them.</p></article><article><span class="principle-index">03 / GOVERNED FLEETS</span><h3>Operate a shared fleet.</h3><p>Share declarative services with explicit identity, limits and lifecycle. Qualify runtime upgrades against application evidence.</p></article></div></section>
{explorer()}
<section class="ux-section section-wrap"><div class="ux-copy"><p class="eyebrow">GOOD INTERFACES, BY DESIGN</p><h2>Make room<br>for the experience.</h2><p>ux-builder owns the design workflow, blueprint, components and themes. Batten’s proposed binding connects that experience to native models and governed operations.</p><a class="text-link" href="integrations.html">Explore the UI boundary <span>↗</span></a></div><div class="review-illustration" aria-label="Illustrative review screen, not an implemented Batten application"><div class="review-top"><span><i></i> Review workspace</span><span>ILLUSTRATION</span></div><div class="review-body"><div class="review-sidebar"><span class="skeleton wide"></span><span class="review-nav active">Review queue <b>→</b></span><span class="review-nav">Activity</span><span class="review-nav">Settings</span></div><div class="review-content"><span class="review-eyebrow">REVIEW / FABRICATED EXAMPLE</span><h3>A decision, with context.</h3><div class="recommendation"><span>✧ Recommendation</span><p>Review the proposed change before approval.</p></div><div class="review-fields"><span>Declared action</span><strong>ApproveReview</strong><span>Authority</span><strong>Checked by the host</strong></div><div class="illustrative-button">Review and confirm <span>↗</span></div></div></div><div class="review-footer">Native meaning <span>→</span> Typed operation <span>→</span> Host authorization</div></div></section>
<section class="reading section-wrap"><p class="eyebrow">FOLLOW THE THINKING</p><div class="reading-grid"><a href="composition.html"><span>01 / AUTHORING</span><h3>Compose an application <b>↗</b></h3><p>Capabilities, declarations and assessment before effects.</p></a><a href="hosting.html"><span>02 / HOSTING</span><h3>Choose an environment <b>↗</b></h3><p>Separate hosting, provider selection and process placement.</p></a><a href="architecture.html"><span>03 / BOUNDARIES</span><h3>Inspect the architecture <b>↗</b></h3><p>Public interfaces, lifecycle and qualification.</p></a></div></section>
<section class="overview-text section-wrap"><details><summary>Read the product overview</summary><div class="prose">{body}</div></details>{provenance}</section></main>"""


def article(
    slug: str, title: str, body: str, toc: list[tuple[str, str]], provenance: str
) -> str:
    aside = "".join(
        f'<a href="#{anchor}">{html.escape(label)}</a>' for anchor, label in toc
    )
    return f'''<main id="main" class="article-main section-wrap"><div class="article-heading"><a class="back-link" href="index.html">← Batten / Design guide</a><p class="eyebrow">THE APPLICATION SDK, EXPLAINED</p><h1>{html.escape(title)}</h1></div>
<div class="article-grid"><article class="prose">{body}{provenance}<a class="button secondary article-next" href="index.html#explore">Explore the composition <span>↗</span></a></article><aside class="on-this-page"><span>ON THIS PAGE</span>{aside}<a class="aside-record" href="{REPO}/tree/main/docs/helix">Open design records ↗</a></aside></div></main>'''


def build() -> None:
    OUT.mkdir(exist_ok=True)
    shutil.copytree(SITE / "assets", OUT / "assets", dirs_exist_ok=True)
    for slug, _ in PAGES:
        source = (GUIDE / f"{slug}.md").read_text()
        heading = re.search(r"^# (.+)$", source, re.M)
        if heading is None:
            raise ValueError("Missing guide heading")
        title = heading.group(1)
        body, toc = markdown(source)
        content = (
            home(body, sources(source))
            if slug == "index"
            else article(slug, title, body, toc, sources(source))
        )
        full_title = (
            "Batten — Declare the app. Govern the fleet."
            if slug == "index"
            else f"{title} — Batten"
        )
        output = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light dark">{social_metadata(slug, full_title)}<meta name="theme-color" content="#f7f6f0"><title>{html.escape(full_title)}</title><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/site.css"><script src="assets/site.js" defer></script></head><body>{header(slug)}{content}<footer class="site-footer section-wrap"><a class="brand" href="index.html">{MARK}<span>batten.</span></a><p>Part of the Novirhyza family.<br>MIT OR Apache-2.0 · Copyright Synaptiq</p><div><a href="{REPO}">Source ↗</a><a href="{REPO}/tree/main/docs/helix">Design records ↗</a><a href="about.html">How this guide is made ↗</a></div></footer></body></html>'''
        (OUT / f"{slug}.html").write_text(output)
    (OUT / ".nojekyll").touch()
    print(f"Built {len(PAGES)} source-checked pages into {OUT}")


def social_metadata(slug: str, title: str) -> str:
    url = PUBLIC_URL + ("" if slug == "index" else f"{slug}.html")
    image = PUBLIC_URL + "assets/social-preview.png"
    values = {
        "description": DESCRIPTION,
        "og:title": title,
        "og:description": DESCRIPTION,
        "og:type": "website",
        "og:site_name": "Batten",
        "og:url": url,
        "og:image": image,
        "og:image:type": "image/png",
        "og:image:width": "1200",
        "og:image:height": "630",
        "og:image:alt": "Batten — Declare the app. Govern the fleet. Local runtime preview.",
        "twitter:card": "summary_large_image",
        "twitter:title": title,
        "twitter:description": DESCRIPTION,
        "twitter:image": image,
        "twitter:image:alt": "Batten — Declare the app. Govern the fleet. Local runtime preview.",
    }
    tags = [f'<link rel="canonical" href="{url}">']
    tags.extend(
        f'<meta {"property" if key.startswith("og:") else "name"}="{key}" content="{html.escape(value, quote=True)}">'
        for key, value in values.items()
    )
    return "".join(tags)


if __name__ == "__main__":
    build()
