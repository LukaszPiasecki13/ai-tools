Write the commit message from the staged diff in this exact form:

    <area>/ <type>(<scope>): <subject>

    <body>

- `<area>` comes first, followed by `/` and a space. It is the top-level part of the repo the
  change touches: `backend`, `frontend`, `firmware` or `docs`. Pick it from the paths in the
  diff. If the diff spans several areas, use the one that carries the main change.
- `<type>` is one of `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `build`, `ci`, `chore`.
  Never leave it out.
- `(<scope>)` is optional: the module or feature, e.g. `security`, `telemetry`, `modem`.
- `<subject>` is imperative mood, lower case, no trailing period, at most 72 characters in total
  for the first line. It says what the change does, not that something changed.
- The body is optional. Add it only when the reason is not obvious from the diff: explain why
  the change was needed, never restate the diff. Wrap lines at 72 characters.

Examples:

    backend/ feat(telemetry): add retry policy for device commands
    firmware/ fix(modem): release reset pin on power-on
    frontend/ refactor(devices): extract drawer header component
    docs/ docs: describe the remote commands flow

Do not mention model names, tool names or session identifiers in the message.
