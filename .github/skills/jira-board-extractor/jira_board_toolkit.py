#!/usr/bin/env python3
"""Read-only Jira board toolkit for AI agents and CLI tools."""

from __future__ import annotations

import base64
import csv
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias

try:
    import requests
except ImportError as exc:
    raise RuntimeError(
        "requests is required. Install with: uv pip install requests"
    ) from exc

try:
    from dotenv import load_dotenv
except ImportError:

    def load_dotenv(*args: object, **kwargs: object) -> None:
        return None


JsonObject: TypeAlias = dict[str, Any]
JsonList: TypeAlias = list[JsonObject]
QueryParams: TypeAlias = dict[str, str | int]

DEFAULT_FIELDS: list[str] = [
    "key",
    "summary",
    "status",
    "assignee",
    "priority",
    "labels",
]
MAX_RESULTS: int = 100


class JiraToolError(Exception):
    pass


class JiraConfigError(JiraToolError):
    pass


class JiraAuthError(JiraToolError):
    pass


class JiraForbiddenError(JiraToolError):
    pass


class JiraNotFoundError(JiraToolError):
    pass


class JiraRateLimitError(JiraToolError):
    pass


class JiraRequestError(JiraToolError):
    pass


@dataclass(frozen=True)
class JiraConfig:
    email: str
    token: str
    base_url: str


def load_env(search_levels: int = 5) -> Path | None:
    """Search for .env in current and parent directories."""
    current_dir = Path(__file__).resolve().parent
    for _ in range(search_levels):
        env_path = current_dir / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            return env_path
        current_dir = current_dir.parent
    load_dotenv()
    return None


def load_config(
    email_override: str | None = None,
    token_override: str | None = None,
    base_url_override: str | None = None,
    search_levels: int = 5,
) -> JiraConfig:
    """Load Jira credentials from .env with optional overrides."""
    load_env(search_levels)

    email_value = (email_override or os.getenv("JIRA_EMAIL", "")).strip()
    token_value = (token_override or os.getenv("JIRA_API_TOKEN", "")).strip()
    base_url_value = (base_url_override or os.getenv("JIRA_BASE_URL", "")).strip()

    if not base_url_value:
        raise JiraConfigError("JIRA_BASE_URL is required")
    if not email_value or not token_value:
        raise JiraConfigError("JIRA_EMAIL and JIRA_API_TOKEN are required")

    return JiraConfig(
        email=email_value,
        token=token_value,
        base_url=base_url_value.rstrip("/"),
    )


