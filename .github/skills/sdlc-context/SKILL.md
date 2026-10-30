---
name: sdlc-context
description: "Etap 1 z 3 pipeline SDLC (orkiestrator: sdlc-run): zbiera kontekst repo (mapa plików, ADR, konwencje, ryzyka), proponuje tier trivial/standard/full i prowadzi dialog pytanie po pytaniu, który kończy się zamrożonymi decyzjami DEC i kryteriami AC. Nie pisze planu ani kodu. Use when the user says \\\"sdlc context\\\", \\\"zbierz kontekst\\\", \\\"ustal wymagania\\\", \\\"przygotuj kontekst zadania\\\", or when sdlc-run routes here; follow with sdlc-plan."
---

<!-- GENERATED FILE - DO NOT EDIT.
     Source: skills/sdlc-context/SKILL.md
     Regenerate: python scripts/sync_copilot.py -->

# SDLC Context

Etap 1 z 3 (kolejny: `sdlc-plan`; całość prowadzi `sdlc-run`). Przed startem przeczytaj wspólny kontrakt
[contract.md](../sdlc-run/contract.md): przepływ, artefakty, manifest `_context.md`, tiery,
triggery ryzyka, tabela subagentów (ID `C-1`..`C-3`) i zasady wspólne. Ten plik opisuje tylko
procedurę etapu 1.

- **Wejście:** opis zadania, plik z opisem albo istniejący `{task_dir}` (wznowienie lub odświeżenie).
- **Wynik:** `00-problem.md`, `01-context.md`, `02-requirements.md`, manifest `_context.md`
  z `context_status: accepted`.
- **Czego nie robi:** nie pisze planu ani kodu i nie zmienia repo docelowego poza `{task_dir}`.

## Zasady etapu

1. **Fakty ustalasz sam, pytasz tylko o decyzje.** Repo, ADR i konwencje sprawdzasz narzędziami;
   user dostaje pytanie dopiero, gdy odpowiedź zależy od jego intencji.
2. **Dialog prowadzi główny wątek** (ten agent), nie subagent.
3. **Zasady wspólne** (dane a nie instrukcje, git tylko do odczytu, ścieżki bezwzględne, subagenci
   jednorazowi, szkielet promptu, mapowanie hosta): [contract.md](../sdlc-run/contract.md),
   sekcja 7. Reguły repo docelowego (`CLAUDE.md`) są nadrzędne wobec tego skilla.
4. **Artefaktów nie kasujesz** i nie nadpisujesz: przy wznowieniu scalasz zmiany.

## Krok 0 - Intake (sam)

1. Ustal problem (tekst i/lub wskazany plik). Brak konkretów: jedno dopytanie.
2. Ustal `{repo_root}`, `{slug}` i `{run_id}` (zmienne: contract, sekcja 2). Dalej:
   - user wskazał istniejący `{task_dir}`: przejdź do sekcji "Wznowienie i odświeżenie";
   - nowy przebieg: wygeneruj nowy `{run_id}`; jeśli taki `{task_dir}` już istnieje, STOP i wybierz
     nowe ID.
3. **Szybka kwalifikacja trivial** (maks. 3 wywołania grep/glob, bez subagenta; kryteria:
   contract, sekcja 5). Jeśli zadanie **oczywiście** spełnia kryteria `trivial`, zarekomenduj
   bezpośrednią implementację i zapytaj o potwierdzenie. Potwierdzone: koniec, bez tworzenia katalogu.
   User odrzuca albo masz jakąkolwiek wątpliwość: idź dalej do pkt 4.
4. Preflight:
   - dostęp do narzędzia subagentów (typy `general-purpose` i `Explore`) oraz do narzędzia pytań
     hosta; brak subagentów = STOP z opisem naprawy, bez fallbacku;
   - Python 3 dostępny w powłoce (skrypty `drift_check.py` i `plan_lint.py`); brak = STOP z opisem
     naprawy;
   - `.tmp/` jest w `.gitignore` repo **przed** utworzeniem `{task_dir}`; jeśli nie, zapytaj usera,
     nie edytuj `.gitignore` sam.
