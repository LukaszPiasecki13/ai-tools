# ui-verify: Chrome MCP troubleshooting

Read this file only when Step 1 of [SKILL.md](SKILL.md) fails (no `chrome-devtools` tools, or
`CONNECTION_CLOSED`). The notes below were verified on native Windows with `chrome-devtools-mcp`
on a managed (corporate) machine; adapt the commands to other platforms.

1. **Check `.mcp.json`** in the repo root. A working config on native Windows:
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
   - Do **not** use `"command": "chrome-devtools"`. In the `chrome-devtools-mcp` package,
     `chrome-devtools` is a CLI (`start`/`status`/`stop`/`click`…), not the MCP server; the server
     binary is `chrome-devtools-mcp`. That config ends in `CONNECTION_CLOSED`.
   - `cmd /c` is required on Windows because `npx` is a `.cmd` shim. On macOS/Linux use
     `"command": "npx"` with `["-y", "chrome-devtools-mcp@latest"]`.
   - No `--executablePath` is needed: the server auto-detects installed Chrome. Add
     `"--executablePath", "<path to chrome>"` only if detection fails (check the path exists first).
2. **Requirements:** Node/npx on PATH (`node --version`), Chrome installed, network access for the
   first `npx` download. A global install is not needed.
3. **Reload the MCP.** Servers load at session start; after any change to `.mcp.json`, run `/mcp`
   (reconnect) or restart the session. Tools then appear as `mcp__chrome-devtools__*`.
4. **Sanity check by hand** (optional): `npx -y chrome-devtools-mcp@latest --help` prints options.
5. **`Protocol error (Target.setDiscoverTargets): Target closed`** on the first
   `list_pages`/`new_page`: the server connected but could not attach to the Chrome it launched.
   Check the browser policy first (step 6). If the policy is not the cause, a launch that was merely
   slow can be retried once.
   - **Do not loop on retries.** Each failed call spawns a new Chrome that holds the profile, so the
     next call fails with `The browser is already running for ...chrome-profile`. Stop the leftover
     MCP-launched Chrome (only processes whose command line contains `chrome-devtools-mcp`) and
     diagnose instead of retrying.
6. **Browser enterprise policy** (most likely cause on a managed Windows machine):
   ```powershell
   Get-ItemProperty HKLM:\SOFTWARE\Policies\Google\Chrome | Select-Object RemoteDebuggingAllowed
   ```
   `RemoteDebuggingAllowed = 0` means IT has blocked remote debugging, which chrome-devtools-mcp
   depends on. Symptoms: `Target closed`, and Chrome started by hand with
   `--remote-debugging-port=9222` never opens the port. No MCP config change fixes this.
   - Edge is not a way around it: check `HKLM:\SOFTWARE\Policies\Microsoft\Edge`; on the machine
     where this was diagnosed it had the same `RemoteDebuggingAllowed = 0`.
   - **Do not edit the policy or look for workarounds**: it is an IT security control. Report it and
     let the user decide: ask IT for an exception, use the Playwright fallback (SKILL.md; needs the
     user's consent), or fall back to non-browser checks with the repository's own test, typecheck,
     lint and build commands.
   - Chrome can still be opened manually for the user to click through (`Start-Process chrome
     {app_url}`), but then you cannot read or drive it; do not claim anything about what was on
     screen.
7. **App not reachable:** if `{app_url}` returns nothing, start the app with `{start_command}` in
   `{app_dir}` in the background and wait for its "ready" line.
8. If it still fails after all of the above, stop and report the exact error to the user.
