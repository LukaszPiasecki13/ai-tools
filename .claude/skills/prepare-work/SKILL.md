---
name: prepare-work
description: Full analyze -> grill -> plan -> independent-review -> implement -> test -> independent-review -> E2E -> docs pipeline for a development task (feature or bug), delegating each phase to a fresh, isolated subagent with human gates between phases. Use when the user says "/prepare-work {description}", "przygotuj i zaimplementuj {opis}", "zrób to end-to-end z review'ami", or asks for a self-contained, rigorously reviewed multi-phase implementation without going through Azure DevOps.
---

# Prepare Work — Analiza -> Grill -> Plan -> Review -> Implementacja -> Testy -> Review -> E2E -> Docs

Ty (orkiestrator) **nie robisz** ciężkiej pracy sam. Na każdą fazę wywołujesz świeżego subagenta (`Agent` tool, `run_in_background: false`, chyba że zaznaczono inaczej) z w pełni samodzielnym promptem — subagent nie widzi tej rozmowy. Ty pilnujesz bramek, relacjonujesz userowi krótkie podsumowania, prowadzisz sesję pytań osobiście (grill-me wymaga żywego dialogu) i egzekwujesz zasady poniżej.

**Niezależność review.** Agent który recenzuje plan/kod nigdy nie może być tym samym uruchomieniem co agent który go napisał — zawsze osobny `Agent` call. W rundach 2-3 tej samej recenzji wolno kontynuować TEGO SAMEGO reviewera przez `SendMessage` (ma kontekst poprzednich zastrzeżeń), ale nigdy tego samego co autor.

## Alokacja modeli Claude (cost-optimized)

| Faza | Model | Uwagi |
|------|-------|-------|
| **0** | Ty (brak AI) | Setup, pytania intake |
| **1** | Claude Haiku 4.5 | Tania analiza, read-heavy |
| **2** | Ty (Skill: grill-me) | Żywy dialog, bez modelu |
| **3** | Claude Sonnet 5 | Plan ogólny wymaga syntezy |
| **4** | Sonnet R1 → **Haiku+ R2-3** | R1 Sonnet tworzy plan, R2+ Haiku z fallback do Sonnet jeśli powierzchowny |
| **5** | Claude Sonnet 5 | Plan szczegółowy (kod, importy) |
| **6** | **Haiku+ fallback Sonnet** | Review szczegółu; jeśli output powierzchowny → Sonnet |
| **7** | Ty (brak AI) | Pytanie: czy implementować? |
| **8** | **Haiku+ fallback Sonnet** | Implementacja; fallback jeśli kod nie przechodzi bramki |
| **9** | **Haiku+ fallback Sonnet** | Testy; fallback jeśli diagnoza niewystarczająca |
| **10** | Claude Sonnet 5 | Review implementacji |
| **11** | Claude Haiku 4.5 | E2E (ui-verify) |
| **12** | Claude Haiku 4.5 | Update dokumentacji |

**"Haiku+ fallback Sonnet"** — Haiku startuje, ale jeśli output jest powierzchowny/niepełny/kod nie przechodzi bramki, ty (orkiestrator) wznowiasz fazę z Sonnet zamiast akceptować niedostateczny rezultat.

---

## Zasady nadrzędne (wklejaj do KAŻDEGO promptu subagenta)