5. Utwórz `{task_dir}`, zapisz `00-problem.md` (pełny opis + `{repo_root}`) i `_context.md` według
   szablonu z contract, sekcja 4 (`tier: unconfirmed`, `ui: unknown`, `context_status: draft`,
   `plan_status: not-started`, `implementation_status: not-started`, rozwiązane `{rules_dirs}` albo
   ostrzeżenie).

## Wznowienie i odświeżenie (gdy podano istniejący `{task_dir}`)

Przeczytaj `_context.md` i wybierz wiersz; nie nadpisuj artefaktów.

| Stan | Akcja |
|---|---|
| `context_status: draft`, brak `01-context.md` | Krok 1 |
| `context_status: draft`, jest `01-context.md`, brak `02-requirements.md` | Krok 2 |
| `context_status: draft`, jest `02-requirements.md` | Gate C |
| `context_status: accepted` i user prosi o odświeżenie (np. po driftcie z `sdlc-plan`) | ustaw `context_status: draft`; pogłębienie `C-2` zmienionych plików (lista z różnic driftu); Krok 2 tylko dla decyzji dotkniętych zmianą; Gate C z nowym snapshotem |
| `context_status: accepted` bez prośby o odświeżenie | nic do zrobienia; wskaż `sdlc-plan {task_dir}` |

## Krok 1 - Discovery (`C-1`: jedno wywołanie, Haiku, cel około 20 tur)

Jedyny krok z prawem szerokiej eksploracji repo, ale tylko w granicach zadania. Model, typ i cel tur:
contract, sekcja 6. Output: `{task_dir}/01-context.md`, **limit około 300 linii**.

Zadanie subagenta:

1. Przeskanuj katalogi ADR (`docs/adr/`, `docs/*/adr/`, `docs/*/bdr/`, `docs/decisions/`). Przeczytaj
   w całości każdy ADR o statusie `Accepted`, który dotyczy modułów z mapy plików. Wpisz do pliku
   tylko ADR dotyczące zadania; pozostałe wymień jednym wierszem „pominięte: numery”.
2. Znajdź istniejący punkt wpięcia, kod do reużycia, testy dotkniętych modułów i dokumenty
   architektury. Zapisz tylko **konwencje niewynikające z kodu** (non-standard practices) z ścieżką
   źródła; nie kopiuj `CLAUDE.md` ani opisu struktury repo.
3. Rozstrzygnij flagę UI oraz triggery ryzyka (tabela: contract, sekcja 5), każdy z dowodem
   (plik/ADR) albo „nie”. Zaproponuj tier według kryteriów z contract, sekcja 5.
4. Ustal **komendy weryfikacji** repo: format/lint, typecheck, testy unit, testy integracyjne, E2E,
   a przy `ui: true` także URL aplikacji, komendę startu i sposób logowania. Źródła w kolejności:
   `CLAUDE.md`/`AGENTS.md`, workflow CI, manifesty (`pyproject.toml`, `package.json` scripts,
   `Makefile`, `*.csproj` itp.), README. Każda komenda ma źródło; nie zgadujesz. Brak źródła = wiersz
   z wartością `brak` (to także informacja dla planu i implementacji).

Struktura `01-context.md` (nagłówki obowiązkowe, nic poza nimi):

```markdown
# Kontekst: {slug}
tier_proposal: trivial|standard|full - uzasadnienie w jednym zdaniu
ui: true|false
## Mapa plików
| Ścieżka (bezwzględna) | Rola w zadaniu | Etap (plan/impl/test) |
## ADR
| Numer/ścieżka | Status | Decyzja (1 zdanie) |
pominięte: ...
## Konwencje niewynikające z kodu
- reguła - źródło
## Ryzyka i luki
- ...
## Triggery ryzyka
- trigger: tak|nie - dowód
## Komendy weryfikacji
| Cel | Komenda | Zakres (cały repo / ścieżka) | Źródło |
|---|---|---|---|
| lint | ... | ... | plik |
| typecheck | ... | ... | plik |
| test-unit | ... | ... | plik |
| test-integration | ... | ... | plik |
| e2e | ... albo brak | ... | plik |
| app (tylko ui: true) | URL; komenda startu; logowanie | ... | plik |
## Fakty do ustalenia w dialogu
- ...
```

