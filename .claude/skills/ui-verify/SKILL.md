---
name: ui-verify
description: Physically click through the running frontend in a real Chrome browser (via the chrome-devtools MCP server) and check each screen/flow against a plan or checklist. Use after implementing frontend changes, when the user asks to "verify the UI matches the plan", "click through the app", or "check the implementation against the spec".
user-invocable: true
---

# UI Verify Skill

Drives the actual app in Chrome (through the `chrome-devtools` MCP server) to confirm
that what got implemented on the frontend matches what was planned — not by reading
the code, but by looking at the rendered screens.

If the `chrome-devtools` MCP tools are not available in this session (check the tool
list), tell the user the MCP server was just registered and the session/client needs
a restart to connect to it. Do not try to fake this with WebFetch or by reading code.

## Inputs

Before starting, gather:

1. **The plan/checklist** — a doc, PR description, or the user's own message listing
   what should exist per screen (e.g. "Users page: table with role column, invite
   button top-right, disabled state for self"). If the user just points at a plan
   file, read it. If they describe it inline, use that as the checklist directly.
2. **The dev server URL.** Default: `http://localhost:5173` (Vite default in
   `frontend/`). Check if it's already running (`list_pages` / try navigating); if
   not, start it in the background from `frontend/`: `npm run dev`, then wait for the
   "ready" log line before navigating.
3. **Auth state**, if screens require login — ask the user for test credentials or a
   known dev-login shortcut rather than guessing.

## Procedure

1. Turn the checklist into a flat list of (screen/route, expected item) pairs. Keep
   this list — it's what you report against at the end.
2. For each screen:
   - `navigate_page` to its route.
   - `take_snapshot` (accessibility tree) to inspect real structure/text/roles —
     this is what you reason from, it's more reliable than pixels for text/labels/
     presence checks.
   - `take_screenshot` for visual evidence to show the user and to catch layout/
     visual issues a snapshot won't (spacing, overlap, broken images, color).
   - Exercise the interactive parts the plan calls for: `click`, `fill`/`fill_form`,
     `hover`, then re-snapshot/re-screenshot to check the resulting state (dialogs,
     validation errors, disabled buttons, toasts).
   - Check `list_console_messages` for errors/warnings thrown while on the page —
     report these even if not in the checklist, they're regressions.
3. Mark each checklist item: match / mismatch / not found, with the concrete
   evidence (snapshot excerpt or screenshot) backing the verdict. Don't guess from
   memory of the code — only report what you actually observed in this pass.
4. Summarize as a punch list, grouped by screen: what matches, what doesn't, what's
   missing, and any console errors encountered. Attach or reference the screenshots
   for anything flagged as a mismatch.

## Notes

- Prefer `take_snapshot` over screenshots for verifying text/labels/presence —
  it gives exact strings and element refs you can act on next (click by ref).
- Use screenshots specifically for visual/layout judgment calls, and always for
  anything you're flagging as wrong, so the user doesn't have to take your word for it.
- Don't stop at the first mismatch — finish the full checklist, then report
  everything together.
- If a route requires state you can't reach through the UI (e.g. seeded data), say
  so rather than silently skipping the check.

## Temporary Files

- Store all screenshots, snapshots, and temporary artifacts in `.tmp/ui-verify/`
- Clean up `.tmp/ui-verify/` after verification completes (remove directory or clear contents)
- This keeps the project directory clean and prevents git from tracking transient files