1. **Plan to hipoteza, nie fakt.** Każda faza weryfikuje założenia poprzedniej fazy względem aktualnego stanu repo (grep/read), zanim na nich zadziała.
2. **Absolutne ścieżki** przy wyszukiwaniu plików (Glob/file_search) — to środowisko nie przeszukuje poprawnie ścieżek względnych poza cwd, zwłaszcza przy wielu working directories.
3. **"Nie znaleziono" wbrew założeniu = STOP, nie rozszerzanie zakresu.** Jeśli coś co plan/analiza zakłada nie potwierdza się w repo — subagent zatrzymuje się i zgłasza rozbieżność w raporcie, nie buduje tego domyślnie od zera.
4. **Zero komend git zmieniających stan** (`commit`, `push`, `reset`, `rebase`...). Wolno: `git status`/`git diff`/`git log` (read-only).
5. **Read przed Edit, zawsze.** Nie ufaj numerom linii/fragmentom kodu z dokumentów planu — czytaj bieżący plik tuż przed edycją.
6. **Weryfikuj sygnatury przed użyciem** — grep w repo, nie zgaduj.
7. **Sprawdź `CLAUDE.md`/`AGENTS.md`/`copilot-instructions.md` repo docelowego** — krytyczne zasady projektowe (np. `.venv`, migracje tylko przez `alembic revision`, zakaz commitów) są nadrzędne wobec ogólnych instrukcji tego skilla.
8. **Wiedza architektoniczna z ai-tools jest obowiązkowa dla faz: plan szczegółowy, review planu/kodu, implementacja, review implementacji.** `ai-tools` to osobny working directory pod `D:\dev\WebApps\ai-tools` — subagent ma do niego dostęp przez bezwzględne ścieżki, niezależnie w jakim repo pracuje. Subagent MUSI przeczytać (Read, bezwzględna ścieżka):
   - zawsze: `D:\dev\WebApps\ai-tools\.claude\rules\architecture-decisions.md`, `security-checklist.md`, `error-handling-patterns.md`
   - odpowiednio do typów dotykanych plików: `python-coding-standards.md` (`*.py`), `frontend-coding-standards.md` (`*.ts`/`*.tsx`/`*.html`/`*.scss`), `powershell-coding-standards.md` (`*.ps1`), `cpp-embedded-coding-standards.md` (`*.cpp`/`*.h`/`*.ino`)
   - dokumentację architektury/ADR **repo docelowego** wskazaną w `01-analysis.md`
   Te reguły są nadrzędne dla jakości kodu i decyzji projektowych w tych czterech fazach.
9. **Nigdy nie dotykaj współdzielonych/żywych zasobów bez rekonesansu** (Faza E2E) — sprawdź `.env`/config przed zapisem, nie zabijaj cudzych procesów, sprzątaj po testowych mutacjach.
10. **Nigdy nie usuwaj ani nie nadpisuj plików w `.tmp/tasks/{slug}/`.** To trwały zapis pracy (do późniejszej analizy, audytu, wznowienia zadania), nie katalog roboczy do sprzątnięcia po zakończeniu — mimo nazwy `.tmp`. Dotyczy to wyłącznie tych dokumentów; "sprzątaj po testowych mutacjach" w zasadzie 9 odnosi się do danych testowych w bazie/UI podczas E2E, nie do artefaktów pipeline'u. Każda faza, która poprawia wcześniejszy dokument (np. po review), **dopisuje** nową sekcję/rundę zamiast kasować poprzednią treść.

## Artefakty

Wszystko w `{repo_root}/.tmp/tasks/{slug}/` — **nigdy nie usuwać, nawet po zakończeniu pipeline'u.**

```
00-problem.md                 # Faza 0 — opis zadania
01-analysis.md                 # Faza 1 — inwentaryzacja kodu
02-requirements.md             # Faza 2 — ustalenia z sesji grill-me
03-plan-overview.md            # Faza 3 — plan ogólny
04-review-overview.md          # Faza 4 — review planu ogólnego (2-3 rundy)
05-plan-detailed.md            # Faza 5 — plan szczegółowy (kod, importy, scenariusze testów)
06-review-detailed.md          # Faza 6 — review planu szczegółowego
07-implementation-log.md       # Faza 8 — log implementacji
08-test-report.md              # Faza 9 — testy jednostkowe/integracyjne + regresja
09-review-implementation.md    # Faza 10 — review kodu
10-e2e-report.md                # Faza 11 — E2E przez ui-verify
11-documentation-update.md      # Faza 12 — aktualizacja dokumentacji
```

Sprawdź czy `.tmp/` jest w `.gitignore` repo docelowego; jeśli nie — zasygnalizuj userowi (nie dodawaj sam bez pytania).

---

## Step 0: Intake

1. Ustal opis problemu (tekst w promptcie i/lub wskazany plik — połącz jeśli oba). Brak konkretów -> jedno dopytanie.
2. Ustal `{repo_root}` (bezwzględna ścieżka) i `{slug}` (kebab-case).
3. Utwórz `.tmp/tasks/{slug}/00-problem.md` z pełnym opisem + `{repo_root}`.
4. Potwierdź z userem start Fazy 1.

## Step 1: Faza 1 — Analiza kodu (subagent, `general-purpose`, model: **Claude Haiku 4.5**)

Ten sam wzorzec co inwentaryzacja: co istnieje / czego brak / co reużywalne / powiązana dokumentacja projektu. Prompt musi zawierać pełną treść `00-problem.md`, instrukcję o bezwzględnych ścieżkach, sprawdzenie `CLAUDE.md`/`AGENTS.md` repo docelowego, i polecenie znalezienia **wszystkich** dokumentów architektury/ADR repo docelowego (będą potrzebne w dalszych fazach).

