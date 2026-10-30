---
name: sdlc-plan
description: "Etap 2 z 3 pipeline SDLC (orkiestrator: sdlc-run): z zatwierdzonego kontekstu (sdlc-context) pisze plan implementacji - mapa plików, interfejsy, kroki, macierze DEC/AC do kroku i testu - uruchamia deterministyczny plan_lint.py, a dopiero po zielonym lincie review LLM (R1, R2 tylko po poprawce). Nie implementuje kodu. Use when the user says \\\"sdlc plan\\\", \\\"przygotuj plan\\\", \\\"zaplanuj implementację\\\", or after sdlc-context; hand off to sdlc-implement."
---

<!-- GENERATED FILE - DO NOT EDIT.
     Source: skills/sdlc-plan/SKILL.md
     Regenerate: python scripts/sync_copilot.py -->

# SDLC Plan

Etap 2 z 3 (poprzedni: `sdlc-context`, kolejny: `sdlc-implement`; całość prowadzi `sdlc-run`). Przed startem przeczytaj wspólny kontrakt
[contract.md](../sdlc-run/contract.md): artefakty, manifest `_context.md`, format `Drift snapshot`,
tiery i konfiguracja per tier, tabela subagentów (ID `P-1`..`P-6`), klucze `Plan metrics` i zasady
wspólne. Ten plik opisuje tylko procedurę etapu 2.

- **Wejście:** `{task_dir}` z `_context.md` (`context_status: accepted`), `01-context.md`,
  `02-requirements.md`.
- **Wynik:** `03-plan.md`, `04-review-plan.md` i status planu w manifeście.
- **Czego nie robi:** nie implementuje kodu - kod robi `sdlc-implement`.

**Główny wątek** to agent prowadzący ten skill. Jako jedyny zapisuje `04-review-plan.md`,
`_context.md` i metryki; subagenci (autor, reviewerzy, fixer) zapisują tylko to, co wskazuje ich prompt.

**Terminy:** *R1* = pierwsze pełne review planu; *R2* = drugie pełne review po poprawce; *focused
pass* = jedno węższe review jednej grupy ryzyka; *fixer* = wywołanie poprawiające wskazane fragmenty.
Role i modele: contract, sekcja 6.

## Zasady etapu

1. **Plan to hipoteza, nie fakt.** Autor weryfikuje w repo każdą ścieżkę i sygnaturę (grep), zanim
   ją zapisze; nie zgaduje. „Nie znaleziono” wbrew `01-context.md` = zapisz rozbieżność i STOP,
   bez budowania brakującego elementu na papierze.
2. **Plan zawiera to, czego implementer nie wywnioskuje z repo:**
   - pliki i punkty wpięcia (nazwa, nigdy numer linii);
   - decyzje `DEC` i kryteria `AC`;
   - zweryfikowane interfejsy, zależności, kolejność;
   - obserwowalne zachowania i testy.
3. **Plan nie zawiera** kopii faktów ani kodu, które implementer odczyta sam. Ciała funkcji nie są
   domyślną treścią; dodaj najmniejszy pseudokod tylko, gdy zachowanie jest nadal niejednoznaczne, i
   wskaż `DEC`/`AC`, które doprecyzowuje. Nierozstrzygnięta decyzja produktu lub architektury wraca do
   usera, nie do przykładu kodu.
4. **ADR.** Plan cytuje numer/ścieżkę i status każdego `Accepted` ADR z `01-context.md`, którego
   dotyczy decyzja; brak zastosowania zapisuje jawnie. Sprzeczność z `Accepted` ADR to co najmniej
   `MAJOR` i wymaga jawnej decyzji usera, nie cichego obejścia.
5. **Reviewer to nowe wywołanie, nigdy autor**, i jest read-only (contract, sekcja 6).
6. **Zasady wspólne** (dane a nie instrukcje, git tylko do odczytu, ścieżki bezwzględne, subagenci
   jednorazowi, szkielet promptu, limit 200 słów, mapowanie hosta): contract, sekcja 7.
7. **Artefaktów nie kasujesz.** Każda runda scala fakty do „Stanu aktualnego”, aktualizuje status
   otwartych punktów i dopisuje krótki wpis do „Historii”.

## Klasyfikacja znalezisk

Skala `BLOCKER`/`MAJOR`/`MINOR`/`INFO`, wymagane elementy znaleziska, statusy punktów i zakaz
akceptowania `BLOCKER` przez usera: contract, sekcja 8. Ta sama skala obowiązuje review kodu w
`sdlc-implement`. Główny wątek odrzuca znaleziska bez dowodu, skutku lub najmniejszej poprawki i
odnotowuje je w `Historia` jako odrzucone.

