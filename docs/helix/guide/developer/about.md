<!-- helix:publish audience=developer page=about kind=explanation voice=onboarding budget=600 reviewed=2026-10-29/microsite_reader_review/9ee51d5ee1a68955 -->
<!-- helix:source .helix.yml sha256:6747bb82a643f84b -->
<!-- helix:source docs/helix/site/build.py sha256:3bffea6ce4b44579 -->

# How this guide is made

The microsite explains Batten’s intended application model and architecture. Its sources are the repository’s vision, requirements, contracts and design decisions.

## Source-backed explanations

Written guide pages translate the design into explanations for application authors and host integrators. Their source headers retain content digests for the artifacts they use.

The builder checks those digests before generating HTML. A changed source requires the affected explanation to be reconciled and stamped again.

## A standalone site

A Python standard-library builder renders the guide and copies local CSS, JavaScript and artwork. The site needs no application backend or external assets.

The architecture explorer changes an illustration of selected capabilities, hosting and execution placement. It does not assess compatibility, execute operations or deploy resources.

## Reader and browser checks

An independent reader evaluates written pages against their tasks and cited sources. HELIX’s documentor checks source freshness, links and prose; the review stamp records the evaluated body.

Browser verification separately checks rendered navigation, interactions and responsive layout. These checks concern the microsite and establish no SDK runtime or platform qualification.

## Read the authoritative design

Source links accompany each explanation. The design records retain exact interface proposals, requirements and unresolved integration dependencies.

[Browse the design records](https://github.com/DocumentDrivenDX/batten/tree/main/docs/helix) or return to the [product overview](index.md).
