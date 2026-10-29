# Batten intent and requirements intake

## Accepted direction

Source: project owner's conversation on 2026-10-29.

- Name: **Batten**, accepted after the naming discussion.
- Family: **Novirhyza**, using the owner's spelling.
- Category: an application software development kit (SDK).
- Foundation: a cleanroom effort based on **UMF, Tether, Weft, and Arras**.
- Purpose: constrain the technology design space and provide good tools to design
  data structures, act on them, and deploy a user interface without app authors
  taking on deployment and integration concerns.
- Current authorization: bootstrap a HELIX repository and prepare to receive
  further requirements.

The proposed tagline, “Define your data. Declare your actions. Ship your app,”
is naming context; it does not establish particular APIs or deployment behavior.

## Scope boundary

This bootstrap captures intent and research and prepares the HELIX activity tree.
Requirements, architecture, implementation, dependency selection, hosting,
publication, and compatibility commitments await additional direction.

Reducing the app author's deployment and integration burden is a product goal.
It leaves open who operates the host, what Batten supplies, and which configuration
or responsibilities remain with the application owner. It does not remove those
concerns from the system design.

## Open questions for requirements

These questions are an intake aid, not a mandatory interview sequence.

| Question | Decision it affects |
|----------|---------------------|
| Who authors and operates apps, and what is the first real workflow? | Audience and initial scope |
| What does “cleanroom” mean here: fresh API design, independent implementation, or another boundary? | Permitted reuse and source provenance |
| What compatibility with the four foundations is required? | Model, query, action, session, and migration contracts |
| Which technology choices should be fixed, and which should app authors control? | Stack and extension boundaries |
| What runs in the browser, server, worker, and host? | Runtime ownership and packaging |
| What does “deploy a UI” mean for the first supported host? | Delivery surface and operating responsibilities |
| How are identity, authorization, secrets, tenancy, and external systems supplied? | Host/application integration boundary |
| What role do agents and durable sessions play? | Tether scope |
| Which data shapes, queries, actions, and storage backends are first? | UMF, Weft, and Arras subsets |
| Is UI generated, authored, or composed from both? | Developer experience and component ownership |
| Which failure, recovery, and observability behaviors matter first? | Operational and verification scope |
| What distribution, license, package naming, and public/private posture are intended? | Repository and release setup |

## Frame handoff

Receive the next requirements in conversation or a supplied source. Preserve their
provenance and resolve conflicts with the owner. Then create the PRD and separate
functional and cross-cutting requirements at the scope the evidence supports.
Add features, stories, and designs only as the scope becomes concrete.

Handwritten SDK and UI source is expected, so the modularity-and-encapsulation
baseline applies. Detailed module ownership, dependency rules, and checkers belong
in Design. No runtime, UI framework, database, or deployment target is selected.
