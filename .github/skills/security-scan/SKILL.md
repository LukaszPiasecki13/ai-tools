---
name: security-scan
description: Audit the current changes against the OWASP security checklist in an isolated subagent.
---

<!-- GENERATED FILE - DO NOT EDIT.
     Source: skills/security-scan/SKILL.md
     Regenerate: python scripts/sync_copilot.py -->

# Security Scan

Audit the working tree changes against the `security-checklist` rule. `$ARGUMENTS`, when
given, narrows the scan to a path or names the base branch to diff against; default is the
uncommitted diff, falling back to the last commit when the tree is clean.

Runs in an isolated context so the audit does not consume the main conversation's window.

## Scope

Start from the diff, then follow each change outward to the boundary it affects. A safe-looking
line inside an unsafe boundary is still a finding.

## Checks

**Secrets** — hardcoded keys, tokens, passwords, connection strings; secrets in log
statements, error messages, test fixtures, or committed config. Any hit is CRITICAL,
and the remediation includes rotating the exposed value, not just deleting the line.

**AuthN/AuthZ** — every new endpoint states who may call it. Missing authorization is the
default failure mode: a route with no dependency/guard is unauthenticated until proven
otherwise. Check for object-level authorization (can this user touch *this* record, not just
*a* record).

**Input validation** — validated at the boundary with a schema, not ad hoc inside handlers.
Check bounds, enums, and identifier formats. Trust nothing from URL params, bodies, headers,
or query strings.

**Injection** — parameterized queries only. Flag any string interpolation reaching SQL, a
shell command, a file path, or an LDAP/XPath expression.

**XSS and rendering** — no user-controlled HTML rendered unsanitized
(`dangerouslySetInnerHTML`, `[innerHTML]`, template `|safe`).

**Transport and storage of tokens** — `httpOnly`/`Secure`/`SameSite` cookies; never
`localStorage`. JWT algorithm pinned and `aud`/`iss` verified.

**Rate limiting** — present on auth and other abuse-prone endpoints.

**Dependencies** — new or changed dependencies: check the version floor is not itself a
known-vulnerable release. A range like `>=3.3.0` pins nothing if 3.3.0 is the vulnerable version.

**Error handling** — internal details (stack traces, SQL, file paths, upstream errors) must
not reach the client response.

## Output

One block per finding, most severe first:

```
[CRITICAL|HIGH|MEDIUM|LOW] path/to/file.py#L42 - <one-line claim>
  Attack: concrete path from untrusted input to impact.
  Evidence: the code that makes it possible.
  Fix: the specific change, and the safer of two options when there is a choice.
```

End with a one-line verdict: what blocks merge, and what is acceptable to defer and why.
Report no findings rather than padding the list — a scan that always finds something
trains the reader to ignore it.
