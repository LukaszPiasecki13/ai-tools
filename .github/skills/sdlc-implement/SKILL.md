---
name: sdlc-implement
description: "Stage 3 of 3 of the SDLC pipeline (orchestrator: sdlc-run): implements an accepted sdlc-plan plan. Use for \"implement plan {task_dir}/03-plan.md\" or \"sdlc implement\" (a path such as .tmp/tasks/{slug}/{run_id}/03-plan.md). Checks drift deterministically, writes tests first, runs static checks and tests before an evidence-first code review, and never commits or pushes automatically."
---

<!-- GENERATED FILE - DO NOT EDIT.
     Source: skills/sdlc-implement/SKILL.md
     Regenerate: python scripts/sync_copilot.py -->

# SDLC Implement — accepted plan to real code

Stage 3 of the SDLC pipeline run by `sdlc-run` (`sdlc-context` -> `sdlc-plan` -> `sdlc-implement`). The plan is a
decision/contract artifact; it need not contain ready-to-copy function bodies. Artifact names,
manifest fields, status transitions, the drift snapshot, models and the finding scale are defined in
[contract.md](../sdlc-run/contract.md) (sections 3-8); this file defines the procedure.

Only plans produced by `sdlc-context` -> `sdlc-plan` are supported; other layouts are a STOP
(Phase 0, step 1).

Paths used below: `{drift_check}` = `${CLAUDE_SKILL_DIR}/../sdlc-run/scripts/drift_check.py`,
`{plan_lint}` = `${CLAUDE_SKILL_DIR}/../sdlc-plan/scripts/plan_lint.py`.

## Non-negotiable rules

1. **Validate before acting.** Accepted status, complete review evidence and no unresolved
   `BLOCKER` (Phase 0). A `BLOCKER` can never be accepted by the user (contract, section 8).
2. **The plan is a contract, not gospel.** The repo may have drifted. Verify paths, signatures and
   decisions against current files; optional snippets are guidance, never authority over current
   code.
3. **Never invent a design decision silently.** A genuine gap is a STOP: ask through the host's
   question tool (`AskUserQuestion` in Claude Code), then amend the plan through Phase 2a
   (mini-Gate P). Never edit accepted `02-requirements.md`/`03-plan.md` outside Phase 2a.
4. **Context hygiene.** The main thread holds the plan and target files. Reviews, the drift
   follow-up and E2E run in fresh subagents. Pass paths and evidence pointers; never paste plan code,
   diffs or target file contents into subagent prompts.
5. **Reuse the producer's facts.** `01-context.md` already holds the ADR index, conventions and
   `Komendy weryfikacji`. Re-check only cited symbols, target paths and ADRs that changed; do not
   re-explore the repository.
6. **Deterministic checks before LLM review.** Tests, formatter, lint and typecheck are green
   (Phase 3) before any reviewer starts. A reviewer never spends tokens on what a tool can report.
7. **Evidence-first review gate.** Fresh, read-only `code-reviewer` contexts. R1 for every task, a
   focused risk pass alongside R1 when triggered. Fresh full-scope R2 after any `BLOCKER`/`MAJOR`
   fix and always for high-risk work (Phase 4); skip it only for an ordinary R1 with no
   `BLOCKER`/`MAJOR` and no code changes. The implementer fixes only unambiguous `BLOCKER`/`MAJOR`.
   Full-scope reviews are capped at R1 plus one R2 for the whole run, including edits after the
   gate; more needs explicit user approval. Never start R3 silently.
8. **Portable commands only.** Run commands from `Komendy weryfikacji` and the plan's `Bramka`
   column, or from repo instructions, CI and manifests with a recorded source. Never assume a
   language, framework, path layout or test tool.
9. **No automatic git commit/push, no automatic ADO state change.** Leave the working tree and
   tracker state to the user.
10. **Docs are updated only on a real discrepancy** between the implementation and a referenced doc,
    plus the smallest documentation update the plan explicitly lists as required. No changelog
    entries for their own sake.
11. **`Accepted` ADRs bind the implementation.** Code that contradicts one is a rule-3 STOP, not
    something to adapt around silently.
12. **"Good code" checklist** applies only when the repository has no more specific standard: SOLID,
    small single-responsibility functions, DI over hardcoded dependencies, DRY, no dead code/unused
    imports, clear naming. Report violations only when they create concrete maintainability risk.

---

## Host integration

Claude Code is primary: `Glob`/`Read` for discovery, `Edit`/`Write` for files, `Agent` for fresh
subagents with the exact `subagent_type`, `AskUserQuestion` for decisions.

