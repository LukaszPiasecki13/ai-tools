---
name: jira-board-extractor
description: Read-only Jira Cloud board data collection skill for backlog, epics, sprints, board configuration, and issue details. Use when the user asks to inspect or export data from a Jira Software board.
---

# Jira Board Extractor Skill

## Purpose

Use this skill to collect structured data from a Jira Software Cloud board, especially:

- board metadata and configuration
- backlog issues
- board issues
- epics
- sprints
- issue details for a given JQL or issue key list

This skill is read-only. It must not create, edit, move, or delete Jira data.

## Reusable Export Script

**Do not reinvent:** use the provided Python script instead of building extraction logic from scratch.

**Script:** [extract_board.py](extract_board.py)

**Agent API (general functions):** [jira_board_toolkit.py](jira_board_toolkit.py)

**Setup:**
```bash
cd .github/skills/jira-board-extractor
uv pip install requests python-dotenv
```

**Usage examples:**

```bash
# Export board 4 as JSON hierarchy (epics → issues → subtasks)
python extract_board.py --board-id 4 --output json --format hierarchy

# Export as CSV flat list (all issues)
python extract_board.py --board-id 4 --output csv --format flat

# Export single epic as markdown tree
python extract_board.py --board-id 4 --epic PAP-4 --output markdown --outfile epic_pap4.md

# Custom JQL filter (high priority only)
python extract_board.py --jql "priority = High" --output json

# Use custom output file
python extract_board.py --board-id 4 --outfile my_export.json
```

**Output options:**
- `--output json|csv|markdown`
- `--format hierarchy|flat|separate`
- `--board-id` (default: 4)
- `--jql` (custom filter)
- `--epic` (single epic)
- `--outfile` (custom path)

**Requires:** `.env` with `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_BASE_URL`

---

## Supported Authentication

Prefer one of these Jira Cloud auth modes:

- Atlassian API token with basic auth: `email + API token`
- OAuth 2.0 bearer token for Jira Cloud

Jira Cloud does not use a classic personal access token in the same way as Jira Data Center. If the user says PAT, confirm whether they mean an Atlassian API token.

For direct board scraping with basic auth, prefer a classic API token without scopes. If the user has an API token with scopes and basic auth returns `401`, switch to OAuth 2.0 or ask for a classic API token.

## Local Configuration

For local use, load credentials from environment variables instead of hardcoding them:

- `JIRA_EMAIL`
- `JIRA_API_TOKEN`
- `JIRA_BASE_URL`

Recommended `.env` format:

```env
JIRA_EMAIL=you@example.com
JIRA_API_TOKEN=your_api_token
JIRA_BASE_URL=https://your-domain.atlassian.net
```

Keep the `.env` file uncommitted. Read the values at runtime only.

## Required Inputs

For a live request, collect only what is necessary:

- Jira site URL, for example `https://example.atlassian.net`
- board id, for example `4`
- auth mode
- email and API token for basic auth, or bearer token for OAuth

Do not ask for secrets unless the user wants the skill to actually connect and fetch data.

## Default Board Flow

**Optimized for token efficiency:**

1. Load credentials from `.env` once (not per request).
2. Validate auth with a single lightweight call: `GET /rest/api/3/myself`.
3. Fetch board metadata once.
4. Fetch all board issues **in a single paginated pass** with field selection.
5. Fetch epics and sprints in parallel (if needed).
6. Group issues by epic/sprint locally (no additional API calls).
7. Cache result to JSON/CSV file.
8. Exit. Do not re-fetch the same data in the same session.

**Anti-patterns to avoid:**
- ❌ Making separate API calls per issue
- ❌ Fetching all fields then filtering locally
- ❌ Re-querying the board multiple times
- ❌ Not using pagination; fetching only page 1
- ❌ Manual loop-based data collection without scripting

## Jira REST Endpoints

Use these endpoints first:

