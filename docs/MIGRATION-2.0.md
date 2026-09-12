# Przebudowa 2.0 — co się zmieniło i co z tym zrobić

Dokument opisuje przebudowę repozytorium `ai-tools` z luźnego zbioru plików w katalogu
`.claude/` na wersjonowany plugin Claude Code z egzekwowaniem reguł, walidacją i CI.

Napisany po polsku, bo jest to raport dla właściciela repozytorium. Pozostała dokumentacja
(`README.md`, `docs/ARCHITECTURE.md`, ADR-y) jest po angielsku, spójnie z treścią samego
toolkitu.

---

## 1. Najkrótsza wersja

| | Przed | Po |
|---|---|---|
| Dystrybucja | ręczne kopiowanie / dwa repa w IDE | plugin + `scripts/install.py` |
| Źródło prawdy | dwa równoległe komplety (`.claude/` i `.github/`) | jeden komplet, `.github/` generowany |
| Reguły CRITICAL | tekst w `CLAUDE.md` | hooki `PreToolUse` + `permissions.deny` |
| Slash-komendy | brak | 9 |
| Hooki | brak | 3, z 45 testami |
| Walidacja | brak | walidator + testy + CI |
| Modele agentów | wszyscy `haiku` | `haiku` do wyszukiwania, `sonnet` do wnioskowania |
| Katalog komponentów | brak | generowany ze źródeł |

Stan końcowy: **6 agentów, 24 skille (15 wiedzy + 9 komend), 7 reguł, 3 hooki, 5 skryptów.**

---

## 2. Co było nie tak — ustalenia z audytu

Każde ustalenie ma dowód w repozytorium lub w dokumentacji Claude Code.

### 2.1 Toolkit nie docierał tam, gdzie pracujesz — **błąd krytyczny**

Metoda „otwieram `ai-tools` obok projektu w IDE" nie działa tak, jak wygląda. Dokumentacja
Claude Code stwierdza wprost:

> `--add-dir` … By default, CLAUDE.md files from these directories **are not loaded**.

Potrzebna jest zmienna `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`. Bez niej nie ładują
się ani instrukcje, ani reguły, ani agenci. Potwierdzenie w drugą stronę:
`waterworks-monitoring-platform` **nie zawierał katalogu `.claude/` w ogóle** — czyli nic z
toolkitu tam nie trafiało.

**Naprawa:** [ADR-001](adr/adr-001-distribute-as-plugin.md) — plugin + marketplace w tym samym
repozytorium.

### 2.2 Dwa komplety plików, już rozjechane

`.claude/` miało 13 skilli i 7 reguł, `.github/` — 6 i 6. Agent `esp32-firmware-engineer`
istniał tylko po stronie Claude'a. Część plików różniła się jednym kluczem frontmattera. Nic
tego nie wykrywało.

**Naprawa:** [ADR-003](adr/adr-003-generated-copilot-mirror.md) — `.github/` generowany przez
`scripts/sync_copilot.py`, a CI wywala się przy rozjeździe.

### 2.3 Reguły CRITICAL nie były egzekwowane

`CLAUDE.md` zawierał blok oznaczony „non-negotiable and enforced without exception". Nic go nie
egzekwowało. Dokumentacja:

> Claude treats them as context, not enforced configuration. To block an action regardless of
> what Claude decides, use a PreToolUse hook instead.

**Naprawa:** [ADR-004](adr/adr-004-enforce-constraints-with-hooks.md) — trzy hooki, 45 testów
(19 komend blokowanych, 19 przepuszczanych, plus ścieżki do sekretów i przypadki fail-open).

### 2.4 `CLAUDE.md` wskazywał na plik, którego nie ma

