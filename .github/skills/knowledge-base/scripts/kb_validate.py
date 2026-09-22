#!/usr/bin/env python3
"""Walidator bazy wiedzy dla agentów AI.

Sprawdza strukturę, metadane, linki, rozmiary i rozjazd doc<->kod w bazie
wiedzy zbudowanej wg skilla `knowledge-base`.

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

STATUSES = {"current", "draft"}
TYPES = {"fact", "decision", "reference", "mixed"}

REQUIRED_ALWAYS = ["id", "status", "type", "scope", "last_reviewed"]

DATE_FIELDS = ["last_reviewed"]
LIST_FIELDS = {"applies_to"}

# (miękki, twardy) limit linii dla dokumentów spoza ADR.
SIZE_LIMIT: tuple[int, int] = (400, 800)
ADR_LIMITS = (80, 150)

# Ile miesięcy od `last_reviewed` dokument liczy się jako świeży (status: current).
DEFAULT_REVIEW_MONTHS = 6

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
    title: str = ""
    headings: list[str] = field(default_factory=list)

    @property
    def doc_id(self) -> str:
        return str(self.meta.get("id", ""))

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
    """Kotwica w stylu GitHub.

    UWAGA: GitHub NIE zwija kolejnych myślników. Nagłówek `Część 3: Analiza — Architektura`
    ma kotwicę `#część-3-analiza--architektura` z podwójnym myślnikiem, bo usunięty
    dwukropek i em-dash zostawiają po sobie dwie spacje. Dodanie tu `re.sub(r"-+", "-", s)`
    wygląda na sprzątanie, a jest regresją: zrywa każdą kotwicę wygenerowaną przez
    standardowe generatory spisu treści. Pokrywa to `test_kb_validate.py`.
    """
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


def add_months(d: date, months: int) -> date:
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    if month == 2:
        leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        max_day = 29 if leap else 28
    elif month in (4, 6, 9, 11):
        max_day = 30
    else:
        max_day = 31
    return date(year, month, min(d.day, max_day))


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


def should_skip(rel: str, exclude: tuple[str, ...] = ()) -> bool:
    return any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(f"/{rel}", pat) for pat in (*SKIP_PATTERNS, *exclude))


def collect(root: Path, scan: list[str], exclude: tuple[str, ...] = ()) -> list[Path]:
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
        if p in seen or should_skip(rel, exclude):
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
        stripped = strip_blocks(text)
        # title nie jest już polem front-matter - pierwszy H1, potem nazwa pliku.
        h1 = next((m.group(2) for m in HEADING_RE.finditer(stripped) if m.group(1) == "#"), None)
        docs.append(
            Document(
                path=p,
                rel=rel,
                meta=meta,
                body=body,
                line_count=text.count("\n") + 1,
                title=str(meta.get("title") or h1 or Path(rel).stem),
                headings=[slugify(m.group(2)) for m in HEADING_RE.finditer(stripped)],
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

    if doc.status and doc.status not in STATUSES:
        out.append(Diagnostic("E003", doc.rel, f"nieznany status: {doc.status}"))

    doc_type = doc.meta.get("type")
    if doc_type and doc_type not in TYPES:
        out.append(Diagnostic("E003", doc.rel, f"nieznana wartość type: {doc_type}"))

    for key in DATE_FIELDS:
        value = doc.meta.get(key)
        if value in (None, "", []) or value == "on-change":
            continue
        if parse_date(value) is None:
            out.append(Diagnostic("E010", doc.rel, f"pole {key}: zły format daty ({value}) - wymagane YYYY-MM-DD"))

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
    soft, hard = ADR_LIMITS if is_adr else SIZE_LIMIT
    if doc.line_count > hard:
        return [Diagnostic("E008", doc.rel, f"{doc.line_count} linii, twardy limit {hard} - dokument do rozbicia")]
    if doc.line_count > soft:
        return [Diagnostic("W104", doc.rel, f"{doc.line_count} linii, miękki limit {soft}")]
    return []


def check_freshness(root: Path, doc: Document, today: date) -> list[Diagnostic]:
    out: list[Diagnostic] = []
    if doc.status == "draft":
        return out

    last_reviewed = parse_date(doc.meta.get("last_reviewed"))
    if last_reviewed:
        deadline = add_months(last_reviewed, DEFAULT_REVIEW_MONTHS)
        if deadline < today:
            out.append(
                Diagnostic(
                    "W101",
                    doc.rel,
                    f"last_reviewed {last_reviewed} + {DEFAULT_REVIEW_MONTHS} mies. minęło - dokument do przeglądu",
                )
            )

    patterns = as_list(doc.meta.get("applies_to"))
    if patterns:
        matched: list[Path] = []
        for pat in patterns:
            if not isinstance(pat, str) or pat.startswith("<"):
                continue
            matched += expand_glob(root, pat)
        if not matched:
            out.append(Diagnostic("W105", doc.rel, f"applies_to nie dopasowuje żadnego pliku: {patterns}"))
        elif last_reviewed:
            last_code = git_last_commit(root, matched)
            if last_code and last_code > last_reviewed:
                out.append(
                    Diagnostic(
                        "W102",
                        doc.rel,
                        f"rozjazd doc/kod: kod zmieniony {last_code}, ostatni przegląd {last_reviewed}",
                    )
                )
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
        if doc.rel == map_rel:
            continue
        if doc.rel not in referenced and doc.doc_id not in text:
            out.append(Diagnostic("W103", doc.rel, "sierota - dokument nieosiągalny z mapy wiedzy"))
    return out


# --------------------------------------------------------------------------- #
# Indeks
# --------------------------------------------------------------------------- #


def build_index(root: Path, docs: list[Document], map_path: Path) -> str:
    rows = ["| Dokument | Typ | Status | Zakres | Ostatni przegląd |", "|---|---|---|---|---|"]
    map_rel = map_path.relative_to(root).as_posix()
    for doc in sorted(docs, key=lambda d: (str(d.meta.get("type", "")), d.rel)):
        if doc.rel == map_rel:
            continue
        try:
            link = Path(doc.rel).relative_to(map_path.parent.relative_to(root)).as_posix()
        except ValueError:
            link = "../" * len(map_path.parent.relative_to(root).parts) + doc.rel
        title = doc.title.replace("|", "\\|")
        rows.append(
            f"| [{title}]({link}) | {doc.meta.get('type', '—')} | {doc.status or '—'} "
            f"| {doc.meta.get('scope', '—')} | {doc.meta.get('last_reviewed', '—')} |"
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
    with_applies_to = [d for d in docs if as_list(d.meta.get("applies_to"))]
    current = [d for d in docs if d.status == "current"]

    def pct(n: int, total: int) -> float:
        return round(100 * n / total, 1) if total else 0.0

    return {
        "dokumentów": len(docs),
        "błędów": sum(1 for c in codes if c.startswith("E")),
        "ostrzeżeń": sum(1 for c in codes if c.startswith("W")),
        "rozjazd_procent": pct(codes.count("W102"), len(with_applies_to)),
        "przeterminowanie_procent": pct(codes.count("W101"), len(current)),
        "naruszenia_rozmiaru": codes.count("E008") + codes.count("W104"),
        "sieroty": codes.count("W103"),
        "wg_statusu": {s: sum(1 for d in docs if d.status == s) for s in sorted(STATUSES)},
        "wg_typu": {t: sum(1 for d in docs if d.meta.get("type") == t) for t in sorted(TYPES)},
    }


# --------------------------------------------------------------------------- #
# Wejście
# --------------------------------------------------------------------------- #


def run(
    root: Path, scan: list[str], map_rel: str, today: date, exclude: tuple[str, ...] = ()
) -> tuple[list[Document], list[Diagnostic]]:
    paths = collect(root, scan, exclude)
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
    parser.add_argument(
        "--exclude", nargs="*", default=[], metavar="GLOB",
        help="dodatkowe wzorce ścieżek (względem --root) pomijane przy skanowaniu, np. docs/notes.md",
    )
    parser.add_argument("--map", default="docs/00_KNOWLEDGE-MAP.md", help="ścieżka mapy wiedzy")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--strict", action="store_true", help="kod wyjścia 1 przy błędach E*")
    parser.add_argument("--fail-on-warn", action="store_true", help="kod wyjścia 1 także przy ostrzeżeniach W*")
    parser.add_argument("--write-index", action="store_true", help="regeneruj tabelę w mapie wiedzy")
    args = parser.parse_args()

    # Komunikaty zawierają polskie znaki; domyślne kodowanie konsoli Windows (cp1252) się na nich wywraca.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Nie znaleziono katalogu: {root}", file=sys.stderr)
        return 2

    docs, diags = run(root, args.scan, args.map, date.today(), tuple(args.exclude))
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
