---
name: adr
description: Record an architecture or business decision as a numbered ADR/BDR in docs/technical/adr/ or docs/business/bdr/.
---

<!-- GENERATED FILE - DO NOT EDIT.
     Source: skills/adr/SKILL.md
     Regenerate: python scripts/sync_copilot.py -->

# Write an ADR

Decision to record: **$ARGUMENTS**

## Process

1. **Find the directory and the next number.** The `architecture-decisions` rule sets the
   convention: technical decisions go to `docs/technical/adr/NNNN-slug.md`, business ones to
   `docs/business/bdr/NNNN-slug.md`, numbered independently per directory and never reusing a
   number. If the repo already has an ADR directory with a different layout (e.g. `docs/adr/`),
   follow it. If none exists, ask where decisions should live before creating one.

2. **Check for a superseded decision.** Grep existing ADRs for the same subject. If this
   decision replaces one, the new ADR says "Zastępuje ADR-NNNN" in `## Notatki` and the old
   one gets "Zastąpiony przez ADR-NNNN" in its `## Notatki`. An ADR is never edited to reverse
   its own decision — the record of what was decided and when is the point.

3. **Write it.** The `architecture-decisions` rule loads automatically in these directories and
   governs the format (front-matter, section order). Write `status: Proposed`; only a human
   sets `Accepted`. The bar for each section:

   - **Context** — the forces in play: constraints, deadlines, existing commitments,
     what breaks if nothing changes. A reader in a year must be able to tell whether the
     context still holds.
   - **Decision** — one sentence in active voice, present tense: "We use X for Y."
   - **Alternatives** — what else was on the table and the specific reason each lost.
     An ADR with no rejected alternatives records a preference, not a decision.
   - **Consequences** — what this makes easy, what it makes hard, what it locks in,
     and what would have to change to reverse it.

4. **Do not invent context.** Everything in the ADR comes from this conversation, the code,
   or the user. Where a fact is needed and missing, ask rather than plausibly fill it in.

## When an ADR is not the answer

Decisions that are cheap to reverse, local to one module, or implied by a rule already in the
toolkit belong in a code comment or the module's docs. Reserve ADRs for choices that are
expensive to unwind: frameworks, data models, auth, deployment topology, cross-cutting
conventions.
