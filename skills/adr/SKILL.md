---
name: adr
description: Record an architecture decision as a numbered ADR in docs/adr/.
disable-model-invocation: true
user-invocable: true
argument-hint: "[decision title]"
---

# Write an ADR

Decision to record: **$ARGUMENTS**

## Process

1. **Find the ADR directory and the next number.** Look for `docs/adr/`, `docs/decisions/`,
   or `doc/adr/`. Follow whatever naming the existing files use; where there are none, the
   `architecture-decisions` rule sets the convention: `adr-NNN-short-title.md`, numbered
   sequentially, never reusing a number. If no directory exists, ask where ADRs should live
   before creating one.

2. **Check for a superseded decision.** Grep existing ADRs for the same subject. If this
   decision replaces one, the new ADR links back to it and the old one's status becomes
   `Superseded by ADR-XXXX`. An ADR is never edited to reverse its own decision —
   the record of what was decided and when is the point.

3. **Write it.** The `architecture-decisions` rule loads automatically in `docs/adr/` and
   governs the format. The bar for each section:

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
