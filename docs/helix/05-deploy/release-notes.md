---
ddx:
  id: batten.release.0.1.0-alpha.1
  type: release-notes
  activity: deploy
  authoring:
    home: repo
  links:
    - id: batten.product-vision
      kind: informed_by
    - id: batten.feature-registry
      kind: informed_by
---

# Batten 0.1.0-alpha.1

## Release Scope

Batten's first design-preview release includes the public requirements, proposed
contracts and documentation microsite. The SDK runtime and installable packages
are not implemented.

- Version: `v0.1.0-alpha.1`, a prerelease.
- Release date: 2026-10-29.
- Publication: GitHub Releases and the repository's GitHub Pages site.
- Release owner: Batten maintainers.

## Audience and Channels

| Audience | What is available | Channel |
| --- | --- | --- |
| Application authors | Vision, composition examples and platform boundaries | Microsite and design records |
| Host integrators | Proposed module, hosting and lifecycle contracts | Repository and release |
| Contributors | Source-stamped guide and reproducible static build | Repository and site archive |

## Highlights

- Explore selectable capabilities, hosting environments and execution placement.
- Read the UMF, Weft, Arras, Tether and ux-builder ownership boundaries.
- Browse the design guide on desktop or phone, in light or dark mode.

## Required Actions Summary

Readers need no installation or account to browse the site. This release
requires no application migration or database changes.

## Changes and Fixes

### New or Improved

The microsite has six source-backed explanations, an interactive architecture
explorer, design-source links and a guide-provenance page. The explorer changes
an illustration; it does not execute or assess an application.

The repository includes requirements, acceptance stories, proposed contracts,
module boundaries and work items. The release archive contains the built static
site with local assets and a checksum file.

The Pages workflow builds and checks the site before deployment. Pull requests
build without publishing; successful pushes to `main` publish the site.

## Breaking Changes and Required Actions

This is the first release. There is no prior public runtime to migrate and no
breaking runtime change. No user action is required.

## Migration or Rollback Guidance

### Upgrade or Migration

Browse the site or download the static site archive. No SDK installation is
provided by this release.

### Rollback or Hold Guidance

Maintainers can redeploy a previously reviewed site revision through the Pages
workflow. Pause publication if the build or link checks fail. Release archives
retain the versioned site independently of later changes on `main`.

## Known Issues and Support

The site describes proposed SDK behavior. Native platform support, live hosting,
UMF saga executors and ux-builder runtime integration require separate qualification.
Remote-worker selection illustrates a design option and grants no execution support.

Use the repository's contribution workflow for feedback. Implementation work
remains governed by project-scoped ddx items.

## References

- [Microsite](https://documentdrivendx.github.io/batten/).
- [Design guide](../guide/developer/index.md).
- [Site build and publishing](../site/README.md).
- [Release](https://github.com/DocumentDrivenDX/batten/releases/tag/v0.1.0-alpha.1).
