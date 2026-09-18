# Szablony dokumentów bazy wiedzy

Gotowe do skopiowania. Każdy szablon ma komplet front-matter zgodny
z [METADATA.md](../METADATA.md) i komentarze `<!-- … -->` z instrukcją, które
usuwasz po wypełnieniu.

## Wybór szablonu

Cztery pliki, nie więcej. Trzy mają własną, nieprzenośną formę i front-matter
odmienny od reszty bazy — te zostają osobno. Wszystko inne, niezależnie od
warstwy, zaczyna się od jednego generycznego szablonu.

| Chcę zapisać… | Szablon | Warstwa | Gdzie |
|---|---|---|---|
| Punkt wejścia do całej bazy | [`KNOWLEDGE-MAP`](./KNOWLEDGE-MAP.template.md) | — | `docs/00_KNOWLEDGE-MAP.md` |
| Nazewnictwo domeny | [`CONTEXT`](./CONTEXT.template.md) | L1 | `CONTEXT.md` (korzeń) |
| Decyzję, której nie chcę tłumaczyć trzeci raz | [`adr`](./adr.template.md) | L1 | `docs/adr/` — nazwy wg reguły `architecture-decisions` |
| Cokolwiek innego: opis modułu, kontrakt API, runbook, zadanie do zlecenia, notatka z badania, eksperyment produktowy… | [`generic`](./generic.template.md) | L2 / L3 / L4 (do wyboru) | `docs/technical/`, `docs/plans/` albo `docs/research/` — wg warstwy |

### Dlaczego jeden szablon zamiast dziesięciu wyspecjalizowanych

Nie da się z góry przewidzieć wszystkich typów dokumentów, jakich zażąda
konkretny projekt — a szablon, którego nikt nie użył, jest samym kosztem bez
korzyści: trzeba go czytać, utrzymywać w spójności z resztą i tłumaczyć, po co
istnieje. `generic.template.md` ma wspólny, jednolity front-matter dla L2/L3/L4
(patrz [METADATA.md](../METADATA.md)) — jedyna różnica to `applies_to`, który ma
sens tylko dla L2 (dokument opisujący konkretny kod) — i podpowiedziami
w treści dobranymi wg warstwy; strukturę pliku projektujesz sam, doraźnie, dla
konkretnego dokumentu.

**Kiedy wydzielić nowy, dedykowany szablon:** dopiero gdy ten sam kształt
sekcji powtórzy się kilkukrotnie dla jednego typu dokumentu w praktyce — nie
zanim to nastąpi. Wydzielenie z realnego powtórzenia daje szablon dopasowany
do tego, czego faktycznie potrzebujesz; wydzielenie z góry daje zgadywankę.

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
   Powiązania między dokumentami linkują do `id` w treści, nie do ścieżek.
3. **Usuń niewypełnione sekcje.** Pusty nagłówek „Konsekwencje" jest gorszy niż
   jego brak — wygląda na kompletny dokument i zatrzymuje pytanie, które powinno
   paść.
4. **Nie kopiuj treści z innych dokumentów.** Link (`plik.md#kotwica`) zamiast
   powtórzenia.
5. **Oznaczaj niepewność w treści**, nie tylko w `type`:
   `> **[HIPOTEZA]** … Podstawa: … Niezweryfikowane wobec: …`
6. **Dopisz dokument do mapy wiedzy** w tym samym commicie.

## Kolejność zakładania bazy od zera

```
1. CONTEXT.md          ← nazewnictwo. Zawsze pierwsze.
2. docs/adr/0001-…     ← pierwsza decyzja, która była realnym wyborem
3. docs/00_KNOWLEDGE-MAP.md
4. CLAUDE.md           ← L0, ze wskazaniem punktu wejścia do bazy
5. walidator + pre-commit
```

Dokumenty L2 powstają wraz z kodem, który opisują — nie wcześniej. Kontrakt
napisany przed implementacją jest specyfikacją (L3), nie kontraktem.
