# Automatyzacja bazy wiedzy

Droga od katalogu plików do bazy, która sama się pilnuje i zasila pipeline
wytwarzania produktu. Pięć etapów, każdy działa samodzielnie i każdy jest
warunkiem wstępnym następnego.

**Zasada nadrzędna:** nie automatyzuj tworzenia wiedzy, zanim nie zautomatyzujesz
jej **weryfikacji**. Generator dokumentacji podpięty do niesprawdzanej bazy
produkuje nieaktualne treści szybciej, niż ktokolwiek zdąży je przeczytać.

---

## Etap 0 — Struktura (fundament)

**Cel:** każdy dokument ma warstwę, metadane i miejsce w mapie.

- Warstwy L0–L4 i katalogi wg [ARCHITECTURE.md](./ARCHITECTURE.md).
- Front-matter we wszystkich plikach pod `docs/` wg [METADATA.md](./METADATA.md).
- `docs/00_KNOWLEDGE-MAP.md` jako jedyny punkt wejścia.
- **`CLAUDE.md` i `.claude/` wersjonowane w repo produktu.**

Ostatni punkt bywa pomijany, a jest warunkiem koniecznym całej reszty. Konfiguracja
agenta w `.gitignore` oznacza: brak jej w CI, brak w sesjach chmurowych, brak
u drugiej osoby, brak w review, brak historii zmian. Dopóki L0 nie jest w repo,
nie ma czego automatyzować — każde uruchomienie agenta startuje z innej wiedzy.

**Miara ukończenia:** `kb_validate.py` przechodzi bez błędów (`E*`).

---

## Etap 1 — Walidacja (pierwszy realny zysk)

**Cel:** baza nie gnije po cichu.

### Pre-commit

```yaml
# .pre-commit-config.yaml
  - repo: local
    hooks:
      - id: kb-validate
        name: walidacja bazy wiedzy
        entry: python scripts/kb_validate.py --root . --strict
        language: system
        files: ^(docs/|CLAUDE\.md|CONTEXT\.md|PRODUCT\.md|\.claude/)
        pass_filenames: false
```

`--strict` → kod wyjścia 1 przy błędach `E*`, 0 przy samych ostrzeżeniach.
Ostrzeżenia w pre-commicie nie blokują nigdy: pierwsza blokada na „dokument
wymaga przeglądu" kończy się `--no-verify`, a potem wyłączeniem hooka.

### CI

Ten sam skrypt na pull requeście, dodatkowo `--report` z podsumowaniem ostrzeżeń
w komentarzu PR. Rozjazdy (`W102`) mają wtedy najlepszy moment na naprawę — obok
diffu, który je spowodował.

### Testy walidatora

`python3 scripts/test_kb_validate.py` — zestaw przypina reguły, które łatwo
„naprawić" w złą stronę. Najważniejsza: kotwice GitHuba **nie zwijają** kolejnych
myślników, więc nagłówek z em-dashem daje kotwicę z `--`. Uproszczenie tego
miejsca zamienia poprawną bazę w kilkanaście fałszywych alarmów. Uruchamiaj po
każdej zmianie walidatora.

### Cotygodniowy przegląd

Raport `--format json` → lista przeterminowanych i rozjechanych dokumentów. To
jest jedyna lista zadań utrzymaniowych bazy, jakiej potrzebujesz.

**Miara ukończenia:** zero błędów `E*` na `main`; liczba `W102` mierzona i malejąca.

---

## Etap 2 — Generowana mapa wiedzy

**Cel:** indeks przestaje być ręcznie utrzymywanym plikiem, który zawsze
odstaje o trzy dokumenty.

Mapa ma dwie części:

- **ręczna** — nawigacja, pakiety kontekstu, „od czego zacząć" (to pisze człowiek),
- **generowana** — pełna tabela dokumentów z front-matter, między znacznikami:

```markdown
<!-- KB-INDEX:START -->
… tabela generowana: id | tytuł | warstwa | status | zweryfikowano …
<!-- KB-INDEX:END -->
```

