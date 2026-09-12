"""Minimal YAML frontmatter reader shared by the toolkit scripts.

Deliberately not PyYAML: these scripts run in CI and in a fresh clone on any machine, and a
dependency-free validator is one that always runs. The subset handled here is the subset the
toolkit actually uses - scalars, inline lists, and block lists. Anything more nested is
returned as a raw string rather than guessed at.
"""

from __future__ import annotations

from pathlib import Path

DELIMITER = "---"


class FrontmatterError(ValueError):
    """Raised when a file that must carry frontmatter does not."""


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def split_top_level(text: str, separator: str = ",") -> list[str]:
    """Split on a separator, ignoring separators inside quotes or brace/bracket groups.

    Glob patterns use brace expansion - `**/*.{ts,tsx}` - so a naive split corrupts them.
    """
    items: list[str] = []
    buffer: list[str] = []
    depth = 0
    quote: str | None = None

    for char in text:
        if quote:
            if char == quote:
                quote = None
            buffer.append(char)
            continue
        if char in {'"', "'"}:
            quote = char
            buffer.append(char)
            continue
        if char in "{[(":
            depth += 1
        elif char in "}])":
            depth = max(0, depth - 1)
        if char == separator and depth == 0:
            items.append("".join(buffer))
            buffer = []
            continue
        buffer.append(char)

    items.append("".join(buffer))
    return [item for item in (part.strip() for part in items) if item]


def _parse_inline_list(value: str) -> list[str]:
    inner = value.strip()[1:-1].strip()
    if not inner:
        return []
    return [_strip_quotes(item) for item in split_top_level(inner)]


def parse(text: str) -> tuple[dict[str, object], str]:
    """Split a document into (frontmatter mapping, body).

    Returns an empty mapping when the document has no frontmatter block.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != DELIMITER:
        return {}, text

    closing = next((i for i, line in enumerate(lines[1:], start=1) if line.strip() == DELIMITER), None)
    if closing is None:
        raise FrontmatterError("frontmatter opened with --- but never closed")

    data: dict[str, object] = {}
    current_key: str | None = None
    block_items: list[str] = []

    def flush() -> None:
        nonlocal current_key, block_items
        if current_key is not None:
            data[current_key] = block_items if block_items else data.get(current_key, "")
        current_key, block_items = None, []

    for raw_line in lines[1:closing]:
        line = raw_line.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue

        stripped = line.strip()

        if stripped.startswith("- ") and current_key is not None:
            block_items.append(_strip_quotes(stripped[2:]))
            continue

        if not line.startswith((" ", "\t")) and ":" in line:
            flush()
            key, _, value = line.partition(":")
            key, value = key.strip(), value.strip()
            if not value:
                current_key = key
                data.setdefault(key, "")
            elif value.startswith("[") and value.endswith("]"):
                data[key] = _parse_inline_list(value)
            else:
                data[key] = _strip_quotes(value)
            continue

        # Indented content that is not a list item (nested mapping): keep it as raw text so
        # a validator can see that the key exists without pretending to understand it.
        if current_key is not None:
            existing = data.get(current_key) or ""
            data[current_key] = f"{existing}\n{stripped}".strip() if isinstance(existing, str) else existing

    flush()
    body = "\n".join(lines[closing + 1 :]).lstrip("\n")
    return data, body


def load(path: Path) -> tuple[dict[str, object], str]:
    return parse(path.read_text(encoding="utf-8"))


def as_list(value: object) -> list[str]:
    """Normalize a frontmatter value that may be a scalar, a comma/space separated string,
    or a list, into a list of strings."""
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    text = str(value)
    if "," in text:
        return [_strip_quotes(part) for part in split_top_level(text)]
    return [_strip_quotes(part) for part in text.split() if part.strip()]
