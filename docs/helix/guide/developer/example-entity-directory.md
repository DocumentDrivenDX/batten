<!-- helix:publish audience=developer page=example-entity-directory kind=how-to voice=onboarding budget=650 reviewed=2026-11-02/microsite_release_reader/337ab39f77ca3f4b -->
<!-- helix:source docs/helix/reference-apps/entity-directory/specs/01-frame/prd.md sha256:7e1797cd1aaff51b -->
<!-- helix:source docs/helix/reference-apps/entity-directory/specs/01-frame/user-stories/US-106-journey.md sha256:e6150764eea46ad8 -->
<!-- helix:source docs/helix/reference-apps/catalog.json sha256:3de4ef2805d0566d -->

# Entity and relationship directory walkthrough

Specification walkthrough. Follow this journey as a directory steward and scoped analyst. Use fabricated data throughout.

These steps describe the app’s required behavior. This release supplies no runnable implementation or qualified native cohort for this app. Use the linked story as the acceptance target; do not infer runtime support from its integration tags.

## Capabilities in this journey

graphs, actions. These tags describe requested integration boundaries.

## 1. Register an entity

An authorized maintainer registers a fabricated entity with its original model identity.

## 2. Create a relationship

Link a related entity through an approved action.

## 3. Traverse the permitted graph

Inspect authorized attributes and relationships as a reader with a narrower view.

## 4. Update permitted attributes

As an authorized maintainer, update approved attributes through a declared action. Inspect the current result and its original model identity.

## 5. Check a hidden path

Include a path through a separate hidden entity. Traversal must disclose no hidden endpoint, property or count.

## Check authority and recovery

Repeat inspection as an anonymous, foreign or revoked actor. No private result or unauthorized mutation should appear. If an operation may have taken effect, inspect its original identity and retain uncertainty until the result is known.

## Continue exploring

[Read the acceptance story](https://github.com/DocumentDrivenDX/batten/blob/main/docs/helix/reference-apps/entity-directory/specs/01-frame/user-stories/US-106-journey.md) or [choose another example](examples.md).
