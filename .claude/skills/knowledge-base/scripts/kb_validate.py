#!/usr/bin/env python3
"""Walidator bazy wiedzy dla agentów AI.

Sprawdza strukturę, metadane, linki, rozmiary i rozjazd doc<->kod w bazie
wiedzy zbudowanej wg .claude/skills/knowledge-base/.

Bez zależności zewnętrznych - wyłącznie biblioteka standardowa, żeby dało się
uruchomić w pre-commit (language: system) i w CI bez instalacji.

Użycie:
    python kb_validate.py --root .                  # raport tekstowy
    python kb_validate.py --root . --strict         # kod wyjścia 1 przy błędach E*
    python kb_validate.py --root . --fail-on-warn   # kod wyjścia 1 także przy W*
    python kb_validate.py --root . --format json    # raport maszynowy + metryki
    python kb_validate.py --root . --write-index    # regeneracja tabeli w mapie wiedzy

Kody diagnostyk: patrz METADATA.md, sekcja 5.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------------- #
# Konfiguracja
# --------------------------------------------------------------------------- #

LAYERS = {"L0", "L1", "L2", "L3", "L4"}
STATUSES = {"draft", "active", "superseded", "archived"}
CONFIDENCES = {"fact", "decision", "hypothesis"}

REQUIRED_ALWAYS = ["id", "title", "layer", "status", "confidence", "owner", "created", "verified"]
REQUIRED_BY_LAYER: dict[str, list[str]] = {
    "L0": [],
    "L1": ["review_after"],
    "L2": ["applies_to", "sources", "review_after"],
    "L3": ["expires"],
    "L4": ["sources"],
}

DATE_FIELDS = ["created", "verified", "review_after", "expires"]
LIST_FIELDS = {"applies_to", "sources", "related", "tags", "supersedes"}

# (miękki, twardy) limit linii
SIZE_LIMITS: dict[str, tuple[int, int]] = {
    "L0": (200, 300),
    "L1": (200, 400),
    "L2": (400, 800),
    "L3": (400, 800),
    "L4": (400, 800),
}
ADR_LIMITS = (80, 150)

# Domyślnie skanowane ścieżki, względem root.
DEFAULT_SCAN = ["docs"]
DEFAULT_EXTRA_FILES = ["CONTEXT.md", "PRODUCT.md"]
SKIP_PATTERNS = ["*.template.md", "*/node_modules/*", "*/.venv/*", "*/.git/*", "*/.tmp/*"]

INDEX_START = "<!-- KB-INDEX:START -->"
INDEX_END = "<!-- KB-INDEX:END -->"


# --------------------------------------------------------------------------- #
# Model
# --------------------------------------------------------------------------- #


@dataclass
class Diagnostic:
    code: str
    path: str
    message: str
    line: int | None = None

    @property
    def is_error(self) -> bool:
        return self.code.startswith("E")

    def __str__(self) -> str:
        where = f"{self.path}:{self.line}" if self.line else self.path
        return f"{self.code}  {where}  {self.message}"


@dataclass
class Document:
    path: Path
    rel: str
    meta: dict[str, Any]
    body: str
    line_count: int
    headings: list[str] = field(default_factory=list)

    @property
    def doc_id(self) -> str:
        return str(self.meta.get("id", ""))

    @property
    def layer(self) -> str:
        return str(self.meta.get("layer", ""))

    @property
    def status(self) -> str:
        return str(self.meta.get("status", ""))


# --------------------------------------------------------------------------- #
# Parsowanie front-matter (podzbiór YAML: skalary, listy blokowe i inline)
# --------------------------------------------------------------------------- #


def _scalar(raw: str) -> Any:
    raw = raw.strip()
    if raw in ("", "~", "null", "None"):
        return None
    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    return raw


def parse_front_matter(text: str) -> tuple[dict[str, Any] | None, str]:
    """Zwraca (metadane, treść). Metadane None, gdy brak front-matter."""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    raw = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")

    meta: dict[str, Any] = {}
    current_key: str | None = None
    for line in raw.split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("- ") and current_key:
            meta.setdefault(current_key, [])
            if isinstance(meta[current_key], list):
                meta[current_key].append(_scalar(line.lstrip()[2:]))
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        current_key = key
        if value == "":
            meta[key] = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            meta[key] = [_scalar(p) for p in inner.split(",") if p.strip()] if inner else []
        else:
            meta[key] = _scalar(value)
    return meta, body


# --------------------------------------------------------------------------- #
# Pomocnicze
# --------------------------------------------------------------------------- #

FENCE_RE = re.compile(r"```.*?```|~~~.*?~~~|:::mermaid.*?:::", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def strip_blocks(text: str) -> str:
    """Usuwa bloki kodu i komentarze HTML. Kod inline zostaje - nagłówek
    `## 6. Stan — `useCrudPageState`` ma kotwicę zawierającą treść z backticków."""
    return HTML_COMMENT_RE.sub("", FENCE_RE.sub("", text))


def strip_noise(text: str) -> str:
    """Jak strip_blocks, dodatkowo bez kodu inline - do wyszukiwania linków."""
    return INLINE_CODE_RE.sub("", strip_blocks(text))


def slugify(heading: str) -> str:
    """Kotwica w stylu GitHub."""
    s = heading.strip().lower()
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    # Znaki spoza [\w\s-] (emoji, interpunkcja) zostawiają w kotwicy GitHuba
    # końcowe myślniki; porównujemy bez nich, żeby nie generować fałszywych E006.
    return re.sub(r"\s", "-", s.strip()).strip("-")


def parse_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def git_last_commit(root: Path, paths: list[Path]) -> date | None:
    if not paths:
        return None
    args = ["git", "-C", str(root), "log", "-1", "--format=%cI", "--"]
    args += [str(p.relative_to(root)) for p in paths[:400]]
    try:
        out = subprocess.run(args, capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    stamp = out.stdout.strip()
    if not stamp:
        return None
    try:
        return datetime.fromisoformat(stamp).date()
    except ValueError:
        return None


def expand_glob(root: Path, pattern: str) -> list[Path]:
    """Rozwija glob w stylu gita. `src/**` oznacza wszystkie pliki pod src/,
    podczas gdy pathlib dopasowałby tam wyłącznie katalogi - stąd wariant `/*`."""
    pattern = pattern.strip().lstrip("./")
    if not pattern:
        return []
    candidates = [pattern] + ([f"{pattern}/*"] if pattern.endswith("**") else [])
    found: list[Path] = []
    for candidate in candidates:
        try:
            found += [p for p in root.glob(candidate) if p.is_file()]
        except (ValueError, IndexError):
            continue
    return sorted(set(found))


# --------------------------------------------------------------------------- #
# Zbieranie dokumentów
# --------------------------------------------------------------------------- #


def should_skip(rel: str) -> bool:
    return any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(f"/{rel}", pat) for pat in SKIP_PATTERNS)


def collect(root: Path, scan: list[str]) -> list[Path]:
    found: list[Path] = []
    for entry in scan:
        base = root / entry
        if base.is_dir():
            found += sorted(base.rglob("*.md"))
        elif base.is_file():
            found.append(base)
    for name in DEFAULT_EXTRA_FILES:
        p = root / name
        if p.is_file():
            found.append(p)
    seen: set[Path] = set()
    result: list[Path] = []
    for p in found:
        rel = p.relative_to(root).as_posix()
        if p in seen or should_skip(rel):
            continue
        seen.add(p)
        result.append(p)
    return result


def load(root: Path, paths: list[Path]) -> tuple[list[Document], list[Diagnostic]]:
    docs: list[Document] = []
    diags: list[Diagnostic] = []
    for p in paths:
        rel = p.relative_to(root).as_posix()
        try:
            text = p.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError) as exc:
            diags.append(Diagnostic("E001", rel, f"nie można odczytać pliku: {exc}"))
            continue
        meta, body = parse_front_matter(text)
        if meta is None:
            diags.append(Diagnostic("E001", rel, "brak front-matter"))
            meta, body = {}, text
        docs.append(
            Document(
                path=p,
                rel=rel,
                meta=meta,
                body=body,
                line_count=text.count("\n") + 1,
                headings=[slugify(m.group(2)) for m in HEADING_RE.finditer(strip_blocks(text))],
            )
        )
    return docs, diags


# --------------------------------------------------------------------------- #
# Reguły
# --------------------------------------------------------------------------- #


def check_metadata(doc: Document) -> list[Diagnostic]:
    out: list[Diagnostic] = []
    if not doc.meta:
        return out

    for key in REQUIRED_ALWAYS:
        if doc.meta.get(key) in (None, "", []):
            out.append(Diagnostic("E002", doc.rel, f"brak wymaganego pola: {key}"))

    layer = doc.layer
    if layer and layer not in LAYERS:
        out.append(Diagnostic("E003", doc.rel, f"nieznana warstwa: {layer}"))
    else:
        for key in REQUIRED_BY_LAYER.get(layer, []):
            if doc.meta.get(key) in (None, "", []):
                out.append(Diagnostic("E002", doc.rel, f"warstwa {layer} wymaga pola: {key}"))

    if doc.status and doc.status not in STATUSES:
        out.append(Diagnostic("E003", doc.rel, f"nieznany status: {doc.status}"))
    conf = doc.meta.get("confidence")
    if conf and conf not in CONFIDENCES:
        out.append(Diagnostic("E003", doc.rel, f"nieznana wartość confidence: {conf}"))

    for key in DATE_FIELDS:
        value = doc.meta.get(key)
        if value in (None, "", []) or value == "on-change":
            continue
        if parse_date(value) is None:
            out.append(Diagnostic("E010", doc.rel, f"pole {key}: zły format daty ({value}) - wymagane YYYY-MM-DD"))

    if doc.status == "superseded" and not doc.meta.get("superseded_by"):
        out.append(Diagnostic("E009", doc.rel, "status 'superseded' bez pola superseded_by"))

    for key in LIST_FIELDS:
        if key in doc.meta and doc.meta[key] is not None and not isinstance(doc.meta[key], list):
            out.append(Diagnostic("E003", doc.rel, f"pole {key} musi być listą"))
    return out


def check_ids(docs: list[Document]) -> list[Diagnostic]:
    out: list[Diagnostic] = []
    seen: dict[str, str] = {}
    for doc in docs:
        if not doc.doc_id:
            continue
        if doc.doc_id in seen:
            out.append(Diagnostic("E004", doc.rel, f"zduplikowane id '{doc.doc_id}' (już w {seen[doc.doc_id]})"))
        else:
            seen[doc.doc_id] = doc.rel
    known = set(seen)
    for doc in docs:
        refs = as_list(doc.meta.get("related")) + as_list(doc.meta.get("supersedes"))
        if doc.meta.get("superseded_by"):
            refs.append(doc.meta["superseded_by"])
        for ref in refs:
            if ref and str(ref) not in known and not str(ref).startswith("<"):
                out.append(Diagnostic("E007", doc.rel, f"odwołanie do nieistniejącego id: {ref}"))
    return out


def check_links(root: Path, doc: Document, by_path: dict[str, Document]) -> list[Diagnostic]:
    out: list[Diagnostic] = []
    clean = strip_noise(doc.body)
    for match in LINK_RE.finditer(clean):
        target = match.group(1).strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "#", "<")):
            if target.startswith("#"):
                anchor = target[1:].split("#")[0].strip("-")
                if anchor and anchor not in doc.headings:
                    out.append(Diagnostic("E006", doc.rel, f"martwa kotwica wewnętrzna: #{anchor}"))
            continue
        file_part, _, anchor = target.partition("#")
        file_part = file_part.split("?")[0]
        if not file_part:
            continue
        resolved = (doc.path.parent / file_part).resolve()
        if not resolved.exists():
            out.append(Diagnostic("E005", doc.rel, f"martwy link: {target}"))
            continue
        if anchor and resolved.suffix == ".md":
            anchor = anchor.strip("-")
            try:
                rel_target = resolved.relative_to(root).as_posix()
            except ValueError:
                continue
            other = by_path.get(rel_target)
            if other is None:
                continue
            if anchor not in other.headings:
                out.append(Diagnostic("E006", doc.rel, f"martwa kotwica: {target}"))
    return out


def check_size(doc: Document) -> list[Diagnostic]:
    is_adr = "/adr/" in doc.rel or Path(doc.rel).name.startswith(("adr-", "ADR-"))
    soft, hard = ADR_LIMITS if is_adr else SIZE_LIMITS.get(doc.layer, (400, 800))
    if doc.line_count > hard:
        return [Diagnostic("E008", doc.rel, f"{doc.line_count} linii, twardy limit {hard} - dokument do rozbicia")]
    if doc.line_count > soft:
        return [Diagnostic("W104", doc.rel, f"{doc.line_count} linii, miękki limit {soft}")]
    return []


def check_freshness(root: Path, doc: Document, today: date) -> list[Diagnostic]:
    out: list[Diagnostic] = []
    if doc.status in ("archived", "superseded", "draft"):
        return out

    review = doc.meta.get("review_after")
    if review and review != "on-change":
        parsed = parse_date(review)
        if parsed and parsed < today:
            out.append(Diagnostic("W101", doc.rel, f"review_after minęło ({review}) - dokument do przeglądu"))

    expires = parse_date(doc.meta.get("expires"))
    if expires and expires < today:
        out.append(Diagnostic("W106", doc.rel, f"expires minęło ({doc.meta['expires']}) - dokument L3 do archiwizacji"))

    patterns = as_list(doc.meta.get("applies_to"))
    if patterns:
        matched: list[Path] = []
        for pat in patterns:
            if not isinstance(pat, str) or pat.startswith("<"):
                continue
            matched += expand_glob(root, pat)
        if not matched:
            out.append(Diagnostic("W105", doc.rel, f"applies_to nie dopasowuje żadnego pliku: {patterns}"))
        else:
            verified = parse_date(doc.meta.get("verified"))
            last_code = git_last_commit(root, matched)
            if verified and last_code and last_code > verified:
                out.append(
                    Diagnostic(
                        "W102",
                        doc.rel,
                        f"rozjazd doc/kod: kod zmieniony {last_code}, weryfikacja {verified}",
                    )
                )
    if doc.layer == "L2" and not re.search(r"\]\([^)]*\.(py|ts|tsx|cpp|h|hpp|sql|yaml|yml|json)", strip_noise(doc.body)):
        out.append(Diagnostic("W107", doc.rel, "dokument L2 bez żadnego linku do kodu"))
    return out


def check_orphans(root: Path, docs: list[Document], map_path: Path | None) -> list[Diagnostic]:
    if map_path is None or not map_path.exists():
        return []
    text = map_path.read_text(encoding="utf-8-sig")
    referenced: set[str] = set()
    for match in LINK_RE.finditer(text):
        target = match.group(1).split("#")[0].strip()
        if not target or target.startswith(("http", "mailto:", "<")):
            continue
        resolved = (map_path.parent / target).resolve()
        try:
            referenced.add(resolved.relative_to(root).as_posix())
        except ValueError:
            continue
    out: list[Diagnostic] = []
    map_rel = map_path.relative_to(root).as_posix()
    for doc in docs:
        if doc.rel == map_rel or doc.status in ("archived", "superseded"):
            continue
        if doc.rel not in referenced and doc.doc_id not in text:
            out.append(Diagnostic("W103", doc.rel, "sierota - dokument nieosiągalny z mapy wiedzy"))
    return out


# --------------------------------------------------------------------------- #
# Indeks
# --------------------------------------------------------------------------- #


def build_index(root: Path, docs: list[Document], map_path: Path) -> str:
    rows = ["| Dokument | Warstwa | Status | Pewność | Zweryfikowano |", "|---|---|---|---|---|"]
    for doc in sorted(docs, key=lambda d: (d.layer, d.rel)):
        if doc.rel == map_path.relative_to(root).as_posix():
            continue
        try:
            link = Path(doc.rel).relative_to(map_path.parent.relative_to(root)).as_posix()
        except ValueError:
            link = "../" * len(map_path.parent.relative_to(root).parts) + doc.rel
        title = str(doc.meta.get("title", Path(doc.rel).stem)).replace("|", "\\|")
        rows.append(
            f"| [{title}]({link}) | {doc.layer or '—'} | {doc.status or '—'} "
            f"| {doc.meta.get('confidence', '—')} | {doc.meta.get('verified', '—')} |"
        )
    return "\n".join(rows)


def write_index(root: Path, docs: list[Document], map_path: Path) -> bool:
    text = map_path.read_text(encoding="utf-8-sig")
    if INDEX_START not in text or INDEX_END not in text:
        return False
    head, _, rest = text.partition(INDEX_START)
    _, _, tail = rest.partition(INDEX_END)
    generated = build_index(root, docs, map_path)
    map_path.write_text(f"{head}{INDEX_START}\n{generated}\n{INDEX_END}{tail}", encoding="utf-8")
    return True


# --------------------------------------------------------------------------- #
# Metryki
# --------------------------------------------------------------------------- #


def metrics(docs: list[Document], diags: list[Diagnostic]) -> dict[str, Any]:
    codes = [d.code for d in diags]
    l2 = [d for d in docs if d.layer == "L2"]
    l12 = [d for d in docs if d.layer in ("L1", "L2")]
    pct = lambda n, total: round(100 * n / total, 1) if total else 0.0  # noqa: E731
    return {
        "dokumentów": len(docs),
        "błędów": sum(1 for c in codes if c.startswith("E")),
        "ostrzeżeń": sum(1 for c in codes if c.startswith("W")),
        "rozjazd_procent": pct(codes.count("W102"), len(l2)),
        "przeterminowanie_procent": pct(codes.count("W101"), len(l12)),
        "naruszenia_rozmiaru": codes.count("E008") + codes.count("W104"),
        "sieroty": codes.count("W103"),
        "wg_warstwy": {layer: sum(1 for d in docs if d.layer == layer) for layer in sorted(LAYERS)},
    }


# --------------------------------------------------------------------------- #
# Wejście
# --------------------------------------------------------------------------- #


def run(root: Path, scan: list[str], map_rel: str, today: date) -> tuple[list[Document], list[Diagnostic]]:
    paths = collect(root, scan)
    docs, diags = load(root, paths)
    by_path = {d.rel: d for d in docs}

    for doc in docs:
        diags += check_metadata(doc)
        diags += check_links(root, doc, by_path)
        diags += check_size(doc)
        diags += check_freshness(root, doc, today)
    diags += check_ids(docs)

    map_path = root / map_rel
    diags += check_orphans(root, docs, map_path if map_path.exists() else None)
    return docs, diags


def main() -> int:
    parser = argparse.ArgumentParser(description="Walidator bazy wiedzy dla agentów AI")
    parser.add_argument("--root", default=".", help="katalog główny repozytorium")
    parser.add_argument("--scan", nargs="*", default=DEFAULT_SCAN, help="katalogi/pliki do skanowania")
    parser.add_argument("--map", default="docs/00_KNOWLEDGE-MAP.md", help="ścieżka mapy wiedzy")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--strict", action="store_true", help="kod wyjścia 1 przy błędach E*")
    parser.add_argument("--fail-on-warn", action="store_true", help="kod wyjścia 1 także przy ostrzeżeniach W*")
    parser.add_argument("--write-index", action="store_true", help="regeneruj tabelę w mapie wiedzy")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Nie znaleziono katalogu: {root}", file=sys.stderr)
        return 2

    docs, diags = run(root, args.scan, args.map, date.today())
    errors = [d for d in diags if d.is_error]
    warnings = [d for d in diags if not d.is_error]

    if args.write_index:
        map_path = root / args.map
        if not map_path.exists():
            print(f"Brak mapy wiedzy: {args.map}", file=sys.stderr)
        elif write_index(root, docs, map_path):
            print(f"Zaktualizowano indeks w {args.map}")
        else:
            print(f"W {args.map} brak znaczników {INDEX_START} / {INDEX_END}", file=sys.stderr)

    if args.format == "json":
        print(
            json.dumps(
                {
                    "metryki": metrics(docs, diags),
                    "błędy": [{"kod": d.code, "plik": d.path, "opis": d.message} for d in errors],
                    "ostrzeżenia": [{"kod": d.code, "plik": d.path, "opis": d.message} for d in warnings],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for diag in sorted(errors, key=lambda d: (d.path, d.code)):
            print(diag)
        if errors and warnings:
            print()
        for diag in sorted(warnings, key=lambda d: (d.path, d.code)):
            print(diag)
        met = metrics(docs, diags)
        print(
            f"\n{met['dokumentów']} dokumentów · {met['błędów']} błędów · {met['ostrzeżeń']} ostrzeżeń"
            f" · rozjazd {met['rozjazd_procent']}% · przeterminowanie {met['przeterminowanie_procent']}%"
        )

    if args.fail_on_warn and diags:
        return 1
    if args.strict and errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