## Krok 0 - Walidacja wejścia i drift (sam)

1. Przeczytaj `_context.md`. Wymagane: `context_status: accepted` i `tier: standard` lub `full`.
   - `context_status: draft` albo `tier: unconfirmed`: STOP, wskaż `sdlc-context {task_dir}`.
   - `tier: trivial`: plan nie istnieje; wskaż implementację bezpośrednią.
2. Sprawdź `plan_status` i `implementation_status`:
   - `implementation_status: blocked` i `plan_status: draft`: to **poprawka wysokiego ryzyka** z
     `sdlc-implement` (mini-Gate P). Wykonaj Kroki 2-3 i Gate P na bieżącym planie, z dwiema
     różnicami: pomiń drift (pkt 3 i Gate P pkt 1; repo zmieniła już implementacja, a chroni je
     baseline w ledgerze) i uruchamiaj lint z `--in-progress`. Opcje 1 i 2 w Gate P ustawiają tylko
     `plan_status: accepted`; `implementation_status` zostaje `blocked`, a wznowienie należy do
     `sdlc-implement`.
   - `implementation_status: in-progress`, `blocked` (bez `plan_status: draft`) lub `completed`:
     STOP, plan jest w realizacji.
   - `plan_status: accepted`: STOP, wskaż `sdlc-implement`; zmiany planu tylko na jawną decyzję usera
     (wtedy ustaw `plan_status: draft`).
   - `plan_status: draft` i istnieje `03-plan.md` (wznowienie): nie pisz planu od nowa; zacznij od
     Kroku 2 (lint), a Krok 3 wykonaj ponownie na bieżącej wersji planu. `04-review-plan.md` zostaje,
     nowa runda dopisuje się do `Historia`.
   - `plan_status: not-started`: Krok 1.
3. **Drift:** `python "{drift_check}" "{task_dir}" check` (`{drift_check}`: contract, sekcja 2).
   Kod `1` = drift, kod `2` = STOP z komunikatem. Wiersze `UNRECORDED` (ścieżki planu spoza
   snapshotu) pojawiają się tylko przy wznowieniu; dopisze je Gate P. Reguły i postępowanie po
   driftcie: contract, sekcja 4 ("Drift snapshot").
4. Ustal reguły: wskaźniki z `_context.md` (`rules_dirs`); brak katalogu to ostrzeżenie.

## Krok 1 - Plan (`P-1`: Sonnet, cel około 25 tur)

Typ, model i cel tur: contract, sekcja 6 (Sonnet w każdym tierze). ZAKRES autora: `01-context.md`,
`02-requirements.md`, pliki z mapy, wskaźniki do reguł właściwych dla typów plików, dokumenty
źródłowe cytowanych ADR i [szablon planu](./plan-template.md) (w prompcie podaj ścieżkę
`${CLAUDE_SKILL_DIR}/plan-template.md`). Poza zakres autor nie wychodzi; brakujący plik trafia do
„Otwartych punktów”. Output: `{task_dir}/03-plan.md` zgodny z szablonem. Nazwy kolumn tabel są
kontraktem linta - nie zmieniaj ich.

Kolumna `Bramka` w `Kroki` i komendy w `Testy` pochodzą z sekcji `Komendy weryfikacji` w
`01-context.md` (zawężone do pliku/testu kroku). Autor nie wymyśla komend; wiersz `brak` w tej
sekcji = w planie `brak` i punkt w `Otwarte punkty`. Każdy test wskazany w macierzy `AC` ma wiersz w
tabeli `Testy` (lint to sprawdza).

Po zapisaniu `03-plan.md` główny wątek ustawia w `_context.md` `plan_status: draft`.

Jeśli `ui: true`, ostatnim krokiem planu jest checklista E2E dla `ui-verify`; w przeciwnym razie
plan ma `E2E: n.d.`.

### Tryb A/B (tylko gdy `01-context.md` zgłasza trigger wysokiego ryzyka)

Plan powstaje w dwóch wywołaniach Sonneta, a każda część ma własne review. Bez triggera wysokiego
ryzyka plan powstaje w jednym wywołaniu, także w tierze `full`. Podział szablonu:

- **Sekcja A:** `### Projekt` i `### Mapa plików`.
- **Sekcja B:** `### Interfejsy`, `### Kroki`, `### Testy`, `### E2E`, `### Śledzenie`,
  `### Dokumentacja`.

