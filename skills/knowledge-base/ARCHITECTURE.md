# Architektura bazy wiedzy dla agentów

Model warstwowy, jednostka wiedzy, kontrakt pobierania. To jest dokument
referencyjny — czytasz go, gdy projektujesz strukturę bazy albo rozstrzygasz,
gdzie umieścić nową informację.

---

## 1. Dlaczego baza wiedzy dla agenta ≠ dokumentacja dla człowieka

Człowiek czyta dokument liniowo, pomija nieistotne fragmenty i sam wyczuwa, że
coś jest nieaktualne. Agent nie robi żadnej z tych trzech rzeczy. Agent ładuje
**mały, precyzyjny podzbiór** bazy, **ufa mu bezwarunkowo** i **nie ma sposobu
sprawdzić, czy treść nadal odpowiada rzeczywistości**, jeśli baza mu tego nie
powie wprost.

Z tego wynikają trzy siły projektowe, którym podporządkowana jest cała reszta:

| Siła | Konsekwencja projektowa |
|---|---|
| **Budżet kontekstu** | Wiedza musi być adresowalna w małych jednostkach. Dokument, którego nie da się załadować w części, nie istnieje dla agenta. |
| **Zaufanie** | Każde twierdzenie normatywne musi mieć źródło (link do kodu, ADR, dowodu). Treść bez źródła jest hipotezą i musi być tak oznaczona. |
| **Świeżość** | Baza musi być walidowana automatycznie jak kod. Baza bez walidacji cicho gnije, a agent powiela zgniliznę z pełnym przekonaniem. |

**Test kontrolny całej bazy:** agent dostaje zadanie i listę plików, które ma
zmienić. Czy potrafi — bez przeszukiwania pełnotekstowego i bez pytania
człowieka — wskazać komplet dokumentów, które go obowiązują, i stwierdzić, czy
są aktualne? Jeśli nie, baza jest zbiorem plików, nie bazą wiedzy.

---

## 2. Model warstwowy L0–L4

Pięć warstw, rozróżnianych **rolą wiedzy**, nie tematem. Temat (backend,
firmware, rynek) jest wymiarem wtórnym — katalogiem wewnątrz warstwy.

| Warstwa | Nazwa | Odpowiada na pytanie | Trwałość | Charakter |
|---|---|---|---|---|
| **L0** | Konstytucja | *Jak agent ma się zachowywać?* | miesiące | normatywna, zawsze w kontekście |
| **L1** | Kanon | *Co jest ustalone i prawdziwe?* | kwartały/lata | normatywna, ładowana selektywnie |
| **L2** | Kontrakty | *Jak zbudowany jest system?* | do najbliższej zmiany kodu | normatywna, weryfikowalna wobec kodu |
| **L3** | Pamięć robocza | *Co robimy teraz?* | dni/tygodnie, wygasa | ulotna, z datą ważności |
| **L4** | Dowody | *Skąd to wiemy?* | wieczna, append-only | dowodowa, nigdy normatywna |

### L0 — Konstytucja

Reguły zachowania agenta: `CLAUDE.md`, `.claude/rules/*.md`, `.claude/agents/*.md`.

- Ładowane **zawsze** (CLAUDE.md) albo **automatycznie po ścieżce** (`rules` z `paths`).
- Budżet: `CLAUDE.md` ≤ 300 linii. Każda dopisana linia obciąża **każde** wywołanie agenta w repo.
- Zawierają **zakazy i tryby pracy**, nie wiedzę o produkcie. „Nigdy nie commituj bez zgody" — tak. „Nasz klient to gmina do 15 tys. mieszkańców" — nie, to L1.
- **Muszą leżeć w repo produktu i być wersjonowane.** L0 poza repo (na dysku dewelopera, w innym projekcie) nie działa w CI, w sesjach chmurowych ani u drugiej osoby.

### L1 — Kanon

Ustalenia, które przetrwają wiele iteracji kodu:

