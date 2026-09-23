---
name: implement-plan
description: 'Implements an already-accepted plan from prepare-to-work into the real repository. Use when the user says "implement plan {task_id}", "zaimplementuj plan {task_id}", or points at a finished plan in .agents_dev_plans/. Requires the plan to already have completed prepare-to-work Phase 7 (full ready-to-copy code). Writes real files, runs two independent review rounds (CodeReviewer then Architect) with fixes applied between rounds, runs unit + integration tests (and UI e2e only if the plan explicitly scopes a UI flow), updates docs only on a genuine discrepancy, and never commits or pushes automatically.'
argument-hint: 'Which plan? e.g. "implement plan 242010" or a path under .agents_dev_plans/'
---

# Implement Plan — accepted plan to real code

Counterpart to `prepare-to-work`: that skill never touches the repository, this skill does nothing else.
Input is a plan file that already went through `prepare-to-work` Phase 6b acceptance and Phase 7 code drafting.

## Non-negotiable rules

1. **Phase 7 is a hard precondition.** If the plan has no full, ready-to-copy code in section 3/4 (only prose/pseudocode), STOP and tell the user to finish `prepare-to-work` first. Do not invent code to fill the gap.
2. **Plan code is a verified starting point, not gospel.** The repo may have drifted since the plan was written. Before writing each layer, verify cited imports/base classes/signatures against the current files; adapt silently for drift, but never adapt away a decision from the plan's section 0 without asking.
3. **Never invent a new design decision silently.** If implementation surfaces a genuine gap the plan didn't cover, STOP, grill the user with one `vscode_askQuestions` call, then apply the fix in the code **and** append it to the plan's decision table (section 0) in the same edit — plan and code must stay in sync.
4. **Context hygiene, adapted.** Unlike `prepare-to-work`, this skill's main thread necessarily holds the plan's file contents and target file contents — it is the one doing the writing. What still goes to subagents: pre-flight drift verification, and both review rounds. Never paste plan code or target file contents into a subagent prompt — pass paths only, the subagent reads them itself.
5. **Convention fidelity by majority, re-verified.** Phase 2B/7 of `prepare-to-work` checked conventions once; the pre-flight step here re-checks only the files the plan actually cites, not the whole directory again.
6. **Exactly two review rounds**, fixed identity: Round 1 = `CodeReviewer`, Round 2 = `Architect`. Apply all fixes from a round in one `multi_replace_string_in_file` call. If BLOCKERs remain after round 2's fixes, STOP and grill — do not silently open a round 3.
7. **No automatic git commit/push.** Leave the working tree for the user to review and commit.
8. **No automatic ADO state change.** Report readiness; state transitions in ADO are a manual Dev decision.
9. **Docs are updated only on a real discrepancy** between what got implemented and what a referenced doc says (module boundary, dependency rule, table/diagram) — never as an unconditional changelog entry.
10. **Target repo's ADRs are read in full before Phase 2 (writing code), not after the fact.** Search `docs/adr/`, `docs/*/adr/` (e.g. `docs/business/adr/`, `docs/technical/adr/`) or `docs/decisions/`. Code that contradicts an `Accepted` ADR is a discrepancy under rule 3 (STOP and grill), not something to silently adapt around.
11. **"Good code" checklist** (no dedicated house style doc exists — inferred from `/memories/repo/refactoring-notes.md` and `CodeReviewer.agent.md`): SOLID, single-responsibility small functions/methods, DI over hardcoded dependencies, DRY, no dead code/unused imports, clear naming. Repo convention (majority, per rule 5) wins over this generic checklist whenever they conflict.

---

## Phase 0 — Resolve and validate the plan

1. Resolve the plan file: if given a path, use it; if given a `task_id`, `file_search .agents_dev_plans/{task_id}-*-implementation-plan.md`. Exactly one match expected — if none or multiple, ask.
2. Read the plan file fully (main thread — this is the one phase where full file content in main context is unavoidable and correct, see rule 4).
3. Validate Phase 7 completion: section 3 must list concrete file paths, and section 4 must contain fenced code blocks with real imports/signatures per layer, not placeholders like `[Action]`. If not satisfied → STOP: *"Plan {task_id} nie ma jeszcze Phase 7 (gotowego kodu) z prepare-to-work. Doko\u0144cz najpierw t\u0119 rund\u0119, zanim zaczniesz implementacj\u0119."*
4. `memory view /memories/repo/` and `/memories/session/prepare-to-work-{task_id}.md` (if it exists) — load decisions and verified facts, don't re-derive them.
5. **Read the target repo's ADRs in full**, before touching any code: `docs/adr/`, `docs/*/adr/` (e.g. `docs/business/adr/`, `docs/technical/adr/`) or `docs/decisions/`. List each ADR's number/path, status (`Proposed`/`Accepted`/`Deprecated`/`Superseded`), and a one-line summary in the ledger under a new "ADRs" section. `Accepted` ADRs relevant to the plan's scope are binding constraints on the implementation (rule 10) — read those in full, not just the title.
6. Create the ledger `/memories/session/implement-plan-{task_id}.md`:

