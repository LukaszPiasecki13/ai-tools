# Metadane i cykl życia dokumentu

Schemat front-matter, statusy, reguły walidacji. To jest kontrakt, który czyta
walidator ([`scripts/kb_validate.py`](./scripts/kb_validate.py)) i na którym
opiera się automatyzacja.

---

## 1. Po co metadane

Bez metadanych baza wiedzy jest katalogiem plików — da się ją czytać, ale nie da
się jej **obsługiwać maszynowo**. Metadane odpowiadają na cztery pytania, których
nie da się wyciągnąć z treści:

| Pytanie | Pole | Co odblokowuje |
|---|---|---|
| Czy to obowiązuje? | `status` | agent odrzuca szkice |
| Czy to nadal prawda? | `last_reviewed` | wykrywanie przeterminowania |
| Czego to dotyczy? | `applies_to` | pobieranie po zakresie + wykrywanie rozjazdu doc↔kod |
| Jakiego rodzaju treść to jest? | `type` | agent nie myli faktu z decyzją |

`applies_to` jest najważniejsze. Jest jedynym polem, które łączy dokument
z kodem w sposób sprawdzalny maszynowo, i to ono zamienia bazę wiedzy z biblioteki
w element pipeline'u.

---

## 2. Schemat front-matter

YAML na samej górze pliku, pomiędzy `---`. Przed nim nie ma nic — ani BOM, ani
pustej linii, ani nagłówka.

```yaml
---
id: be-telemetry-module
status: current
type: fact
scope: backend/telemetry
last_reviewed: 2026-09-12
applies_to:
  - backend/app/modules/telemetry/**
---
```

### Pola

| Pole | Wymagane | Typ | Znaczenie |
|---|---|---|---|
| `id` | **tak** | slug | Unikalny w całym repo, stabilny — nie zmienia się przy przenoszeniu pliku. Do niego linkują inne dokumenty w treści (nie ma osobnego pola `related`). |
| `status` | **tak** | enum | Zależy od `type`. Zwykłe dokumenty: `current` / `draft`. ADR-y (`type: decision`): `Proposed` / `Accepted` / `Rejected` / `Superseded`. |
| `type` | **tak** | enum | `fact` / `decision` / `reference` / `mixed`. |
| `scope` | **tak** | string | Hierarchiczny opis zakresu, wolny tekst, np. `backend/telemetry`, `business/pricing`. |
| `last_reviewed` | **tak** | `YYYY-MM-DD` | Data ostatniego sprawdzenia treści wobec rzeczywistości. |
| `applies_to` | nie | lista globów | Ścieżki kodu, których dokument dotyczy. Gdy obecne, włącza wykrywanie rozjazdu doc↔kod (§4). |
| `title` | nie | string | Jeśli brak, walidator bierze pierwszy nagłówek `#` z treści, a w ostateczności nazwę pliku. |

Powyższa tabela to komplet — nowe pole dodawaj dopiero wtedy, gdy potrafisz
wskazać mechanizm, który bez niego nie działa. Każde kolejne jest kosztem
ponoszonym przy **każdym** dokumencie.

