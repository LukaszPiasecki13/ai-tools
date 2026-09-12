---
id: spec-<slug>
title: <Zadanie — jedno zdanie o celu>
layer: L3
domain: <backend|frontend|firmware|product|market>
status: draft          # draft → active (w realizacji) → archived (zamknięte)
confidence: decision
owner: <imię>
created: <YYYY-MM-DD>
verified: <YYYY-MM-DD>
expires: <YYYY-MM-DD>  # po tej dacie dokument jest do archiwizacji albo odnowienia
related: [<id-kanonu>, <id-kontraktu>]
---

<!--
Specyfikacja zadania do zlecenia agentowi albo człowiekowi.

L3 z definicji WYGASA. Specyfikacja bez `expires` po pół roku będzie czytana
jako opis systemu (antywzorzec A6) i ktoś zbuduje na nieistniejącym komponencie.

Najważniejsza różnica między dobrą a złą specyfikacją dla agenta:
dobra rozstrzyga z góry wszystko, co dałoby się rozstrzygnąć, i nazywa wprost
to, czego nie rozstrzyga. Agent, który natrafi na lukę, nie zatrzyma się —
wypełni ją własnym założeniem i pójdzie dalej.
-->

# <Tytuł zadania>

| | |
|---|---|
| **Cel** | <co ma być prawdą po zakończeniu> |
| **Priorytet** | <wysoki / średni / niski> |
| **Blokuje** | <co czeka na to zadanie> |
| **Zablokowane przez** | <czego brakuje, żeby zacząć> |

## 1. Kontekst

<!--
Dlaczego to zadanie istnieje. Stan faktyczny z dowodami — ścieżki, liczby,
linki do kodu. Nie streszczaj dokumentów kanonu; linkuj do nich.
-->

## 2. Zakres

**W zakresie:**
- <konkretna rzecz do zrobienia>

**Poza zakresem:**
<!-- Równie ważne jak zakres. Agent bez tej listy rozszerzy zadanie
     "przy okazji" i review stanie się niemożliwe do przeprowadzenia. -->
- <czego NIE ruszać> — <dlaczego>

## 3. Decyzje już podjęte

<!--
Rozstrzygnięcia, których wykonawca NIE kwestionuje i o które NIE pyta.
Każda pozycja w trybie rozkazującym, z powodem.
To jest sekcja, która najbardziej skraca czas realizacji — każda pozycja
to pytanie, które nie zostanie zadane w połowie pracy.
-->

1. **<Decyzja>** — <powód>. Źródło: [ADR-<NNNN>](<ścieżka>)

## 4. Ograniczenia

<!-- Czego nie wolno naruszyć: reguły repo, niezmienniki, kompatybilność,
     bezpieczeństwo, budżet czasu. -->

- <ograniczenie>

## 5. Materiał wejściowy

<!--
Pakiet kontekstu: dokładna lista dokumentów i plików do przeczytania,
z podaniem PO CO. Lista bez uzasadnień zostanie przeczytana pobieżnie.
-->

| Dokument / plik | Po co |
|---|---|
| `<ścieżka>` | <czego tam szukać> |

## 6. Produkt zadania

<!-- Co konkretnie ma powstać: pliki, dokumenty, zmiany. Ścieżkami. -->

- `<ścieżka>` — <co zawiera>

## 7. Definicja ukończenia

<!--
Warunki sprawdzalne. "Działa poprawnie" nie jest warunkiem sprawdzalnym.
Ostatnie trzy pozycje są obowiązkowe w każdej specyfikacji — bez nich baza
wiedzy rozjeżdża się z kodem przy każdej iteracji (patrz AUTOMATION.md, Etap 4).
-->

- [ ] <warunek sprawdzalny>
- [ ] Testy przechodzą: `<polecenie>`
- [ ] Dokumenty L2 dopasowane przez `applies_to` zaktualizowane, `verified` podbite
- [ ] Decyzje nieodwracalne podjęte w trakcie mają ADR
- [ ] `kb_validate.py --strict` przechodzi

## 8. Otwarte punkty

<!--
Wypełniane w trakcie realizacji, nie na starcie.
Każdy punkt: waga · fakty · rekomendacja · konsekwencja alternatywy.
Status: OPEN → RESOLVED albo ACCEPTED-BY-USER.
-->

| # | Waga | Punkt | Rekomendacja | Status |
|---|---|---|---|---|
| 1 | blocker/major/minor | <opis> | <co proponujesz> | OPEN |
