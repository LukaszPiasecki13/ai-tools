# Antywzorce bazy wiedzy dla agentów

Dziewięć sposobów, w jakie baza wiedzy przestaje działać dla agenta, mimo że
dla człowieka wygląda dobrze. Każdy: objaw → koszt → naprawa.

Kolejność nieprzypadkowa — od najkosztowniejszych.

---

## A1. Konstytucja poza repo albo ponad budżet

**Objaw.** `CLAUDE.md` i `.claude/` w `.gitignore`, albo trzymane w osobnym repo
narzędziowym i kopiowane ręcznie. Albo odwrotnie: są w repo, ale `CLAUDE.md`
rozrósł się do 500+ linii, bo każdy incydent dopisał regułę.

**Koszt.** Poza repo: agent w CI, w sesji chmurowej i u drugiej osoby dostaje
**inną wiedzę** niż lokalnie, reguły nie przechodzą przez review i nie da się
powiedzieć, z jaką konstytucją powstał commit sprzed miesiąca. Każdy pozostały
mechanizm automatyzacji stoi na tym fundamencie — i wali się razem z nim.
Ponad budżet: stały narzut w **każdym** wywołaniu agenta, a im dłuższa lista,
tym słabiej przestrzegana pojedyncza pozycja.

**Naprawa.** L0 wersjonowane w repo produktu. Repo narzędziowe trzyma
**szablony**, z których się generuje albo synchronizuje; instancja mieszka
w produkcie. Sekrety i ustawienia lokalne idą do `settings.local.json`, które
zostaje w `.gitignore`. Budżet twardy: `CLAUDE.md` ≤ 300 linii. Wiedza
wyzwalana ścieżką → `.claude/rules/` z `paths`; wiedza proceduralna wywoływana
na żądanie → skill. `CLAUDE.md` zostaje z **zakazami, trybami pracy
i wskazaniem punktu wejścia do bazy**.

---

## A2. Monolit