- **Model.** Run the main thread on Sonnet (`/model sonnet`); use Opus only when the user chooses
  it. Record the model actually used in `Implementation metrics`.
- **Integrations.** Use Azure DevOps or memory integrations only when configured; otherwise report
  the limitation and rely on the accepted artifacts.
- **Copilot mirror** (secondary): use `runSubagent` with the exact custom-agent name and the host's
  native file/question tools.
- If a required subagent fails or returns incomplete output, set `implementation_status: blocked`,
  record the reason in the ledger and ask; never fall back to self-review.

---

## Phase 0 — Resolve and validate the plan

1. **Resolve the input.** The input is a direct path to `03-plan.md` whose siblings are
   `_context.md` (with a `tier:` key), `00-problem.md`, `01-context.md`, `02-requirements.md` and
   `04-review-plan.md`; `{task_dir}` is its directory and `{plan_key}` = `{slug}-{run_id}`.
   Any other input (a task ID, a different layout, missing companions): STOP and ask the user for
   `{task_dir}/03-plan.md` of a `sdlc-plan` run, or to re-plan with `sdlc-context` and
   `sdlc-plan`.
2. **Read** `03-plan.md`, `02-requirements.md` and `01-context.md` in full, and from
   `04-review-plan.md` only `Stan aktualny` and `Otwarte punkty` (its `Historia` is not needed).
3. **Validate.** STOP and ask unless all hold:
   - `_context.md`: `context_status: accepted`, `plan_status: accepted`;
   - `04-review-plan.md` records R1, the focused pass when a trigger exists, and R2 after any
     `BLOCKER`/`MAJOR` fix;
   - in `04-review-plan.md` and in the plan's `Otwarte punkty`, every `BLOCKER` is `RESOLVED` and
     every `MAJOR` is `RESOLVED` or `ACCEPTED-BY-USER` with a recorded consequence;
   - the plan has concrete files, `DEC`/`AC`, interfaces, steps with `Bramka`, and tests; code
     blocks are optional;
   - every `DEC`/`AC` the plan references exists in `02-requirements.md`. A missing one means a
     corrupt artifact set: STOP and point to `sdlc-context`/`sdlc-plan` (never fetch it from a
     tracker).