```markdown
# implement-plan {task_id} — state
Plan file: ...
Repo(s): ...
Phase: 0
## ADRs
## Files written
## Pre-flight drift found
## Review rounds
## Static checks
## Test results
## Docs changes
```

7. Determine repo(s) from the plan's header (`backend` / `frontend` / both). If both, run Phases 1-6 sequentially per repo, not interleaved.

---

## Phase 1 — Pre-flight drift check (subagent, per repo)

One `Explore` (medium) subagent per repo, not per file:

> Repo: `{repo_path}`. I'm about to apply code from an accepted plan (`{plan_path}`, do not read its narrative — I'll tell you exactly what to check). For each of these symbols/files the plan's code cites as a base/import: {list extracted from the plan's code blocks — base classes, imported repository/service/schema symbols, migration `down_revision` HEAD}. Check each still exists with the same signature/location. Return ONLY a table `cited symbol | plan expects | actual (file:line) | drift: none/signature/moved/removed`. No commentary.

Resolve `drift: none` silently. For `signature`/`moved`/`removed`, adapt the plan's code to match current reality when it's a mechanical fix (import path, renamed parameter). If the drift changes behavior or a decision from section 0 no longer holds, treat it as rule 3 (STOP and grill, then sync the plan).

Log findings in the ledger under "Pre-flight drift found".

---

## Phase 2 — Write the code

For each layer in the plan's file manifest (section 3), in dependency order (migration → models → schemas → repositories → services → DI wiring → API → tests):

1. Write/modify the file with `create_file` / `replace_string_in_file` / `multi_replace_string_in_file`, using the plan's Phase-7 code adjusted for Phase 1 drift.
2. Preserve every `# Decision N: ...` inline comment from the plan's code — it's what makes review round 2 able to trace coverage.
3. After each layer, run the repo's formatter/linter and fix mechanically-flagged issues immediately (this is tooling, not a review round):
   - Backend: `ruff check {changed_paths}` and `ruff format {changed_paths}` (Python 3.14, line-length 88, rules in `pyproject.toml`); `mypy {changed_paths}` for typing.
   - Frontend: `npm run lint` scoped to changed files where the tool allows, else full run.

Update the ledger's "Files written" after each layer.

---

## Phase 3 — Local self-check before spending review budget

Before either review round, run a **fast** pass so obviously broken code never reaches a reviewer:
- Backend: `mypy` clean on changed files, then unit tests only for the touched module(s) (`pytest {module}/tests/unit`).
- Frontend: `npm run lint` clean, then `npm test -- {changed spec files}` (vitest) if changed files have matching specs, else the module's existing spec set.

Fix failures directly; do not proceed to Phase 4 with known-red output.

---

## Phase 4 — Review Round 1: CodeReviewer

`runSubagent agentName=CodeReviewer`:

> Plan: `{plan_path}` (for context on scope/decisions only — do not re-litigate decisions, verify the code against them). Repo: `{repo_path}`. Changed files: {paths only}. Task {task_id} — fetch it yourself if you need AC: `mcp_azure_devops__wit_work_item action=get id={task_id}`.
> Review only the changed files per your standard correctness/security/performance/style pass. Additionally: (a) verify every `# Decision N` comment matches what section 0 of the plan actually decided, (b) flag any SOLID/DRY/DI violation or dead code per the "good code" checklist, (c) flag any deviation from the majority convention of the surrounding directory.
> Do NOT edit any file. Return your standard `| Line | Issue | Severity | Category | Fix |` table.

Apply every CRITICAL/HIGH/MEDIUM fix in **one** `multi_replace_string_in_file` call across all affected files. Log round + issues + resolutions in the ledger.

---

## Phase 5 — Review Round 2: Architect

`runSubagent agentName=Architect`:

> Plan: `{plan_path}` (context only). Repo: `{repo_path}`. Changed files: {paths only}. Referenced architecture docs: `docs/2-system-architecture/2.2-backend-architecture.md` (backend) / `docs/1-frontend-architecture/1.1-frontend-architecture.md` + `1.2-frontend-conventions.md` (frontend) — adjust these paths to whatever this repo actually uses if they don't exist. Also read every ADR under `docs/adr/`, `docs/*/adr/`, or `docs/decisions/` relevant to the changed files (from the Phase 0 "ADRs" ledger section).
> Check the changed files against these docs: layer boundaries (API → Service → Repository → Infrastructure, never skipped or reversed), module dependency rules, structural symmetry (a rule applied to a parent entity but silently missing on a subordinate/parallel one), and conformance with every relevant `Accepted` ADR — cite the ADR number/path for each check, not just "compliant". Also check whether anything implemented here should be reflected back into these docs (new module, new table in a diagram, new dependency rule) — list candidates, do not edit docs yourself.
> Do NOT edit any file. Return `VERDICT: CLEAN` or `VERDICT: ISSUES (n)` with a table `# | severity (BLOCKER/MAJOR/MINOR) | file:line | issue | doc citation | recommended fix`, plus a short `DOC UPDATE CANDIDATES` list.

Apply every BLOCKER/MAJOR fix in one `multi_replace_string_in_file` call. If BLOCKERs remain after this fix pass, STOP: list them via `vscode_askQuestions` (`Kolejna runda review` / `Akceptuj\u0119 ryzyko, kontynuuj` / `Popraw\u0119 r\u0119cznie, zaczekaj`). Do not proceed to Phase 6 while an unresolved BLOCKER stands and the user hasn't chosen.

Log round + issues + resolutions + doc-update candidates in the ledger.

---

## Phase 6 — Static checks, then tests

Static analysis is a hard gate before this phase's tests run — Phase 2/3 only checked
per-layer or partial-file, this is the full pass over everything touched, after the code has
settled through both review rounds:

- Backend: `ruff check {changed_paths}`, `ruff format --check {changed_paths}`, `mypy {changed_paths}`. If cross-file typing makes a partial `mypy` run unreliable (e.g. a changed shared schema/base class), run `mypy app` (or the repo's documented full command) instead of the scoped one.
- Frontend: `npm run lint` and `npm run typecheck`, scoped to changed files where the tool supports it, else full run.

Fix every finding — do not defer a `ruff`/`mypy`/lint/typecheck failure to "known issue" or a review round; those rounds review logic and architecture, not tooling-catchable errors. Record the exact commands and pass/fail in the ledger under a new "Static checks" section before moving on.

Then run the automated tests. Backend, for each touched module:
```
pytest code/cloud_run/fastapi/app/modules/{module}/tests/unit
pytest code/cloud_run/fastapi/app/modules/{module}/tests/integration
```
Only if the plan's scope explicitly includes a UI end-to-end flow (rare — most tasks don't), additionally run the relevant test(s) under `tests/UI/` (Selenium). Do not run the full `tests/UI/` suite for unrelated backend changes.

Frontend:
```
npm test -- {changed spec files or module path}
```
There is no Playwright/Cypress e2e layer in this frontend as of this writing — do not fabricate an e2e step. State this explicitly in the DoD/report rather than silently skipping it.

Fix failures, re-run only the failed tests, then run the full touched-module suite once green (never claim green from a partial run). Record pass/fail counts in the ledger.

---

## Phase 7 — Documentation update (conditional)

Only edit docs if Phase 5's `DOC UPDATE CANDIDATES` (or your own observation) shows the implementation genuinely diverges from or extends what a referenced doc states — e.g. a new module not in the dependency diagram, a new table not in the module definitions, a rule that's now stricter/looser than documented.

If found: edit only the specific section, cite the plan (`{plan_path}`) as the source, keep the edit scoped (~200 words), and do not touch unrelated sections. If nothing diverges, state explicitly *"Docs zgodne z implementacj\u0105, brak zmian"* and move on — do not add a changelog entry for its own sake.

---

## Phase 8 — Persist and report

1. `memory` → `/memories/repo/`: append reusable facts only — drift found in Phase 1, any convention correction, verified test commands, migration HEAD after this task. Not task-specific narration.
2. Final message to the user, in Polish, no filler:
   - table `runda | reviewer | znalezione problemy | jak naprawiono`
   - static checks: `ruff`/`mypy`/`lint`/`typecheck` status (clean, or fixed and now clean)
   - test results summary (unit/integration/frontend, pass counts)
   - docs: zmienione sekcje lub "brak zmian"
   - explicit: working tree not committed — pliki zmienione: {list}
   - remaining risks / unresolved MINORs left as-is
   - direct question: `git diff` review teraz, czy commitowa\u0107 samodzielnie?

---

## Token discipline

- Main thread necessarily holds the plan file and the files it writes (rule 4) — but pre-flight verification and both review rounds happen in subagents whose transcripts are discarded.
- Never re-run Phase 1 drift checks for a symbol already confirmed `drift: none` in the ledger.
- No progress narration between phases; act, then report the delta.
- Do not paste full file diffs into the chat response — the ledger and the final Phase 8 table are the record; the response summarizes, it doesn't repeat file contents.
