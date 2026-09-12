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
| Czy to obowiązuje? | `status`, `layer` | agent odrzuca szkice i dokumenty zastąpione |
| Czy to nadal prawda? | `verified`, `review_after` | wykrywanie przeterminowania |
| Czego to dotyczy? | `applies_to` | pobieranie po zakresie + wykrywanie rozjazdu doc↔kod |
| Jak pewna jest ta treść? | `confidence` | agent nie myli hipotezy z ustaleniem |

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
title: Moduł telemetry — ingest, normalizacja, zapytania
layer: L2
domain: backend
status: active
confidence: fact
owner: lukasz
created: 2026-09-12
verified: 2026-09-12
review_after: 2026-12-12
applies_to:
  - backend/app/modules/telemetry/**
sources:
  - backend/app/modules/telemetry/services/ingest.py
related:
  - adr-0009-normalizacja-telemetrii
  - be-architecture
supersedes: []
superseded_by: null
tags: [telemetria, ingest]
---
```

### Pola

| Pole | Wymagane | Typ | Znaczenie |
|---|---|---|---|
| `id` | **tak** | slug | Unikalny w całym repo, stabilny. Do niego linkują `related`. Nie zmienia się przy przenoszeniu pliku. |
| `title` | **tak** | string | Zdanie, nie hasło. To ono trafia do mapy wiedzy. |
| `layer` | **tak** | `L0`–`L4` | Warstwa wg [ARCHITECTURE.md](./ARCHITECTURE.md). |
| `status` | **tak** | enum | `draft` / `active` / `superseded` / `archived`. |
| `confidence` | **tak** | enum | `fact` / `decision` / `hypothesis`. |
| `owner` | **tak** | string | Człowiek odpowiedzialny. Jedna osoba, nie zespół. |
| `created` | **tak** | `YYYY-MM-DD` | Data powstania. Nigdy nie zmieniana. |
| `verified` | **tak** | `YYYY-MM-DD` | Data ostatniego sprawdzenia treści wobec rzeczywistości. **To jest najważniejsza data w pliku.** |
| `review_after` | L1, L2 | `YYYY-MM-DD` lub `on-change` | Termin ważności. `on-change` = ważny, dopóki nie zmieni się kod z `applies_to`. |
| `applies_to` | L2 | lista globów | Ścieżki kodu, których dokument dotyczy. |
| `sources` | L2, L4 | lista | Linki do kodu (`plik.py#L154`), URL-e, nazwy źródeł. |
| `related` | nie | lista `id` | Powiązane dokumenty. Nie ścieżki — `id`. |
| `domain` | nie | string | `backend` / `frontend` / `firmware` / `product` / `market`. |
| `supersedes` / `superseded_by` | przy zastąpieniu | lista / `id` | Łańcuch zastąpień. |
| `expires` | L3 | `YYYY-MM-DD` | Po tej dacie dokument roboczy jest automatycznie do archiwizacji. |
| `tags` | nie | lista | Wyłącznie do wyszukiwania. Nigdy nie niosą znaczenia normatywnego. |

### Wymagalność per warstwa

| Warstwa | Dodatkowo wymagane |
|---|---|
| L0 | — (wystarczy zestaw obowiązkowy; reguły `.claude/rules/*` zachowują własne `paths` i `description`) |
| L1 | `review_after` |
| L2 | `applies_to`, `sources`, `review_after` |
| L3 | `expires` |
| L4 | `sources` |

---

## 3. `confidence` — trzy poziomy pewności

Rozróżnienie, którego brak jest najczęstszą przyczyną, dla której agent buduje na
piasku. Te trzy rzeczy wyglądają w tekście identycznie i muszą być rozdzielone
metadanymi.

| Wartość | Co to znaczy | Jak agent ma to traktować |
|---|---|---|
| `fact` | Stan rzeczywisty, sprawdzalny (kod robi X, pomiar dał Y, ustawa mówi Z) | Można na tym budować. Rozbieżność z rzeczywistością = defekt dokumentu. |
| `decision` | Ustalenie ludzkie — mogło być inne, zostało wybrane | Wiążące. Zmiana wyłącznie przez nowy ADR, nigdy „przy okazji" w kodzie. |
| `hypothesis` | Założenie niesprawdzone | **Nigdy nie jest podstawą do działania.** Agent może je testować i musi je oznaczać w wynikach. |

Dokument mieszający poziomy (np. plan biznesowy: fakty rynkowe + decyzje + prognozy)
deklaruje najsłabszy z nich i oznacza sekcje w treści:

```markdown
> **[HIPOTEZA]** Docelowy rynek to 1300–1700 gmin.
> Podstawa: szacunek własny. Niezweryfikowane wobec rejestru GUS.
```

---

## 4. Cykl życia

```
draft ──► active ──► superseded ──► archived
             │                          ▲
             └──────────────────────────┘
                   (dezaktualizacja bez następcy)
```

| Status | Znaczenie | Zachowanie agenta |
|---|---|---|
| `draft` | W opracowaniu, niezatwierdzone | Czyta wyłącznie na jawne wskazanie. Nigdy nie cytuje jako podstawy. |
| `active` | Obowiązuje | Normalny tryb. |
| `superseded` | Zastąpione przez `superseded_by` | Nie czyta treści — podąża za `superseded_by`. Czyta oryginał tylko przy pytaniu „dlaczego zmieniliśmy zdanie". |
| `archived` | Nieaktualne, bez następcy | Pomija. Nie kasuje. |

**Nic nie jest kasowane.** Archiwum kosztuje kilobajty, a odtworzenie odrzuconego
wariantu i jego uzasadnienia kosztuje dni — plus ryzyko, że wrócicie do pomysłu,
który raz już odrzuciliście ze słusznego powodu.

### Przeterminowanie

`review_after` minęło i `status: active` → walidator zgłasza **ostrzeżenie**, nie
błąd. Dokument nadal obowiązuje; jest tylko zgłoszony do przeglądu. Sam upływ
czasu nie czyni treści fałszywą — czyni ją niesprawdzoną.

Sugerowane horyzonty:

| Typ | `review_after` |
|---|---|
| ADR ze statusem `accepted` | `on-change` (żyje, aż zostanie zastąpiony) |
| Słownik `CONTEXT.md` | 6 miesięcy |
| `PRODUCT.md` | 3 miesiące (startup przed PMF: 1 miesiąc) |
| Kontrakt L2 | `on-change` |
| Analiza rynku / konkurencji (L4) | 6–12 miesięcy |
| Dane cenowe, koszty, dostępność sprzętu | 3 miesiące |

### Rozjazd doc↔kod

Dla dokumentów z `applies_to` i `review_after: on-change` walidator porównuje
datę ostatniego commitu w objętym kodzie z `verified`. Kod nowszy niż weryfikacja
→ **ostrzeżenie o rozjeździe**.

To nie oznacza, że dokument jest błędny — oznacza, że nikt tego nie sprawdził po
zmianie. Reakcja jest tania: przejrzyj, popraw albo tylko podbij `verified`.
Wykonywana regularnie, kosztuje minuty; pominięta przez kwartał, zamienia się
w przepisanie dokumentu od zera.

---

## 5. Reguły walidacji

Zestaw egzekwowany przez [`scripts/kb_validate.py`](./scripts/kb_validate.py).

### Błędy (blokują commit / CI)

| Kod | Reguła |
|---|---|
| `E001` | Brak front-matter w pliku pod `docs/` |
| `E002` | Brak pola obowiązkowego |
| `E003` | Niedozwolona wartość `status` / `layer` / `confidence` |
| `E004` | Zduplikowane `id` w repo |
| `E005` | Martwy link względny (plik nie istnieje) |
| `E006` | Martwa kotwica (`#sekcja` nie istnieje w pliku docelowym) |
| `E007` | `related` / `superseded_by` wskazuje na nieistniejące `id` |
| `E008` | Przekroczony twardy limit rozmiaru |
| `E009` | `status: superseded` bez `superseded_by` |
| `E010` | Zły format daty (wymagane `YYYY-MM-DD`) |

### Ostrzeżenia (raportowane, nie blokują)

| Kod | Reguła |
|---|---|
| `W101` | `review_after` minęło przy `status: active` |
| `W102` | Rozjazd: kod z `applies_to` nowszy niż `verified` |
| `W103` | Sierota — dokument nieosiągalny z mapy wiedzy |
| `W104` | Przekroczony miękki limit rozmiaru |
| `W105` | `applies_to` nie dopasowuje żadnego istniejącego pliku |
| `W106` | `expires` minęło przy `status: active` (L3) |
| `W107` | Dokument L2 bez żadnego linku do kodu w treści |

Podział jest celowy. **Błędy to naruszenia struktury** — zawsze możliwe do
naprawienia natychmiast i zawsze warte zablokowania commitu. **Ostrzeżenia to
dług** — nie wolno im blokować pracy, bo pierwsza blokada na „dokument wymaga
przeglądu" kończy się wyłączeniem całej walidacji. Ostrzeżenia raportuje się
zbiorczo i spłaca w rytmie przeglądu (patrz [AUTOMATION.md](./AUTOMATION.md)).
