---
name: security-scan
description: Audit the current changes against the OWASP security checklist in an isolated subagent.
disable-model-invocation: true
user-invocable: true
argument-hint: "[optional path or base branch]"
context: fork
agent: code-reviewer
background: false
---

# Security Scan

Audit the working tree changes against the `security-checklist` rule. `$ARGUMENTS`, when
given, narrows the scan to a path or names the base branch to diff against; default is the
uncommitted diff, falling back to the last commit when the tree is clean.

Runs in an isolated context so the audit does not consume the main conversation's window.

Claude Code uses the forked `code-reviewer` agent configured above. In the generated Copilot
mirror, launch `code-reviewer` as a Local subagent; if that cannot be done, report the scan as
limited rather than claiming an isolated review.

## Scope

Start from the diff, then follow each change outward to the boundary it affects. A safe-looking
line inside an unsafe boundary is still a finding.

## Checks

**Secrets** — hardcoded keys, tokens, passwords, connection strings; secrets in log
statements, error messages, test fixtures, or committed config. Any confirmed exposure is BLOCKER,
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

Use the shared finding schema, most severe first. Do not cap BLOCKER/MAJOR findings; group MINOR/INFO findings and return at most five, noting if more were omitted.

```
[BLOCKER|MAJOR|MINOR|INFO] path/to/file.py#L42 - <concise claim>
  Category: security
  Evidence: exact code or configuration that enables the issue.
  Attack path: concrete source-to-impact path.
  Scenario/impact: trigger and consequence.
  Fix: the specific change, and the safer of two options when there is a choice.
```

Use `VERDICT: CLEAN`, `VERDICT: FINDINGS`, or `VERDICT: LIMITED`; state what blocks delivery and what can be deferred. Uncertain claims are `UNCLEAR`, not findings. Do not assign numeric confidence.
Report no findings rather than padding the list — a scan that always finds something
trains the reader to ignore it.
