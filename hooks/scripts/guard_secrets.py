#!/usr/bin/env python3
"""PreToolUse(Read|Edit|Write) guard: keep credential files out of the context window.

A secret that reaches the transcript is a secret that must be rotated. `.gitignore` prevents
a commit; it does nothing about a read. This guard is the read-side half.

It ships with the plugin, so the protection follows the toolkit into every project instead of
depending on each repository remembering to configure `permissions.deny`.

Fails open on unexpected input: a guard that crashes must not halt all work.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import PurePosixPath

# Files that are safe by construction: they carry variable names, never values.
SAFE_SUFFIXES = (".example", ".sample", ".template", ".dist", ".schema", ".md")

SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(^|/)\.env(\.[\w-]+)?$", re.IGNORECASE), "environment file with secret values"),
    (re.compile(r"\.(pem|key|p12|pfx|jks|keystore)$", re.IGNORECASE), "private key or certificate store"),
    (re.compile(r"(^|/)id_(rsa|dsa|ecdsa|ed25519)$"), "SSH private key"),
    (re.compile(r"(^|/)\.npmrc$|(^|/)\.pypirc$|(^|/)\.netrc$"), "package registry credentials"),
    (re.compile(r"service[-_]account[\w-]*\.json$", re.IGNORECASE), "service account key"),
    (re.compile(r"(^|/)credentials(\.json|\.yaml|\.yml)?$", re.IGNORECASE), "credentials file"),
    (re.compile(r"(^|/)secrets?\.(json|ya?ml|toml|ini)$", re.IGNORECASE), "secrets file"),
    (re.compile(r"(^|/)\.aws/credentials$|(^|/)\.docker/config\.json$"), "cloud provider credentials"),
    (re.compile(r"(^|/)settings\.local\.json$"), "machine-local settings, may hold tokens"),
]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        raw_path = payload.get("tool_input", {}).get("file_path", "")
    except Exception:
        sys.exit(0)

    if not isinstance(raw_path, str) or not raw_path:
        sys.exit(0)

    normalized = str(PurePosixPath(raw_path.replace("\\", "/")))

    if normalized.lower().endswith(SAFE_SUFFIXES):
        sys.exit(0)

    for pattern, description in SECRET_PATTERNS:
        if pattern.search(normalized):
            json.dump(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            f"Blocked by ai-tools guard: {normalized} is a {description}. "
                            "Reading it would put credentials in the transcript. "
                            "Use the matching .example file for the variable names, and read "
                            "values from the environment at runtime. If this file genuinely "
                            "holds no secrets, say so and the user can allow it explicitly."
                        ),
                    }
                },
                sys.stdout,
            )
            sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