**Wywołanie subagenta:** `Agent(description="Faza 1 - analiza kodu", prompt="{...}", subagent_type="general-purpose", model="claude-haiku-4-5-20251001", run_in_background=false)`

Output: `01-analysis.md` (tabela co istnieje / czego brak / reużywalne / dokumentacja / ryzyka) + krótkie podsumowanie w odpowiedzi (max 200 słów).

### Gate 1
Streść userowi analizę (2-4 zdania). Pytanie: kontynuować do sesji pytań, czy pogłębić analizę (kontynuacja tego samego subagenta przez `SendMessage`)?

## Step 2: Faza 2 — Sesja pytań (grill-me) — **prowadzisz osobiście, nie deleguj**

Grill-me wymaga żywego dialogu z userem — to jedyna faza bez izolowanego subagenta (subagent nie może prowadzić za Ciebie rozmowy z userem w czasie rzeczywistym).

1. Wywołaj `Skill("grill-me")` w kontekście: przedmiotem grillowania jest **decyzje projektowe do zadania** opisanego w `00-problem.md`, z uwzględnieniem luk/ryzyk z `01-analysis.md`.
2. Zgodnie z zasadą grillingu: fakty (stan repo, istniejące wzorce) ustalasz sam albo przez subagenta eksploracyjnego — nigdy nie pytaj usera o coś, co możesz sprawdzić. Pytania do usera dotyczą wyłącznie decyzji, które faktycznie należą do niego.
3. Sesja kończy się gdy frontier jest pusty i user potwierdza wspólne zrozumienie.
4. Zapisz ustalenia do `02-requirements.md` (lista decyzji + uzasadnienia, nie transkrypt pytań).

## Step 3: Faza 3 — Plan ogólny (subagent, `general-purpose`, model: **Claude Sonnet 5**)

Prompt zawiera: pełną treść `00-problem.md`, polecenie przeczytania `01-analysis.md` i `02-requirements.md`, zasadę "plan to hipoteza" (weryfikacja względem repo), oraz **zasadę 8** (czytanie ai-tools rules + dokumentacji architektury repo docelowego — dla planu ogólnego wystarczy `architecture-decisions.md` z ai-tools plus dokumentacja architektury repo docelowego z `01-analysis.md`).

**Wywołanie subagenta:** `Agent(description="Faza 3 - plan ogólny", prompt="{...}", subagent_type="general-purpose", model="claude-sonnet-5", run_in_background=false)`

Output: `03-plan-overview.md` — architektura, przepływ (UX/dane), warianty rozważone, decyzje projektowe i uzasadnienie, zgodność z ADR-ami. Krótkie podsumowanie w odpowiedzi.

## Step 4: Faza 4 — Review planu ogólnego (fresh subagent, model: **Sonnet R1 → Haiku+ R2-3**)

**Runda 1 (model: Claude Sonnet 5):** nowy, niezależny subagent (nigdy ten sam co autor planu) dostaje w prompcie: pełną treść `00-problem.md` i `02-requirements.md`, polecenie przeczytania `03-plan-overview.md`, oraz zasadę 8 (ai-tools rules + dokumentacja architektury). Zadanie: znaleźć niewyjaśnione sprawy, sprzeczności z wymaganiami/ADR-ami, brakujące decyzje — **nie oceniać stylu, tylko kompletność i spójność**. Output: `04-review-overview.md` (sekcja "Runda 1") + lista otwartych punktów w odpowiedzi.

**Wywołanie R1:** `Agent(description="Faza 4 R1 - review planu ogólnego", prompt="{...}", subagent_type="code-reviewer", model="claude-sonnet-5", run_in_background=false)`

**Między rundami:** przekaż otwarte punkty do agenta z Fazy 3 przez `SendMessage` (ma kontekst) — niech zaktualizuje `03-plan-overview.md`.

**Runda 2-3 (model: Claude Haiku 4.5 z fallback do Sonnet):** kontynuuj TEGO SAMEGO reviewera (Haiku) przez `SendMessage` — sprawdza czy jego punkty zostały zaadresowane, dopisuje "Rundę N" do `04-review-overview.md`. **FALLBACK RULE:** Jeśli Haiku R2 zwróci "brak dalszych uwag" bez konkretnych zastrzeżeń, albo jego review będzie powierzchowne — zatrzymaj się i wznów R2 z Sonnet zamiast kontynuować z Haiku. Zatrzymaj się gdy reviewer ma czystą opinię, albo po 3 rundach (wtedy przedstaw userowi nierozstrzygnięte kwestie do ręcznej decyzji).

