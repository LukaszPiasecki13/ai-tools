---
name: knowledge-base
description: "Projektowanie, porządkowanie i utrzymanie bazy wiedzy czytanej przez agentów AI - warstwy L0-L4, metadane, szablony dokumentów, walidacja i automatyzacja. Use when the user wants to build, restructure, audit or automate a knowledge base / documentation set for AI agents, asks how to organize docs for a product or startup so agents can use them, mentions 'baza wiedzy', 'biblioteka wiedzy', 'uporządkować dokumentację', or needs templates for PRODUCT.md, ADR, context packs, glossary or module contracts."
---

# Knowledge Base — baza wiedzy dla agentów AI

Baza wiedzy dla agenta to nie dokumentacja. Dokumentacja jest optymalizowana pod
człowieka, który czyta liniowo i sam wyczuwa, co jest nieaktualne. Baza wiedzy
jest optymalizowana pod **pobieranie w ograniczonym budżecie kontekstu przez
czytelnika, który ufa bezwarunkowo i nie wykrywa przeterminowania**.

Ta różnica rządzi każdą decyzją poniżej.

## Materiały

| Plik | Kiedy czytać |
|---|---|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Projektujesz strukturę, rozstrzygasz gdzie coś umieścić, rozbijasz duży dokument |
| [METADATA.md](./METADATA.md) | Piszesz front-matter, ustalasz statusy, definiujesz reguły walidacji |
| [AUTOMATION.md](./AUTOMATION.md) | Wdrażasz walidację, hooki, pakiety kontekstu, pętlę zadanie→kod→baza |
| [ANTIPATTERNS.md](./ANTIPATTERNS.md) | Audytujesz istniejącą bazę albo diagnozujesz, dlaczego agent pracuje na złym materiale |
| [templates/](./templates/) | Tworzysz konkretny dokument — gotowe szablony z instrukcją użycia |
| [scripts/kb_validate.py](./scripts/kb_validate.py) | Walidujesz bazę (linki, metadane, rozmiary, rozjazd doc↔kod) |

Czytaj **wybiórczo**. Cały zestaw naraz jest potrzebny wyłącznie przy pełnym
projektowaniu bazy od zera.

## Wdrożenie walidatora w repo docelowym

`kb_validate.py` jest **dostarczany do projektu**, nie uruchamiany z pluginu —
ma stać w repo, żeby działał w pre-commicie i w CI także tam, gdzie plugin nie
jest zainstalowany.

```bash
mkdir -p scripts
cp "${CLAUDE_SKILL_DIR}/scripts/kb_validate.py" scripts/
cp "${CLAUDE_SKILL_DIR}/scripts/test_kb_validate.py" scripts/
python3 scripts/test_kb_validate.py      # 16 testów, tylko stdlib
python3 scripts/kb_validate.py --root . --strict
```

`${CLAUDE_SKILL_DIR}` wskazuje katalog tego skilla niezależnie od tego, gdzie
zainstalowano plugin. Skrypty korzystają wyłącznie z biblioteki standardowej,
więc w repo docelowym nie pojawia się żadna nowa zależność.

Aktualizacja: skopiuj ponownie oba pliki i uruchom testy. Testy przypinają
zachowania, które łatwo zepsuć „upraszczając" (zgodność kotwic z GitHubem),
więc kopiowanie samego walidatora bez nich jest fałszywą oszczędnością.

## Wybór trybu

Ustal, który z czterech trybów obowiązuje, i idź tylko jego ścieżką.

### Tryb A — nowa baza od zera

1. [ARCHITECTURE.md](./ARCHITECTURE.md) §2, §5 — warstwy i katalogi.
2. Załóż L1 w kolejności: `CONTEXT.md` (słownik) → `PRODUCT.md` → pierwsze ADR.
   **Słownik pierwszy.** Bez ustalonych nazw wszystko poniżej opisuje te same
   rzeczy trzema słowami.
3. `docs/00_KNOWLEDGE-MAP.md` z szablonu, nawet gdy wskazuje trzy pliki.
4. `CLAUDE.md` (L0) ≤ 300 linii, z jawnym wskazaniem punktu wejścia do bazy.
5. Walidator + pre-commit — [AUTOMATION.md](./AUTOMATION.md) Etap 1.

Nie zakładaj pustych katalogów „na przyszłość". Katalog powstaje przy pierwszym
dokumencie, który do niego trafia.

