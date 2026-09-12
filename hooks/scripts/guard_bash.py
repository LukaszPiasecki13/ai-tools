#!/usr/bin/env python3
"""PreToolUse(Bash) guard: block irreversible or policy-violating shell commands.

Reads the hook payload on stdin and prints a PreToolUse decision object on stdout.

Design rules for this file:
  * Fail open. Any unexpected input, and the command is allowed through - a guard that
    crashes must not be able to halt all work.
  * Deny only what is irreversible or explicitly forbidden by policy. Every additional
    pattern costs a false positive somewhere, and a guard that cries wolf gets disabled.
  * Never rewrite the command. Denying with a reason keeps the human in control.
"""

from __future__ import annotations

import json
import re
import sys

# (compiled pattern, human-readable reason, suggested alternative)
RULES: list[tuple[re.Pattern[str], str, str]] = [
    (
        re.compile(r"\bgit\s+push\b(?=.*\s(--force|-f)(\s|$))(?!.*--force-with-lease)"),
        "force push overwrites remote history and can destroy a teammate's work",
        "use --force-with-lease, or push a new branch",
    ),
    (
        re.compile(r"\bgit\s+reset\s+(--hard|--merge)\b"),
        "hard reset discards committed and uncommitted work with no recovery path",
        "commit or stash first, then reset - or use 'git revert' to undo a commit safely",
    ),
    (
        re.compile(r"\bgit\s+clean\b.*\s-\w*f"),
        "git clean permanently deletes untracked files, including ones never committed",
        "review 'git clean -n' output and delete the specific paths yourself",
    ),
    (
        re.compile(r"\bgit\s+(checkout|restore)\s+(--\s+)?(\.|\*)(\s|$)"),
        "this discards every uncommitted change in the working tree",
        "stash first ('git stash push -m wip'), or restore the specific file",
    ),
    (
        re.compile(r"\bgit\s+branch\s+-D\b"),
        "force-deleting a branch drops commits that exist nowhere else",
        "use 'git branch -d' - it refuses only when commits would be lost",
    ),
    (
        re.compile(r"\bgit\s+(commit|rebase|merge|cherry-pick)\b.*--no-verify\b"),
        "--no-verify skips the project's own pre-commit checks",
        "fix what the hook reports, or run the check manually and explain why it is wrong",
    ),
    (
        re.compile(r"\bchmod\s+(-\w+\s+)*777\b"),
        "mode 777 makes the path world-writable",
        "grant the narrowest mode that works (644 for files, 755 for directories)",
    ),
    (
        re.compile(r"\b(curl|wget)\b[^|]*\|\s*(sudo\s+)?(ba|z|k|)sh\b"),
        "piping a downloaded script straight into a shell executes unreviewed remote code",
        "download to a file, read it, then run it",
    ),
    (
        re.compile(r"\bDROP\s+(TABLE|DATABASE|SCHEMA)\b", re.IGNORECASE),
        "dropping a table, database or schema destroys data irreversibly",
        "run it yourself against the intended environment, after a backup",
    ),
]

# `rm -rf` is only blocked when the target is dangerously broad; `rm -rf node_modules`
# is ordinary housekeeping and must stay allowed.
RM_RECURSIVE_FORCE = re.compile(r"\brm\s+(?:-\w+\s+)*-\w*r\w*")
# Targets that make a recursive delete catastrophic: filesystem root, home, a bare wildcard,
# the current or parent directory, or a Windows drive root.
_RM_PREFIX = r"\brm\s+(?:-\w+\s+)*"
_RM_TARGETS = "|".join(
    [
        r"/\s*$",
        r"/(?:bin|etc|usr|var|lib|home|opt|Users)\b",
        r"~(?:/\s*)?$",
        r"\$HOME(?:/\s*)?$",
        r"\*\s*$",
        r"\.\s*$",
        r"\.\.(?:/\s*)?$",
        r"[A-Za-z]:[\\/]?\s*$",
    ]
)
DANGEROUS_RM_TARGETS = re.compile(_RM_PREFIX + "(?:" + _RM_TARGETS + ")")

# Reading secrets through the shell would bypass the file-path guard.
SECRET_READ = re.compile(
    r"\b(cat|bat|less|more|head|tail|nl|strings|xxd|type|Get-Content)\b[^|;&]*"
    r"(\.env(?!\.(example|sample|template|dist))\b"
    r"|\.pem\b|\.p12\b|\.pfx\b|id_rsa\b|id_ed25519\b"
    r"|credentials\.json\b|service-account[^\s]*\.json\b)"
)

# The project's virtual environment is mandatory; a bare `pip install` targets whatever
# interpreter happens to be first on PATH.
BARE_PIP_INSTALL = re.compile(r"(?<!\w)(?<!uv )pip3?\s+install\b")
VENV_PIP_MARKERS = re.compile(
    r"(\.venv|venv|env)[\\/](bin|Scripts)[\\/]|^\s*uv\s|\buv\s+pip\b|\buv\s+add\b"
    r"|VIRTUAL_ENV|--user\b|\bpipx\b|\bdocker\b|\bpoetry\s+(add|install)\b"
)


def deny(reason: str, alternative: str) -> None:
    """Emit a deny decision and exit successfully - exit code 0 with JSON is the
    documented way to return a PreToolUse decision."""
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Blocked by ai-tools guard: {reason}. Instead: {alternative}.",
            }
        },
        sys.stdout,
    )
    sys.exit(0)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        command = payload.get("tool_input", {}).get("command", "")
    except Exception:
        sys.exit(0)  # fail open

    if not isinstance(command, str) or not command.strip():
        sys.exit(0)

    for pattern, reason, alternative in RULES:
        if pattern.search(command):
            deny(reason, alternative)

    if RM_RECURSIVE_FORCE.search(command) and DANGEROUS_RM_TARGETS.search(command):
        deny(
            "recursive delete of a root, home or wildcard path",
            "delete the specific directory by its full relative path",
        )

    if SECRET_READ.search(command):
        deny(
            "this reads a file that holds credentials",
            "read the variable names from the .env.example file, and keep the values in the environment",
        )

    if BARE_PIP_INSTALL.search(command) and not VENV_PIP_MARKERS.search(command):
        deny(
            "pip install outside the project virtual environment pollutes the system interpreter",
            "activate the project venv first, or call it explicitly "
            "(.venv/bin/python -m pip install ... / .venv\\Scripts\\python -m pip install ...)",
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
