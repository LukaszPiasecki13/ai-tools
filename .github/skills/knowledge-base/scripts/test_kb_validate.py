#!/usr/bin/env python3
"""Testy walidatora bazy wiedzy.

Bez zależności zewnętrznych - `python3 -m unittest discover -s <katalog>` albo
`python3 test_kb_validate.py`. Pokrywają reguły, które łatwo "naprawić" w złą
stronę, przede wszystkim zgodność kotwic z zachowaniem GitHuba.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import kb_validate as kb  # noqa: E402

FRONT_MATTER = """---
id: {id}
title: {title}
layer: {layer}
status: active
confidence: fact
owner: t
created: 2026-01-01
verified: {verified}
review_after: {review}
---
"""


def doc(doc_id: str, title: str = "Dokument", layer: str = "L1", verified: str = "2026-01-01", review: str = "2030-01-01") -> str:
    return FRONT_MATTER.format(id=doc_id, title=title, layer=layer, verified=verified, review=review)


class TestSlugify(unittest.TestCase):
    """Kotwice muszą odpowiadać temu, co generuje GitHub i generatory spisów treści."""

    def test_nie_zwija_kolejnych_myslnikow(self) -> None:
        # Regresja: usunięty dwukropek i em-dash zostawiają dwie spacje -> dwa myślniki.
        self.assertEqual(
            kb.slugify("Część 3: Analiza Techniczna — Architektura"),
            "część-3-analiza-techniczna--architektura",
        )
        self.assertEqual(kb.slugify("4.1. Model biznesowy — przychody"), "41-model-biznesowy--przychody")

    def test_zachowuje_tresc_kodu_inline(self) -> None:
        self.assertEqual(kb.slugify("5.3. Wiring — `dependencies.py`"), "53-wiring--dependenciespy")
        self.assertEqual(kb.slugify("4.1. `core`"), "41-core")

    def test_polskie_znaki_zostaja(self) -> None:
        self.assertEqual(kb.slugify("Zależności cykliczne"), "zależności-cykliczne")

    def test_emoji_nie_zostawia_koncowego_myslnika(self) -> None:
        self.assertEqual(kb.slugify("1. Stan wyjściowy (Etapy 1–4) ✅"), "1-stan-wyjściowy-etapy-14")


class TestFrontMatter(unittest.TestCase):
    def test_lista_blokowa_i_inline(self) -> None:
        meta, _ = kb.parse_front_matter("---\na:\n  - x\n  - y\nb: [p, q]\nc: null\n---\ntreść\n")
        assert meta is not None
        self.assertEqual(meta["a"], ["x", "y"])
        self.assertEqual(meta["b"], ["p", "q"])
        self.assertIsNone(meta["c"])

    def test_wartosc_z_dwukropkiem_i_cudzyslowem(self) -> None:
        meta, body = kb.parse_front_matter('---\ntitle: "Moduł: telemetria"\n---\n# Nagłówek\n')
        assert meta is not None
        self.assertEqual(meta["title"], "Moduł: telemetria")
        self.assertTrue(body.startswith("# Nagłówek"))

    def test_brak_front_matter(self) -> None:
        meta, body = kb.parse_front_matter("# Bez metadanych\n")
        self.assertIsNone(meta)
        self.assertEqual(body, "# Bez metadanych\n")


class TestGlob(unittest.TestCase):
    def test_gwiazdka_gwiazdka_lapie_pliki(self) -> None:
        # `src/**` w stylu gita oznacza pliki, nie tylko katalogi.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "mod").mkdir(parents=True)
            (root / "src" / "mod" / "a.py").write_text("x", encoding="utf-8")
            self.assertEqual(len(kb.expand_glob(root, "src/**")), 1)
            self.assertEqual(len(kb.expand_glob(root, "src/**/*.py")), 1)


class TestRegulyNaRepo(unittest.TestCase):
    """Testy end-to-end na tymczasowym repozytorium."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs").mkdir()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True, capture_output=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_validator(self) -> list[kb.Diagnostic]:
        _, diags = kb.run(self.root, ["docs"], "docs/00_KNOWLEDGE-MAP.md", date(2026, 6, 1))
        return diags

    def codes(self) -> list[str]:
        return [d.code for d in self.run_validator()]

    def test_poprawny_dokument_bez_uwag(self) -> None:
        (self.root / "docs" / "a.md").write_text(doc("a") + "# A\n", encoding="utf-8")
        self.assertEqual(self.codes(), [])

    def test_brak_front_matter(self) -> None:
        (self.root / "docs" / "a.md").write_text("# A\n", encoding="utf-8")
        self.assertIn("E001", self.codes())

    def test_martwy_link_i_zywa_kotwica(self) -> None:
        (self.root / "docs" / "a.md").write_text(
            doc("a") + "# A\n## Sekcja B\n[żywa](#sekcja-b) [martwa](./brak.md)\n", encoding="utf-8"
        )
        codes = self.codes()
        self.assertIn("E005", codes)
        self.assertNotIn("E006", codes)

    def test_link_w_bloku_kodu_ignorowany(self) -> None:
        (self.root / "docs" / "a.md").write_text(
            doc("a") + "# A\n```md\n[przykład](./nie-istnieje.md)\n```\n", encoding="utf-8"
        )
        self.assertNotIn("E005", self.codes())

    def test_duplikat_id(self) -> None:
        (self.root / "docs" / "a.md").write_text(doc("x") + "# A\n", encoding="utf-8")
        (self.root / "docs" / "b.md").write_text(doc("x") + "# B\n", encoding="utf-8")
        self.assertIn("E004", self.codes())

    def test_superseded_bez_nastepcy(self) -> None:
        (self.root / "docs" / "a.md").write_text(
            doc("a").replace("status: active", "status: superseded") + "# A\n", encoding="utf-8"
        )
        self.assertIn("E009", self.codes())

    def test_przeterminowanie_to_ostrzezenie(self) -> None:
        (self.root / "docs" / "a.md").write_text(doc("a", review="2026-01-01") + "# A\n", encoding="utf-8")
        codes = self.codes()
        self.assertIn("W101", codes)
        self.assertFalse([c for c in codes if c.startswith("E")])

    def test_twardy_limit_rozmiaru(self) -> None:
        (self.root / "docs" / "a.md").write_text(doc("a") + "# A\n" + "x\n" * 900, encoding="utf-8")
        self.assertIn("E008", self.codes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
