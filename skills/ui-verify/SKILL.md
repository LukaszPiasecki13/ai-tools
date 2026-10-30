---
name: ui-verify
description: Physically click through the running frontend in a real Chrome browser (via the chrome-devtools MCP server) and check each screen/flow against a plan or checklist. Use after implementing frontend changes, when the user asks to "verify the UI matches the plan", "click through the app", or "check the implementation against the spec".
user-invocable: true
---

# UI Verify Skill

Drives the actual app in Chrome (through the `chrome-devtools` MCP server) to confirm
that what got implemented on the frontend matches what was planned — not by reading
the code, but by looking at the rendered screens.

## Primary Driver: Chrome MCP

**Chrome MCP is the MANDATORY primary driver for this skill.** You MUST follow this sequence:

### Step 0: Load Chrome MCP Tools (REQUIRED FIRST)

Before opening the browser or doing anything else:

```
ToolSearch(query: "select:mcp__chrome-devtools__navigate_page,mcp__chrome-devtools__take_snapshot,mcp__chrome-devtools__take_screenshot,mcp__chrome-devtools__list_console_messages,mcp__chrome-devtools__click,mcp__chrome-devtools__fill,mcp__chrome-devtools__fill_form,mcp__chrome-devtools__hover,mcp__chrome-devtools__list_pages")
```

**Do not skip this step.** ToolSearch checks if Chrome MCP is available before you attempt to use it.

### Step 1: Check Availability

- If ToolSearch succeeds → Chrome MCP tools are loaded and available. Proceed to "Inputs" section.
- If ToolSearch fails or Chrome MCP server is `CONNECTION_CLOSED` → tell the user:
  > "Chrome MCP server failed to connect. Please restart it (check `.mcp.json` in the repo root) and try again. Cannot proceed without Chrome MCP."
  >
  > Do not fake verification with WebFetch/code reading. The only allowed fallback driver is Playwright with its own Chromium, and only after the user agrees — see "Fallback: Playwright" below.

  Then read [troubleshooting.md](troubleshooting.md) (loaded only in this case) and work through it
  with the user.

#### Fallback: Playwright with its own Chromium (when the MCP is unavailable)

Playwright downloads its own Chromium, which does not read the `Google\Chrome` / `Microsoft\Edge` policy keys, so it works where chrome-devtools-mcp is blocked (verified on a managed Windows machine: headless run, screenshot and console capture all worked).

**Gate — ask first.** Because this sidesteps an IT policy, do not use it unless the user has said yes in this conversation. Say what you would do ("run Playwright's bundled Chromium headless against localhost; nothing in the repo changes") and wait.

**Setup — outside the repo**, so the app's `package.json` stays untouched (use the scratchpad directory):
```bash
mkdir -p <scratchpad>/pw && cd <scratchpad>/pw
npm init -y && npm i playwright
npx playwright install chromium     # one-time download, cached in %LOCALAPPDATA%\ms-playwright
```

**Run** — write a script per screen/flow and execute it with `node`, passing the app URL in the
`APP_URL` environment variable (PowerShell: `$env:APP_URL='{app_url}'; node smoke.mjs`; bash:
`APP_URL='{app_url}' node smoke.mjs`). Template (smoke test of a page):
```js
// smoke.mjs
import { chromium } from 'playwright';
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
const problems = [];
page.on('console', m => { if (['error', 'warning'].includes(m.type())) problems.push(`${m.type()}: ${m.text()}`); });
page.on('pageerror', e => problems.push(`pageerror: ${e.message}`));
await page.goto(process.env.APP_URL, { waitUntil: 'networkidle' }); // APP_URL = {app_url}
console.log('url:', page.url(), '| title:', await page.title());
console.log(await page.locator('body').innerText());      // text/presence checks
await page.screenshot({ path: 'screen.png' });            // visual evidence
// interactions: await page.getByRole('button', { name: '...' }).click(); then re-check
console.log('console problems:', problems.length ? problems : 'none');
await browser.close();
```
Equivalents of the MCP procedure: `page.goto` = navigate, `locator.innerText()` / `page.getByRole(...)` / `locator.ariaSnapshot()` = snapshot, `page.screenshot` = screenshot, `page.on('console')` = console messages, `.click()` / `.fill()` = interactions. Prefer role/text locators over CSS selectors. Look at each screenshot (Read tool) before giving a verdict.

**Notes**
- Headless by default; it runs its own browser, so it never touches the user's Chrome or the MCP profile.
- Expect `ERR_CONNECTION_REFUSED` console errors if a backend the app needs (`{api_url}`, when the inputs name one) is not running. Report it as the cause rather than as a UI bug, and say that logged-in screens/data cannot be verified without it.
- Store screenshots under `.tmp/ui-verify/` and clean up afterwards, as in "Temporary Files".
- Say explicitly in the report that the verification was done through the Playwright fallback, not the Chrome MCP.

## Inputs

Before starting, gather (a caller such as `sdlc-implement` passes them; otherwise find them):

1. **The plan/checklist** — a doc, PR description, or the user's own message listing
   what should exist per screen (e.g. "Users page: table with role column, invite
   button top-right, disabled state for self"). If the user just points at a plan
   file, read it. If they describe it inline, use that as the checklist directly.
2. **The app**: `{app_url}`, `{start_command}` and `{app_dir}` (where the command runs), plus
   `{api_url}` when the app needs a backend. Sources in order: the caller (for `sdlc-implement`,
   the `app` row of `Komendy weryfikacji` in `01-context.md`), repo instructions (`CLAUDE.md`,
   README), the app's manifest/scripts and framework config. Record the source of each value; if
   none is found, ask the user — never assume a port or folder. Check whether the app is already
   running (`list_pages` / navigate); if not, run `{start_command}` in `{app_dir}` in the background
   and wait for its "ready" line before navigating.
3. **Auth state**, if screens require login — use the caller's login instructions, otherwise ask
   the user for test credentials or a known dev-login shortcut rather than guessing.

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

## Cleanup — leave no trace

Clean up after yourself at the end of **every** run, including runs that failed or were aborted. Do it after the report is written, so screenshots you cite are still available while you write it.

1. **Files:** delete `.tmp/ui-verify/` (and `.tmp/` itself if it is now empty). Check `git status` to confirm nothing from the run is left in the repo.
2. **App:** stop it only if *you* started it in this run (`{start_command}`). If it was already running when you began, leave it alone.
3. **Browsers:** close pages you opened. With the Playwright fallback, call `browser.close()` (also on failure paths — use `try/finally`). If the MCP left Chrome running, end only processes whose command line contains `chrome-devtools-mcp`; never touch the user's own Chrome windows.
4. **Playwright scripts:** keep them in the scratchpad directory, never in the repo. The installed `playwright` package and the Chromium cache are reusable — do not delete them unless the user asks.
5. **Do not undo what the user declined.** If a cleanup command is denied, don't retry it with another tool — list what is left (paths/PIDs) in the report and let the user decide.
6. Mention in the report what you cleaned up and what, if anything, you left behind.