To jest schemat **v2**, celowo lżejszy niż jego poprzednik (patrz „Zmiana
schematu" niżej). `id` i `applies_to` to jedyne pola, które warstwa mechaniczna
dodaje ponad to, co repo już realnie używało — reszta (`layer`, `domain`,
`confidence`, `owner`, `created`, `verified`, `review_after`, `expires`,
`sources`, `related`, `supersedes`, `superseded_by`) została usunięta, nie
przemianowana. Rozważane, ale **nie narzucone** rozszerzenia — dodaj je do repo
tylko wtedy, gdy faktycznie ich potrzebujesz, i wtedy zgłoś zmianę do tego pliku:

- `type: hypothesis` — dla treści świadomie niesprawdzonej (dziś: opisz to w
  treści dokumentu, np. blockquote `> **[HIPOTEZA]** ...`).
- `status: superseded` / `status: archived` — dziś zastępstwo i archiwizację
  opisuje się w treści dokumentu i przenosi plik (np. do `plans/archive/`),
  bez osobnego stanu maszynowego.
- `sources` — dziś źródła faktów żyją w treści dokumentu, nie w metadanych.

---

## 3. `type` — cztery rodzaje treści

Rozróżnienie, którego brak jest częstą przyczyną, dla której agent buduje na
piasku. Te rzeczy wyglądają w tekście identycznie i muszą być rozdzielone
metadanymi.

| Wartość | Co to znaczy | Jak agent ma to traktować |
|---|---|---|
| `fact` | Stan rzeczywisty, sprawdzalny (kod robi X, pomiar dał Y, ustawa mówi Z) | Można na tym budować. Rozbieżność z rzeczywistością = defekt dokumentu. |
| `decision` | Ustalenie ludzkie — mogło być inne, zostało wybrane | Wiążące. Zmiana wyłącznie przez nowy ADR, nigdy „przy okazji" w kodzie. |
| `reference` | Materiał odsyłający / słownikowy, nie twierdzenie samo w sobie | Punkt wejścia, nie źródło prawdy — sprawdź dokument, do którego odsyła. |
| `mixed` | Dokument łączący kilka rodzajów treści (np. plan: fakty + decyzje + prognozy) | Traktuj sekcja po sekcji; oznacz w treści, co jest czym, jeśli to niejasne z kontekstu. |

---

## 4. Cykl życia

Nomenklatura zależy od `type`:

### Zwykłe dokumenty (`fact`, `reference`, `mixed`)

| Status | Znaczenie | Zachowanie agenta |
|---|---|---|
| `draft` | W opracowaniu, niezatwierdzone | Czyta wyłącznie na jawne wskazanie. Nigdy nie cytuje jako podstawy. Pomijany w sprawdzaniu przeterminowania. |
| `current` | Obowiązuje | Normalny tryb. |

### ADR-y (`type: decision`)

| Status | Znaczenie | Zachowanie agenta |
|---|---|---|
| `Proposed` | Czeka na przegląd człowieka — decyzja nie jest ostateczna | Czyta, ale nie cytuje jako wiążące; nigdy nie zmienia się przez agenta (zmiana wymaga nowego ADR) |
| `Accepted` | Zaakceptowana przez człowieka | Wiążąca. Zmiany wyłącznie nowym ADR-em. |

**Nic nie jest kasowane** — ale dziś to konwencja treści i lokalizacji pliku
(np. przeniesienie do `plans/archive/`, dopisek w treści), a nie osobny stan
`status`. Zobacz listę rozważanych, nienarzuconych rozszerzeń w §2, jeśli
projekt faktycznie potrzebuje maszynowego rozróżnienia zastąpione/archiwalne.

### Przeterminowanie

Dokument bez jawnego pola „ważne do": walidator liczy termin jako
`last_reviewed + DEFAULT_REVIEW_MONTHS` (stała w `kb_validate.py`, domyślnie
6 miesięcy). Minięty termin przy `status: current` → **ostrzeżenie** (`W101`),
nie błąd. Dokument nadal obowiązuje; jest tylko zgłoszony do przeglądu. Sam
upływ czasu nie czyni treści fałszywą — czyni ją niesprawdzoną.

### Rozjazd doc↔kod

Dla dokumentów z `applies_to` walidator porównuje datę ostatniego commitu
w objętym kodzie z `last_reviewed`. Kod nowszy niż przegląd → **ostrzeżenie
o rozjeździe** (`W102`).

To nie oznacza, że dokument jest błędny — oznacza, że nikt tego nie sprawdził po
zmianie. Reakcja jest tania: przejrzyj, popraw albo tylko podbij `last_reviewed`.
Wykonywana regularnie, kosztuje minuty; pominięta przez kwartał, zamienia się
w przepisanie dokumentu od zera.

---

## 5. Reguły walidacji

Zestaw egzekwowany przez [`scripts/kb_validate.py`](./scripts/kb_validate.py).

### Błędy (blokują commit / CI)

| Kod | Reguła |
|---|---|
| `E001` | Brak front-matter w pliku pod `docs/` |
| `E002` | Brak pola obowiązkowego (`id`, `status`, `type`, `scope`, `last_reviewed`) |
| `E003` | Niedozwolona wartość `status` / `type` (status musi być `draft`/`current` dla zwykłych dokumentów, `Proposed`/`Accepted` dla ADR-ów), albo `applies_to` nie jest listą |
| `E004` | Zduplikowane `id` w repo |
| `E005` | Martwy link względny (plik nie istnieje) |
| `E006` | Martwa kotwica (`#sekcja` nie istnieje w pliku docelowym) |
| `E008` | Przekroczony twardy limit rozmiaru |
| `E010` | Zły format daty (wymagane `YYYY-MM-DD`) |

### Zmiana schematu

Schemat będzie się zmieniał. Bez reguły migracji pierwsza zmiana zamienia całą
bazę w czerwony raport i kończy się wyłączeniem walidacji.

**Wersja schematu jest jedna dla całego repo** i mieszka w tym pliku (nagłówek
poniżej), nie w polu każdego dokumentu — pole `schema_version` w setkach plików
to koszt bez korzyści, bo i tak wszystkie migrujesz naraz.

| Rodzaj zmiany | Tryb wprowadzenia |
|---|---|
| Nowe pole opcjonalne | od razu, bez migracji |
| Nowe pole **obowiązkowe** | najpierw jako ostrzeżenie (`W1xx`) przez jeden cykl przeglądu, potem jako błąd (`E002`) |
| Nowa wartość w enumie | od razu |
| Usunięcie wartości z enumu | najpierw ostrzeżenie, migracja istniejących dokumentów, dopiero potem usunięcie z walidatora |
| Zmiana znaczenia istniejącego pola | zabroniona — dodaj nowe pole, stare oznacz jako wycofywane |

Migrację przeprowadza się skryptem jednorazowym w osobnym commicie, nigdy ręcznie
plik po pliku i nigdy w tym samym commicie co zmiana walidatora — inaczej nie da
się odróżnić, co zmieniła migracja, a co człowiek.

**Wersja schematu: 2.0** (2026-09-18) — zastępuje v1.0. Zmiana wynika z realnego
konfliktu: dwa niezależne projekty w tym samym repo-konsumencie zaczęły używać
dwóch różnych schematów front-matter (v1 tutaj vs. lżejszy schemat już przyjęty
w praktyce). v2 rozstrzyga na korzyść lżejszego, już używanego schematu i dodaje
do niego wyłącznie `id` i `applies_to` — żaden dokument napisany pod lżejszy
schemat nie wymaga przepisania pól, które już ma.

### Ostrzeżenia (raportowane, nie blokują)

| Kod | Reguła |
|---|---|
| `W101` | `last_reviewed` + `DEFAULT_REVIEW_MONTHS` minęło przy `status: current` |
| `W102` | Rozjazd: kod z `applies_to` nowszy niż `last_reviewed` |
| `W103` | Sierota — dokument nieosiągalny z mapy wiedzy |
| `W104` | Przekroczony miękki limit rozmiaru |
| `W105` | `applies_to` nie dopasowuje żadnego istniejącego pliku |

Podział jest celowy. **Błędy to naruszenia struktury** — zawsze możliwe do
naprawienia natychmiast i zawsze warte zablokowania commitu. **Ostrzeżenia to
dług** — nie wolno im blokować pracy, bo pierwsza blokada na „dokument wymaga
przeglądu" kończy się wyłączeniem całej walidacji. Ostrzeżenia raportuje się
zbiorczo i spłaca w rytmie przeglądu (patrz [AUTOMATION.md](./AUTOMATION.md)).
