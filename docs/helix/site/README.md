# Batten microsite

The microsite projects the vision, requirements and design into source-stamped
reader explanations. It is separate from Batten's unimplemented SDK runtime.

Build from the repository root with Python's standard library:

```sh
python3 docs/helix/site/build.py
python3 -m http.server 8814 --bind 127.0.0.1 --directory docs/helix/site/dist
```

Open `http://127.0.0.1:8814/`. Generated output lives in `dist/`, which Git ignores.
All links and assets are relative so the output can be served beneath a project
prefix. No runtime CDN, backend, analytics or external font is required.

Written source pages live in `docs/helix/guide/developer/`. Their HELIX provenance
headers bind them to source content digests. The builder rejects stale sources.
An independent reader evaluates explanations before documentor records a review.

With HELIX's documentor available, run:

```sh
documentor check-pages docs/helix/guide --root . --strict-prose
documentor check --root .
```

The installed HELIX plugin owns the publishing catalog. No catalog is vendored.
The custom static assembly uses `build.py`; do not hand-edit generated HTML.
The site's module/host controls illustrate the design and make no service calls.

## GitHub Pages

The public site is https://documentdrivendx.github.io/batten/. The repository
uses GitHub Actions as its Pages publishing source.

The Pages workflow builds with Python 3.12 and verifies generated routes, local
assets, fragments and project-prefix-safe links. Official actions are pinned by
commit SHA. Pull requests build without deploying; successful pushes to `main`
publish through the `github-pages` environment using the job-scoped Pages/OIDC
permissions. No deployment credential is stored in the repository.

Run the publication check locally after building:

```sh
python3 docs/helix/site/verify.py
```

To retry publication, rerun the Pages workflow for the reviewed `main` revision.
To restore an earlier site, revert the reviewed source change and let the same
workflow rebuild it. A release archive also preserves its exact static output.
The standalone build command itself does not modify hosting configuration.
