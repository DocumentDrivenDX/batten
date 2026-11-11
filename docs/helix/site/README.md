# Batten microsite

The microsite turns the design guide pages in `docs/helix/guide/developer/` into a
static site. The home page is stamped with the package version from
`packages/batten/pyproject.toml`.

From the repository root, with Python 3.11 or later and its standard library:

```sh
python3 docs/helix/site/build.py
python3 docs/helix/site/verify.py
python3 -m http.server 8814 --bind 127.0.0.1 --directory docs/helix/site/dist
```

Open `http://127.0.0.1:8814/`. Generated output lives in `dist/`, which Git ignores.
All links and assets are relative so the output can be served beneath a project
prefix. No runtime CDN, backend, analytics or external font is required.
`verify.py` checks generated routes, local assets, fragments, social metadata and
the version stamp. Do not hand-edit generated HTML.

Each guide page lists the design documents it draws on in `helix:source` comments;
the build fails if a cited file is missing. The module/host controls on the home
page illustrate the design and make no service calls.

## GitHub Pages

The public site is https://documentdrivendx.github.io/batten/. The Pages workflow
builds and verifies the site on pull requests and publishes it on pushes to `main`.