**Wywołanie R2+:** `Agent(description="Faza 4 R{N} - review planu ogólnego (kontynuacja)", prompt="{...}", subagent_type="code-reviewer", model="claude-haiku-4-5-20251001", run_in_background=false)` — jeśli fallback wymagany, retry z `model="claude-sonnet-5"`

### Gate 4
Pokaż userowi finalny stan planu ogólnego + czy review jest czysty. Zapytaj o zgodę na plan szczegółowy.

## Step 5: Faza 5 — Plan szczegółowy (subagent, `general-purpose`, model: **Claude Sonnet 5**)

Prompt: pełna treść `00-problem.md`, polecenie przeczytania `02-requirements.md`, `03-plan-overview.md`, `04-review-overview.md`; zasada 8 w pełnym zakresie (wszystkie odpowiednie pliki z `ai-tools/.claude/rules/` wg typu plików + dokumentacja architektury repo docelowego); zasada weryfikacji sygnatur przed użyciem w kodzie planu.

**Wywołanie subagenta:** `Agent(description="Faza 5 - plan szczegółowy", prompt="{...}", subagent_type="general-purpose", model="claude-sonnet-5", run_in_background=false)`

Output: `05-plan-detailed.md` — ponumerowane kroki (plik, gotowy kod zgodny ze stylem repo, importy, zależności, scenariusze testowe per krok), ostatni krok = checklista E2E do `ui-verify`.

## Step 6: Faza 6 — Review planu szczegółowego (fresh subagent, model: **Haiku+ fallback Sonnet**)

Nowy, niezależny subagent (Haiku). Prompt: `00-problem.md`, polecenie przeczytania `05-plan-detailed.md` + wszystkich wcześniejszych dokumentów fazy 3-4, zasada 8 w pełnym zakresie. Sprawdza: zgodność z ai-tools rules, zgodność z architekturą/ADR repo docelowego, poprawność sygnatur/importów, kompletność scenariuszy testowych, wykonalność kroków w podanej kolejności.

**Wywołanie subagenta:** `Agent(description="Faza 6 - review planu szczegółowego", prompt="{...}", subagent_type="code-reviewer", model="claude-haiku-4-5-20251001", run_in_background=false)`

**FALLBACK RULE:** Jeśli Haiku zwróci powierzchowny output (np. "wygląda OK" bez konkretnych uwag) — zatrzymaj się i wznów tę fazę z Sonnet zamiast kontynuować. To ostatnia bramka przed implementacją.

Output: `06-review-detailed.md`. Jeśli są istotne zastrzeżenia — przekaż do autora planu (`SendMessage`) do poprawy, potem krótka runda weryfikacyjna tym samym reviewerem (analogicznie do Fazy 4, max 2-3 rundy).

### Gate 6
Pokaż userowi finalną listę kroków planu szczegółowego + status review. Iteruj do jawnej akceptacji.

## Step 7: Gate — pytanie czy implementować

**Obowiązkowe, osobne pytanie**, nawet jeśli user już zaakceptował plan: *"Plan (ogólny + szczegółowy) zaakceptowany i zrecenzowany. Zaczynam implementację?"* Nie przechodź do Fazy 8 bez jawnego "tak"/potwierdzenia.

## Step 8: Faza 8 — Implementacja (subagent, `general-purpose`, model: **Haiku+ fallback Sonnet**)

Prompt: `00-problem.md`, polecenie przeczytania `05-plan-detailed.md` (+ `06-review-detailed.md` z poprawkami), zasady 1-7, i zasada 8 w pełnym zakresie (ai-tools rules wg typu plików + architecture-decisions + security-checklist + error-handling-patterns + dokumentacja architektury repo docelowego) — implementacja musi być zgodna z tymi regułami, nie tylko z planem.

**Wywołanie subagenta:** `Agent(description="Faza 8 - implementacja", prompt="{...}", subagent_type="general-purpose", model="claude-haiku-4-5-20251001", run_in_background=false)`

**FALLBACK RULE:** Jeśli jakikolwiek smoke test/bramka nie przechodzi (import error, typo w kodzie, zły style) — zatrzymaj się w `07-implementation-log.md` i wznów tę fazę z Sonnet zamiast kontynuować z Haiku.

Bramki: smoke test po każdym pliku backendowym (np. import test), cięższa bramka po warstwie backendowej (rejestracja tras), jedna bramka `typecheck` na końcu frontendu. Zero commitów.