class JiraClient:
    """Minimal read-only Jira API client with pagination helpers."""

    def __init__(self, config: JiraConfig) -> None:
        self.base_url = config.base_url
        self.email = config.email
        self.token = config.token
        self.headers = self._build_headers()

    def _build_headers(self) -> dict[str, str]:
        auth_value = f"{self.email}:{self.token}"
        auth_b64 = base64.b64encode(auth_value.encode()).decode()
        return {
            "Authorization": f"Basic {auth_b64}",
            "Accept": "application/json",
        }

    def validate_auth(self) -> None:
        """Validate credentials with a lightweight request."""
        self.get_json("/rest/api/3/myself")

    def get_json(self, endpoint: str, params: QueryParams | None = None) -> JsonObject:
        """GET a Jira endpoint and return JSON response."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as exc:
            status_code = exc.response.status_code if exc.response else 0
            if status_code == 401:
                raise JiraAuthError("Unauthorized: invalid email or token") from exc
            if status_code == 403:
                raise JiraForbiddenError("Forbidden: no access to resource") from exc
            if status_code == 404:
                raise JiraNotFoundError("Not found: resource does not exist") from exc
            if status_code == 429:
                raise JiraRateLimitError("Rate limited: wait and retry") from exc
            raise JiraRequestError(f"HTTP {status_code}") from exc
        except requests.exceptions.RequestException as exc:
            raise JiraRequestError("Request failed") from exc

    def fetch_paginated(
        self,
        endpoint: str,
        params: QueryParams,
        response_key: str,
    ) -> JsonList:
        """Fetch paginated results using startAt and maxResults."""
        collected_entries: JsonList = []
        start_at = 0

        while True:
            page_params: QueryParams = {
                **params,
                "startAt": start_at,
                "maxResults": MAX_RESULTS,
            }
            response_body = self.get_json(endpoint, page_params)
            page_entries = response_body.get(response_key, [])
            if not page_entries:
                break

            collected_entries.extend(page_entries)

            if response_body.get("isLast", True):
                break

            start_at += MAX_RESULTS

        return collected_entries

    def get_board(self, board_id: int) -> JsonObject:
        return self.get_json(f"/rest/agile/1.0/board/{board_id}")

    def get_epics(self, board_id: int) -> JsonList:
        response_body = self.get_json(f"/rest/agile/1.0/board/{board_id}/epic")
        return response_body.get("values", [])

    def get_sprints(self, board_id: int) -> JsonList:
        response_body = self.get_json(f"/rest/agile/1.0/board/{board_id}/sprint")
        return response_body.get("values", [])

    def get_backlog(self, board_id: int) -> JsonList:
        return self.fetch_paginated(
            f"/rest/software/1.0/board/{board_id}/backlog",
            {},
            response_key="issues",
        )

    def get_board_issues(self, board_id: int) -> JsonList:
        return self.fetch_paginated(
            f"/rest/software/1.0/board/{board_id}/issue",
            {},
            response_key="issues",
        )

    def search_issues(self, jql: str, field_names: list[str] | None = None) -> JsonList:
        params: QueryParams = {"jql": jql, "maxResults": MAX_RESULTS}
        if field_names:
            params["fields"] = ",".join(field_names)
        return self.fetch_paginated("/rest/api/3/search", params, "issues")

    def get_issue(self, issue_key: str, field_names: list[str] | None = None) -> JsonObject:
        params: QueryParams | None = None
        if field_names:
            params = {"fields": ",".join(field_names)}
        return self.get_json(f"/rest/api/3/issue/{issue_key}", params)


def build_board_snapshot(
    client: JiraClient,
    board_id: int,
    issue_source: str = "board",
    jql: str | None = None,
    include_backlog: bool = False,
    include_sprints: bool = False,
    include_epics: bool = True,
) -> JsonObject:
    """Fetch board metadata and issue lists in one call flow."""
    board_info = client.get_board(board_id)

    epic_rows = client.get_epics(board_id) if include_epics else []
    sprint_rows = client.get_sprints(board_id) if include_sprints else []
    backlog_rows = client.get_backlog(board_id) if include_backlog else []

    if issue_source == "board":
        issue_rows = client.get_board_issues(board_id)
    elif issue_source == "backlog":
        issue_rows = backlog_rows
    elif issue_source == "jql":
        if not jql:
            raise JiraRequestError("JQL is required for issue_source=jql")
        issue_rows = client.search_issues(jql)
    else:
        raise JiraRequestError("Unsupported issue_source")

    return {
        "board": board_info,
        "epics": epic_rows,
        "sprints": sprint_rows,
        "backlog": backlog_rows,
        "issues": issue_rows,
    }


def filter_issues_by_epic(issues: JsonList, epic_key: str) -> JsonList:
    """Return only issues that belong to the given epic key."""
    target_key = epic_key.upper()
    filtered_issues: JsonList = []
    for issue in issues:
        issue_epic_key = get_epic_key(issue)
        if issue_epic_key == target_key:
            filtered_issues.append(issue)
    return filtered_issues


def get_epic_key(issue: JsonObject) -> str | None:
    fields = issue.get("fields", {})
    if fields.get("parent"):
        return fields["parent"].get("key")
    if fields.get("customfield_10005"):
        return fields["customfield_10005"].get("key")
    return None


def extract_issue_field(issue: JsonObject, field_name: str) -> Any:
    fields = issue.get("fields", {})
    if field_name == "key":
        return issue.get("key", "")
    if field_name == "summary":
        return fields.get("summary", "")
    if field_name == "status":
        status_value = fields.get("status") or {}
        return status_value.get("name", "")
    if field_name == "assignee":
        assignee_value = fields.get("assignee") or {}
        return assignee_value.get("displayName", "")
    if field_name == "priority":
        priority_value = fields.get("priority") or {}
        return priority_value.get("name", "")
    if field_name == "labels":
        return ", ".join(fields.get("labels", []))
    if field_name == "created":
        return fields.get("created", "")
    if field_name == "updated":
        return fields.get("updated", "")
    if field_name == "issuetype":
        issue_type_value = fields.get("issuetype") or {}
        return issue_type_value.get("name", "")
    return fields.get(field_name)


def select_issue_fields(issues: JsonList, field_names: list[str]) -> JsonList:
    """Return issues as a list of dicts with selected field names."""
    selected_rows: JsonList = []
    for issue in issues:
        row: JsonObject = {}
        for field_name in field_names:
            row[field_name] = extract_issue_field(issue, field_name)
        selected_rows.append(row)
    return selected_rows


def group_issues_by_epic(epics: JsonList, issues: JsonList) -> JsonObject:
    """Return issues grouped by epic key with subtasks."""
    epic_map: JsonObject = {}
    issue_to_epic: dict[str, str] = {}

    for issue in issues:
        epic_key = get_epic_key(issue)
        if epic_key:
            issue_to_epic[issue.get("key", "")] = epic_key

    for epic in epics:
        epic_key = epic.get("key", "")
        epic_map[epic_key] = {"name": epic.get("name", ""), "issues": []}

        for issue in issues:
            if issue_to_epic.get(issue.get("key", "")) != epic_key:
                continue

            issue_fields = issue.get("fields", {})
            assignee_value = issue_fields.get("assignee") or {}
            assignee_name = assignee_value.get("displayName", "")
            status_value = issue_fields.get("status") or {}
            status_name = status_value.get("name", "")

            subtask_entries: JsonList = []
            for subtask in issue_fields.get("subtasks", []):
                subtask_fields = subtask.get("fields", {})
                subtask_status = subtask_fields.get("status") or {}
                subtask_status_name = subtask_status.get("name", "")
                subtask_entries.append(
                    {
                        "key": subtask.get("key", ""),
                        "summary": subtask_fields.get("summary", ""),
                        "status": subtask_status_name,
                    }
                )

            issue_entry = {
                "key": issue.get("key", ""),
                "summary": issue_fields.get("summary", ""),
                "status": status_name,
                "assignee": assignee_name,
                "subtasks": subtask_entries,
            }
            epic_map[epic_key]["issues"].append(issue_entry)

    return epic_map


def flatten_issues(
    issues: JsonList,
    field_names: list[str] | None = None,
) -> JsonList:
    """Flatten issues into a list of selected fields."""
    selected_fields = field_names or DEFAULT_FIELDS
    return select_issue_fields(issues, selected_fields)


def build_tree_lines(epics: JsonList, issues: JsonList) -> list[str]:
    """Build an ASCII tree (epics -> issues -> subtasks)."""
    lines: list[str] = []
    issue_to_epic: dict[str, str] = {}

    for issue in issues:
        epic_key = get_epic_key(issue)
        if epic_key:
            issue_to_epic[issue.get("key", "")] = epic_key

    for epic in epics:
        epic_key = epic.get("key", "")
        epic_name = epic.get("name", "")
        if epic_name:
            lines.append(f"EPIC: {epic_key} - {epic_name}")
        else:
            lines.append(f"EPIC: {epic_key}")

        epic_issues = [
            issue for issue in issues
            if issue_to_epic.get(issue.get("key", "")) == epic_key
        ]

        if not epic_issues:
            lines.append("  (no issues)")
        else:
            for index, issue in enumerate(epic_issues):
                is_last_issue = index == len(epic_issues) - 1
                prefix = "  `-" if is_last_issue else "  |-"
                summary = issue.get("fields", {}).get("summary", "")
                status = issue.get("fields", {}).get("status", {})
                status_name = status.get("name", "")
                lines.append(
                    f"{prefix} {issue.get('key', '')}: {summary} [{status_name}]"
                )

                subtasks = issue.get("fields", {}).get("subtasks", [])
                for subtask_index, subtask in enumerate(subtasks):
                    is_last_subtask = subtask_index == len(subtasks) - 1
                    subtask_prefix_left = "     " if is_last_issue else "  |  "
                    subtask_prefix = "`-" if is_last_subtask else "|-"
                    subtask_summary = subtask.get("fields", {}).get("summary", "")
                    subtask_status = subtask.get("fields", {}).get("status", {})
                    subtask_status_name = subtask_status.get("name", "")
                    lines.append(
                        f"{subtask_prefix_left}{subtask_prefix} "
                        f"{subtask.get('key', '')}: {subtask_summary} "
                        f"[{subtask_status_name}]"
                    )

        lines.append("")

    return lines


def update_issue_fields_local(
    issue: JsonObject,
    field_updates: JsonObject,
) -> JsonObject:
    """Return a copy of issue with local field updates applied."""
    issue_copy: JsonObject = {**issue}
    fields_copy: JsonObject = {**issue.get("fields", {})}
    fields_copy.update(field_updates)
    issue_copy["fields"] = fields_copy
    return issue_copy


def export_json(payload: Any, outfile: str | Path) -> None:
    """Export JSON payload to file."""
    output_path = Path(outfile)
    with output_path.open("w", encoding="utf-8") as file_handle:
        json.dump(payload, file_handle, indent=2, ensure_ascii=False)


def export_csv(rows: JsonList, outfile: str | Path) -> None:
    """Export rows to CSV file."""
    if not rows:
        return

    output_path = Path(outfile)
    column_names: list[str] = []
    for row in rows:
        for key_name in row.keys():
            if key_name not in column_names:
                column_names.append(key_name)

    with output_path.open("w", newline="", encoding="utf-8") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=column_names)
        writer.writeheader()
        writer.writerows(rows)


def export_markdown(lines: list[str], outfile: str | Path) -> None:
    """Export lines to a Markdown file."""
    output_path = Path(outfile)
    with output_path.open("w", encoding="utf-8") as file_handle:
        file_handle.write("\n".join(lines))