- `CONTEXT.md` — słownik domeny (jedno pojęcie = jedna nazwa, reszta na liście `_Unikać_`).
- `PRODUCT.md` — kanon produktu: problem, klient, zakres, wartość, wykluczenia.
- `docs/adr/` — rejestr decyzji (jedna decyzja = jeden plik).
- `docs/business/` — segmenty, model przychodowy, rejestr ryzyk.

Kanon jest **jedynym miejscem, gdzie decyzja mieszka**. Każde inne wystąpienie
to link, nigdy kopia. Jeśli w trzech dokumentach da się przeczytać, ile kosztuje
abonament, to za pół roku w trzech dokumentach będą trzy różne kwoty.

### L2 — Kontrakty

Opis zbudowanego systemu, weryfikowalny wobec kodu:

- architektura (warstwy, zależności, zakazy),
- moduł/komponent (odpowiedzialność, publiczne API, niezmienniki),
- kontrakt interfejsu (REST, format telemetrii, schemat zdarzeń, rejestr czujników),
- runbook (procedura operacyjna: provisioning, wdrożenie, recovery).

Każdy dokument L2 ma w metadanych `applies_to` — glob ścieżek kodu, których
dotyczy. To ten jeden atrybut zamienia bazę z biblioteki w mechanizm: pozwala
wykryć rozjazd doc↔kod i pozwala agentowi pobrać dokumenty **po zakresie
zadania**, a nie po zgadywaniu nazwy pliku.

**Reguła dowodu:** twierdzenie L2 o zachowaniu systemu ma link do kodu
(`backend/app/modules/telemetry/services/ingest.py#L154`) albo do testu, który
to zachowanie utrwala. Bez linku to jest L3 (plan), nie L2 (kontrakt).

### L3 — Pamięć robocza

Plany, briefy, specyfikacje zadań, katalogi przebiegów (`.tmp/tasks/…`).

- Każdy dokument L3 ma `status` i datę. Po zamknięciu → `archived`, nie kasowany.
- L3 **nigdy nie jest źródłem prawdy o stanie systemu.** Plan opisuje zamiar.
  Agent, który przeczyta plan i uzna, że opisany etap już istnieje, zbuduje na
  fikcji. Stan opisuje L2 + kod.
- Zamknięcie zadania z L3 ma obowiązkowy produkt uboczny: **delta w L1/L2**.
  Zadanie bez aktualizacji kanonu lub kontraktu jest niedokończone.

### L4 — Dowody

Badania rynku, analizy konkurencji, wywiady, pomiary, notatki ze spotkań,
zrzuty danych.

- **Append-only.** Nie poprawiamy starego badania — dopisujemy nowe i w treści
  poprzedniego dopisujemy, czym zostało zastąpione.
- Zawsze z datą i źródłem. Dowód bez daty jest bezużyteczny — nie wiadomo, czy
  opisuje rynek sprzed miesiąca czy sprzed trzech lat.
- **Nigdy nie normatywne.** Agent nie podejmuje decyzji na podstawie L4. L4
  zasila decyzję, która trafia do L1 jako ADR. Z badania wynika rekomendacja,
  z ADR wynika obowiązek.

### Reguła nadrzędności

```
L0 > L1 > L2 > L3 > L4
```

Konflikt rozstrzyga warstwa wyższa. **Konflikt jest defektem, nie sytuacją
normalną** — agent, który go wykryje, ma obowiązek zapisać go jako otwarty punkt
(albo zadanie), a nie milcząco wybrać wersję. Dwie sprzeczne prawdy w bazie to
gwarancja, że kolejny agent trafi na tę drugą.

---

## 3. Jednostka wiedzy

**Jeden plik = jedno pytanie, na które da się odpowiedzieć.**

Nazwa pliku jest odpowiedzią na to pytanie, nie tematem. `04_telemetry_module.md`
jest w porządku jako dokument modułu; `notatki.md`, `analiza.md`, `różne.md` — nie.

### Budżety rozmiaru