Output: `07-implementation-log.md` (wykonane kroki, odstępstwa, rozbieżności, `git status`/`git diff --stat`, otwarte pytania).

### Gate 8
Pokaż podsumowanie + `git status`/`diff --stat`. Rozstrzygnij nierozwiązane rozbieżności z userem przed testami.

## Step 9: Faza 9 — Testy jednostkowe/integracyjne (subagent, `test-writer` lub `general-purpose`, model: **Haiku+ fallback Sonnet**)

Jak w poprzedniej wersji pipeline'u: najpierw poznaj konwencje istniejących testów (jeśli "nie znaleziono" wbrew założeniu planu — STOP i zgłoś, nie buduj infrastruktury od zera); pisz testy wg scenariuszy z `05-plan-detailed.md`; przy failure najpierw diagnoza (debug print/`-s`/izolowana repro), dopiero potem naprawa; po zazielenieniu — pełna regresja modułu, klasyfikacja niepowiązanych failures przez `git status`/`git diff` (pre-existing vs wprowadzone); jeden przebieg `typecheck` frontendu jeśli dotyczy. Zero commitów.

**Wywołanie subagenta:** `Agent(description="Faza 9 - testy", prompt="{...}", subagent_type="test-writer", model="claude-haiku-4-5-20251001", run_in_background=false)`

**FALLBACK RULE:** Jeśli Haiku zgłosi failure test'u ale jego diagnoza będzie niewystarczająca (np. "może to być bug w kodzie" bez konkretnego wskazania przyczyny) — zatrzymaj się i wznów tę fazę z Sonnet.

Output: `08-test-report.md`.

## Step 10: Faza 10 — Review implementacji (fresh subagent, `code-reviewer`, model: **Claude Sonnet 5**)

Nowy, niezależny subagent (nie ten który implementował). Prompt: `00-problem.md`, polecenie przeczytania `05-plan-detailed.md`, `07-implementation-log.md`, `08-test-report.md`, oraz **pełny zakres zasady 8** (ai-tools rules + security-checklist + error-handling-patterns + architecture-decisions + dokumentacja repo docelowego) — to główna bramka jakości, musi ocenić kod względem tych reguł, nie tylko "czy działa". Sprawdza też zgodność z planem i czy testy faktycznie pokrywają zaimplementowaną logikę.

**Wywołanie subagenta:** `Agent(description="Faza 10 - review implementacji", prompt="{...}", subagent_type="code-reviewer", model="claude-sonnet-5", run_in_background=false)`

Output: `09-review-implementation.md` — lista znalezisk (bugi, niezgodności z rules/architekturą, braki w testach), ranked po istotności.

### Gate 10
Jeśli są istotne znaleziska — przekaż do implementującego agenta (`SendMessage`) do poprawy, potem krótka runda weryfikacyjna (max 2-3 rundy, jak w Fazie 4). Pokaż userowi finalny status przed E2E.

## Step 11: Faza 11 — E2E przez ui-verify (subagent, `general-purpose`, model: **Claude Haiku 4.5**, tylko jeśli zadanie dotyka UI)

Prompt: `00-problem.md`, polecenie przeczytania checklisty E2E z ostatniego kroku `05-plan-detailed.md`, oraz jawne polecenie: **"Wywołaj `Skill('ui-verify')` z tą checklistą jako inputem."** Dodaj zasady rekonesansu środowiska z poprzedniej wersji pipeline'u (sprawdź `.env` przed zapisem, nie zabijaj cudzych procesów, weryfikuj przez pełny round-trip/reload, sprzątaj dane testowe po sobie, waliduj krzyżowo przez drugi widok jeśli istnieje).

**Wywołanie subagenta:** `Agent(description="Faza 11 - E2E ui-verify", prompt="{...}", subagent_type="general-purpose", model="claude-haiku-4-5-20251001", run_in_background=false)`

Output: `10-e2e-report.md` (punch list z ui-verify + potwierdzenie sprzątania danych).

Jeśli zadanie nie dotyka UI — pomiń tę fazę i zanotuj to w podsumowaniu końcowym.

## Step 12: Faza 12 — Update dokumentacji (subagent, `documentation-writer`, model: **Claude Haiku 4.5**)

