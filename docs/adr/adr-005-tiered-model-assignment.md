# ADR-005: Assign agent models by the cost of being wrong

## Status
Accepted

## Date
2026-09-12

## Context

Every agent in the toolkit was set to `model: haiku` — `explorer`, `documentation-writer`, but
also `debugger`, `code-reviewer`, `test-writer` and `esp32-firmware-engineer`. The stated
intent was cost optimization.

The intent is right; the application was not. These agents do different kinds of work:

- `explorer` searches and reports. The output is verifiable on sight: a file path is either
  right or wrong, and the caller notices immediately.
- `code-reviewer` and `debugger` produce judgments that are trusted *because* nobody re-checks
  them. A review that misses a defect does not look like a failure — it looks like a clean
  review. The cost surfaces later, as a bug, a second debugging session, or an incident.

Optimizing the second group for token price moves the cost to where it is least visible and
most expensive, which is the opposite of optimization.

## Decision

Assign the cheapest model that does the job *correctly*, judged by the cost of an undetected
error:

| Model | Agents | Rationale |
|-------|--------|-----------|
| `haiku` | `explorer`, `documentation-writer` | High-volume retrieval and drafting; errors are visible on delivery |
| `sonnet` | `debugger`, `code-reviewer`, `test-writer`, `esp32-firmware-engineer` | Root-cause reasoning, review judgment, test design, hardware risk; errors are silent |
| `opus` | none by default | Reserved for deliberate use on hard architecture work |

Use family aliases (`haiku`, `sonnet`) rather than pinned model ids, so the newest allowed
version is substituted automatically.

Context isolation is the other half of cost control and is orthogonal to model choice:
`/ai-tools:security-scan` runs `context: fork` with `agent: code-reviewer`, so a wide audit
costs the main conversation one summary rather than a full diff read.

## Consequences

### Positive
- Review and diagnosis run on a model able to do them; findings can be trusted.
- Search and documentation stay cheap, which is where the volume is.
- `validate_toolkit.py` warns when an agent has no `model`, so the choice is always explicit.

### Negative
- Higher per-invocation cost for four agents. Accepted: a missed defect costs more than the
  model did.
- The assignment is a judgment, not a measurement. Revisit it if a `sonnet` agent turns out to
  be doing work `haiku` handles reliably, or vice versa.

### Neutral
- Aliases mean the actual model changes as new versions ship. That is intended; a pinned id
  would quietly age.
