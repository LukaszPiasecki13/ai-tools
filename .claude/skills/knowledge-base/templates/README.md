# Szablony dokumentów bazy wiedzy

Gotowe do skopiowania. Każdy szablon ma komplet front-matter zgodny
z [METADATA.md](../METADATA.md) i komentarze `<!-- … -->` z instrukcją, które
usuwasz po wypełnieniu.

## Wybór szablonu

| Chcę zapisać… | Szablon | Warstwa | Gdzie |
|---|---|---|---|
| Punkt wejścia do całej bazy | [`KNOWLEDGE-MAP`](./KNOWLEDGE-MAP.template.md) | — | `docs/00_KNOWLEDGE-MAP.md` |
| Czym jest produkt, dla kogo, co jest poza zakresem | [`PRODUCT`](./PRODUCT.template.md) | L1 | `PRODUCT.md` (korzeń) |
| Nazewnictwo domeny | [`CONTEXT`](./CONTEXT.template.md) | L1 | `CONTEXT.md` (korzeń) |
| Decyzję, której nie chcę tłumaczyć trzeci raz | [`adr`](./adr.template.md) | L1 | `docs/adr/NNNN-tytul.md` |
| Kto jest klientem i co go boli | [`segment-persona`](./segment-persona.template.md) | L1 | `docs/product/segments/` |
| Ryzyko, które może wywrócić projekt | [`risk-register`](./risk-register.template.md) | L1 | `docs/product/ryzyka.md` |
| Jak zbudowany jest moduł / komponent | [`component`](./component.template.md) | L2 | `docs/technical/<obszar>/` |
| Kontrakt API / formatu wiadomości / schematu | [`interface-contract`](./interface-contract.template.md) | L2 | `docs/technical/<obszar>/` |
| Procedurę operacyjną krok po kroku | [`runbook`](./runbook.template.md) | L2 | `docs/technical/runbooks/` |
| Zadanie do zlecenia agentowi albo człowiekowi | [`spec`](./spec.template.md) | L3 | `docs/plans/` |
| Hipotezę produktową do sprawdzenia | [`experiment`](./experiment.template.md) | L3→L4 | `docs/research/experiments/` |
| Wynik badania, analizy, wywiadu | [`research-note`](./research-note.template.md) | L4 | `docs/research/` |

## Jeden szablon na artefakt

Szablony w tym katalogu są **kanoniczne**. Jeżeli inny plik w repo opisuje ten
sam artefakt, ma linkować tutaj, a nie utrzymywać drugiej wersji:

| Artefakt | Forma (kanon) | Kiedy go użyć (osobny dokument) |
|---|---|---|
| ADR | [`adr.template.md`](./adr.template.md) | [`domain-modeling/ADR-FORMAT.md`](../../domain-modeling/ADR-FORMAT.md) — kryteria „czy to zasługuje na ADR", numeracja |
| Słownik | [`CONTEXT.template.md`](./CONTEXT.template.md) | [`domain-modeling/CONTEXT-FORMAT.md`](../../domain-modeling/CONTEXT-FORMAT.md) — jak pisać hasła i listę `_Unikać_` |

Podział jest celowy: **kiedy** i **jak** to dwa różne pytania, ale **forma** ma
jedno źródło. Dwa szablony tego samego artefaktu to antywzorzec
[A4](../ANTIPATTERNS.md) — nowe dokumenty rozjeżdżają się z istniejącymi
i żadna konwencja nie jest egzekwowana.

## Zasady wspólne

1. **Front-matter jest obowiązkowy.** Plik bez niego nie przejdzie walidacji (`E001`).
2. **`id` jest stabilne.** Nadajesz raz; przeniesienie pliku go nie zmienia.
   Linki `related` wskazują `id`, nie ścieżki.
3. **Usuń niewypełnione sekcje.** Pusty nagłówek „Konsekwencje" jest gorszy niż
   jego brak — wygląda na kompletny dokument i zatrzymuje pytanie, które powinno
   paść.
4. **Nie kopiuj treści z innych dokumentów.** Link (`plik.md#kotwica`) zamiast
   powtórzenia.
5. **Oznaczaj niepewność w treści**, nie tylko w `confidence`:
   `> **[HIPOTEZA]** … Podstawa: … Niezweryfikowane wobec: …`
6. **Dopisz dokument do mapy wiedzy** w tym samym commicie.

## Kolejność zakładania bazy od zera

```
1. CONTEXT.md          ← nazewnictwo. Zawsze pierwsze.
2. PRODUCT.md          ← co budujemy i dla kogo
3. docs/adr/0001-…     ← pierwsza decyzja, która była realnym wyborem
4. docs/00_KNOWLEDGE-MAP.md
5. CLAUDE.md           ← L0, ze wskazaniem punktu wejścia do bazy
6. walidator + pre-commit
```

Dokumenty L2 powstają wraz z kodem, który opisują — nie wcześniej. Kontrakt
napisany przed implementacją jest specyfikacją (L3), nie kontraktem.