| Typ | Miękki limit | Twardy limit | Powód |
|---|---|---|---|
| `CLAUDE.md` (L0) | 200 | 300 | ładowany zawsze, w każdym wywołaniu |
| Reguła `.claude/rules/*` | 150 | 250 | ładowana automatycznie po ścieżce |
| ADR (L1) | 80 | 150 | decyzja, która nie mieści się na 150 liniach, to dwie decyzje |
| `CONTEXT.md` (L1) | 200 | 400 | powyżej — podziel na konteksty i zrób `CONTEXT-MAP.md` |
| Dokument L2 | 400 | 800 | powyżej — podziel po granicy odpowiedzialności |
| Dokument L3/L4 | 400 | 800 | powyżej — podziel po jednostce zadania/badania |

Twardy limit nie jest estetyką. Dokument na 1700 linii to ~25 tys. tokenów —
agent albo załaduje go w całości (i zostanie mu połowa okna na pracę), albo nie
załaduje wcale. Jedno i drugie jest porażką. **Dokument przekraczający twardy
limit traktuj jak dług techniczny z konkretnym planem rozbicia.**

### Rozbijanie dużego dokumentu

Nie po długości — **po adresowalności**. Pytanie kontrolne: *jakie pytanie
zadałby agent, żeby trafić dokładnie tutaj?* Każda odpowiedź to kandydat na
osobny plik. Rozdział, do którego nikt nigdy nie trafi osobno, zostaje tam, gdzie
jest.

Po rozbiciu oryginał zostaje jako **strona-rozdzielacz**: tytuł, jedno zdanie
kontekstu, lista linków do części. Nigdy nie zostawiaj po sobie martwych linków
— wszystkie kotwice z zewnątrz muszą dalej prowadzić do treści.

### Stabilne kotwice

Nagłówki są adresami publicznymi. Zmiana nagłówka zrywa każdy link
`plik.md#kotwica` w repo i każdy link zapisany w pamięci agenta z poprzedniej
sesji. Nagłówki zmieniaj świadomie i naprawiaj linki w tym samym commicie —
walidator (patrz [AUTOMATION.md](./AUTOMATION.md)) to wymusi.

---

## 4. Kontrakt pobierania wiedzy

Kolejność, w jakiej agent dochodzi do właściwych dokumentów. Wpisz ją do
`CLAUDE.md` — inaczej agent domyślnie zacznie od `grep`, czyli od najgorszej
możliwej strategii.

1. **Mapa wiedzy** (`docs/00_KNOWLEDGE-MAP.md`) — jedyny punkt wejścia. Zawiera
   spis wszystkich dokumentów z jednym zdaniem opisu i warstwą.
2. **Dopasowanie po zakresie** — agent zna pliki, które zamierza zmienić;
   dopasowuje je do `applies_to` w metadanych i ładuje trafione dokumenty.
3. **Głęboki link** — do konkretnej sekcji (`plik.md#kotwica`), nie do całego pliku.
4. **Pełnotekstowe szukanie** — ostateczność. Każde użycie tego kroku to sygnał,
   że mapa albo `applies_to` mają lukę. Luka jest do zgłoszenia, nie do obejścia.

### Pakiet kontekstu

Dla powtarzalnych typów zadań zdefiniuj gotowy zestaw dokumentów — *pakiet
kontekstu*. Zamiast wybierać materiał za każdym razem od nowa, agent dostaje
nazwę pakietu. Mechanizm wpięcia, format zapisu w mapie wiedzy i przykład —
[AUTOMATION.md](./AUTOMATION.md), Etap 3. Gdy pakiet zaczyna być za duży, to
nie pakiet jest za duży — to dokumenty w nim naruszyły budżet rozmiaru.

---

## 5. Struktura katalogów

Warstwa jest wymiarem pierwszym, temat drugim.

