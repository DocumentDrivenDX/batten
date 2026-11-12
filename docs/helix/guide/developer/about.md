<!-- helix:publish audience=developer page=about kind=explanation voice=onboarding budget=600 reviewed=2026-11-03/microsite_dependency_reader/9ee51d5ee1a68955 -->
<!-- helix:source .helix.yml sha256:6747bb82a643f84b -->
<!-- helix:source docs/helix/site/build.py sha256:933642f6e4408d89 -->

# How this guide is made

The microsite explains Batten’s intended application model and architecture. Its sources are the repository’s vision, requirements, contracts and design decisions.

## Source-backed explanations

Written guide pages translate the design into explanations for application authors and host integrators. Each page lists the design sources it draws on, and the build fails if a cited source no longer exists.

## A standalone site

A Python standard-library builder renders the guide and copies local CSS, JavaScript and artwork. The site needs no application backend or external assets.

The architecture explorer changes an illustration of selected capabilities, hosting and execution placement. It does not assess compatibility, execute operations or deploy resources.

## Read the authoritative design

Source links accompany each explanation. The design records retain exact interface proposals, requirements and unresolved integration dependencies.

[Browse the design records](https://github.com/DocumentDrivenDX/batten/tree/main/docs/helix) or return to the [product overview](index.md).