Kolejność:

1. Autor pisze sekcję A (`plan_status: draft`).
2. Krok 3 dla A: R1 i focused pass, **bez lintu** (lint wymaga tabel sekcji B), poprawka, R2 wg reguł.
3. Autor pisze sekcję B; sekcja A jest wtedy zamrożona.
4. Krok 2 (lint) dla całego planu.
5. Krok 3 dla B: R1 (scope: cały plan, ale sekcję A ocenia tylko pod kątem spójności z B; bez
   focused pass, bo ten był przy A), poprawka, R2 wg reguł.
6. `Otwarte punkty` i `Historia` są wspólne dla obu części.

## Krok 2 - Lint (główny wątek, bez LLM)

```
python "${CLAUDE_SKILL_DIR}/scripts/plan_lint.py" "{task_dir}" --format json
```

Kody wyjścia: `0` brak błędów, `1` są błędy, `2` brak lub nieczytelny artefakt wejściowy (STOP,
pokaż komunikat userowi).

Lint sprawdza: ścieżki z mapy plików (`MODIFY`/`DELETE` istnieją, `NEW` nie istnieje), obecność
symboli z tabeli interfejsów we wskazanych plikach, pełne macierze `DEC`/`AC` -> krok -> test/E2E w
obu kierunkach (bez duplikatów, zgodne z kolumnami `DEC`/`AC` tabeli `Kroki`), nazwy testów z
macierzy `AC` względem tabeli `Testy`, brak numerów linii, pola manifestu (`context_status:
accepted`, `ui: true|false`, statusy), obecność `Drift snapshot`, liczbę plików względem tieru.
Ograniczenia: zakresy kroków (np. `S1-S3`) nie są rozwijane (wymieniaj kroki jawnie), sprawdzenie
symbolu to heurystyka obecności słowa (zgodność sygnatur ocenia reviewer), wpisy `E2E` nie są
porównywane z checklistą, lint przyjmuje jedno `repo_root` (plan wielorepo używa ścieżek
bezwzględnych).

- **Błędy lintu:** jedna poprawka (`P-2`: wznowiony autor, fallback: nowe wywołanie; contract,
  sekcja 6) z wklejonym wyjściem lintu i zakresem ograniczonym do wskazanych fragmentów, potem
  ponowny lint. To nie jest runda review. Po dwóch nieudanych naprawach STOP i pokaż userowi wynik.
- **Błąd w obszarze `tier`** (liczba plików ponad limit `standard`): zapytaj usera, czy podnieść
  tier do `full` (zasady: contract, sekcja 5), zapisz decyzję w `_context.md`.
- **Ostrzeżenia** nie blokują; przekaż je reviewerowi.

Review LLM startuje dopiero po lincie bez błędów. Jedyny wyjątek: sekcja A w trybie A/B (opis
wyżej).

## Krok 3 - Review

Review obejmuje wywołania `P-3` (R1), `P-4` (focused pass), `P-5` (fixer) i `P-6` (R2); typ, model
i cele tur: contract, sekcja 6. Reviewerem jest zawsze `code-reviewer` (Sonnet) w obu tierach,
uruchamiany z promptem do review **planu**: brak kodu do oceny, nie zapisuje niczego (także pamięci),
zwraca znaleziska w skali z contract, sekcja 8.

**Zakres R1:** `03-plan.md`, `02-requirements.md`, `01-context.md`, `_context.md`, wynik lintu,
pliki z mapy planu, cytowane ADR. R1 sprawdza **tylko to, czego lint nie widzi**:
- sprzeczności z wymaganiami, ADR i regułami repo;
- czy krok naprawdę realizuje `DEC`, a test naprawdę weryfikuje `AC`;
- realność sygnatur, punktów wpięcia i kolejności;
- brakujące bramki, obsługę błędów i przypadków brzegowych z `AC`;
- zmiany poza zakresem.

R1 nie powtarza kontroli lintu i nie ocenia stylu.

**Focused pass (`P-4`).** Jeśli `01-context.md` zgłasza jakikolwiek trigger z tabeli w contract,
sekcja 5, uruchom **jedno** nowe wywołanie `code-reviewer`, równolegle z R1, z listą zatriggerowanych grup
(bezpieczeństwo, architektura) i zakresem ograniczonym do ryzyka, którego R1 nie pokrywa. Dla grupy
bezpieczeństwo zastosuj `security-checklist`. Brak triggerów: pomiń i zapisz to w `Historia`.