```
repo/
├── CLAUDE.md                       # L0 — konstytucja (WERSJONOWANA, nie w .gitignore)
├── CONTEXT.md  ─┐                  # L1 — słownik (albo docs/CONTEXT.md)
├── PRODUCT.md  ─┘                  # L1 — kanon produktu
├── .claude/
│   ├── rules/                      # L0 — reguły po ścieżce
│   ├── agents/                     # L0 — definicje subagentów
│   └── skills/                     # L0 — wiedza proceduralna on-demand
└── docs/
    ├── 00_KNOWLEDGE-MAP.md         # punkt wejścia, indeks całej bazy
    ├── adr/                        # L1 — decyzje (jedno miejsce, całe repo)
    ├── product/                    # L1 — segmenty, persony, model przychodowy, ryzyka
    ├── technical/                  # L2 — architektura, moduły, kontrakty, runbooki
    │   ├── backend/
    │   ├── frontend/
    │   └── firmware/
    ├── plans/                      # L3 — plany, briefy, specyfikacje
    │   └── archive/                # L3 — zamknięte, zachowane
    └── research/                   # L4 — dowody, badania, analizy
        └── competitors/
```

**Jeden katalog `docs/adr/` jest domyślny, nie obowiązkowy.** Numeracja wspólna
dla decyzji biznesowych i technicznych ułatwia jedno pytanie: „wszystkie
zaakceptowane decyzje" nie wymaga przeszukania dwóch drzew.

Rozdzielenie na `docs/business/adr/` i `docs/technical/adr/` jest równie
uprawnionym wyborem, gdy odbiorcy obu typów decyzji faktycznie się różnią —
biznesowe czyta i akceptuje ktoś inny niż techniczne, więc osobne katalogi
odpowiadają osobnym procesom przeglądu, nie tylko estetyce. To nie jest
teoretyczna alternatywa: `waterworks-monitoring-platform` używa dokładnie tego
podziału, świadomie i konsekwentnie zapisanego w regule `architecture-decisions`
i w `CLAUDE.md` repozytorium.

**Rozstrzyga zawsze konwencja już zapisana w projekcie**, nie domyślna
rekomendacja tego pliku. Jeśli zakładasz bazę od zera i nie masz powodu do
podziału — zacznij od jednego katalogu, bo dodanie podziału później jest tanie,
a scalenie dwóch drzew z powrotem w jeden jest robotą do wykonania ręcznie.

---

## 6. Reguły niezmienne

Siedem reguł, które utrzymują bazę przy życiu. Łamanie każdej z nich ma
przewidywalny, konkretny koszt.

1. **Jeden fakt — jedno miejsce.** Wszędzie indziej link. *Koszt złamania:* N kopii rozjeżdża się w N wersji.
2. **Twierdzenie normatywne ma źródło.** Kod, ADR albo dowód L4. *Koszt:* agent powiela zmyślenie z pełną pewnością siebie.
3. **Decyzja mieszka w ADR.** Plan i dokument techniczny opisują skutek decyzji, nie podejmują jej. *Koszt:* decyzje podjęte w planach są niewidoczne i cicho unieważniane.
4. **Nic nie jest kasowane — jest zastępowane.** Dopisek w treści + przeniesienie pliku. *Koszt:* tracisz uzasadnienie „dlaczego nie zrobiliśmy tego tamtędy" i wracasz do odrzuconego pomysłu.
5. **Każdy dokument ma datę ostatniego przeglądu (`last_reviewed`).** Nie datę utworzenia. *Koszt:* nie da się odróżnić prawdy od archeologii.
6. **Dokument bez wpisu w mapie nie istnieje.** *Koszt:* sierota, której agent nigdy nie znajdzie, a człowiek będzie nadal aktualizował.
7. **Zmiana kodu objętego `applies_to` unieważnia weryfikację dokumentu.** *Koszt:* kontrakt L2 opisuje system sprzed trzech kwartałów, a agent buduje na jego podstawie.

Reguły 5 i 7 są egzekwowalne automatycznie — patrz [AUTOMATION.md](./AUTOMATION.md).
Reguły 1–4 i 6 egzekwuje review; walidator wykrywa tylko ich najbardziej
oczywiste naruszenia (sieroty, zduplikowane `id`, martwe linki).
