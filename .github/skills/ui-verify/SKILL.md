---
name: ui-verify
description: "Physically click through the running frontend in a real Chrome browser (via the chrome-devtools MCP server) and check each screen/flow against a plan or checklist. Use after implementing frontend changes, when the user asks to \"verify the UI matches the plan\", \"click through the app\", or \"check the implementation against the spec\"."
---

<!-- GENERATED FILE - DO NOT EDIT.
     Source: skills/ui-verify/SKILL.md
     Regenerate: python scripts/sync_copilot.py -->

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

#### Troubleshooting when the MCP is missing or won't connect

1. **Check `.mcp.json`** in the repo root. The working config on native Windows is:
   ```json
   {
     "mcpServers": {
       "chrome-devtools": {
         "command": "cmd",
         "args": ["/c", "npx", "-y", "chrome-devtools-mcp@latest"]
       }
     }
   }
   ```
   - Do **not** use `"command": "chrome-devtools"`. In the `chrome-devtools-mcp` package, `chrome-devtools` is a CLI (`start`/`status`/`stop`/`click`…), not the MCP server — the server binary is `chrome-devtools-mcp`. That config ends in `CONNECTION_CLOSED`.
   - `cmd /c` is required because `npx` is a `.cmd` shim on Windows.
   - No `--executablePath` needed: the server auto-detects installed Chrome. Add `"--executablePath", "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"` to `args` only if detection fails (check the path exists first; 32-bit `Program Files (x86)` is usually wrong).
2. **Requirements:** Node/npx on PATH (`node --version`), Chrome installed, network access for the first `npx` download. A global install is not needed.
3. **Reload the MCP.** Servers are loaded at session start — after any change to `.mcp.json`, run `/mcp` (reconnect) or restart the session. Tools then appear as `mcp__chrome-devtools__*`.
4. **Sanity check the server by hand** (optional): `npx -y chrome-devtools-mcp@latest --help` should print options.
5. **`Protocol error (Target.setDiscoverTargets): Target closed`** on the first `list_pages`/`new_page`: the server connected but could not attach to the Chrome it launched. Check the corporate policy first (step 6). If the policy is not the cause, a launch that was merely slow can be retried once.
   - **Do not loop on retries.** Each failed call spawns a new Chrome that holds the profile, so the next call fails with `The browser is already running for ...chrome-profile`. If you see that error, stop the leftover MCP-launched Chrome (only processes whose command line contains `chrome-devtools-mcp`) and diagnose instead of retrying.
6. **Check Chrome enterprise policy — the most likely cause on a managed (corporate) machine:**
   ```powershell
   Get-ItemProperty HKLM:\SOFTWARE\Policies\Google\Chrome | Select-Object RemoteDebuggingAllowed
   ```
   `RemoteDebuggingAllowed = 0` means IT has blocked remote debugging, which chrome-devtools-mcp depends on. Symptoms: `Target closed`, and Chrome started by hand with `--remote-debugging-port=9222` never opens the port. No MCP config change fixes this.
   - **Edge is not a way around it**: check `HKLM:\SOFTWARE\Policies\Microsoft\Edge` — on the managed machine where this was diagnosed it has the same `RemoteDebuggingAllowed = 0`.
   - **Do not edit the policy in the registry or look for workarounds** — it is an IT security control. Report it to the user and let them decide: ask IT for an exception, use Playwright with its own Chromium (see below — needs the user's consent, since it sidesteps the policy organizationally), or fall back to non-browser checks: `npm run test`, `typecheck`, `lint`, `build` in `frontend/`.
   - Chrome can still be opened manually for the user to click through (`Start-Process chrome http://localhost:5173`), but then you cannot read or drive it — do not claim anything about what was on screen.
7. **Dev server:** if `http://localhost:5173` returns nothing, start `npm run dev` in `frontend/` in the background and wait for the "ready" line.
8. If it still fails after all of the above, stop and report the exact error to the user.

#### Fallback: Playwright with its own Chromium (when the MCP is unavailable)

Playwright downloads its own Chromium, which does not read the `Google\Chrome` / `Microsoft\Edge` policy keys, so it works where chrome-devtools-mcp is blocked. Verified on the managed Windows machine: headless run, screenshot and console capture all worked.

**Gate — ask first.** Because this sidesteps an IT policy, do not use it unless the user has said yes in this conversation. Say what you would do ("run Playwright's bundled Chromium headless against localhost; nothing in the repo changes") and wait.

**Setup — outside the repo**, so `frontend/package.json` stays untouched (use the scratchpad directory):
```bash
mkdir -p <scratchpad>/pw && cd <scratchpad>/pw
npm init -y && npm i playwright
npx playwright install chromium     # one-time download, cached in %LOCALAPPDATA%\ms-playwright
```

**Run** — write a script per screen/flow and execute it with `node`. Template (smoke test of a page):
```js
// smoke.mjs
import { chromium } from 'playwright';
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
const problems = [];
page.on('console', m => { if (['error', 'warning'].includes(m.type())) problems.push(`${m.type()}: ${m.text()}`); });
page.on('pageerror', e => problems.push(`pageerror: ${e.message}`));
await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
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
- Expect `ERR_CONNECTION_REFUSED` console errors if the backend (`VITE_API_URL`, default `http://127.0.0.1:8000`) is not running. Report it as the cause rather than as a UI bug, and say that logged-in screens/data cannot be verified without it.
- Store screenshots under `.tmp/ui-verify/` and clean up afterwards, as in "Temporary Files".
- Say explicitly in the report that the verification was done through the Playwright fallback, not the Chrome MCP.

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

## Cleanup — leave no trace

Clean up after yourself at the end of **every** run, including runs that failed or were aborted. Do it after the report is written, so screenshots you cite are still available while you write it.

1. **Files:** delete `.tmp/ui-verify/` (and `.tmp/` itself if it is now empty). Check `git status` to confirm nothing from the run is left in the repo.
2. **Dev server:** stop it only if *you* started it in this run (`npm run dev`). If it was already running when you began, leave it alone.
3. **Browsers:** close pages you opened. With the Playwright fallback, call `browser.close()` (also on failure paths — use `try/finally`). If the MCP left Chrome running, end only processes whose command line contains `chrome-devtools-mcp`; never touch the user's own Chrome windows.
4. **Playwright scripts:** keep them in the scratchpad directory, never in the repo. The installed `playwright` package and the Chromium cache are reusable — do not delete them unless the user asks.
5. **Do not undo what the user declined.** If a cleanup command is denied, don't retry it with another tool — list what is left (paths/PIDs) in the report and let the user decide.
6. Mention in the report what you cleaned up and what, if anything, you left behind.