Prompt: `00-problem.md`, `03-plan-overview.md`, `07-implementation-log.md`, oraz reguła z `CLAUDE.md` repo docelowego o dokumentowaniu (jeśli istnieje — np. "nowy moduł -> nowy plik + wpis w indeksie; zmiana istniejącego modułu -> update istniejącej sekcji, nie duplikacja"). Subagent aktualizuje `docs/` repo docelowego zgodnie z jego istniejącym układem — nie wymyśla nowej struktury dokumentacji bez potwierdzenia.

**Wywołanie subagenta:** `Agent(description="Faza 12 - update dokumentacji", prompt="{...}", subagent_type="documentation-writer", model="claude-haiku-4-5-20251001", run_in_background=false)`

Output: `11-documentation-update.md` (co zaktualizowano/utworzono, linki).

### Gate 12 — raport końcowy

```
══════════════════════════════════════════════════════════
  PREPARE WORK — {tytuł zadania}
══════════════════════════════════════════════════════════
  Faza 1  Analiza:              {1 zdanie}
  Faza 2  Grill-me:             ustalenia w 02-requirements.md
  Faza 3  Plan ogólny:          zaakceptowany po {N} rundach review
  Faza 5  Plan szczegółowy:     {liczba kroków}, zrecenzowany
  Faza 8  Implementacja:        {N/M kroków}, {liczba rozbieżności}
  Faza 9  Testy:                {wynik}, regresja: {czysta/pre-existing}
  Faza 10 Review kodu:          {liczba znalezisk}, {rozwiązane/otwarte}
  Faza 11 E2E (ui-verify):      {wynik / pominięto - brak UI}
  Faza 12 Dokumentacja:         {zaktualizowane pliki}

  Zmienione pliki: patrz 07-implementation-log.md
  Artefakty: {repo_root}/.tmp/tasks/{slug}/
  Commit: NIE wykonano — working tree gotowy do Twojego review.
══════════════════════════════════════════════════════════
```

---

## Fallback Strategy dla "Haiku+"

"Haiku+ fallback Sonnet" oznacza poniższą strategię:

1. **Haiku startuje fazę** — model rozpoczyna pracę zgodnie z promptem.
2. **Monitor output**: Ty (orkiestrator) czytasz raport subagenta. Szukasz sygnałów:
   - **Faza 4-6 (review)**: Haiku zwrócił "OK, brak problemów" bez konkretnych uwag, albo jego uwagi są powierzchowne/ogólne?
   - **Faza 8 (implementacja)**: Kod nie przechodzi smoke test'u (import error, typo, zły style), a Haiku nie poradził sobie z naprawą?
   - **Faza 9 (testy)**: Test nie przechodzi, a Haiku zgłasza "może to bug" bez konkretnej diagnozy (bez debugowania)?
3. **Jeśli sygnał**: Zatrzymaj się i wznów tę fazę z Sonnet zamiast zaakceptować wynik Haiku.
   - Jeśli to była srednia runda (np. R2 recenzji) — możesz wznowić R2 z Sonnet.
   - Jeśli to była Faza 8 z błędem kodu — możesz wznowić od tego konkretnego kroku z Sonnet (nie całą fazę od nowa).
4. **Jeśli brak sygnału**: Output jest konkretny i kompletny — zaakceptuj wynik i przejdź do gate'u.

**Celem fallback strategy** jest oszczędzanie na modelach (Haiku tanszy), ale z safety netem — jeśli Haiku zawali na fazie gdzie to faktycznie ryzykuje, kupujesz sobie Sonnet, zamiast budować na słabym fundamencie.

---

## Obsługa błędów

- **Subagent zgłasza rozbieżność / STOP** (zasada 3): nie kontynuuj automatycznie. Przedstaw userowi, poczekaj na decyzję.
- **Review nie kończy się po 3 rundach**: przedstaw userowi nierozstrzygnięte punkty, niech zdecyduje czy iterować dalej, zaakceptować z zastrzeżeniami, czy zmienić podejście.
- **Bramka (import/test/typecheck) nie przechodzi**: pokaż pełny błąd, nie napraw bez pytania jeśli przyczyna nie jest oczywista z raportu subagenta.
- **Cofnięcie do wcześniejszej, już zaakceptowanej fazy**: kontynuuj tamtego subagenta przez `SendMessage` jeśli sesja wciąż "żyje", inaczej nowy subagent tej fazy z pełnym kontekstem zmiany + odwołaniem do istniejących plików w `.tmp/tasks/{slug}/`.
- Nigdy nie omijaj Gate 7 (jawne pytanie o rozpoczęcie implementacji) i Gate 4 (review planu ogólnego) — to twarde checkpointy człowieka.