Generator (`kb_validate.py --write-index`) nadpisuje wyłącznie obszar między
znacznikami. Dzięki temu sierota (`W103`) staje się niemożliwa: dokument, który
istnieje, jest w tabeli automatycznie.

**Miara ukończenia:** `W103` = 0 trwale, bez ręcznej pracy.

---

## Etap 3 — Pakiety kontekstu (pobieranie po zakresie)

**Cel:** agent dostaje dokładnie te dokumenty, które go obowiązują — ani jednego
więcej.

Dwa mechanizmy, uzupełniające się:

**Automatyczny, po ścieżce.** `.claude/rules/*.md` z polem `paths` ładują się same,
gdy agent dotknie pasującego pliku. Tu trzymasz to, co obowiązuje **zawsze** przy
danym typie kodu (standardy, checklisty bezpieczeństwa). Budżet: krótko, bo to
wchodzi do kontekstu bez pytania.

**Na żądanie, po zakresie zadania.** Agent zna listę plików do zmiany →
dopasowuje ją do `applies_to` → ładuje trafione dokumenty L2 + wskazane przez nie
`related`. To pokrywa wiedzę projektową, która jest za duża, żeby ładować ją zawsze.

Nazwane pakiety dla powtarzalnych zadań zapisz w mapie wiedzy:

```markdown
## Pakiety kontekstu

**`backend-feature`** — nowa funkcja w backendzie
1. `CONTEXT.md` (słownik)
2. `docs/technical/backend/01_architektura.md`
3. dokument modułu dopasowany przez `applies_to`
4. ADR-y `active` z `domain: backend`
```

**Miara ukończenia:** agent rozpoczynający typowe zadanie nie używa wyszukiwania
pełnotekstowego do znalezienia kontekstu.

---

## Etap 4 — Pętla zwrotna: zadanie → kod → baza

**Cel:** baza aktualizuje się jako element definicji ukończenia, nie jako
osobne zadanie „kiedyś potem".

Naturalnym miejscem wpięcia jest skill [`prepare-work`](../prepare-work/SKILL.md)
— wariant pełny ma obowiązkową Fazę 11 (Dokumentacja), wariant uproszczony
zasadę 12. **Wpięcie nie jest wykonane**; poniższa lista jest gotowa do dopisania
tam, gdy uznasz to za właściwe. Warunek wyzwalania trzymaj po stronie repo
docelowego (`docs/00_KNOWLEDGE-MAP.md` albo front-matter z `layer:`), żeby
projekty bez bazy warstwowej nie płaciły za nic.

```
   ┌──────────────────────────────────────────────────────────┐
   │                                                          │
   ▼                                                          │
L1/L2 ──► specyfikacja (L3) ──► implementacja ──► test ──► delta L1/L2
kanon       pakiet kontekstu      kod + testy            ADR / kontrakt
i kontrakty  jako wejście                                 verified++
```

**Reguła twarda:** zadanie jest ukończone, gdy zawiera deltę w bazie wiedzy albo
jawne stwierdzenie „brak zmian w bazie" z uzasadnieniem. Bez tego każda iteracja
powiększa dystans między kodem a wiedzą, a agent w kolejnej iteracji dostaje
gorszy materiał wejściowy niż w poprzedniej. To jest dokładnie ten mechanizm,
przez który baza wiedzy degraduje się mimo dobrych intencji.

Konkretne wpięcia:

| Moment | Działanie |
|---|---|
| Start zadania | Załaduj pakiet kontekstu. Sprzeczność między dokumentami → otwarty punkt, nie cichy wybór. |
| Decyzja w trakcie | Nieodwracalna i nieoczywista → ADR **teraz**, nie po zakończeniu. |
| Zmiana zachowania systemu | Aktualizacja dokumentu L2 w tym samym commicie co kod. |
| Nowe pojęcie w rozmowie | Wpis do `CONTEXT.md` od razu. Termin nienazwany do jutra będzie miał trzy nazwy. |
| Zamknięcie zadania | `verified` podbite w dotkniętych dokumentach; dokument L3 → `archived`. |