Zakazane w `01-context.md`: przegląd repo, kopie `CLAUDE.md`, rekomendacje projektowe, kod.
Plik ma być dokładnym wejściem dla dialogu i planu, nie raportem z eksploracji.

**Pogłębienie (`C-2`, cel około 10 tur)** uruchamiasz **tylko na prośbę usera** (zgłoszoną w dialogu
lub w Gate C) albo przy odświeżeniu po driftcie. To nowe wywołanie z listą konkretnych luk lub
zmienionych plików; scala fakty do `01-context.md` bez przekraczania limitu.

## Krok 2 - Dialog (sam, pytanie po pytaniu)

Nie deleguj dialogu. Delegować wolno tylko krótki read-only fact-check (`C-3`: świeży `Explore`,
Haiku, cel około 8 tur, zwraca fakt i źródło, maks. 100 słów).

1. **Potwierdzenie tieru (jedyne w całym przepływie).** Przedstaw jednym zdaniem zaproponowany tier
   z uzasadnieniem i poproś o decyzję: zatwierdź albo zmień. Gate C pokazuje już potwierdzoną
   wartość i o tier nie pyta. Wybór `trivial` w tym miejscu: zasady w contract, sekcja 5
   ("Zmiana tieru po utworzeniu `{task_dir}`"), koniec etapu.
2. Zadawaj decyzje **po jednej**, bez limitu liczby, w kolejności od najbardziej wpływającej na
   resztę. Każde pytanie zawiera fakt z repo, rekomendację i konsekwencję alternatywy; użyj narzędzia
   pytań hosta (`AskUserQuestion` w Claude Code) z opcjami, jeśli decyzja ma skończony zbiór.
3. Nie pytaj o to, co ustalisz z repo lub `01-context.md`; nie powtarzaj zamkniętych decyzji.
4. Decyzja sprzeczna z `Accepted` ADR to jawny punkt do rozstrzygnięcia przez usera, nie ciche
   obejście.
5. Zapisz `02-requirements.md`: `DEC-NN` z uzasadnieniem (nie transkrypt) i `AC-NN` z perspektywy
   usera, każde weryfikowalne obserwacją. Każda pozycja zaczyna się od identyfikatora w osobnej
   linii (`- DEC-01: ...`, `- AC-01: ...`); `plan_lint.py` odczytuje je z początku linii.

## Gate C - akceptacja pakietu kontekstu (blokująca, jedyna w tym skillu)

Pokaż: potwierdzony tier, liczbę plików z mapy, triggery ryzyka, flagę UI, komendy weryfikacji
(wiersze `brak` wyraźnie), listę `DEC`/`AC`, otwarte punkty. Jeśli `ui: true`, sprawdź, że skill
`ui-verify` jest dostępny, a wiersz `app` ma URL i komendę startu; brak = zgłoś przed akceptacją.
Zapytaj o jedną decyzję: **akceptuj pakiet** albo **wróć** (do dialogu lub pogłębienia).

Po jawnej akceptacji wykonaj po kolei (status `accepted` zapisujesz **na końcu**, więc przerwanie w
trakcie zostawia `draft`, a nie zaakceptowany kontekst bez snapshotu):

1. W `_context.md` ustaw `tier` (potwierdzony) i `ui`.
2. Zapisz `Drift snapshot`:
   `python "{drift_check}" "{task_dir}" snapshot` (`{drift_check}`: contract, sekcja 2; format i kody
   wyjścia: contract, sekcja 4). Kod `2` = STOP i pokaż komunikat.
3. Uzupełnij w `Plan metrics` klucze `context_*` z tabeli w contract, sekcja 4 (nieznane wartości:
   `unknown`). Poproś o opcjonalne wklejenie kosztu z `/usage` (`tokens_usd`; zasady: contract,
   sekcja 4).
4. Ustaw `context_status: accepted`.
5. Poinformuj: kolejny krok to `sdlc-plan {task_dir}`; można go zacząć w czystym kontekście
   (`/clear`), bo cały stan jest w plikach.

Bez jawnej akceptacji nie ustawiaj `context_status: accepted`.