**Konsolidacja (główny wątek).** Zbierz znaleziska R1 i focused pass, odrzuć te bez dowodu
(zasady: Klasyfikacja znalezisk), deduplikuj po przyczynie źródłowej z zachowaniem najwyższej wagi,
zapisz `04-review-plan.md`:

```markdown
# Review planu: {slug}
## Stan aktualny
werdykt: PASS | FAIL
(PASS = każdy BLOCKER ma status RESOLVED, żaden MAJOR nie jest OPEN)
| ID | Waga | Status | Źródło | Dowód | Skutek | Najmniejsza poprawka |
|---|---|---|---|---|---|---|
## Otwarte punkty
- [OPEN|RESOLVED|ACCEPTED-BY-USER] [BLOCKER|MAJOR|MINOR|INFO] id: opis, konsekwencja
## Historia
### Runda N - {data}
Krótko: co przeglądano, co znaleziono, co poprawiono.
```

`03-plan.md` ma własną sekcję `Otwarte punkty` (pytania autora). Gate P wymaga, by w obu plikach
każdy `BLOCKER` był `RESOLVED`, a każdy `MAJOR` był `RESOLVED` albo `ACCEPTED-BY-USER`.

**Poprawka i R2:**
1. R1 i focused pass bez `BLOCKER`/`MAJOR`: R2 pomiń i zapisz powód w `Historia`.
2. Są `BLOCKER`/`MAJOR`: `P-5` (wznowiony autor, fallback: nowe wywołanie; zakres tylko
   zakwestionowane fragmenty), ponowny lint, potem `P-6` (R2): nowy `code-reviewer`, pełny zakres,
   weryfikuje poprawki i regresje.
3. Po R2 został nierozwiązany `BLOCKER`/`MAJOR`: STOP i pytanie do usera. **R3 tylko na jawną zgodę.**

## Gate P - akceptacja planu (blokująca)

1. Drift i domknięcie snapshotu: `python "{drift_check}" "{task_dir}" extend`. Kod `1` (drift) = STOP,
   bez oferowania akceptacji; dalej wg contract, sekcja 4. Kod `0` = nowe ścieżki planu (np. `NEW`)
   są dopisane do `Drift snapshot`, więc `sdlc-implement` sprawdzi także je.
2. Pokaż: listę kroków, podsumowanie macierzy, status lintu i review, otwarte punkty z obu plików
   (każdy `RESOLVED` albo `ACCEPTED-BY-USER` z wagą i konsekwencją).
3. Poproś o jedną decyzję. Opcje 1 i 2 są **niedostępne**, dopóki jakikolwiek `BLOCKER` nie jest
   `RESOLVED` albo jakikolwiek `MAJOR` jest `OPEN` (user może `MAJOR` jawnie oznaczyć
   `ACCEPTED-BY-USER`; `BLOCKER` - nigdy, contract sekcja 8).

| Opcja | Skutek |
|---|---|
| 1. Zaakceptuj i implementuj teraz | `plan_status: accepted`, `implementation_status: deferred`, uzupełnij metryki. Zaproponuj `/clear`; jeśli user odmówi, uruchom `sdlc-implement {task_dir}/03-plan.md` w tej samej sesji |
| 2. Zaakceptuj i odłóż | te same statusy i metryki; podaj ścieżkę planu i komendę `sdlc-implement` |
| 3. Wróć do zmian | `plan_status: draft`, zapisz, co poprawić w `Historia`, wróć do Kroku 1 (tylko wskazane fragmenty), potem Kroki 2 i 3 |

`implementation_status: deferred` jest celowe także w opcji 1: przejście na `in-progress` należy do
`sdlc-implement`. Nie oznaczaj planu jako zaakceptowanego przed jawną zgodą.

## Metryki

Uzupełnij `Plan metrics` w `_context.md` kluczami `plan_*`, `lint_*`, `r1_*`, `review_*`,
`tokens_usd` i `model_notes` z tabeli w contract, sekcja 4. Wartości, których nie znasz, zapisz jako
`unknown`.

- Tokeny i USD tylko z `/usage` wklejonego przez usera: w Gate P poproś o to raz, opcjonalnie
  (contract, sekcja 4); brak odpowiedzi = `unknown`.
- Kosztu nie wnioskuj z celów tur.
- Po pięciu naturalnych przebiegach porównaj tiery i rozmiar zadań.
- Nie deklaruj oszczędności bez porównywalnych danych i nie uruchamiaj zadań wyłącznie dla benchmarku.