### Definicja ukończenia — fragment do wklejenia

```markdown
- [ ] Kod + testy przechodzą
- [ ] Dokumenty L2 dopasowane przez `applies_to` są zaktualizowane i mają nowe `verified`
- [ ] Nowe/zmienione decyzje nieodwracalne mają ADR
- [ ] Nowe pojęcia domenowe są w CONTEXT.md
- [ ] `kb_validate.py --strict` przechodzi
- [ ] Dokument zadania (L3) ma status `archived`
```

**Miara ukończenia:** commity zmieniające kod z `applies_to` zmieniają też
odpowiadający dokument albo jawnie deklarują, że nie muszą.

---

## Etap 5 — Wytwarzanie sterowane bazą

Dopiero gdy etapy 0–4 działają, baza może **generować pracę**, a nie tylko ją
opisywać. Kolejność ma znaczenie — generowanie z niesprawdzanej bazy propaguje
błędy szybciej, niż człowiek je wyłapie.

| Zastosowanie | Wejście | Wyjście |
|---|---|---|
| Generowanie briefu zadania | `PRODUCT.md` + ADR + luka w kontrakcie L2 | gotowa specyfikacja L3 |
| Wykrywanie luk | moduły kodu bez dokumentu L2 | lista brakujących kontraktów |
| Audyt spójności | `CONTEXT.md` vs nazewnictwo w kodzie | lista rozjazdów terminologicznych |
| Onboarding nowego repo | `PRODUCT.md` + `CONTEXT.md` + szablony | szkielet bazy nowego produktu |
| Przegląd decyzji | ADR-y z `review_after` minionym | lista decyzji do potwierdzenia |
| Pakiet sprzedażowy / raport | `PRODUCT.md` + L4 dowody | materiał zewnętrzny bez zmyśleń |

Największy zysk w kontekście **wielu produktów**: `PRODUCT.md` + `CONTEXT.md` +
zestaw ADR to kompletny, przenośny „genom" produktu. Nowy produkt startuje z tych
samych szablonów i tej samej konstytucji L0 — zmienia się wyłącznie treść L1.

---

## Czego nie automatyzować

| Nie automatyzuj | Powód |
|---|---|
| Pisania ADR bez człowieka | ADR zapisuje **wybór**, a wyboru nie da się wyprowadzić z kodu. Agent przygotowuje szkic i alternatywy; decyzję i status `accepted` nadaje człowiek. |
| Słownika z kodu | Nazwy w kodzie są skutkiem słownika, nie jego źródłem. Odwrócenie kierunku utrwala każdą złą nazwę. |
| Podbijania `verified` przy każdym commicie | Data weryfikacji, która podnosi się sama, przestaje cokolwiek znaczyć. Podbija ją ten, kto faktycznie sprawdził. |
| Kasowania „nieaktualnych" dokumentów | Automat nie odróżnia nieaktualnego od niewygodnego. Archiwizacja — tak; kasowanie — nigdy. |
| Streszczania L4 do L1 | Skrót dowodu gubi zastrzeżenia i niepewność, a zostawia liczbę, która wygląda na pewnik. |

---

## Metryki zdrowia bazy

Mierz kwartalnie. Cztery liczby wystarczą; piąta zaczyna być raportem dla samego
raportu.

| Metryka | Definicja | Próg alarmowy |
|---|---|---|
| **Rozjazd** | `W102` / liczba dokumentów L2 | > 30% |
| **Przeterminowanie** | `W101` / liczba dokumentów L1+L2 | > 25% |
| **Pokrycie kontraktami** | moduły kodu z dokumentem L2 / wszystkie moduły | < 70% |
| **Naruszenia rozmiaru** | dokumenty ponad twardym limitem | > 0 |

Wszystkie cztery liczy `kb_validate.py --format json`. Jeśli rosną mimo przeglądów,
przyczyną jest prawie zawsze pominięty Etap 4 — baza aktualizowana osobno od kodu
zawsze przegra z tempem kodu.
