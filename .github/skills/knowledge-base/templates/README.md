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
| Decyzję, której nie chcę tłumaczyć trzeci raz | [`adr`](./adr.template.md) | L1 | `docs/adr/` — nazwy wg reguły `architecture-decisions` |
| Kto jest klientem i co go boli | [`segment-persona`](./segment-persona.template.md) | L1 | `docs/product/segments/` |
| Ryzyko, które może wywrócić projekt | [`risk-register`](./risk-register.template.md) | L1 | `docs/product/ryzyka.md` |
| Jak zbudowany jest moduł / komponent | [`component`](./component.template.md) | L2 | `docs/technical/<obszar>/` |
| Kontrakt API / formatu wiadomości / schematu | [`interface-contract`](./interface-contract.template.md) | L2 | `docs/technical/<obszar>/` |
| Procedurę operacyjną krok po kroku | [`runbook`](./runbook.template.md) | L2 | `docs/technical/runbooks/` |
| Zadanie do zlecenia agentowi albo człowiekowi | [`spec`](./spec.template.md) | L3 | `docs/plans/` |
| Hipotezę produktową do sprawdzenia | [`experiment`](./experiment.template.md) | L3→L4 | `docs/research/experiments/` |
| Wynik badania, analizy, wywiadu | [`research-note`](./research-note.template.md) | L4 | `docs/research/` |

## Miejsce wśród istniejących komponentów toolkitu

Dwa z tych szablonów dotykają artefaktów, które toolkit już obsługuje gdzie
indziej. Żaden ich nie zastępuje — dokładają wyłącznie **front-matter** wymagany
przez bazę wiedzy. Przy rozbieżności wygrywa komponent z kolumny „autorytet":

| Artefakt | Autorytet formy i nazewnictwa | Co dokłada ten katalog |
|---|---|---|
| ADR | reguła `architecture-decisions`, komenda `/adr`, kryteria w skillu `domain-modeling` | [`adr.template.md`](./adr.template.md) — front-matter, polskie nagłówki sekcji |
| Słownik | `CONTEXT-FORMAT.md` w skillu `domain-modeling` | [`CONTEXT.template.md`](./CONTEXT.template.md) — front-matter; treść haseł bez zmian |

Ma to znaczenie praktyczne: dwa konkurencyjne szablony tego samego artefaktu to
antywzorzec [A4](../ANTIPATTERNS.md). Jeśli kiedykolwiek te pliki zaczną mówić
co innego niż wskazany autorytet, to **te pliki** są do poprawy.

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