**Objaw.** Jeden dokument na 1000+ linii („plan biznesowy", „dokumentacja
architektury") zawierający wizję, analizę rynku, architekturę, kosztorys i roadmapę.

**Koszt.** Agent albo ładuje ~25 tys. tokenów, żeby poznać jedną liczbę, albo nie
ładuje nic. Nikt nie utrzymuje takiego pliku sekcja po sekcji, więc części
rozjeżdżają się między sobą — w jednym dokumencie żyją dwie sprzeczne wersje tej
samej liczby i obie wyglądają wiarygodnie.

**Naprawa.** Rozbicie po adresowalności, nie po długości: każdy rozdział, do
którego ktoś trafi osobno, to osobny plik. Oryginał zostaje stroną-rozdzielaczem
z linkami. Kolejność rozbijania: najpierw części o największym tempie zmian
(ceny, konkurencja, roadmapa), na końcu stabilna wizja.

---

## A3. Brak punktu wejścia

**Objaw.** Dziesiątki plików w `docs/`, żadnego indeksu. Pusty `README.md` w korzeniu.

**Koszt.** Agent zaczyna od `grep`. Znajduje dokument pasujący słowem kluczowym,
a nie dokument właściwy — najczęściej nieaktualny szkic albo plan zamiast
kontraktu. Człowiek dopisuje nowy plik obok, bo nie wie, że istnieje starszy na
ten sam temat.

**Naprawa.** `docs/00_KNOWLEDGE-MAP.md` jako jedyny punkt wejścia, wskazany
z `CLAUDE.md`. Tabela generowana z front-matter (Etap 2 w [AUTOMATION.md](./AUTOMATION.md)).

---

## A4. Dwie konwencje albo jeden fakt w wielu miejscach

**Objaw.** Szablon ADR mówi `adr-NNN-tytul.md` z sekcjami po angielsku, a w repo
leżą pliki `0001-tytul.md` z sekcjami po polsku. Reguła obejmuje `docs/adr/**`,
a ADR-y leżą w `docs/business/adr/`. Albo, ten sam problem na poziomie treści
zamiast konwencji: cena abonamentu w dokumencie produktowym, w ADR o modelu
przychodowym i w planie biznesowym; numer pinu GPIO w dokumencie sprzętowym
i w opisie modułu.

**Koszt.** Dla konwencji: reguła **nie ładuje się nigdy** — glob nie trafia.
Wygląda na aktywną, jest martwa. Agent tworzy nowy dokument wg szablonu,
niezgodny z resztą repo, i baza ma dwie równoległe konwencje, z których żadna
nie jest egzekwowana. Dla faktów: N kopii rozjeżdża się do N wersji — pytanie
tylko kiedy. Agent trafia losowo, a człowiek poprawia jedną i jest przekonany,
że zaktualizował bazę.

**Naprawa.** Jedna konwencja, wygrywa ta faktycznie używana w repo — szablon
dopasowany do rzeczywistości, nie odwrotnie. Globy reguł sprawdzane przeciwko
realnym ścieżkom przy każdej zmianie struktury katalogów — walidator to wykrywa
(`W105`). Dla faktów: jedno miejsce kanoniczne, wszędzie indziej **głęboki
link** (`plik.md#kotwica`). Jeśli powtórzenie jest konieczne dla czytelności,
zapisz je jako cytat z jawnym wskazaniem źródła — nie jako niezależne zdanie.

---

## A5. Decyzja poza rejestrem decyzji

**Objaw.** Rozstrzygnięcie zapisane w planie, w komentarzu do zadania albo
w akapicie dokumentu technicznego. ADR nie powstał, bo „to była oczywista sprawa".
Wariant tego samego problemu od strony L4: analiza konkurencji kończy się
rekomendacją, rekomendacja jest traktowana jak ustalenie, ustalenie nigdy nie
trafia do ADR.

**Koszt.** Decyzja jest niewidoczna dla kogokolwiek, kto nie czytał tego
konkretnego pliku. Zostaje cicho unieważniona przy następnej zmianie, bo nikt nie
wie, że była decyzją. Uzasadnienie i odrzucone warianty giną — i po pół roku
wraca pomysł, który raz już odrzucono ze słusznego powodu. Dla L4 konkretnie:
nikt nie wie, czy rekomendacja obowiązuje — połowa zespołu (i agentów) działa
wg niej, połowa nie, a zmiana zdania nie ma gdzie zostać zapisana.

**Naprawa.** Decyzja nieodwracalna + nieoczywista + z realną alternatywą → ADR.
Wszystkie trzy warunki naraz; jeśli któregoś brak, ADR jest zbędnym szumem.
Pozostałe dokumenty (w tym L4) opisują **skutek** decyzji i linkują do ADR —
L4 dostarcza materiału, obowiązek powstaje wyłącznie w L1. Badanie kończące się
rekomendacją ma jawny następny krok: ADR albo świadome odłożenie z datą.

---

## A6. Plan udający stan

**Objaw.** Dokument „plan wdrożenia" z etapami oznaczonymi ✅, czytany jako opis
systemu. Brak rozróżnienia między „zaplanowane", „zrobione" a „zrobione inaczej,
niż planowano".

**Koszt.** Agent czyta plan, uznaje, że etap istnieje, i buduje na komponencie,
którego nie ma — albo który powstał z innym interfejsem. Klasa błędów najtrudniejsza
do wykrycia, bo agent działa pewnie i spójnie z materiałem, który dostał.

**Naprawa.** Plan to L3, dokument roboczy. Stan opisuje L2 z linkami do kodu.
Ukończenie etapu planu **wymaga** powstania albo aktualizacji dokumentu L2 —
dopiero wtedy wolno postawić ✅. Sam znaczek w planie nie jest dowodem istnienia.

---

## A7. Zgnilizna linków

**Objaw.** Linki względne o złej głębokości (`../../` zamiast `../../../`),
odwołania do plików przeniesionych albo nigdy nieistniejących.

**Koszt.** Agent traktuje link jako obietnicę istnienia. Martwy link to albo
zmarnowana tura, albo — gorzej — wniosek, że komponent nie istnieje, i próba
zbudowania go od zera. Zgnilizna narasta cicho: 2–3 linki na reorganizację
katalogów, kilkanaście w rok.

**Naprawa.** Walidacja linków w pre-commicie (`E005`, `E006`). To jedyny
antywzorzec w pełni rozwiązywalny automatem i dlatego pierwszy do wdrożenia —
najtańszy zysk w całej liście.

---

## A8. Dokument bez daty weryfikacji

**Objaw.** Brak metadanych albo wyłącznie data utworzenia.

**Koszt.** Nie da się odróżnić prawdy od archeologii. Agent traktuje analizę
konkurencji sprzed dwóch lat tak samo jak wczorajszy pomiar — jedno i drugie to
dla niego po prostu tekst w repo.

**Naprawa.** `last_reviewed` obowiązkowe. Podbija je ten, kto **sprawdził**, nie
ten, kto poprawił literówkę.

---

## A9. Mieszanie faktu, decyzji i hipotezy

**Objaw.** W jednym akapicie: „rynek to 1300–1700 gmin" (szacunek),
„startujemy od temperatury i ciśnienia" (decyzja), „koszt sprzętu 1,4–3,5 tys."
(przedział z niepewnością). Wszystkie trzy zdania wyglądają identycznie.

**Koszt.** Agent cytuje hipotezę jako fakt w materiale zewnętrznym. Albo buduje
plan na liczbie, która była zgadywana. To najczęstsza droga do zmyśleń
o wysokiej pewności — model nie zmyślił, tylko wiernie powtórzył niezweryfikowane
założenie.

**Naprawa.** Jawne znaczniki w treści przy każdym twierdzeniu niepewnym:
`> **[HIPOTEZA]** … Podstawa: … Niezweryfikowane wobec: …`. Front-matter nie
rozróżnia dziś poziomów pewności (`type` opisuje rodzaj dokumentu, nie jego
pewność) — patrz METADATA.md §2, rozważane rozszerzenie `type: hypothesis`.

---

## Szybki audyt

Pięć poleceń. Każde odpowiada na jedno pytanie, którego nie widać gołym okiem.

```bash
# A1 — czy konstytucja jest wersjonowana i pod budżetem?
git check-ignore -v CLAUDE.md .claude/ ; git ls-files CLAUDE.md .claude/ | head
wc -l CLAUDE.md

# A2 — monolity
find docs -name '*.md' -exec wc -l {} + | sort -rn | head -10

# A3 — punkt wejścia
ls docs/*KNOWLEDGE-MAP* docs/README.md README.md 2>/dev/null

# A4 — czy globy reguł trafiają w cokolwiek
grep -rn '^paths:' .claude/rules/

# A7 + A8 — martwe linki i brak metadanych
python scripts/kb_validate.py --root . --format text
```
