---
name: test-focus
description: Run only the tests affected by the current changes, then widen if they pass.
disable-model-invocation: true
user-invocable: true
argument-hint: "[optional path or test name filter]"
---

# Focused Test Run

Changed files:

!`git status --short`

Run the smallest test set that can disprove the current change, then widen. A full suite on
every edit is slow enough that it stops being run at all.

## Process

1. **Map changes to tests.** For each changed source file, find its test by convention
   (`test_<module>.py`, `<Component>.test.tsx`, `<name>.spec.ts`) and by grepping for imports
   of the changed module. A changed shared utility pulls in every test that imports it.

2. **Run that set**, using the project's own runner and flags:

   | Stack | Command |
   |-------|---------|
   | pytest | `pytest <paths> -x -q` (add `-k <filter>` when `$ARGUMENTS` narrows it) |
   | Vitest | `npx vitest run <paths>` |
   | Jest | `npx jest <paths>` |
   | PlatformIO host tests | `pio test -e native -f <filter>` |

   Use the project's virtual environment or package manager — never a global interpreter.

3. **On failure, stop and diagnose.** Read the assertion and the diff before touching
   anything. Do not re-run hoping for a different result, and never adjust a test so it
   passes unless the test itself is what is wrong — in which case say so explicitly and
   explain why the old expectation was incorrect.

4. **On success, widen once**: run the full suite for the affected package or app. A focused
   pass proves the change works; only the wider run shows what it broke.

5. **Report** the exact commands run and their results. Never report a suite as passing
   without the output that says so.

## Coverage

Only when asked. Use the project's configured threshold — do not introduce one. Coverage
tells you what was executed, not what was verified; a rising number with no new assertions
is not progress.