4. **Choose the entry point** from `implementation_status` and the ledger
   (`sdlc-implement-{plan_key}-state.md` in `{task_dir}`):

   | `implementation_status` | Ledger | Action |
   |---|---|---|
   | `not-started` | any | STOP: the plan was never accepted through Gate P |
   | `deferred` | none | new run: continue with step 5 |
   | `deferred` or `in-progress` | exists | ask whether to resume; on approval keep its baseline and report, continue from the phase recorded in it |
   | `blocked` | exists | show the recorded reason; if it was a high-risk amendment, require `plan_status: accepted` again (Gate P done, which counts as the user's confirmation); otherwise ask for the decision; then set `in-progress` and continue from the phase recorded in the ledger |
   | `in-progress` or `blocked` | none | STOP: state without evidence |
   | `completed` | any | STOP: ask before any duplicate implementation |

5. Load verified project/session memory through configured integrations if available; otherwise
   record the limitation. Do not invent facts.
6. **ADRs.** Take the ADR index from `01-context.md`. List the ADR directories (`docs/adr/`,
   `docs/*/adr/`, `docs/*/bdr/`, `docs/decisions/`) once and compare with the index. Read in full
   only `Accepted` ADRs that the index marks as relevant and any ADR that is not in the index (added
   since discovery) and touches the plan's scope. Record number, status and a one-line summary in
   the ledger section `ADRs`.
7. **Commands.** Copy `Komendy weryfikacji` from `01-context.md` into the ledger section `Commands`,
   narrowed per step with the plan's `Bramka`. For a `brak` row: derive the command from repo
   instructions, CI or manifests and record its source; for tests, map changed files to tests by
   convention (`test_<module>.py`, `<name>.spec.ts`) and by imports of the changed module. If no
   test command can be established, ask the user.
8. **Ledger.** Create `sdlc-implement-{plan_key}-state.md` and set `{review_report}` =
   `sdlc-implement-{plan_key}-review.md`, both in `{task_dir}` (or in configured session memory).
   Never overwrite phase reports.

```markdown
# sdlc-implement {plan_key} — state
Plan file: ...
Repo(s): ...
Phase: 0
Blocked reason: none
## Baseline
## ADRs
## Commands
## Pre-flight drift found
## Tests-first
## Files written
## Amendments
## Deterministic checks
## Review rounds
## Review report
## Findings outcomes
## Docs changes
```

9. **Repos.** Determine repo(s) from `_context.md`; with several, run Phases 1-6 per repo
   sequentially, not interleaved.
10. **Baseline.** For each target repo, before its first edit, record `git status --porcelain`,
    pre-existing changed paths and hashes of existing untracked files. If Git/baseline capture
    fails, STOP. If a planned target path is already modified or untracked at baseline, STOP and ask
    rather than mixing changes. Leave unrelated baseline changes untouched and exclude them from
    review.

---

## Phase 1 — Pre-flight drift check (deterministic)

Skip this phase when resuming a run that already wrote files, or whose ledger already has a filled
`Pre-flight drift found` section or an entry in `Amendments`: that drift was decided, and the snapshot
is not updated after Phase 1, so a re-check would report it again. From then on the ledger baseline
governs.

Run `python "{drift_check}" "{task_dir}" check --format json` (0 LLM tokens).

| Exit | Meaning | Action |
|---|---|---|
| `0` | no drift (a `head` change alone is informational) | record "none" in the ledger and continue |
| `1` | drift in listed files | one fresh `explorer` (contract, section 6, `I-1`), only for the drifted paths: "Repo `{repo}`. Plan `{plan_path}`. For each path in {list}, compare the plan's anchors and interfaces with the current file. Return ONLY a table `plan item \| expects \| actual (file:line) \| drift: none/signature/moved/removed`." |
| `2` | no snapshot or unreadable input | STOP and show the message |

For `signature`/`moved`/`removed`, adapt only mechanical changes. Drift that changes behavior or
conflicts with an accepted `DEC`/`AC` is a rule-3 STOP (Phase 2a). Record findings in the ledger
section `Pre-flight drift found`.

---

## Phase 2 — Tests first, then code

Before the first write, set `implementation_status: in-progress` in `_context.md`. Re-check the
baseline before each write; never overwrite a path that was already changed at baseline.

1. **Tests first (default).** For every `AC` whose plan `Testy` row is a unit or integration test,
   write the test, run it with its ledger command and confirm it fails for the expected reason
   (assertion or missing behavior, not a broken test). Record command and red result in the ledger
   section `Tests-first`.
   - Exceptions, each with a recorded reason: UI/E2E-only `AC`, migrations/schema whose test needs
     the migrated database, a repository without a test framework, config/docs-only changes.
   - After the red run, change a test only when the test itself is wrong, and record why; R1 checks
     these records.
2. **Code, step by step.** Implement the plan's `Kroki` in order. After each step run its `Bramka`
   and keep it green before the next step. Trace each change to its `DEC`/`AC`; do not add comments
   that merely repeat the plan.
3. **Formatter/lint per step** with the ledger commands, scoped to changed files where the tool
   allows; fix mechanical findings immediately (tooling, not a review round).

Update the ledger sections `Files written` and `Tests-first` as you go.

## Phase 2a — Amendment (mini-Gate P)

Use when rule 3 or Phase 1 surfaces a genuine new decision.

1. STOP. Set `implementation_status: blocked`, write `Blocked reason` in the ledger, and ask the user
   with the repo fact, your recommendation and the consequence of the alternative.
2. After the decision, write it down: append the next free `DEC-NN` (and `AC-NN` if needed) to
   `02-requirements.md` and update the affected rows of `03-plan.md` (file map, steps, matrices,
   tests).
3. Run `python "{plan_lint}" "{task_dir}" --in-progress --format json`; fix until exit `0`.
4. Apply the Phase 0 baseline rule to every path the amendment added: a path already modified or
   untracked at baseline is a STOP. The drift snapshot is not updated (it describes the repo before
   implementation).
5. Append `Poprawka N - {date}` to `Historia` in `04-review-plan.md` (decision, changed rows, lint
   result) and record it in the ledger section `Amendments`, with the phase to resume from.
6. Close the amendment by risk (high-risk triggers: contract, section 5):
   - **Not high-risk (mini-Gate P):** show the user the changed `DEC`/`AC`/steps and ask for
     confirmation. After it, set `implementation_status: in-progress` and continue from the recorded
     phase. `plan_status` stays `accepted`.
   - **High-risk:** set `plan_status: draft`, keep `implementation_status: blocked`, and hand over to
     `sdlc-plan {task_dir}`, which reviews the amended plan and repeats Gate P. Stop here. On
     resume (Phase 0 step 4, `blocked` row) Gate P counts as the confirmation: set `in-progress` and
     continue from the recorded phase.

---

## Phase 3 — Deterministic gate before review

Run on the full task delta, with the ledger commands, before any reviewer starts:

1. Formatter check, lint and typecheck on changed paths. When a scoped run is unreliable (a changed
   shared type, base class or config), run the repository's full command.
2. Tests: every test named in the plan, then the unit and integration suites of every touched
   module/package (map changed files to tests by convention and imports), then one wider run of the
   touched packages.
3. Fix failures directly and re-run until green. Never claim green from a partial run; never defer
   a tool failure to a review round.

Record exact commands and results (pass/fail counts) in the ledger section `Deterministic checks`;
R1 receives this summary.

---

## Phase 4 — Review R1 (+ focused risk pass)

Build the task delta from the Phase 0 baseline. Give the reviewer paths, never pasted content: the
plan, `02-requirements.md`, `01-context.md`, `04-review-plan.md` (`Stan aktualny`), the ledger
sections `Tests-first` and `Deterministic checks`, relevant ADRs, changed files, and their direct
dependencies/callers/tests. The reviewer reads new task files in full; exclude baseline paths.
`DEC`/`AC` completeness was settled in Phase 0; a reviewer that finds a missing one reports it as a
finding, the orchestrator does not look it up elsewhere.

Run a fresh, read-only `code-reviewer` subagent (contract, section 6, `I-2`). R1 reviews the full
task delta against the accepted plan, every `AC`/`DEC`, test adequacy, relevant contracts and ADRs,
and checks that every test changed after its red run has a recorded reason. Return an `AC`/`DEC`
coverage matrix (`satisfied` / `gap` / `unclear` / `N/A` with evidence or reason); every `gap` is a
finding. Findings use the scale in contract, section 8. Do not edit files.

**Risk triggers (single source; the trigger table in [contract.md](../sdlc-run/contract.md) mirrors this list, so update both).** Before R1, trigger a focused pass when the delta touches security boundaries (auth, tenant/sensitive-data isolation, untrusted input/injection, secrets/tokens/crypto, dependencies with known vulnerability or supply-chain risk) or architecture boundaries (public contracts, migrations/schema, new modules/layers, cross-repo integration, Accepted ADRs). Run one fresh `code-reviewer` subagent (`I-3`) with only the triggered focus, in parallel with R1; for security triggers, instruct it to apply `security-checklist` and the `security-scan` finding format. Deduplicate findings by root cause; retain the highest severity.

**High-risk work** (mandatory R2) is the narrower subset: security boundaries, auth, migrations/schema, or public-contract changes. Other triggers alone (new module/layer, cross-repo integration, Accepted ADR) require the focused pass but not R2 unless a BLOCKER/MAJOR was fixed.

Reviewers must not write anywhere in the working tree, including project-memory files; instruct them to return durable conventions in the report and let the orchestrator decide whether to record them.

If R1 or a triggered focused pass fails or cannot cover its required scope, set
`implementation_status: blocked` with the reason and ask; do not proceed on a partial review.

### Resolve R1 findings before R2

The implementer fixes only unambiguous `BLOCKER`/`MAJOR` findings. Log `MINOR`/`INFO` (at most five
grouped); do not change code for them. If a fix needs a new design decision, conflicts with the
accepted plan/ADR, or leaves a required `AC`/`DEC` `unclear`, use Phase 2a. After code fixes, re-run
the Phase 3 checks for the affected scope and record commands/results. Do not start R2 with
known-red checks.

---

## Phase 5 — Fresh full-scope R2

Run a new, read-only `code-reviewer` subagent (`I-4`) after any `BLOCKER`/`MAJOR` fixes and always
for high-risk work (see Phase 4). Skip R2 only for an ordinary task where R1 found no
`BLOCKER`/`MAJOR` and no code changed; record that reason.

R2 receives the complete task delta after fixes, the same companion paths as R1, the Phase 3
re-run results, R1 findings and the previous coverage matrix. It independently re-reads the full
scope, verifies each `AC`/`DEC` and prior finding, and looks for regressions introduced by fixes. It
does not edit files. Update the report and ledger with its matrix and findings.

R2 also checks relevant architecture docs and ADRs for genuine discrepancies, returning `DOC UPDATE CANDIDATES` or `none`; it must not edit docs.

If R2 finds a `BLOCKER`/`MAJOR`, a required `AC`/`DEC` remains `unclear`, or R2 is
`LIMITED`/incomplete: set `implementation_status: blocked` with the reason, stop before Phase 6 and
ask via `AskUserQuestion`. Do not self-review as fallback or open R3 without explicit user approval.
Options: fix manually, authorize one additional bounded cycle, or accept a `MAJOR` as documented
risk (a `BLOCKER` can never be accepted; contract, section 8). Proceed only when the gate is clear.

---

## Phase 6 — Final confirmation and E2E

1. **Final deterministic run.** If any code or test changed after the last full Phase 3 run, re-run
   Phase 3 once over the whole delta; otherwise the last Phase 3 results are final (say so in the
   ledger).
2. **Edits after R2.** If a failure here requires a code or test edit after R2 already ran, run one
   bounded fresh review (`I-4`) limited to files changed since R2, same schema. This does not open
   R3; a `BLOCKER`/`MAJOR` there is a Phase 5 STOP. If R2 was skipped, the edit triggers the R2
   required by Phase 5. Never treat a review of an earlier candidate as validation of later edits.
3. **E2E** only when `ui: true` in `_context.md`:
   - If the `e2e` row of `Komendy weryfikacji` names a test command, run only the specs that cover
     the plan's E2E checklist.
   - Run the plan's `### E2E` checklist through one fresh `general-purpose` subagent (`I-5`) with
     this prompt: "Invoke the skill `ui-verify`. Checklist: `{task_dir}/03-plan.md`, section E2E.
     App: URL, start command and login from the `app` row of `{task_dir}/01-context.md`. Write the
     punch list to `{task_dir}/sdlc-implement-{plan_key}-e2e.md`. Return at most 150 words: verdict
     per checklist item and console errors."
   - If the subagent, the skill or browser tooling is unavailable, set `implementation_status:
     blocked`, report that E2E could not be executed and do not mark any dependent `AC` as
     `satisfied`. Link the punch list in `{review_report}`.

Record pass/fail counts in the ledger.

---

## Phase 7 — Documentation update (conditional)

Apply any documentation update the plan explicitly lists as required. Beyond that, only edit docs if Phase 5's `DOC UPDATE CANDIDATES` (or your own observation) shows the implementation genuinely diverges from or extends what a referenced doc states — e.g. a new module not in the dependency diagram, a new table not in the module definitions, a rule that's now stricter/looser than documented.

If found: edit only the specific section, cite the plan (`{plan_path}`) as the source, keep the edit scoped (~200 words), and do not touch unrelated sections. If nothing diverges, state explicitly *"Docs zgodne z implementacją, brak zmian"* and move on — do not add a changelog entry for its own sake.

---

## Phase 8 — Persist and report

1. Treat `{review_report}` as the canonical review record. Include the baseline, R1/R2 `AC`/`DEC`
   matrices, risk-pass trigger or skip reason, findings and their confirmed/rejected/duplicate/fixed
   status, tests-first records, deterministic check commands/results, amendments, verdict and
   limitations. Append actual calls/models, touchpoints, duration, review/rework counts and
   `tokens_usd` to a separate `Implementation metrics` section in `_context.md`; do not modify
   `Plan metrics`. For `tokens_usd`, ask once, optionally, for the cost from `/usage`; no answer =
   `unknown` (contract, section 4).
2. On successful completion, set `implementation_status: completed`. Keep the state ledger short and
   link to the review report.
3. If a memory integration is configured, append verified reusable conventions/test commands only. Otherwise record that memory was unavailable; do not claim a memory update.
4. Final message to the user, in Polish, no filler:
   - table `runda | reviewer | BLOCKER/MAJOR | rozwiązanie`
   - `AC`/`DEC` coverage and R2 status, including skip reason when applicable
   - tests-first exceptions, static checks and test results (commands and pass counts)
   - docs changed or "brak zmian"; report path and changed files
   - explicit: working tree not committed, remaining `MINOR`/`INFO`, risks, or blocked reason
   - direct question: `git diff` review now, or commit it yourself?

---

## Token discipline

- Drift is a script, not a subagent; an `explorer` runs only for files the script reports.
- The main thread holds plan and target files; R1, the focused pass, R2 and E2E run in fresh
  subagent contexts that receive paths, not content. Keep only findings, matrices and concise
  evidence in the report.
- Reuse `01-context.md` (ADR index, conventions, commands); read only `Stan aktualny` and
  `Otwarte punkty` of `04-review-plan.md`.
- Deterministic checks run before reviews, so no review round is spent on tool-detectable errors.
- No progress narration between phases; act, then report the delta.
- Do not paste full file diffs into the chat response — the ledger and the final Phase 8 table are the record; the response summarizes, it doesn't repeat file contents.