### Tryb B — porządkowanie istniejących materiałów

1. **Inwentaryzacja przed zmianą.** Lista plików + rozmiar + odpowiedź na
   pytanie „czym to jest?" w jednym zdaniu. Bez tego nie wiadomo, co przenosisz.
2. **Audyt** wg [ANTIPATTERNS.md](./ANTIPATTERNS.md) — sekcja „Szybki audyt".
   Wynik zapisz z dowodami (ścieżki, liczby), nie z wrażeniami.
3. **Klasyfikacja** każdego pliku do warstwy L0–L4. Plik pasujący do dwóch
   warstw jest kandydatem do rozbicia — to jest sygnał, nie problem klasyfikacji.
4. **Plan migracji fazami**, od największego kosztu do najmniejszego.
   Kolejność, która się sprawdza: L0 do repo → punkt wejścia → walidacja linków →
   metadane → rozbicie monolitów.
5. **Migracja wykonywana etapami, każdy w osobnym commicie.** Nigdy nie
   przenoś i nie przepisuj treści w jednym kroku — wtedy diff nie pokazuje,
   co się naprawdę zmieniło.

Porządkowanie jest destrukcyjne (przenosi, dzieli, zmienia adresy). Plan
przedstaw człowiekowi **przed** wykonaniem.

### Tryb C — pojedynczy dokument

1. Ustal warstwę (§2 ARCHITECTURE) → wybierz szablon z [templates/](./templates/).
2. Wypełnij front-matter zgodnie z [METADATA.md](./METADATA.md) §2.
3. Dopisz wpis do mapy wiedzy — dokument spoza mapy nie istnieje.
4. Uruchom walidator.

### Tryb D — utrzymanie

Cykl przeglądu: `kb_validate.py --format json` → lista przeterminowanych (`W101`)
i rozjechanych (`W102`) → przegląd, poprawka albo samo podbicie `verified`.
Metryki zdrowia: [AUTOMATION.md](./AUTOMATION.md), sekcja końcowa.

## Reguły, których nie łam

1. **Słownik przed resztą.** Nieustalone nazewnictwo skaża każdy kolejny dokument.
2. **Jeden fakt — jedno miejsce.** Wszędzie indziej głęboki link.
3. **Decyzja mieszka w ADR.** Nie w planie, nie w komentarzu, nie w czacie.
4. **Nic nie kasujesz** — `superseded_by` albo `archived`.
5. **Twierdzenie normatywne ma źródło.** Bez źródła to hipoteza i musi być tak
   oznaczona (`confidence: hypothesis`).
6. **Zapisuj natychmiast.** Pojęcie i decyzja trafiają do pliku w tej samej turze,
   w której powstały. Batch na koniec sesji nie nastąpi.
7. **Budżet L0.** `CLAUDE.md` ≤ 300 linii. Reszta to reguły ścieżkowe i skille.
8. **Plan to nie stan.** Stan systemu opisuje wyłącznie L2 z linkami do kodu.

## Typowe rozstrzygnięcia

| Sytuacja | Rozstrzygnięcie |
|---|---|
| „Gdzie zapisać, że wybraliśmy Postgres?" | ADR (L1). Dokument architektury (L2) opisuje skutek i linkuje. |
| „Dokument ma 1500 linii, dzielić?" | Tak, po adresowalności. Oryginał zostaje rozdzielaczem z linkami. |
| „Analiza konkurencji — gdzie?" | L4 `docs/research/`. Wnioski wiążące → osobny ADR. |
| „Nowe pojęcie w rozmowie" | `CONTEXT.md` natychmiast, z listą `_Unikać_`. |
| „Dokumentacja API — L1 czy L2?" | L2, z `applies_to` na kod endpointów. |
| „Cennik — gdzie?" | L1 `docs/product/`, jedno miejsce. `review_after` 3 miesiące. |
| „Stary plan po wdrożeniu" | `status: archived`, przeniesienie do `plans/archive/`. Nie kasować. |
| „Sprzeczność między dwoma dokumentami" | Wygrywa wyższa warstwa. Sprzeczność zapisz jako otwarty punkt — to defekt do naprawy, nie wybór do dokonania. |
| „Czy to zasługuje na ADR?" | Trzy warunki naraz: nieodwracalne, nieoczywiste, z realną alternatywą. Brak któregoś → bez ADR. |
