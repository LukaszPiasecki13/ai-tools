# Dokąd zmierza branża IT: automatyzacja, workflow i budowa firmy od zera

**Raport analityczny — wrzesień 2026**
Odbiorca: programista, który jednocześnie zakłada i prowadzi firmę.

---

## Spis treści

- [0. Jak czytać ten raport](#0-jak-czytać-ten-raport)
- [1. Streszczenie: osiem tez](#1-streszczenie-osiem-tez)
- [Część I — Diagnoza: co faktycznie wiadomo](#część-i--diagnoza-co-faktycznie-wiadomo)
  - [1.1 Adopcja jest niemal powszechna, zaufanie spada](#11-adopcja-jest-niemal-powszechna-zaufanie-spada)
  - [1.2 Produktywność: dwa obozy badań i to, co je godzi](#12-produktywność-dwa-obozy-badań-i-to-co-je-godzi)
  - [1.3 Wąskie gardło przesunęło się z pisania na weryfikację](#13-wąskie-gardło-przesunęło-się-z-pisania-na-weryfikację)
  - [1.4 Dług utrzymaniowy: co pokazuje GitClear, a czego nie](#14-dług-utrzymaniowy-co-pokazuje-gitclear-a-czego-nie)
  - [1.5 Bezpieczeństwo: nowa powierzchnia ataku](#15-bezpieczeństwo-nowa-powierzchnia-ataku)
  - [1.6 Rynek pracy rozdwoił się](#16-rynek-pracy-rozdwoił-się)
  - [1.7 Warstwa agentowa się standaryzuje](#17-warstwa-agentowa-się-standaryzuje)
  - [1.8 Ekonomia modeli: koszt inferencji spada, to nie jest przewaga](#18-ekonomia-modeli-koszt-inferencji-spada-to-nie-jest-przewaga)
- [Część II — Co z tego wynika dla Ciebie jako dewelopera](#część-ii--co-z-tego-wynika-dla-ciebie-jako-dewelopera)
- [Część III — Co z tego wynika dla Ciebie jako właściciela firmy](#część-iii--co-z-tego-wynika-dla-ciebie-jako-właściciela-firmy)
- [Część IV — Gdzie mogę się mylić: scenariusze i sygnały ostrzegawcze](#część-iv--gdzie-mogę-się-mylić-scenariusze-i-sygnały-ostrzegawcze)
- [Część V — Plan działania 30 / 90 / 365 dni](#część-v--plan-działania-30--90--365-dni)
- [Załącznik A — Tabela tez i status weryfikacji](#załącznik-a--tabela-tez-i-status-weryfikacji)
- [Załącznik B — Źródła](#załącznik-b--źródła)

---

## 0. Jak czytać ten raport

### Skala pewności

Każda teza jest oznaczona poziomem dowodu. To nie ozdobnik — to najważniejsza część raportu,
bo w tej dziedzinie 90% tekstów cytuje te same trzy liczby bez sprawdzenia, skąd pochodzą.

| Poziom | Znaczenie |
|--------|-----------|
| **[A]** | Badanie pierwotne, dokument prawny albo dane telemetryczne z dużej próby — zweryfikowane bezpośrednio u źródła |
| **[B]** | Wiarygodny raport branżowy lub źródło wtórne; albo źródło pierwotne z realnym konfliktem interesów (dostawca sprzedaje rozwiązanie problemu, który opisuje) |
| **[C]** | Dane samoraportowane, anegdota, prognoza analityczna albo liczba, której nie udało się doprowadzić do źródła pierwotnego |

Traktuj **[C]** jako hipotezę do zweryfikowania na własnych danych, nigdy jako podstawę decyzji,
której nie da się cofnąć.

### Dlaczego liczby w tej branży trzeba sprawdzać — konkretny przykład

W trakcie zbierania materiału trafiłem na tekst opisujący „analizę LinearB 8,1 mln pull requestów
w 4800+ organizacjach", z której rzekomo wynika, że *„programiści czują się o 20% szybsi, a są
o 19% wolniejsi"*.

To są **co do cyfry** wyniki badania METR z lipca 2025 — innej metodologii (RCT na 16 osobach
i 246 zadaniach), innej próby, innego typu danych. Prawdopodobieństwo, że analiza telemetrii
8,1 mln PR-ów niezależnie odtworzy dokładnie tę samą parę liczb, jest znikome. To niemal na pewno
zlepienie dwóch źródeł w jedno przez autora tekstu albo przez warstwę streszczającą.

**Wniosek praktyczny:** zanim oprzesz decyzję na liczbie z bloga, doprowadź ją do dokumentu
źródłowego. Jeśli się nie da — to nie jest dana, to jest plotka o danej. W tym raporcie liczby
bez ścieżki do źródła są oznaczone **[C]** albo ich nie ma.

### Czego ten raport nie robi

Nie prognozuje, „czy AI zastąpi programistów". To pytanie jest źle postawione i nie da się na nie
odpowiedzieć dowodowo. Raport odpowiada na pytanie węższe i użyteczniejsze: **co się faktycznie
zmieniło w sposobie wytwarzania i sprzedawania oprogramowania, i jakie decyzje to zmienia u Ciebie.**

---

## 1. Streszczenie: osiem tez

1. **Adopcja narzędzi AI jest niemal powszechna, a zaufanie do nich spada.** To nie jest sprzeczność
   — to opis narzędzia, które pomaga wystarczająco często, by go używać, i zawodzi wystarczająco
   często, by mu nie ufać. **[A]**
2. **Nie ma jednego „efektu AI na produktywność".** Jest funkcja trzech zmiennych: doświadczenia,
   znajomości bazy kodu i progu jakości. Ta sama metodologia daje +26% i −19% w zależności od
   ustawienia tych zmiennych. **[A]**
3. **Wąskie gardło przeniosło się z pisania kodu na decyzję, czy kod jest bezpieczny do wdrożenia.**
   Potwierdzają to trzy niezależne źródła danych. **[A]**
4. **Koszt utrzymania rośnie szybciej niż koszt wytworzenia maleje** — duplikacja i churn w górę,
   refactoring w dół. Dowód jest korelacyjny, nie przyczynowy, a źródło ma konflikt interesów. **[B]**
5. **Powstała nowa, realnie eksploatowana powierzchnia ataku**: prompt injection przez treści,
   które agent czyta (issue, README, zależności). Są udokumentowane incydenty w łańcuchu dostaw
   z 2026 r. **[A]**
6. **Rynek pracy nie zapadł się — rozdwoił.** Popyt na seniorów i specjalizacje (AI, security,
   infra, dane) rośnie; wejście dla juniorów istotnie się zwęziło. **[A]**
7. **Dla firmy: model nie jest przewagą, a szybkość budowy przestała być przewagą.** Przewagą są
   dane z użycia, bycie systemem zapisu dla procesu klienta, dystrybucja w niszy i zgodność
   regulacyjna. **[B]**
8. **Największym ryzykiem biznesowym nie jest konkurencja, tylko retencja.** Produkty AI-native
   mają dramatycznie gorsze utrzymanie przychodu niż klasyczny B2B SaaS — z wyjątkiem
   wysokiego segmentu cenowego. **[A]**

---

# Część I — Diagnoza: co faktycznie wiadomo

## 1.1 Adopcja jest niemal powszechna, zaufanie spada

**[A]** Badanie Stack Overflow: **84%** respondentów używa lub planuje używać narzędzi AI, przy
czym zaufanie do poprawności generowanego kodu spadło do **29%**, z 40% rok wcześniej (−11 p.p.).
Dla porównania w 2023 r. używało lub planowało używać ok. 70%, przy zaufaniu ok. 40%.
([Stack Overflow](https://stackoverflow.blog/2026/02/18/closing-the-developer-ai-trust-gap/))

**[B]** Źródła wtórne podają dodatkowo, że ok. **46%** aktywnie nie ufa wynikom, a tylko ok. **3%**
deklaruje wysokie zaufanie. Nie udało mi się potwierdzić tych dwóch liczb w publikacji Stack
Overflow, więc traktuj je jako kierunkowe.

**[B]** DORA (ok. 5000 respondentów + ponad 100 godzin wywiadów jakościowych) raportuje adopcję
rzędu **90%** wśród programistów. ([DORA 2025](https://dora.dev/dora-report-2025/))

### Dlaczego to nie jest sprzeczność

Rosnąca adopcja przy spadającym zaufaniu wygląda odwrotnie do typowego cyklu przyjmowania
technologii — zwykle używanie buduje zaufanie. Tutaj dzieje się coś innego: im więcej ktoś używa
narzędzia, tym lepiej zna jego tryby awarii. Spadek zaufania to nie jest rozczarowanie, to jest
**kalibracja**. Ludzie, którzy narzędzia używają najwięcej, oceniają je najostrożniej.

To pierwszy sygnał, który powinieneś przenieść na własny warsztat: **kompetencją nie jest
używanie AI, tylko wiedza, kiedy jej wynik odrzucić.**

---

## 1.2 Produktywność: dwa obozy badań i to, co je godzi

To jest miejsce, gdzie najczęściej czyta się jedną stronę sporu i wyciąga wniosek na całą branżę.
Obie strony mają solidne dowody i obie są prawdziwe — w swoich warunkach.

### Obóz „AI spowalnia"

**[A] METR, lipiec 2025** — randomizowane badanie kontrolowane. 16 doświadczonych deweloperów
open source, 246 realnych zadań w **ich własnych** repozytoriach (średnio 22 tys. gwiazdek,
ponad 1 mln linii kodu). Zadania losowo przydzielane do grupy „wolno używać AI" i „nie wolno".

Wynik: z dostępem do AI zadania trwały **19% dłużej**. Przed badaniem ci sami ludzie prognozowali
przyspieszenie o 24%, a po wykonaniu pracy oceniali, że byli szybsi o 20%. Kierunek subiektywnej
oceny był odwrotny do faktu.
([METR](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/))

**Zastrzeżenia, które podają sami autorzy** (i które większość cytujących pomija):

- Badanie **nie** dowodzi, że AI nie przyspiesza deweloperów w ogóle — tylko w tym ustawieniu.
- Nie można wykluczyć efektu uczenia się: uczestnicy mieli w większości poniżej ~50 h praktyki z Cursorem.
- Próba to ochotnicy — możliwy błąd doboru.
- Repozytoria miały wysokie standardy jakości i dużo niejawnych wymagań, co działa na niekorzyść AI.
- Narzędzia z okna luty–czerwiec 2025 (Cursor Pro, Claude 3.5/3.7); to w tej dziedzinie odległa epoka.

### Obóz „AI przyspiesza"

**[B] GitHub + Accenture + Microsoft** — również RCT, ale na innej populacji i z innymi metrykami.
Wzrost ukończonych zadań o **26,08%** (proxy: PR-y, commity, buildy). W samym Accenture przyrost
PR-ów tygodniowo wyniósł **7,5–8,7%**, przy **+84%** udanych buildów. Największe zyski odnotowali
**mniej doświadczeni** deweloperzy.
([GitHub](https://github.blog/news-insights/research/research-quantifying-github-copilots-impact-in-the-enterprise-with-accenture/))

Zastrzeżenie: metryki są proxy ilościowym. Więcej PR-ów nie znaczy więcej dostarczonej wartości,
a badanie prowadził dostawca narzędzia.

### Co godzi te wyniki

Nie ma jednej liczby „efektu AI". Jest funkcja co najmniej trzech zmiennych:

| Zmienna | AI pomaga | AI przeszkadza |
|---------|-----------|----------------|
| **Doświadczenie** | junior / mid | senior z ugruntowanym warsztatem |
| **Znajomość bazy kodu** | nowy dla Ciebie kod, nowy język, nowy framework | kod, który znasz na pamięć |
| **Próg jakości** | prototyp, skrypt, narzędzie wewnętrzne | dojrzałe repo z niejawnymi wymaganiami |
| **Typ pracy** | greenfield, boilerplate, testy, migracje mechaniczne | zmiana przecinająca architekturę |

**[B] DORA** opisuje ten sam mechanizm w skali organizacji: AI działa jak **wzmacniacz**, nie jak
przyspieszacz. Podnosi przepustowość i **jednocześnie** podnosi niestabilność dostarczania. W zespole
ze słabym procesem efektem jest szybsze produkowanie kiepskiej pracy.
Raport DORA z 2026 r. („ROI of AI-assisted Software Development") dokłada do tego **model krzywej J**:
po wdrożeniu najpierw jest spadek produktywności, dopiero potem zwrot.
([DORA 2025](https://dora.dev/dora-report-2025/), [DORA ROI 2026](https://dora.dev/ai/roi/report/))

> **Konsekwencja dla Ciebie:** jeżeli mierzysz sobie „czy AI mi pomaga" wrażeniem — mierzysz źle.
> Badanie METR pokazuje 39-punktowy rozjazd między odczuciem a faktem u ludzi, którzy są w tym
> dobrzy. Zaufaj tylko licznikowi czasu albo metryce dostarczania.

---

## 1.3 Wąskie gardło przesunęło się z pisania na weryfikację

Trzy niezależne źródła, trzy różne metodologie, ten sam wniosek. To najmocniej udowodniona teza
w tym raporcie.

**[A] CircleCI**, telemetria ponad **28 mln** przebiegów CI:

- średnia przepustowość **+59% r/r** — największy wzrost aktywności od pierwszej edycji raportu w 2019 r.,
- ale rozkład jest skrajnie nierówny: top 5% zespołów podwoiło przepustowość (6,8 → 13,4 uruchomień
  dziennie), **mediana zespołu urosła o 4%**, dolne 25% nie urosło wcale,
- kluczowe: przepustowość na **gałęzi głównej** dla mediany zespołu **spadła o 7%**, wskaźniki
  powodzenia są na pięcioletnim minimum, a czasy odtworzenia rosną,
- przepustowość na gałęziach feature wzrosła o ok. 50% — **i niemal nic z tego nie przełożyło się
  na wdrożone zmiany**.

([CircleCI 2026](https://circleci.com/resources/2026-state-of-software-delivery-q2-pulse/))

**[B] DORA**: wzrost przepustowości przy równoczesnym wzroście niestabilności.

**[B] Thoughtworks Technology Radar v34** (kwiecień 2026) nazywa to zjawisko *cognitive debt* —
długiem poznawczym — i formułuje rekomendację, która brzmi jak cofnięcie się o dekadę, a nie jak
nowość: **powrót do fundamentów inżynierskich**. Radar ostrzega wprost, że „w miarę jak agenty
stają się sprawniejsze, ludzie są niebezpiecznie kuszeni, by wyjść z pętli".
([Thoughtworks](https://www.thoughtworks.com/about-us/news/2026/combat-ai-cognitive-debt-radar-v34))

### Dlaczego to jest najważniejsza pojedyncza obserwacja w raporcie

Jeśli generowanie kodu tanieje o rząd wielkości, a weryfikacja nie tanieje wcale, to **koszt
weryfikacji staje się dominującym kosztem wytwarzania oprogramowania**. Wszystko inne wynika z tego
jednego zdania:

- dlatego testy z „dobrej praktyki" awansowały do rangi infrastruktury,
- dlatego specyfikacja wraca do łask (spec-driven development),
- dlatego umiejętność czytania cudzego kodu jest dziś wyżej wyceniana niż umiejętność pisania własnego,
- dlatego przewagą zespołu jest CI, a nie liczba rąk.

---

## 1.4 Dług utrzymaniowy: co pokazuje GitClear, a czego nie

**[B] GitClear, „The Maintainability Gap"** — analiza **623 mln** zmian w kodzie z lat 2023–2026:

| Sygnał | Zmiana |
|--------|--------|
| Duplikacja bloków kodu | **+81%** (40,3 → 73,0 na mln zmienionych linii) |
| Copy/paste w obrębie commita | **+41%** — dziś 5× częstszy niż refactoring |
| Refactoring (przenoszenie kodu) | spadek z **21%** (2022) do **3,8%** (2026 YTD) |
| Utrzymanie kodu starszego niż rok | **−74%** (1,7% → 0,46% zmian) |
| Konstrukcje maskujące błędy | **+47%** |
| Churn dwutygodniowy | **+15%** |
| Wywołania funkcji międzyplikowe (miara reużycia) | **−35%** |

([GitClear](https://www.gitclear.com/the_ai_code_quality_maintainability_gap))

### Krytyka, którą trzeba dołożyć

1. **To korelacja, nie przyczynowość** — i autorzy sami to piszą: *„Nagłówkiem nie jest »AI pisze
   zły kod«"*. Wskazują na domyślny sposób pracy z AI, nagradzający kod atomowy, nie na technologię.
2. **Konflikt interesów.** GitClear (część GitKraken) sprzedaje analitykę jakości kodu. Raport
   diagnozuje problem, który firma rozwiązuje komercyjnie. To nie dyskwalifikuje danych, ale nakazuje
   ostrożność przy interpretacji.
3. **Brak alternatywnych wyjaśnień.** Raport nie rozważa, że w tym samym okresie zmienił się skład
   próby, struktura zespołów, albo że spadek „utrzymania starego kodu" wynika z tempa powstawania
   nowego, a nie z zaniedbania.
4. **Metryki strukturalne ≠ jakość.** Duplikacja bywa świadomym wyborem (rozprzęganie modułów).
   Wzrost o 81% jest jednak zbyt duży, by wytłumaczyć go samą zmianą stylu.

**Wniosek wyważony:** dane są wystarczająco spójne z resztą obrazu (CircleCI: spadek przepustowości
na main; DORA: wzrost niestabilności), by traktować je poważnie, ale **nie są dowodem przyczynowym**.
Najbezpieczniejsza interpretacja: domyślny, nieopanowany workflow z agentem produkuje kod o gorszej
utrzymywalności. To jest problem procesu, nie modelu — a więc **do rozwiązania po Twojej stronie**.

---

## 1.5 Bezpieczeństwo: nowa powierzchnia ataku

### Kod generowany bywa funkcjonalny i niebezpieczny jednocześnie

**[B] Veracode, GenAI Code Security Report** — 80 wystandaryzowanych zadań, ponad 100 modeli:
**45%** próbek wprowadza podatność z listy OWASP Top 10. Java wypada najgorzej (72% niepowodzeń),
XSS (CWE-80) — 86%. Aktualizacja z wiosny 2026: poprawność składniowa przekracza 95%, ale **wskaźnik
zdawalności testów bezpieczeństwa stoi w miejscu na poziomie ok. 55% od dwóch lat** — gdy w promptcie
nie ma jawnych wytycznych bezpieczeństwa.
([Veracode 2025](https://www.veracode.com/resources/analyst-reports/2025-genai-code-security-report/),
[aktualizacja 2026](https://www.veracode.com/blog/spring-2026-genai-code-security/))

To jest najważniejsza asymetria w całym temacie: **modele poprawiły się w „czy działa" i nie
poprawiły się w „czy jest bezpieczne"**. Funkcjonalność jest weryfikowalna przez uruchomienie.
Bezpieczeństwo nie jest.

### Prompt injection: realnie eksploatowany, nie teoretyczny

Simon Willison opisuje mechanizm jako **„śmiertelną triadę"** (*lethal trifecta*): system jest
podatny, gdy równocześnie ma (1) dostęp do prywatnych danych, (2) ekspozycję na niezaufane treści
i (3) kanał wyprowadzenia danych na zewnątrz. Kluczowa uwaga: **nie ma tu odpowiednika
parametryzacji zapytań SQL** — nie istnieje mechanizm, który oddzieli „dane" od „instrukcji",
bo dla modelu to jest ten sam strumień tekstu.
([Simon Willison](https://simonw.substack.com/p/fireside-chat-about-agentic-engineering))

**[A/B] Udokumentowane incydenty z 2026 r.:**

- **Clinejection** — ujawniony 9 lutego 2026, eksploatowany w praktyce 17 lutego 2026. Łańcuch:
  prompt injection przez **tytuł zgłoszenia GitHub** → wyciek tokenu publikacji npm ze środowiska
  workflow → zatrucie cache artefaktów CI → publikacja złośliwego pakietu do npm. Do rozpoczęcia
  ataku wystarczyło **założyć jedno zgłoszenie** — uprawnienie, które ma każde darmowe konto GitHub.
- **Mastra AI** — 17 czerwca 2026, przejęcie konta opiekuna i ponowna publikacja ponad **140 pakietów**
  w scope npm z podstawioną zależnością typosquat.
- **Zatrute pliki kontekstu** — pakiety podrzucające `.cursorrules` i `CLAUDE.md` z instrukcjami
  ukrytymi w znakach zerowej szerokości; po otwarciu projektu asystent „wykonuje skan bezpieczeństwa",
  który wyprowadza lokalne sekrety.

([CSA Labs](https://labs.cloudsecurityalliance.org/research/csa-research-note-claude-code-github-action-prompt-injection/),
[CSO Online](https://www.csoonline.com/article/4167465/supply-chain-attacks-take-aim-at-your-ai-coding-agents.html))

**Zmiana modelu zagrożenia:** wcześniej atakujący potrzebował uprawnień do zapisu w zaufanym
repozytorium. Dziś potrzebuje możliwości **utworzenia zgłoszenia albo pull requesta**.

> To dotyczy Cię bezpośrednio. W repozytorium `ai-tools` trzymasz pliki, które propagują się do
> wszystkich Twoich projektów — `CLAUDE.md`, reguły, skille, hooki. To jest dokładnie ten wektor.
> Każda zależność, która może dopisać coś do pliku kontekstu, ma potencjalnie wpływ na to, co robi
> Twój agent w każdym repozytorium.

---

## 1.6 Rynek pracy rozdwoił się

### Dane twarde: młodzi w zawodach eksponowanych na AI

**[A] Stanford Digital Economy Lab, „Canaries in the Coal Mine", aktualizacja z sierpnia 2026.**
Dane płacowe ADP: **4,6 mln pracowników**, ponad **730 zawodów**, do połowy 2026 r.

- Zatrudnienie osób w wieku **22–25 lat** w zawodach silnie eksponowanych na AI jest **19% niżej**
  niż wynikałoby z trendu ich rówieśników w zawodach mniej eksponowanych (w lipcu 2025 r. luka
  wynosiła 15% — **rozjazd się pogłębia**).
- U pracowników doświadczonych **nie ma analogicznej luki**.
- **Nie ma dowodów na powszechne wypieranie ludzi z rynku pracy** w skali gospodarki.
- Mechanizm to **ograniczenie rekrutacji**, nie zwolnienia.
- Spadki koncentrują się tam, gdzie AI **automatyzuje** zadania; tam, gdzie **wspomaga** — zatrudnienie
  jest płaskie lub rośnie.
- Spada zatrudnienie w pracy opartej na wiedzy **skodyfikowanej**; rośnie tam, gdzie liczy się
  wiedza **milcząca** (tacit).

Autorzy explicite zastrzegają: to **nie jest dowód rozstrzygający**. Różnice w wykształceniu
częściowo tłumaczą lukę, część trendów wyprzedza upowszechnienie generatywnej AI, a wyniki mogą
nie uogólniać się poza próbę ADP. Stopy procentowe tłumaczą niewiele, bo rozjazd pogłębiał się
**po** szczycie stóp.
([Stanford](https://digitaleconomy.stanford.edu/news/canariesaug26/))

### Dane z rynku ofert

**[B] The Pragmatic Engineer, „State of the software engineering job market in 2026"**
(źródła: TrueUp, Workforce.ai, Indeed, FRED):

- Oferty w USA rosną; największe firmy technologiczne rekrutują o ok. **20% więcej** niż rok temu,
  ale wciąż poniżej szczytu z 2021 r.
- Rozjazd geograficzny: USA i UK w górę, Kanada płasko, **Niemcy i Francja w dół**.
- Rozjazd wewnątrz Big Tech: Apple +10%, Google +5%, Microsoft −1,1%, Amazon −1,3%; Meta urosła
  o ok. 20%, po czym zwolniła 10% załogi.
- Najszybciej rosną: fintech (Ramp +94%, Rippling +55%), **security** (Wiz +84%),
  obserwowalność/infra AI (Datadog +68%), narzędzia projektowe (Figma +41%).
- **Spada** popyt na mobile i frontend. Rośnie gwałtownie na role związane z AI.

([Pragmatic Engineer](https://newsletter.pragmaticengineer.com/p/state-of-the-job-market-2026))

### Jak to czytać

Popularna teza „rynek juniorów się zawalił" jest **przesadzona w formie, w jakiej krąży**, ale
kierunkowo prawdziwa. Liczby w rodzaju „−67% ofert entry-level" krążą bez ścieżki do źródła
pierwotnego **[C]** — nie opierałbym na nich decyzji. Za to dane Stanforda są solidne i mówią rzecz
węższą, lecz istotniejszą: **zwęziło się wejście, nie rynek**.

Mechanizm jest zrozumiały i dla Ciebie jako przyszłego pracodawcy ma konsekwencję: praca, którą
kiedyś dostawał junior — proste taski, boilerplate, poprawki — jest właśnie tą pracą, którą agent
robi najlepiej. Znika **szczebel**, nie zawód. Kto wejdzie wyżej, ma rynek. Kto wchodzi dołem, ma
problem.

---

## 1.7 Warstwa agentowa się standaryzuje

**[B]** **MCP** (Model Context Protocol, otwarty przez Anthropic pod koniec 2024) osiągnął rząd
**110 mln pobrań SDK miesięcznie** i ponad **10 tys.** wdrożeń serwerów w firmach (dane na kwiecień
2026, z 97 mln w lutym 2026). Wspierają go Anthropic, OpenAI, Google, Microsoft i Amazon.

**[B]** **A2A** (Agent-to-Agent) osiągnął wersję **1.0** w kwietniu 2026, jest wspierany przez ponad
**150 organizacji** i został przekazany Linux Foundation.

Podział ról jest czytelny: **MCP standaryzuje dostęp agenta do narzędzi i danych**, **A2A —
komunikację między agentami**.
([przegląd protokołów, arXiv](https://arxiv.org/html/2505.02279v1))

### Dlaczego to jest ważniejsze, niż wygląda

Standaryzacja interfejsu to moment, w którym warstwa przestaje być przewagą konkurencyjną i staje
się infrastrukturą. Tak samo stało się z HTTP, POSIX i S3. Dwie konsekwencje:

1. **Dla dewelopera:** integracja z narzędziami przestaje być projektem, a staje się konfiguracją.
   Wartość przenosi się z „umiem spiąć" na „wiem, co spiąć i jak to zabezpieczyć".
2. **Dla firmy:** jeśli Twoja przewaga polegała na integracji z systemem X, standaryzacja ją zeruje.
   Jeśli polega na tym, że **jesteś systemem X** — standaryzacja ją wzmacnia, bo obniża koszt
   wejścia do Twojego produktu.

---

## 1.8 Ekonomia modeli: koszt inferencji spada, to nie jest przewaga

**[B]** Skala spadku: GPT-4 startował w marcu 2023 r. z ceną **30 USD / 60 USD** za milion tokenów
(wejście/wyjście). Modele szybkie z 2026 r. są w okolicach **0,10 USD / 0,40 USD** — rząd spadku
o **ponad 99%** w trzy lata. Tylko między początkiem 2025 a początkiem 2026 ceny API spadły o ok. 80%.
Hostowane modele o otwartych wagach plasują się w przedziale ok. 0,07–0,90 USD za milion tokenów.

Zastrzeżenie **[C]**: konkretne cenniki zmieniają się co kwartał i pochodzą z zestawień wtórnych.
Przed policzeniem jednostkowej ekonomii sprawdź aktualny cennik u dostawcy. Kierunek jest pewny,
poziom — nie.

**Co z tego wynika:**

- **Koszt inferencji przestaje być barierą wejścia.** Jeśli Twój model biznesowy zakładał, że
  konkurent nie zbuduje tego samego, bo to za drogie — ta bariera zniknęła.
- **I odwrotnie:** to samo dotyczy Ciebie. Rzeczy, które rok temu były nieopłacalne, dziś są.
  Przeliczaj odrzucone pomysły co kilka miesięcy.
- **Marża się poprawia.** ICONIQ prognozuje marżę brutto produktów AI: 45% (2025) → **53% (2026)**
  → 59% (2027). To wciąż istotnie poniżej klasycznego SaaS-a — jeśli wyceniasz firmę mnożnikiem
  SaaS-owym, popełniasz błąd. **[B]**
  ([ICONIQ](https://www.iconiq.com/growth/reports/state-of-ai-2026))

---

# Część II — Co z tego wynika dla Ciebie jako dewelopera

## 2.1 Co rośnie w cenie, a co tanieje

| Tanieje (nie buduj na tym tożsamości zawodowej) | Drożeje (tu inwestuj) |
|---|---|
| Pisanie boilerplate'u, CRUD-ów, mapowań | Ocena, **czy** wygenerowany kod jest poprawny i bezpieczny |
| Znajomość składni kolejnego frameworka | Projektowanie granic modułów i kontraktów |
| Przepisywanie kodu między językami | Pisanie specyfikacji na tyle precyzyjnej, że jest wykonywalna |
| Szukanie rozwiązania na Stack Overflow | Debugowanie systemu, którego kodu nie napisałeś |
| Tempo pisania | Projektowanie testów, które faktycznie łapią błędy |
| — | **Modelowanie zagrożeń** i higiena łańcucha dostaw |
| — | Wiedza dziedzinowa (milcząca), której nie ma w dokumentacji |

Ostatni wiersz jest najmocniej udokumentowany: dane Stanforda pokazują spadek zatrudnienia w pracy
opartej na wiedzy **skodyfikowanej** i wzrost tam, gdzie liczy się wiedza **milcząca**. Model umie
wszystko, co jest zapisane. Nie umie tego, czego nikt nie zapisał — na przykład dlaczego czujnik
ciśnienia na tej konkretnej hydroforni daje fałszywe odczyty przy mrozie.

## 2.2 System pracy z agentami, który ma pokrycie w dowodach

Wszystkie poniższe punkty mają źródło w Części I — to nie są preferencje.

**1. Testy przestały być opcjonalne — i to jest zmiana ekonomiczna, nie moralna.**
Willison ujmuje to wprost: testy są dziś „praktycznie darmowe", bo pisze je agent, a jednocześnie
są jedynym mechanizmem, który skaluje weryfikację razem z generowaniem. Bez nich pracujesz
dokładnie w scenariuszu opisanym przez CircleCI: dużo kodu na gałęziach feature, nic na `main`.
Czerwony/zielony TDD działa z agentem szczególnie dobrze, bo daje mu **falsyfikowalny** warunek
stopu zamiast „wygląda dobrze".

**2. Weryfikuj ręcznie to, czego test nie łapie.** Uruchom serwer, uderz `curl`-em, obejrzyj wynik.
Testy sprawdzają to, co przewidziałeś; awarie biorą się z tego, czego nie przewidziałeś.

**3. Jakość istniejącego kodu jest mnożnikiem.** Agent podąża za wzorcami w repozytorium
„niemal co do joty". Oznacza to, że **bałagan się zwielokrotnia, a porządek też**. Godzina spędzona
na wyprostowaniu wzorca w module zwraca się na każdym kolejnym pliku, który agent w nim napisze.
To jest najlepszy dostępny argument za refaktoryzacją — i jednocześnie wyjaśnienie danych GitCleara.

**4. Zacznij od specyfikacji, nie od promptu — ale traktuj to jako eksperyment, nie standard.**
Thoughtworks opisuje *spec-driven development* jako przepływ **spec → plan → implementacja**,
z narzędziami takimi jak Amazon Kiro, GitHub spec-kit czy Tessl Framework. **Sprostowanie:**
w Radarze v34 technika ta siedzi w pierścieniu **„Assess"** — najostrożniejszym z czterech
(Assess/Trial/Adopt/Hold) — nie w centrum radaru, jak wcześniej sugerowałem. Sami autorzy nazywają
te przepływy „rozbudowanymi i opiniotwórczymi" i wprost wskazują otwarte problemy: trudno
zrecenzować sam plik specyfikacji, a nie jest jasne, dla kogo właściwie przeznaczone są generowane
artefakty pośrednie.
([Thoughtworks — Spec-driven development](https://www.thoughtworks.com/radar/techniques/spec-driven-development))

Powód, dla którego mimo to warto spróbować, zostaje ten sam: specyfikacja jest artefaktem, który
da się zrecenzować **zanim** powstanie kod. Recenzja specyfikacji na jednej stronie kosztuje ułamek
recenzji diffa na 900 linii — ale „Assess" oznacza: sprawdź na małym projekcie, zanim postawisz
na tym proces całego zespołu.

**5. Uruchamiaj agenty w piaskownicy.** Kontener, ograniczone sekrety, ograniczona sieć. Po incydencie
Clinejection traktowanie treści z zewnątrz (issue, README zależności, komentarze w PR) jako danych
zaufanych jest po prostu błędem konfiguracyjnym.

**6. Sprawdzaj triadę przy każdej automatyzacji.** Zanim uruchomisz agenta w CI, zadaj trzy pytania:
czy ma dostęp do prywatnych danych? czy widzi treści z zewnątrz? czy ma czym je wyprowadzić?
Dwie odpowiedzi „tak" to ostrzeżenie. Trzy — to podatność, niezależnie od tego, jak dobry jest prompt.

**7. Twarde ograniczenia zapisuj jako hooki, nie jako prose'y w `CLAUDE.md`.**
To zresztą reguła, którą masz już zapisaną w `CLAUDE.md` tego repozytorium — i jest zgodna z tym,
co Thoughtworks nazywa *agent harness*: kontrolą wyprzedzającą (skille, specyfikacje) i zwrotną
(testy mutacyjne, CI), które wymuszają korektę **przed** recenzją człowieka. Instrukcja to kontekst;
tylko hook to egzekucja.

## 2.3 Higiena poznawcza: realne ryzyko, ostrożny dowód

**[B]** Gergely Orosz formułuje to najostrzej: *„jeśli używasz AI i życie robi się dużo łatwiejsze,
to pytanie brzmi — czy na pewno wystarczająco się starasz?"*. Sam nie używa AI do pisania tekstów
(wyłączył nawet Grammarly), żeby nie stracić warsztatu, a w kodowaniu świadomie akceptuje, że
zdolność ręcznego pisania mu się pogorszy. Jego rada: **wybierz świadomie umiejętności, które chcesz
zachować, i używaj ich mimo dostępności narzędzi.**

**[C]** Badanie MIT Media Lab („Your Brain on ChatGPT") wprowadziło pojęcie *długu poznawczego*
i pokazało w EEG słabszą łączność sieci neuronalnych u osób piszących eseje z LLM. **Traktuj to
ostrożnie**: preprint, mała próba, zadanie eseistyczne (nie inżynierskie), a sam zespół MIT
opublikował wytyczne odradzające interpretacje typu „AI niszczy mózg".

Wniosek, który wytrzymuje obie te uwagi: **ryzyko atrofii jest realne, dowód na jego skalę słaby.**
Racjonalna odpowiedź to nie abstynencja, tylko świadomy wybór — ustal, które umiejętności są Twoim
kapitałem (u Ciebie prawdopodobnie: architektura, debugowanie systemów wbudowanych, projektowanie
schematu danych), i te ćwicz bez asysty.

## 2.4 Czego nie robić

- **Nie mierz produktywności wrażeniem.** METR: 39 punktów rozjazdu między odczuciem a faktem.
- **Nie akceptuj kodu, którego nie umiesz obronić na recenzji.** Jeśli nie potrafisz wyjaśnić,
  dlaczego ta linia tam jest — nie jest gotowa, tylko wygenerowana.
- **Nie stawiaj kariery na byciu szybkim.** Szybkość jest tym, co zostało utowarowione.
- **Nie ignoruj tego, że domyślny workflow degraduje utrzymywalność.** Dane GitCleara to ostrzeżenie
  o procesie, nie o narzędziu.
- **Nie ufaj liczbom bez źródła** — łącznie z tymi z tego raportu oznaczonymi **[C]**.

---

# Część III — Co z tego wynika dla Ciebie jako właściciela firmy

## 3.1 Co przestało być przewagą

**Szybkość budowy.** Skoro koszt wytworzenia spadł u Ciebie, spadł też u każdego konkurenta.
Czas od pomysłu do działającego MVP przestał być wyróżnikiem — stał się stawką wejścia.

**Dostęp do modelu.** Model jest towarem: ceny spadają, dostawcy są zamienni, a warstwa integracji
się standaryzuje (MCP, A2A). Produkt, który jest rozpoznawalnie cienką nakładką na model,
nie ma czym się bronić.

**[C]** Krąży prognoza, że „80% startupów-nakładek upadnie do końca 2026". Nie doprowadziłem jej
do źródła pierwotnego — traktuj jako retorykę, nie dane. **Kierunek** jest jednak zgodny z całą
resztą materiału i z tym, co mówią inwestorzy.

## 3.2 Co jest przewagą

Zgodnie z tym, na co wskazują a16z i Sequoia, przewaga siedzi w aktywach, których dostawca modelu
nie skopiuje, wypuszczając funkcję **[B]**:

**1. Dane powstające z użycia produktu.** Nie „mamy dane" — zbiór danych sam w sobie jest słabym
fosem. Przewagą są dane, które **przyrastają, im dłużej klient korzysta**, i których nie da się
kupić ani wygenerować.

**2. Bycie systemem zapisu dla procesu klienta.** Jeśli Twój produkt jest miejscem, gdzie proces
się *odbywa* (a nie tylko go podgląda), wymiana Cię oznacza wymianę procesu. To najtrwalszy rodzaj
przewagi w B2B.

**3. Dystrybucja w niszy, po którą duzi nie sięgną.** Nie dlatego, że nie potrafią — dlatego, że
rynek jest dla nich za mały, a koszt dotarcia za wysoki.

**4. Zgodność regulacyjna jako fosa.** Niedoceniane, a w Polsce w 2026 r. wyjątkowo aktualne
(patrz 3.5). Wymagania, które dla dużego gracza są kosztem, dla wyspecjalizowanego dostawcy
są barierą wejścia chroniącą go przed konkurencją.

**[B] Y Combinator.** W liście „Requests for Startups" na jesień 2026 r. YC kieruje founderów
w stronę problemów **świata fizycznego i infrastruktury** — obronność, opieka zdrowotna, opieka nad
seniorami, zbieranie danych z rzeczywistości, „system operacyjny świata fizycznego" — oraz osobno
w stronę **infrastruktury zgodności regulacyjnej przemyślanej od zera pod AI**.
([YC RFS](https://www.ycombinator.com/rfs))

> **Sprostowanie do popularnej interpretacji — i przykład metody z sekcji 0.**
> W obiegu wtórnym te same zapytania streszcza się hasłami „wygrywa głębia, nie szybkość"
> oraz „zastępuj usługę, nie wspomagaj narzędziem". Pierwotnie zacytowałem je tak w tym raporcie.
> Po sprawdzeniu strony źródłowej: **YC tego tak nie formułuje**, a w punkcie o edukacji mówi
> wręcz odwrotnie — szuka narzędzia, które *„nie zastępuje nauczycieli, tylko czyni ich
> skuteczniejszymi"*. Kierunek na dziedzinę, świat fizyczny i regulacje jest w RFS realnie obecny;
> ramka „głębia kontra szybkość" jest dopisana przez komentatorów. **[C]**
>
> Zostawiam to sprostowanie w tekście zamiast po cichu poprawić, bo pokazuje dokładnie ten
> mechanizm, przed którym ostrzega sekcja 0: teza brzmiąca sensownie i zgodna z resztą obrazu
> przeszła u mnie bez sprawdzenia, bo *pasowała*. To jest najczęstszy tryb awarii przy pisaniu
> takich raportów — i przy pracy z agentem.

> ### Uwaga wprost o Twoim projekcie
>
> `waterworks-monitoring-platform` trafia w tę tezę niemal wzorcowo, i warto, żebyś to widział,
> zanim zaczniesz szukać „czegoś bardziej AI-owego":
>
> - **nisza, po którą duzi nie sięgną** — małe gminy i ZWiK to rynek za mały dla dużego dostawcy SCADA,
> - **wiedza milcząca** — zachowanie czujników na konkretnych obiektach nie jest nigdzie zapisane,
>   więc żaden model tego nie wie,
> - **system zapisu** — historia pomiarów i alarmów per obiekt to dokładnie ten typ danych,
>   który przyrasta z użyciem i którego nie da się przenieść do konkurenta,
> - **fosa regulacyjna** — zaopatrzenie w wodę i ścieki to sektor objęty NIS2/KSC (punkt 3.5),
> - **sprzętowa bariera wejścia** — gateway na obiekcie to koszt, który konkurent też musi ponieść.
>
> To nie jest projekt „mało nowoczesny", bo nie jest zbudowany wokół modelu. To jest projekt
> ustawiony pod **te przewagi, które według materiału z 2026 r. faktycznie się bronią**.

## 3.3 Najważniejsza liczba w tym raporcie dla Ciebie: retencja

**[A] ChartMogul**, dane z ok. **3500 firm** (≈2700 B2B SaaS, 600 B2C, 200 AI-native), próg 250 tys.
USD ARR:

| Typ firmy | NRR (mediana) | GRR (mediana) |
|---|---|---|
| B2B SaaS | **82%** | — |
| B2C SaaS | 49% | — |
| **AI-native** | **48%** | **40%** |

I rozbicie AI-native **po punkcie cenowym** — to jest właściwa lekcja:

| Cena | NRR | GRR |
|---|---|---|
| **> 250 USD/mies.** | **85%** | **70%** |
| 50–249 USD/mies. | 61% | 45% |
| **< 50 USD/mies.** | **32%** | **23%** |

([ChartMogul](https://chartmogul.com/reports/saas-retention-the-ai-churn-wave/))

**Efekt „turysty AI":** w tanim, samoobsługowym segmencie klient kupuje, żeby sprawdzić, a nie żeby
używać. Widzi siebie jako testującego, nie jako klienta.

Zastrzeżenie autorów: w wyższych progach ARR próbka spada do ok. 50 firm na przedział, więc wyniki
są **kierunkowe, nie rozstrzygające**. Jest też sygnał poprawy: mediana GRR firm AI-native wzrosła
w ciągu roku z 27% do 40% — turyści odpadli, zostali ci, którzy wdrażają produkcyjnie.

**Wnioski operacyjne:**

1. **Tani self-service dla produktu AI jest pułapką.** GRR 23% oznacza, że przez rok tracisz trzy
   czwarte przychodu i musisz je odbudować samą sprzedażą. To nie jest biznes, to jest bieżnia.
2. **Wyżej wyceniony produkt dla mniejszej liczby klientów, którzy wdrażają go w proces, jest
   bezpieczniejszy** niż tania skala. To argument za sprzedażą do gmin/ZWiK, a nie za
   „samoobsługowym dashboardem za 29 zł".
3. **Mierz GRR od pierwszego dnia**, nie tylko ARR. ARR rośnie także wtedy, gdy produkt jest dziurawy.

## 3.4 Model cenowy się przesuwa

**[B] ICONIQ**, zmiana w ciągu sześciu miesięcy:

- wycena oparta na zużyciu: 35% → **42%**,
- wycena oparta na wyniku: 18% → **23%**,
- **37%** firm planuje zmienić model cenowy w ciągu roku — powody: oczekiwania klientów, presja
  konkurencji, marża.

Logika jest prosta: przy koszcie zmiennym (inferencja) cena za stanowisko odrywa się od kosztu
obsługi. Klient natomiast coraz częściej chce płacić za **wynik**, bo wynik jest tym, co kupuje.

Dla monitoringu wodociągów naturalną jednostką jest **obiekt** (przepompownia, hydrofornia, SUW),
ewentualnie kanał pomiarowy — nie użytkownik. Gmina nie kupuje dostępów, kupuje nadzór nad
infrastrukturą. Cena za obiekt jest jednocześnie zrozumiała dla kupującego i skorelowana z Twoim
kosztem (sprzęt + transmisja + retencja danych).

## 3.5 Regulacje: to jest Twoja przewaga, nie tylko koszt

### NIS2 / ustawa o KSC — dotyczy Twoich klientów bezpośrednio

**[A]** Nowelizacja ustawy o krajowym systemie cyberbezpieczeństwa (wdrożenie NIS2) **weszła w życie
3 kwietnia 2026 r.** Sektory objęte obejmują wprost **zaopatrzenie w wodę oraz ścieki**.
Ustawa dotyczy przede wszystkim średnich i dużych podmiotów, wyjątkowo także małych i mikro.
Podnosi kary administracyjne i wzmacnia odpowiedzialność osobistą członków organów zarządzających.
([Schoenherr](https://www.schoenherr.eu/content/poland-new-cybersecurity-rules-in-poland-implementation-of-nis2))

**Uwaga metodologiczna — rozbieżność między źródłami.** Terminy dalszych obowiązków podawane są
różnie: jedno źródło mówi o **3 marca 2027** dla większości obowiązków, inne o rejestracji
i samoocenie w systemie **S46 do 3 października 2026**, obowiązkach z rozdziału 3 **do 3 kwietnia
2027** i pierwszym audycie podmiotów kluczowych **do 3 kwietnia 2028**; przytaczane są też kary
do **100 mln zł** plus do 100 tys. zł dziennie za trwające naruszenie **[B]**.
**Nie podejmuj decyzji na podstawie tego akapitu** — daty i progi potwierdź w tekście ustawy
i u prawnika. Fakt wejścia w życie i objęcie sektora wodociągowego są pewne; szczegółowy kalendarz
w źródłach wtórnych się rozjeżdża.

**Dlaczego to szansa, a nie tylko obciążenie:** Twoi klienci **muszą** wykazać się nadzorem nad
bezpieczeństwem infrastruktury. Produkt, który dostarcza im dowód — rejestr zdarzeń, ścieżkę audytu,
raport gotowy do przedstawienia — przestaje być „miłym dodatkiem do monitoringu", a staje się
pozycją w budżecie zgodności. To zupełnie inna rozmowa sprzedażowa i inny budżet.
Masz już po temu fundament: `AuditAwareSession`, która blokuje zapis bez wpisu audytowego,
to dokładnie ten rodzaj mechanizmu, który w takiej rozmowie się pokazuje.

### AI Act — dobra wiadomość, o ile nie budujesz systemu wysokiego ryzyka

**[A]** Rozporządzenie **(UE) 2026/1744** („Digital Omnibus on AI") opublikowano w Dzienniku
Urzędowym **24 lipca 2026 r.**, weszło w życie **27 lipca 2026 r.** Zmienia AI Act
(rozporządzenie 2024/1689):

- obowiązki dla systemów wysokiego ryzyka z **Aneksu III** (m.in. rekrutacja, scoring kredytowy,
  edukacja, **infrastruktura krytyczna**) → przesunięte na **2 grudnia 2027 r.**,
- obowiązki dla systemów wbudowanych w produkty regulowane (**Aneks I**) → **2 sierpnia 2028 r.**,
- **nie przesunięto**: obowiązków przejrzystości (art. 50, od 2 sierpnia 2026, z czteromiesięcznym
  okresem przejściowym na znakowanie treści), obowiązków dostawców modeli ogólnego przeznaczenia
  ani zakazów praktyk niedopuszczalnych (art. 5).

([White & Case](https://www.whitecase.com/insight-alert/eu-ai-omnibus-enters-force-amending-ai-act),
[Gibson Dunn](https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/))

**Co to znaczy dla Ciebie konkretnie:** monitoring infrastruktury wodociągowej **może** wpaść
w kategorię infrastruktury krytycznej z Aneksu III, jeśli dołożysz komponent AI podejmujący
lub istotnie wspierający decyzje. Dopóki system jest **read-only i nie podejmuje decyzji** — jak
zapisałeś w `CLAUDE.md` projektu — ryzyko klasyfikacji jest znacznie niższe. To jest realny argument
za tym, żeby **sterowanie wprowadzać świadomie i późno**, a nie „przy okazji". Masz czas do grudnia
2027, ale przesunięcie terminu to nie jest powód, żeby czekać: budowa ścieżki audytu po fakcie
kosztuje wielokrotnie więcej niż zaprojektowanie jej od razu.

## 3.6 Otoczenie: czy to bańka i co z tego wynika

**[B]** Spór jest realny i nierozstrzygnięty. Strona sceptyczna (m.in. Michael Burry) wskazuje na
finansowanie kołowe — dostawcy infrastruktury finansują zakupy swoich klientów, co zawyża
raportowany wzrost przychodów — oraz na zaniżanie amortyzacji: jeśli GPU amortyzuje się księgowo
przez 5–6 lat, a ekonomicznie zużywa przez 2–3, zyski są zawyżone. Strona przeciwna odpowiada,
że finansowanie wendorskie samo w sobie nie jest patologią, dopóki produkt końcowy się sprzedaje.

**[B] Gartner** prognozuje, że **ponad 40% projektów agentowych zostanie anulowanych do końca 2027**
— z powodu kosztów, niejasnej wartości biznesowej i braku kontroli ryzyka. Opisuje też zjawisko
**„agent washing"**: przebranżawianie starych chatbotów i RPA na „agenty". Według Gartnera
z tysięcy dostawców przedstawiających się jako agentowi realnych jest ok. **130**.
([Gartner](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027))

**[C]** Osobno: głośny raport MIT NANDA o „95% pilotów genAI bez mierzalnego zwrotu" jest cytowany
znacznie mocniej, niż na to zasługuje. Podstawa to 52 wywiady, 153 ankiety i 300 publicznych wdrożeń
— to jest badanie jakościowe, nie pomiar. Cytowanie go jako „95% AI nie działa" jest nadużyciem.

**Co z tego wynika praktycznie — niezależnie od tego, kto ma rację:**

1. **Nie buduj modelu biznesowego opartego na tanim kapitale.** Jeśli scenariusz bańki się zrealizuje,
   pierwszą ofiarą jest finansowanie startupów przedprzychodowych.
2. **Buduj tak, żeby zamiana dostawcy modelu była zadaniem na tydzień, nie na kwartał.** Abstrakcja
   nad dostawcą to dziś decyzja architektoniczna o skutkach biznesowych.
3. **Sprzedawaj rozwiązanie problemu, nie technologię.** Gmina nie kupuje AI. Kupuje wiedzę, że
   pompa padła, zanim mieszkańcy stracą wodę. Jeśli „agent washing" się skompromituje, produkt
   sprzedawany jako „monitoring" przetrwa, a sprzedawany jako „AI" oberwie rykoszetem.
4. **Przychód od klientów bije rundę finansowania** — zawsze, ale w scenariuszu korekty szczególnie.

## 3.7 Finansowanie w CEE

**[B]** Rynek jest aktywny: większość nowo zebranych funduszy w regionie celuje w pre-seed / seed /
Series A, a w Polsce zamykane są istotne rundy w obszarze AI. Inwestorzy deklarują apetyt na wczesne
etapy. ([Vestbee](https://www.vestbee.com/insights/articles/vc-funds-raised-in-q2-2026))

**Kontrapunkt.** Dla produktu z Twojego profilu — B2B, sektor publiczny, długi cykl sprzedaży,
komponent sprzętowy — VC nie musi być właściwym paliwem. Logika VC wymaga rynku, na którym da się
zbudować spółkę wartą setki milionów. Rynek małych gmin i ZWiK jest ograniczony rozmiarem, ale
**zyskowny i lepki**, a lepkość właśnie udowodniłem liczbami w 3.3.

Uczciwy wniosek: **najpierw sprawdź, czy potrzebujesz VC.** Jeśli 15–20 gmin płacących rocznie
za obiekt da Ci dochód, z którego wyżyjesz i finansujesz rozwój, to jest lepsza pozycja negocjacyjna
niż runda zebrana przed pierwszym klientem. Runda ma sens wtedy, gdy masz dowód, że model się
powtarza, i chcesz przyspieszyć wejście na sąsiednie sektory (ścieki, ciepłownictwo, energetyka
komunalna) szybciej, niż pozwala cash flow.

---

# Część IV — Gdzie mogę się mylić: scenariusze i sygnały ostrzegawcze

Raport, który nie mówi, w jakich warunkach jest nieaktualny, jest publicystyką. Trzy scenariusze
na najbliższe 18–24 miesiące:

### Scenariusz A — Konsolidacja i normalizacja (moim zdaniem najbardziej prawdopodobny)

Zdolności modeli rosną stopniowo, warstwa agentowa staje się infrastrukturą, rynek nagradza tych,
którzy rozwiązują konkretne problemy w konkretnych branżach. Część projektów agentowych upada
(zgodnie z prognozą Gartnera), ale bez szoku systemowego. Praktyki inżynierskie dojrzewają
w kierunku spec-driven i mocniejszej weryfikacji.

**Co robić:** dokładnie to, co opisuje Część V.

### Scenariusz B — Korekta rynkowa

Materializuje się teza o finansowaniu kołowym, kapitał wysycha, wyceny spadają, firmy bez przychodu
znikają w ciągu dwóch–trzech kwartałów.

**Sygnały wczesne:** cięcia w capex największych dostawców chmury; **wzrost** cen API zamiast spadku;
wydłużenie okresu między rundami w CEE; masowe zwolnienia w firmach AI-native.
**Co robić:** dywersyfikuj dostawców modeli, trzymaj rezerwę gotówki na 12 miesięcy, priorytetyzuj
przychód nad wzrostem. Produkt sprzedawany do sektora komunalnego jest w tym scenariuszu
**relatywnie odporny** — budżety gmin nie reagują na cykl VC.

### Scenariusz C — Skokowy wzrost zdolności

Pojawia się generacja modeli, która wiarygodnie zamyka pętlę „specyfikacja → działający, utrzymywalny
system" bez nadzoru. Wtedy część tez z Części II traci ważność — ale **nie te o weryfikacji,
bezpieczeństwie i odpowiedzialności**, bo ktoś nadal musi odpowiadać za skutki.

**Sygnały wczesne:** odwrócenie trendu GitCleara (duplikacja i churn zaczynają spadać);
wskaźnik bezpieczeństwa Veracode rusza z 55% w górę; przepustowość na `main` w danych CircleCI
zaczyna rosnąć razem z feature branchami.
**Co robić:** przesunąć się jeszcze mocniej w stronę dziedziny, relacji z klientem i odpowiedzialności
regulacyjnej — bo to są jedyne rzeczy, których ten scenariusz nie unieważnia.

### Trzy wskaźniki, które warto śledzić kwartalnie

1. **Wskaźnik bezpieczeństwa Veracode** (stoi na ~55% od dwóch lat). Ruch w górę = zmiana jakościowa.
2. **Przepustowość na gałęzi głównej w danych CircleCI** (mediana: −7%). Jeśli zacznie rosnąć,
   znaczy to, że weryfikacja wreszcie nadąża za generowaniem.
3. **Luka zatrudnienia młodych u Stanforda** (15% → 19%). Jeśli przestanie rosnąć, teza o „zniknięciu
   szczebla wejścia" wymaga rewizji.

---

# Część V — Plan działania 30 / 90 / 365 dni

## Jako deweloper

### Najbliższe 30 dni

- [ ] **Zmierz się obiektywnie.** Przez dwa tygodnie notuj czas zadań z agentem i bez. Nie ufaj
      odczuciu — METR pokazał 39 punktów rozjazdu.
- [ ] **Przejrzyj triadę w swoich automatyzacjach.** Każdy workflow CI z agentem: prywatne dane?
      niezaufane wejście? kanał wyjścia? Napraw zanim dopiszesz kolejną funkcję.
- [ ] **Ustaw piaskownicę.** Agenty w kontenerze, sekrety poza zasięgiem, zawężona sieć.
- [ ] **Wybierz trzy umiejętności, których nie oddajesz AI.** Zapisz je. Ćwicz ręcznie.

### Najbliższe 90 dni

- [ ] **Wprowadź przepływ spec → plan → implementacja** dla każdej zmiany większej niż jeden plik.
      Recenzuj specyfikację, nie diff.
- [ ] **Podnieś próg CI**, aż będzie realnie blokujący: lint, typy, testy, skan zależności.
      W `waterworks` masz już `ruff`, `mypy`, `pytest`, `vitest`, `pio test` — zepnij je w bramkę,
      która nie przepuszcza.
- [ ] **Zamień powtarzające się „nigdy" z `CLAUDE.md` na hooki.** Instrukcja to kontekst; hook to egzekucja.
- [ ] **Przeprowadź audyt utrzymywalności** własnego kodu pod kątem sygnałów z 1.4: duplikacja,
      maskowanie błędów, kod nietykany od miesięcy.

### Najbliższe 365 dni

- [ ] **Pogłębiaj dziedzinę, nie stos technologiczny.** Twoja przewaga nie jest w tym, że umiesz
      FastAPI. Jest w tym, że rozumiesz, jak zachowuje się przepompownia.
- [ ] **Zbuduj publiczny dowód kompetencji** — `ai-tools` już nim jest; utrzymuj go jako portfolio
      warsztatu, nie tylko jako narzędzie.
- [ ] **Naucz się modelowania zagrożeń na poziomie roboczym**, nie hasłowym. To najszybciej rosnąca
      specjalizacja w danych o ofertach (Wiz +84%) i jednocześnie najsłabszy punkt kodu generowanego.

## Jako właściciel firmy

### Najbliższe 30 dni

- [ ] **Zdefiniuj jednostkę wartości i przelicz cenę na obiekt**, nie na użytkownika (3.4).
- [ ] **Zacznij mierzyć GRR i NRR od pierwszego klienta.** ARR sam w sobie nie mówi nic (3.3).
- [ ] **Odbądź pięć rozmów z gminami/ZWiK o NIS2** — nie sprzedażowych, tylko rozpoznawczych.
      Czego się boją, kto odpowiada, jaki mają budżet na zgodność, co muszą wykazać.
- [ ] **Zweryfikuj kalendarz KSC u prawnika.** Źródła wtórne się rozjeżdżają, a Ty budujesz
      na tym argument sprzedażowy.

### Najbliższe 90 dni

- [ ] **Zbuduj „pakiet dowodowy zgodności"** jako funkcję produktu: ścieżka audytu, rejestr zdarzeń,
      raport do pobrania. Masz już `AuditAwareSession` — brakuje warstwy, którą pokazuje się
      kontrolerowi.
- [ ] **Odłóż self-service.** Dane o retencji mówią jasno: tanio i samoobsługowo to najgorszy
      możliwy segment dla produktu AI (GRR 23%).
- [ ] **Abstrahuj dostawcę modelu**, jeśli w ogóle go używasz. Decyzja architektoniczna o skutku
      biznesowym w scenariuszu B.
- [ ] **Napisz jedno zdanie, czym jest produkt, bez słowa „AI".** Jeśli się nie da — problem jest
      w produkcie, nie w zdaniu.

### Najbliższe 365 dni

- [ ] **Doprowadź do 10–20 płacących obiektów, zanim pomyślisz o rundzie.** Dowód powtarzalności
      jest wart więcej niż deck.
- [ ] **Zdecyduj świadomie: bootstrap czy VC** (3.7). Nie dryfuj w tę decyzję.
- [ ] **Zmapuj sektory sąsiednie** (ścieki, ciepłownictwo, energetyka komunalna) — te same gminy,
      ten sam kupujący, ta sama fosa regulacyjna, inny zestaw czujników.
- [ ] **Trzymaj sterowanie poza zakresem tak długo, jak się da.** Read-only to nie ograniczenie,
      to pozycja regulacyjna (3.5) i ograniczenie odpowiedzialności.

---

## Zamiast zakończenia: pięć zdań, które warto zapamiętać

1. **Generowanie kodu staniało o rząd wielkości. Weryfikacja nie staniała wcale.** Cała reszta
   z tego wynika.
2. **AI wzmacnia to, co już masz.** Dobry proces przyspiesza, zły produkuje bałagan szybciej.
3. **Nie znika zawód, znika szczebel wejścia** — i to jest problem całej branży, nie tylko juniorów,
   bo seniorzy muszą skądś pochodzić.
4. **Dla firmy przewagą nie jest to, co zbudowałeś, tylko czego konkurent nie może skopiować,
   wypuszczając funkcję**: dane z użycia, proces klienta, nisza, zgodność.
5. **Twoim największym aktywem jest wiedza, której nie ma w żadnej dokumentacji.** Model wie
   wszystko, co zapisano. Nie wie, dlaczego ten czujnik kłamie przy mrozie.

---

## Załącznik A — Tabela tez i status weryfikacji

| # | Teza | Dowód | Źródła niezależne | Główne zastrzeżenie |
|---|------|-------|-------------------|---------------------|
| 1 | Adopcja ~84–90%, zaufanie spadło do 29% | **A** | Stack Overflow, DORA | Szczegółowe rozbicia zaufania niepotwierdzone u źródła |
| 2 | Efekt AI na produktywność zależy od kontekstu, nie jest stały | **A** | METR (−19%), GitHub/Accenture (+26%) | Obie strony mają ograniczenia metodologiczne, które same podają |
| 3 | Wąskie gardło = weryfikacja, nie pisanie | **A** | CircleCI (28 mln workflow), DORA, Thoughtworks | Najmocniej potwierdzona teza raportu |
| 4 | Utrzymywalność kodu degraduje się | **B** | GitClear (623 mln zmian) | Korelacja, nie przyczynowość; konflikt interesów wydawcy |
| 5 | Kod generowany jest niebezpieczny w ~45% przypadków | **B** | Veracode 2025 + aktualizacja 2026 | Warunki laboratoryjne, bez wytycznych bezpieczeństwa w promptcie |
| 6 | Prompt injection jest eksploatowany w praktyce | **A** | Clinejection, Mastra AI, zatrute pliki kontekstu | — |
| 7 | Luka zatrudnienia młodych = 19% i rośnie | **A** | Stanford / ADP, 4,6 mln pracowników | Autorzy: „nie dowód rozstrzygający" |
| 8 | Rynek pracy rozwarstwia się, nie kurczy | **B** | Pragmatic Engineer (TrueUp, Indeed, FRED) | Dane głównie z USA |
| 9 | MCP i A2A stają się standardem | **B** | dane o pobraniach, Linux Foundation | Liczby pobrań ze źródeł wtórnych |
| 10 | Koszt inferencji spadł o >99% od 2023 | **B** | zestawienia cenników | Konkretne poziomy zmieniają się kwartalnie |
| 11 | Retencja AI-native jest dramatycznie gorsza niż B2B SaaS | **A** | ChartMogul, 3500 firm | ~50 firm na przedział w wyższych progach ARR |
| 12 | Przewagą są dane z użycia, proces, nisza, zgodność | **B** | a16z, Sequoia, YC RFS 2026 | Teza inwestorska, nie pomiar |
| 13 | >40% projektów agentowych zostanie anulowanych do 2027 | **B** | Gartner | Prognoza analityczna, nie dane |
| 14 | KSC/NIS2 objęło sektor wodociągowy od 3.04.2026 | **A** | kancelarie prawne (2 niezależne) | Kalendarz dalszych obowiązków rozjeżdża się między źródłami |
| 15 | AI Act: wysokie ryzyko przesunięte na 2.12.2027 / 2.08.2028 | **A** | Rozporządzenie (UE) 2026/1744, 2 kancelarie | — |
| 16 | „95% pilotów genAI zawodzi" | **C** | MIT NANDA | Badanie jakościowe cytowane jako pomiar ilościowy |
| 17 | „80% startupów-nakładek upadnie do końca 2026" | **C** | źródła wtórne | Nie doprowadzone do źródła pierwotnego |
| 18 | Ryzyko atrofii umiejętności | **C** | MIT Media Lab (preprint), Orosz (opinia) | Mała próba, zadanie nieinżynierskie, brak recenzji |

---

## Załącznik B — Źródła

### Badania pierwotne i dane telemetryczne

- [METR — Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)
- [GitHub — Quantifying GitHub Copilot's impact in the enterprise with Accenture](https://github.blog/news-insights/research/research-quantifying-github-copilots-impact-in-the-enterprise-with-accenture/)
- [CircleCI — 2026 State of Software Delivery, Q2 Pulse](https://circleci.com/resources/2026-state-of-software-delivery-q2-pulse/)
- [Stanford Digital Economy Lab — Canaries in the Coal Mine, aktualizacja sierpień 2026](https://digitaleconomy.stanford.edu/news/canariesaug26/)
- [ChartMogul — The SaaS Retention Report: The AI churn wave](https://chartmogul.com/reports/saas-retention-the-ai-churn-wave/)
- [GitClear — The Maintainability Gap: 2026 AI Code Quality Research](https://www.gitclear.com/the_ai_code_quality_maintainability_gap)
- [Veracode — 2025 GenAI Code Security Report](https://www.veracode.com/resources/analyst-reports/2025-genai-code-security-report/)
- [Veracode — Spring 2026 GenAI Code Security Update](https://www.veracode.com/blog/spring-2026-genai-code-security/)
- [arXiv — A Survey of Agent Interoperability Protocols (MCP, ACP, A2A, ANP)](https://arxiv.org/html/2505.02279v1)
- [MIT Media Lab — Your Brain on ChatGPT](https://www.media.mit.edu/publications/your-brain-on-chatgpt/)

### Raporty branżowe

- [DORA — 2025 State of AI-assisted Software Development](https://dora.dev/dora-report-2025/)
- [DORA — ROI of AI-assisted Software Development (2026)](https://dora.dev/ai/roi/report/)
- [Thoughtworks — Technology Radar v34: cognitive debt i powrót do fundamentów](https://www.thoughtworks.com/about-us/news/2026/combat-ai-cognitive-debt-radar-v34)
- [Thoughtworks — Spec-driven development](https://www.thoughtworks.com/radar/techniques/spec-driven-development)
- [Stack Overflow — Mind the gap: Closing the AI trust gap for developers](https://stackoverflow.blog/2026/02/18/closing-the-developer-ai-trust-gap/)
- [ICONIQ — 2026 State of AI: The Builder's Economy](https://www.iconiq.com/growth/reports/state-of-ai-2026)
- [Gartner — Over 40% of Agentic AI Projects Will Be Canceled by End of 2027](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)

### Praktycy i analiza rynku

- [Simon Willison — Fireside chat about agentic engineering](https://simonw.substack.com/p/fireside-chat-about-agentic-engineering)
- [The Pragmatic Engineer — State of the software engineering job market in 2026](https://newsletter.pragmaticengineer.com/p/state-of-the-job-market-2026)
- [Y Combinator — Requests for Startups](https://www.ycombinator.com/rfs)
- [Vestbee — VC funds raised in Q2 2026 to invest in Europe](https://www.vestbee.com/insights/articles/vc-funds-raised-in-q2-2026)

### Bezpieczeństwo

- [Cloud Security Alliance Labs — prompt injection w GitHub Action agenta kodującego](https://labs.cloudsecurityalliance.org/research/csa-research-note-claude-code-github-action-prompt-injection/)
- [CSO Online — Supply-chain attacks take aim at your AI coding agents](https://www.csoonline.com/article/4167465/supply-chain-attacks-take-aim-at-your-ai-coding-agents.html)
- [Phoenix Security — Supply Chain Attacks 2026: npm, PyPI, VS Code, AI Agents](https://phoenix.security/accelerating-supply-chain-attacks-npm-pypi-vsx-ai-enabled-2026/)

### Regulacje

- [Schoenherr — Poland: New cybersecurity rules, implementation of NIS2](https://www.schoenherr.eu/content/poland-new-cybersecurity-rules-in-poland-implementation-of-nis2)
- [White & Case — EU AI Omnibus enters into force, amending the AI Act](https://www.whitecase.com/insight-alert/eu-ai-omnibus-enters-force-amending-ai-act)
- [Gibson Dunn — EU AI Act Omnibus Agreement: Postponed High-Risk Deadlines](https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/)
- [EU Artificial Intelligence Act — High-level summary](https://artificialintelligenceact.eu/high-level-summary/)

---

*Raport przygotowany we wrześniu 2026 na podstawie źródeł publicznie dostępnych w dniu sporządzenia.
Dane rynkowe i regulacyjne zmieniają się szybko — przed podjęciem decyzji o skutkach prawnych
lub finansowych zweryfikuj stan faktyczny u źródła.*