- `GET /rest/agile/1.0/board/{boardId}`
- `GET /rest/agile/1.0/board/{boardId}/configuration`
- `GET /rest/software/1.0/board/{boardId}/backlog`
- `GET /rest/software/1.0/board/{boardId}/issue`
- `GET /rest/agile/1.0/board/{boardId}/epic`
- `GET /rest/agile/1.0/board/{boardId}/sprint`

Use Jira REST API v3 for issue-level enrichment when needed:

- `GET /rest/api/3/issue/{issueIdOrKey}`
- `GET /rest/api/3/search`

## Pagination

Handle both pagination styles:

- offset pagination with `startAt` and `maxResults`
- token pagination with `nextPageToken` and `maxResults`

Do not assume the same pagination style for all board endpoints.

## Fields To Request (Token Efficiency)

**Always use `fields` query param to select only required fields.** This drastically reduces response size and network overhead.

Example request:

```
GET /rest/api/3/search?jql=project=PAP&fields=key,summary,status,assignee,priority,labels
```

Typical fields needed for issue export:

- `key`
- `summary`
- `status`
- `issuetype`
- `assignee`
- `priority`
- `labels`
- `updated`

**Omit** changelog, comments, worklogs, and other heavy expansions unless explicitly required.

## Batch Processing & Scripting

**Never make interactive manual API calls for bulk extraction.** Write a script (Python/PowerShell) instead:

**Benefits:**
- Single pass through data (no re-fetching)
- Pagination handled automatically
- Results cached locally in JSON/CSV
- Reusable for future extractions
- Lower API call count

**Recommended script outline:**

1. Load credentials from `.env` once
2. Fetch board metadata once
3. Fetch all issues in one pass with pagination
4. Fetch epics and sprints in parallel (non-blocking)
5. Write results to local file (JSON or CSV)
6. Exit cleanly

Example structure in Python:

```python
# Load .env once
email, token = load_credentials()

# Fetch board
board = fetch_board(board_id)

# Fetch issues with selected fields, one pass with pagination
all_issues = fetch_all_issues_paginated(
    jql="project=PAP",
    fields=["key", "summary", "status", "assignee"]
)

# Save to file
write_json("board_export.json", {
    "board": board,
    "issues": all_issues
})
```

## Avoid Over-Fetching

- **Only paginate if needed**: If user wants top 50 issues, stop at page 1, don't fetch all pages.
- **Cache results**: Save output to `.json` locally; reuse without re-querying.
- **Parallel requests**: Fetch epics and sprints concurrently if both are needed.
- **Limit maxResults**: Use `maxResults=100` (API max) only if you need that volume.

## Error Handling

Treat these as the main failure classes:

- `401 Unauthorized`: bad or missing credentials
- `403 Forbidden`: authenticated but not permitted to view the board
- `404 Not Found`: wrong board id or board not visible to the user
- `429 Too Many Requests`: back off and retry with delay
- `5xx`: transient Jira service issue

If the board page is accessible in the browser but the API returns `403`, assume the account lacks browse permissions or the board is private.

## Output Shape

Prefer a normalized result such as:

```json
{
  "board": {"id": 4, "name": "...", "type": "scrum"},
  "configuration": {},
  "backlog": [],
  "epics": [],
  "sprints": [],
  "issues": []
}
```

## Notes For Copilot

- Ask for auth only when the user wants live data extraction or validation.
- Prefer API token/basic auth for quick setup in Jira Cloud.
- Never hardcode secrets into the skill file.
- If the user only wants a reusable skill definition, keep the file generic and secret-free.
## Validation

Before calling board endpoints, validate auth with a lightweight request such as:

- `GET /rest/api/3/myself`

If that succeeds, use the board endpoints above. If it fails with `401` or `403`, ask the user to verify the email, token type, and board permissions.

If a scoped token is in use and both the site URL and `api.atlassian.com` return `401` under basic auth, do not keep retrying. Treat that as a sign that the token is not suitable for this basic-auth flow.