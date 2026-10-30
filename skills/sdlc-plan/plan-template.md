# Plan: {slug}

<!-- Tabele czyta maszynowo scripts/plan_lint.py: zachowaj nazwy kolumn, formaty ID
     (DEC-NN, AC-NN, S1..Sn) i dozwolone wartości Action/Status. Treść poza tabelami jest wolna.
     Tryb A/B (SKILL.md): sekcja A = Projekt + Mapa plików; sekcja B = pozostałe sekcje "###". -->

## Stan aktualny

### Projekt

Przepływ danych lub UX w kilku zdaniach. Zgodność z ADR: numer/ścieżka i status każdego
`Accepted` ADR z `01-context.md`, którego dotyczy decyzja, albo jawnie "brak zastosowania".
Odrzucone warianty opisuj tylko wtedy, gdy zmieniają decyzję.

### Mapa plików

Ścieżki względem `{repo_root}` (przy wielu repo: bezwzględne). `Action`: NEW | MODIFY | DELETE.
`Anchor`: klasa/funkcja/sekcja pliku, nigdy numer linii.

| Path | Action | Anchor | DEC/AC |
|---|---|---|---|
| src/foo/service.py | MODIFY | `FooService.run` | DEC-01, AC-01 |
| src/foo/report.py | NEW | - | DEC-02, AC-02 |

### Interfejsy

Tylko symbole, które implementer musi znać dokładnie i których nie wywnioskuje z kodu.
`Status`: NEW | EXISTING | CHANGED. Sygnatury zweryfikowane w repo.

| File | Symbol | Signature | Status |
|---|---|---|---|
| src/foo/service.py | FooService.run | `def run(self, limit: int) -> Result` | CHANGED |
| src/foo/report.py | build_report | `def build_report(rows: list[Row]) -> str` | NEW |

### Kroki

ID `S1`, `S2`, ... w kolejności wykonania. `DEC`/`AC` muszą zgadzać się z macierzami w `Śledzenie`.
`Bramka`: najtańsza komenda potwierdzająca krok, zawężona z `Komendy weryfikacji` w `01-context.md`.

| Step | Opis | DEC | AC | Bramka |
|---|---|---|---|---|
| S1 | Dodaj parametr `limit` | DEC-01 | AC-01 | `pytest tests/unit/test_service.py` |
| S2 | Dodaj moduł raportu | DEC-02 | AC-02 | `pytest tests/unit/test_report.py` |

### Testy

Każdy test wskazany w kolumnie `Test` macierzy `AC` musi mieć tu wiersz (lint to sprawdza).
Komendy uruchomienia pochodzą z sekcji `Komendy weryfikacji` w `01-context.md`.

| Test | AC | Wejście | Oczekiwany wynik | Przypadki brzegowe |
|---|---|---|---|---|
| test_run_respects_limit | AC-01 | 100 wierszy, limit 10 | 10 wierszy | limit 0, limit > liczba wierszy |
| test_build_report | AC-02 | 2 wiersze | raport z 2 pozycjami | pusta lista |

### E2E

Tylko gdy `ui: true`: checklista obserwowalnych kroków użytkownika z oczekiwanym rezultatem
każdego. Inaczej: `E2E: n.d.`.

### Śledzenie

Każdy `DEC`/`AC` z `02-requirements.md` musi mieć wiersz; kroki wymieniaj jawnie (bez zakresów).
`Test`/`E2E` może być `n.d.`, ale nie oba naraz.

| DEC | Step |
|---|---|
| DEC-01 | S1 |
| DEC-02 | S2 |

| AC | Step | Test | E2E |
|---|---|---|---|
| AC-01 | S1 | test_run_respects_limit | n.d. |
| AC-02 | S2 | test_build_report | n.d. |

### Dokumentacja

Najmniejsza wymagana aktualizacja dokumentacji albo "brak".

## Otwarte punkty

- [OPEN|RESOLVED|ACCEPTED-BY-USER] [blocker|major|minor] id: fakt + rekomendacja + konsekwencja
  alternatywy

## Historia

### Runda 1 - {data}
Krótko: co zapisano i co zmieniło status.