Sekcja „Access to Sensitive Files" odsyłała do `permissions.deny` w `.claude/settings.json`.
Ten plik został usunięty commitem `fa30a25` („chore: remove deprecated settings.json"). Opisana
ochrona nie istniała.

**Naprawa:** `templates/project/settings.json` z pełną listą `permissions.deny`, instalowany
przez `install.py --settings` i przez `/ai-tools:onboard-project`.

### 2.5 Reguła frontendowa nie ładowała się w projekcie React — **błąd krytyczny**

```yaml
paths: ["**/*.ts", "**/*.html", "**/*.scss"]   # brak **/*.tsx
```

Twój frontend to React 19 (`.tsx`). Reguła nie ładowała się **nigdy** podczas edycji
komponentu. Dla porównania `security-checklist` i `error-handling-patterns` miały `.tsx`
poprawnie — czyli była to literówka, nie decyzja.

**Naprawa:** reguła przepisana na `typescript-coding-standards` z globami
`**/*.{ts,tsx,mts,cts}`, `**/*.{js,jsx,mjs,cjs}`, `**/*.{html,scss,css}`.

### 2.6 Sprzeczność między regułami

`python-coding-standards` nakazywała „Use `uv` exclusively - not pip or poetry", a `CLAUDE.md`
w sekcji CRITICAL — „always `.venv`", przy projekcie na `requirements.txt` i setuptools.
Dokumentacja Claude Code ostrzega, że przy sprzecznych instrukcjach model wybiera arbitralnie.

**Naprawa:** reguła mówi teraz „idź za tym, czego projekt już używa", z tabelą dla uv / pip /
poetry i niezmiennikami wspólnymi (nigdy interpreter systemowy, nigdy `.venv` w repo,
instalacja zależności wymaga zgody).

### 2.7 Nieaktualna i niedoprecyzowana porada bezpieczeństwa

Reguła mówiła: „Do NOT use `python-jose` — unmaintained since 2022". Sprawdziłem: PyPI pokazuje
wydania **3.4.0 i 3.5.0**, więc teza o porzuceniu jest nieprawdziwa. Prawdziwy problem jest
inny i węższy — OSV/GitHub Advisory Database:

| CVE | Opis | Naprawione w |
|---|---|---|
| CVE-2024-33663 | algorithm confusion z kluczami OpenSSH ECDSA | 3.4.0 |
| CVE-2024-33664 | DoS przez skompresowany JWE („JWT bomb") | 3.4.0 |
| CVE-2024-29370 | dotyczy ≤ 3.3.0 | — |

**Naprawa:** reguła podaje konkretne CVE i próg `>=3.4.0`. Patrz też sekcja 7 — dotyczy to
Twojego backendu.

### 2.8 Martwe odwołania

- `skills/to-spec` odsyłał do nieistniejącej komendy `/setup-matt-pocock-skills`
- `skills/jira-board-extractor` odsyłał do `.claudeignore`, którego w repo nie ma (jest
  `.copilotignore`), i do ścieżki `cd .claude/skills/...`
- agenci linkowali `../../CLAUDE.md` i `.claude/rules/*.md` — ścieżki nieprawidłowe po
  instalacji jako plugin

**Naprawa:** wszystkie odwołania po nazwie komponentu zamiast po ścieżce; skill Jiry używa
`${CLAUDE_SKILL_DIR}`, które działa niezależnie od miejsca instalacji.

### 2.9 Wszyscy agenci na `haiku`

Włącznie z `code-reviewer` i `debugger`. To nie jest optymalizacja kosztu, tylko przeniesienie
go w miejsce, gdzie najtrudniej go zauważyć: przeoczony błąd w review nie wygląda jak porażka,
tylko jak czysty przegląd.

**Naprawa:** [ADR-005](adr/adr-005-tiered-model-assignment.md).

---

## 3. Nowa struktura

```
ai-tools/
├── .claude-plugin/         plugin.json + marketplace.json     ← NOWE
├── agents/                 6 agentów            (było .claude/agents/)
├── skills/                 24 skille            (było .claude/skills/)
├── rules/                  7 reguł              (było .claude/rules/)
├── hooks/                  hooks.json + 3 skrypty             ← NOWE
├── templates/project/      CLAUDE.md, settings.json, mcp      ← NOWE
├── scripts/                5 narzędzi                         ← NOWE
├── tests/                  testy hooków                       ← NOWE
├── docs/                   architektura, katalog, koszty, ADR ← NOWE
└── .github/                GENEROWANY mirror + CI
```

Przeniesienia zrobione przez `git mv`, więc historia pliku jest zachowana (`git log --follow`
działa).

---

## 4. Co musisz zrobić

### Krok 1 — zainstaluj plugin (na każdej maszynie)

```
/plugin marketplace add lukaszpiasecki13/ai-tools
/plugin install ai-tools@ai-tools
```

### Krok 2 — zainstaluj reguły

```bash
python scripts/install.py --user           # dla wszystkich projektów na tej maszynie
```

albo per projekt, z automatycznym doborem do stacku:

```bash
python scripts/install.py --target ../waterworks-monitoring-platform --settings
```

Sprawdzone na Twoim projekcie — wykrywa poprawnie `python`, `typescript`, `embedded`.

### Krok 3 — przestań otwierać dwa repa obok siebie

Do pracy **nad** toolkitem:

```bash
claude --plugin-dir /ścieżka/do/ai-tools
```

Ładuje kopię roboczą na żywo, `/reload-plugins` podchwytuje zmiany bez reinstalacji.

### Krok 4 — przenieś reguły projektowe do projektu

Blok „Project-Specific Rules (waterworks-monitoring-platform)" zniknął z `CLAUDE.md` toolkitu
— reguły jednego projektu nie mogą jechać do wszystkich innych. Ich treść jest zachowana w
`templates/project/CLAUDE.md.template` (git, `.venv`, Alembic, dokumentacja modułów, pin map
firmware). Uruchom w projekcie:

```
/ai-tools:onboard-project
```

albo skopiuj szablon ręcznie do `waterworks-monitoring-platform/CLAUDE.md` i uzupełnij komendy.

---

## 5. Zmiany łamiące

| Zmiana | Skutek | Co zrobić |
|---|---|---|
| `.claude/{agents,skills,rules}` → katalogi w korzeniu | stare ścieżki nie działają | zainstaluj plugin |
| `frontend-coding-standards` → `typescript-coding-standards` | stara nazwa nie istnieje | reinstalacja reguł |
| `frontend-patterns` → `angular-patterns` (+ nowy `react-patterns`) | inna nazwa skilla | — |
| `.claude/settings.json` nie wraca do tego repo | to szablon dla projektów | `templates/project/settings.json` |
| agenci `code-reviewer` bez `Edit`/`Write` | reviewer nie poprawia kodu | fixy przez `debugger` lub wątek główny |

---

## 6. Co doszło

**9 slash-komend** (`/ai-tools:<nazwa>`): `commit`, `pr-description`, `adr`, `security-scan`,
`test-focus`, `onboard-project`, `fastapi-endpoint`, `react-feature`, `toolkit-validate`.
`security-scan` działa w `context: fork` — audyt czyta cały diff w osobnym oknie kontekstu, a
do głównej rozmowy wraca sam wynik.

**3 hooki:** `guard_bash` (operacje nieodwracalne), `guard_secrets` (odczyt plików z
poświadczeniami), `format_after_edit` (formatowanie, ale **tylko** jeśli projekt ma już
skonfigurowany dany formatter).

**5 skryptów:** `validate_toolkit.py`, `sync_copilot.py`, `generate_catalog.py`, `install.py`,
`_frontmatter.py`. Wszystkie na samej bibliotece standardowej — CI nie ma kroku instalacji
zależności, więc zachowuje się identycznie jak świeży klon.

**CI** (`.github/workflows/validate-toolkit.yml`): walidator, testy hooków, kontrola dryfu
mirrora i katalogu.

**Nowy skill `react-patterns`** — oparty na tym, co faktycznie masz w projekcie: React 19,
TanStack Query, react-hook-form + zod, Radix, Tailwind.

---

## 7. Ustalenia spoza toolkitu — do Twojej decyzji

Nie dotykałem repozytorium `waterworks-monitoring-platform`. Dwie rzeczy wymagają tam działania:

### 7.1 Podatna zależność — do sprawdzenia w pierwszej kolejności

`backend/pyproject.toml` zawiera:

```toml
"python-jose[cryptography]>=3.3.0"
```

Dolna granica dopuszcza wersję 3.3.0, podatną na CVE-2024-33663, CVE-2024-33664 i
CVE-2024-29370 (naprawione w 3.4.0). Zakres `>=3.3.0` **niczego nie gwarantuje** — instalacja z
cache'u albo starszy lockfile mogą wciągnąć 3.3.0.

Minimalna poprawka: podnieś próg do `>=3.4.0`. Docelowo reguła `security-checklist` zaleca
`PyJWT` dla nowego kodu. Sprawdź, co faktycznie jest zainstalowane:

```bash
.venv/bin/python -m pip show python-jose
```

### 7.2 Projekt nie ma konfiguracji Claude Code

Brak `CLAUDE.md`, brak `.claude/`. Krok 2 i 4 powyżej to naprawiają.

---

## 8. Czego świadomie nie zrobiłem

- **Nie blokuję `git commit` hookiem.** Zablokowanie rozwaliłoby `/ai-tools:commit`, a wymóg
  zgody to preferencja procesu, nie operacja nieodwracalna. Blokowane jest to, czego nie da się
  cofnąć: force push, `reset --hard`, `clean -f`, `checkout .`.
- **Nie zmieniałem treści `prepare-work`** poza poprawką nazwy reguły. To 1000 linii dopracowanego
  pipeline'u — przepisywanie go przy okazji restrukturyzacji byłoby zmianą niezwiązaną z zadaniem.
- **Nie generuję `.claude/` w tym repo jako kopii.** Trzeci komplet plików to trzecie miejsce na
  rozjazd; do pracy nad toolkitem służy `--plugin-dir`.
- **Nie dodałem MCP do pluginu.** `ui-verify` potrzebuje serwera `chrome-devtools`, ale plugin
  włączający sobie serwer MCP uruchamiany przez `npx` to instalacja kodu bez pytania. Jest
  `templates/project/mcp.json.example` do świadomego skopiowania.
- **Nie ruszałem `.copilotignore`.** Działa i nie koliduje z niczym.
