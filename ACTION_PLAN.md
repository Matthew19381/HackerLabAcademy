# ACTION PLAN — HackerLabAcademy

**Data:** 2026-08-09
**Autor:** Claude Code (audyt techniczny + plan działania), na podstawie audytu z 2026-08-09 i `MASTER_PLAN.md` / `CLAUDE.md` Systemu Głównego.
**Cel dokumentu:** dać dowolnemu modelowi AI (bez pamięci tej rozmowy, bez dodatkowych pytań do człowieka) komplet kroków do wykonania pivotu HackerLabAcademy z samodzielnej platformy do nauki hakingu na narzędzie wspomagające istniejącą subskrypcję TryHackMe (THM) użytkownika, naprawy długu technicznego i domknięcia integracji z ekosystemem System-Główny.

> **Zasada pracy w tym repo (analogicznie do `docs/INTEGRACJA-MODULOW.md` Systemu Głównego):** ten plan dotyczy WYŁĄCZNIE `HackerLabAcademy/`. Zmiany w `System-Glowny/` (np. dopisanie klucza modułu do `MODULE_KEYS`) wykonuje osobna sesja tamtego projektu — tu tylko przygotuj wartości do przekazania (patrz Faza 5).

---

## Streszczenie stanu

HackerLabAcademy jest najbardziej dojrzałym kodowo modułem ekosystemu: działająca aplikacja FastAPI + React z 22 routerami, 17 serwisami, 17 modelami SQLAlchemy, 86 przechodzącymi testami backendu i 20 stronami frontendu, build przechodzi. Projekt jest jednak zbudowany wokół modelu „naucz się hakowania od zera z własnym hostowanym DVWA + XP/50 poziomów/35 osiągnięć + ranking CTF”, który ma zostać zarzucony na rzecz narzędzia do utrwalania wiedzy z TryHackMe. Zero kodu integracyjnego z System-Głównym istnieje. Dokumentacja repo (TASKS.md, INTEGRATION_MAP.md, README, CLAUDE.md) jest w kilku miejscach nieaktualna względem kodu, a nowy kierunek pivotu nie jest jeszcze nigdzie w repo spisany — ten plan jest pierwszym miejscem, gdzie istnieje.

## Cel projektu i mierzalne kryteria sukcesu

**Cel:** HackerLabAcademy przestaje hostować własne środowisko do nauki hakingu od zera (DVWA, laby, kill-chain ataków, ranking CTF) i staje się narzędziem do:
1. utrwalania wiedzy zdobywanej na TryHackMe (spaced repetition komend/narzędzi/konceptów),
2. notatek/cheat-sheetów z pokoi i ścieżek THM,
3. ręcznego trackingu ukończonych pokoi/ścieżek THM (THM nie ma publicznego API do scrapowania postępu),
4. quizów utrwalających i mentora AI tłumaczącego koncepty z THM,
5. widocznego, informacyjnego (nie rankingowego) modułu w dashboardzie Systemu Głównego.

**Kryteria sukcesu (mierzalne, weryfikowalne komendą/testem):**
- [ ] `pytest backend/tests -q` przechodzi w 100% po każdej fazie (zero regresji), liczba testów nie spada poniżej stanu sprzed fazy bez świadomego uzasadnienia (usunięte testy = usunięta funkcja, udokumentowane w CHANGELOG.md).
- [ ] `npm run build` (frontend) przechodzi bez błędów po każdej fazie.
- [ ] `docker compose up --build` w katalogu projektu kończy się działającym backendem (`curl http://localhost:8003/api/health` → 200) i frontendem (`curl http://localhost/` → 200) — obecnie niezweryfikowane wykonawczo i prawdopodobnie zepsute (patrz Faza 3).
- [ ] `GET /api/v1/summary?user_id=1` zwraca poprawny JSON zgodny z kontraktem Systemu Głównego (Faza 5) i `System-Głowny` (`POST /api/v1/integrations/summary` lub agregator) widzi moduł `hackerlab-academy` bez błędu w `errors`.
- [ ] Zero endpointów/UI z mechaniką rankingową (leaderboard) lub karą-obietnicą niewyegzekwowaną w kodzie.
- [ ] Zero kodu zależnego od uruchamiania własnych podatnych maszyn (DVWA/Docker-w-Dockerze) w ścieżce głównej aplikacji.
- [ ] `git status` czysty po każdej fazie (wszystko commitowane albo świadomie w `.gitignore`).

---

## Architektura docelowa

**Stack docelowy — za standardem ekosystemu (LinguaAI = referencja, zaktualizowany 2026-08-09):**

| Warstwa | Technologia | Port |
|---|---|---|
| Backend | **Python 3.12** (obecnie 3.11 — wymaga podniesienia, patrz zadanie 3.4 niżej) + FastAPI 0.115 + SQLAlchemy 2.0 + Pydantic 2.9 | `:8003` (docelowo, patrz Faza 4) |
| Frontend | React 19.2 + Vite + Tailwind + React Router 7.13 — **już zgodne ze standardem, ROZSTRZYGNIĘTE 2026-08-09, brak downgrade'u** | `:5173`/`:5174` (dev) / `:80` (prod, Docker) |
| Baza danych | SQLite (`backend/data/HackerLabAcademy.db`, wolumen Docker) | — |
| AI | Gemini (domyślnie) / OpenRouter / Ollama, wybór przez `AI_PROVIDER` | — |

**Moduły backendu po pivocie** (Router → Service → SQLAlchemy Session, wzorzec zachowany):
- `topics`, `flashcards`, `errors`, `exercises`, `mentor`, `conversation`, `cves`, `videos`, `articles`, `writeups`, `certificates`, `stats`, `brain`, `daily`, `vocabulary`, `ctf` (bez leaderboardu), `defense`, `downloads`, `ai_config`, `placement`
- **nowy**: `thm_progress` (tracker pokoi/ścieżek THM) — Faza 6
- **nowy**: `integration` (`/api/v1/summary`) — Faza 5
- **usunięte**: `labs`, `attack` — Faza 2

**Kontrakt integracji z System-Głównym (DOKŁADNY, zweryfikowany w kodzie `System-Glowny/backend`, nie zgadywany):**

1. **Moduł wystawia** `GET /api/v1/summary?user_id=<int>&date=<YYYY-MM-DD>`. System-Główny woła go pod `{base_url}{summary_endpoint}` gdzie `base_url` dla `hackerlab-academy` to `http://localhost:8003` (zarejestrowane w `System-Glowny/backend/config.py` i `.env.example`, `MODULE_ENDPOINTS`). Format odpowiedzi (Pydantic `ModuleSummary`/ręczny dict — oba akceptowalne, pola muszą się zgadzać):
   ```json
   {
     "module": "hackerlab-academy",
     "user_id": "1",
     "date": "2026-08-09",
     "summary": { "...metryki dnia specyficzne dla modułu..." },
     "events": [
       {
         "event_type": "thm_room_completed",
         "module": "hackerlab-academy",
         "user_id": "1",
         "timestamp": "2026-08-09T10:00:00Z",
         "data": {},
         "score": null,
         "tags": ["learning"],
         "affect": null,
         "evidence_id": null,
         "plan_item_id": null
       }
     ],
     "wellbeing_contribution": null
   }
   ```
   Zasady: read-only, bez wywołań AI, liczone z lokalnej DB. `wellbeing_contribution` musi zostać `null` dopóki nie istnieje Affect Engine — zakaz fabrykowania.
   Implementacja referencyjna do skopiowania wzorca (NIE kodu 1:1, dane inne): `C:/GoogleDriveSync/Projekty/LinguaAI/backend/routers/integration.py`.

2. **Moduł publikuje eventy** `POST http://localhost:8000/api/v1/integrations/event`, nagłówek `X-Module-Key: <klucz>`. Body = `ModuleEvent`:
   ```python
   class ModuleEvent(BaseModel):
       event_type: str          # np. "thm_room_completed", "flashcard_reviewed", "error_logged"
       module: str               # zawsze "hackerlab-academy" — klucz pozwala publikować TYLKO ten moduł
       user_id: str
       timestamp: datetime        # default: now(UTC)
       data: dict[str, Any] = {}
       duration_seconds: int | None = None
       score: float | None = None       # 0-100 jeśli dotyczy
       tags: list[str] = []
       affect: dict[str, int] | None = None       # {mood, energy, stress} 1-5, opcjonalne
       evidence_id: str | None = None
       plan_item_id: str | None = None
   ```
   Dedup po `module+user_id+event_type+timestamp` po stronie huba (retry bezpieczny → `status: "duplicate"`). Błąd sieci **nigdy** nie może blokować UX modułu → kolejka + retry lokalnie.
   Klucz modułu: wygenerować `python -c "import secrets; print(secrets.token_urlsafe(32))"`, przekazać do sesji `System-Glowny` do dopisania w `System-Glowny/backend/.env` → `MODULE_KEYS=...,hackerlab-academy=<klucz>`, ten sam klucz zapisać lokalnie w `HackerLabAcademy/backend/.env` jako `SYSTEM_GLOWNY_MODULE_KEY`.

3. **Moduł przyjmuje dyrektywy** `POST /api/v1/directives` (u siebie, w `HackerLabAcademy/backend`). Minimalny zestaw: `{"directive": "survival_mode", "enabled": true}` → cel dzienny spada do 1 sesji fiszek 5 min, `{"directive": "priority", "value": "<temat>"}`, `{"directive": "quiet_hours", "from": "HH:MM", "to": "HH:MM"}`. System-Główny zacznie je wysyłać dopiero w swojej Fazie 4 — endpoint może istnieć wcześniej i po prostu czekać.

**Zasady etyczne obowiązujące w każdej fazie poniżej** (z MASTER_PLAN §0, egzekwowane w code review każdego zadania):
- Zakaz dark patterns: ranking, loot-boxy, karzące streaki, sztuczna pilność, shaming.
- Gamifikacja tylko informacyjna (postęp, opanowanie) — nie kontrolująca.
- Każda funkcja wpływająca na naukę ma poziom dowodu META/RCT/OBS/HIPOTEZA przy sobie w `NEURO_PLAN.md`.
- Zakaz fabrykowania liczb bez podstawy ("+200% retencji" itp.).
- Feedback na poziomie zadania, nigdy osoby.

---

## Pivot: z samodzielnej platformy do narzędzia wspomagającego THM

To jest strategiczna mapa zmian, którą Fazy 1-2 poniżej realizują krok po kroku.

### Zostaje (do adaptacji, nie do wyrzucenia)

| Co | Pliki | Adaptacja wymagana |
|---|---|---|
| Silnik fiszek + eksport Anki + TTS | `backend/routers/flashcards.py`, `backend/services/anki_service.py`, `backend/services/audio_service.py`, `backend/services/sm2_service.py` | Brak natychmiastowej — migracja SM-2→FSRS dopiero w Fazie 8 (blokowana przez System-Główny) |
| Pętla „błąd → fiszka” | `backend/routers/errors.py`, `backend/models/error_item.py` | Koncepcyjnie 1:1 pasuje do „pomyłka w pokoju THM → karta powtórkowa”; dodać pole źródła (nazwa pokoju THM) — Faza 6 |
| CVE Explorer | `backend/routers/cves.py`, `backend/services/cve_service.py` | Bez zmian, zostaje jako warstwa bieżących wydarzeń |
| Mentor AI | `backend/routers/mentor.py`, `backend/services/lesson_service.py` (`mentor_chat`) | Dodać stopniowane wskazówki (Faza 7, HL-4); zmienić framing promptu na „wytłumacz koncept/pokój z THM” |
| Certyfikaty PDF, szablony write-upów | `backend/routers/certificates.py`, `backend/routers/writeups.py` | Przeorientować treść na raporty z pokoi/ścieżek THM — Faza 6 |
| Rdzeń XP/statystyk/osiągnięć (bez rankingu) | `backend/services/achievement_service.py`, `backend/models/achievement.py` | Usunąć wyłącznie leaderboard (Faza 2); XP/achievements zostają jako informacyjny tracker |
| Terminal Simulator | `frontend/src/data/terminal_scenarios.js`, `frontend/src/pages/Terminal.jsx` | Rozszerzyć o realistyczne komendy nmap/burp/metasploit — Faza 6 |
| Moduł Artykułów | `backend/routers/articles.py` | Naturalny nośnik notatek/cheat-sheetów z THM zamiast lekcji generowanych od zera |
| CTF (rozwiązywanie zagadek, bez leaderboardu) | `backend/routers/ctf.py`, `frontend/src/pages/CTF.jsx` | Usunąć tylko zakładkę/endpoint leaderboard (Faza 2) i wyegzekwować karę za hint (Faza 4) |

### Znika

| Co | Pliki | Powód |
|---|---|---|
| Cały cykl życia kontenera DVWA (start/stop/reset) | `backend/routers/labs.py`, `backend/services/lab_service.py`, `backend/tests/test_labs.py`, `frontend/src/pages/Lab.jsx`, trasa `/lab` w `App.jsx` | To dokładnie „własne środowisko do hakowania” — THM już to dostarcza. Usunięcie eliminuje zależność od `subprocess`/Dockera-w-Dockerze |
| Attack Scenario kill-chain | `backend/routers/attack.py`, `backend/models/attack_scenario.py`, `backend/tests/test_attack.py`, `frontend/src/pages/AttackScenario.jsx`, trasa `/attack` | Zbudowany wokół wewnętrznych labów DVWA; bez `labs.py` nie ma celu ataku |
| Ranking CTF (leaderboard) | `GET /api/v1/ctf/leaderboard` w `backend/routers/ctf.py` (linia ok. 138), zakładka „Leaderboard” w `frontend/src/pages/CTF.jsx` | Dark pattern zakazany przez MASTER_PLAN §0.6 i własny NEURO_PLAN HL-8 |
| Generowanie labów DVWA per temat | `generate_lab_instructions` w `backend/services/lesson_service.py`, pole `lab_type` w `backend/models/topic.py` używane do treści `dvwa_*` | Treść labów była budowana wokół własnej hostowanej podatnej appki; do zastąpienia odnośnikiem do pokoju THM |
| Martwe pliki | `HackerLabAcademy.db` (root, jeśli to relikt sprzed przeniesienia do `backend/data/`), `cyber_tutor.db`, `Zmiany_CyberTutor.txt`, `test.db` | Zero referencji w kodzie (zweryfikowane grepem), zaśmiecają drzewo robocze |

### Dochodzi

| Co | Nowe pliki | Opis |
|---|---|---|
| Ręczny tracker pokoi/ścieżek THM | `backend/models/thm_progress.py`, `backend/routers/thm_progress.py`, `frontend/src/pages/ThmProgress.jsx` | Nazwa pokoju/ścieżki, kategoria, data ukończenia, notatki, link; zasila XP/osiągnięcia |
| Fiszki z notatek THM | rozszerzenie `backend/routers/flashcards.py` (`quick-create`) | Pole `source_notes` — wklejona notatka z pokoju zamiast gołego terminu jako źródło generacji |
| Talia powtórkowa składni narzędzi | rozszerzenie `frontend/src/data/terminal_scenarios.js` + seed fiszek | nmap/burp/metasploit/gobuster itd. jako osobna kategoria fiszek |
| Integracja z Systemem Głównym | `backend/routers/integration.py`, `backend/services/hub_publisher.py`, `backend/routers/directives.py` | INT-1/INT-2/INT-3, patrz Architektura docelowa |
| FSRS wspólny (po Fazie 3 Systemu Głównego) | — | Zablokowane do czasu powstania wspólnego silnika w `System-Glowny`; patrz Faza 8 |

---

## Fazy działania

Kolejność: krytyczny dług techniczny i fundamenty → zgodność ze standardem ekosystemu → integracja → nowe funkcje pivotu → jakość. Każde zadanie ma ID `F<faza>.<numer>` używane w polu „Zależności”.

## Faza 0 — Higiena repo (fundament, zero ryzyka, ~30 min)

- [ ] **F0.1 Rozstrzygnąć niezacommitowane zmiany.**
  Opis: `git status` pokazuje `TASKS.md` zmodyfikowany oraz `IMPROVEMENTS.md`, `NEURO_PLAN.md` nieśledzone. Przed jakąkolwiek dalszą zmianą trzeba mieć czysty punkt startowy: sprawdzić `git diff TASKS.md`, zdecydować czy zmiany są celowe (jeśli tak — commitować teraz, jeśli to WIP sprzed pivotu — nadpisać w Fazie 1).
  Pliki: `TASKS.md`, `IMPROVEMENTS.md`, `NEURO_PLAN.md`.
  Komenda: `git add TASKS.md IMPROVEMENTS.md NEURO_PLAN.md && git commit -m "chore: zapis WIP przed pivotem THM-companion"`.
  Kryterium akceptacji: `git status` w katalogu `HackerLabAcademy/` zwraca „nothing to commit, working tree clean”.
  Zależności: brak.

- [ ] **F0.2 Usunąć martwe pliki.**
  Opis: `cyber_tutor.db` (relikt sprzed zmiany nazwy, zero referencji w kodzie — zweryfikowane grepem), `Zmiany_CyberTutor.txt` (0 bajtów), `test.db` (relikt sprzed izolowanych baz testowych w `conftest.py`). Przed usunięciem: `grep -rn "cyber_tutor\|test\.db" backend/ frontend/src/` — potwierdzić brak żywych odwołań.
  Pliki do usunięcia: `HackerLabAcademy/cyber_tutor.db`, `HackerLabAcademy/Zmiany_CyberTutor.txt`, `HackerLabAcademy/test.db`.
  Komenda: `git rm cyber_tutor.db Zmiany_CyberTutor.txt test.db`.
  Kryterium akceptacji: pliki nie istnieją w drzewie roboczym ani w indeksie git; `pytest backend/tests -q` nadal 100% zielone (potwierdza że nic ich nie potrzebowało).
  Zależności: F0.1.

- [ ] **F0.3 Naprawić `.gitignore` (samobójcza reguła na `.env.example`).**
  Opis: linia `backend/.env.example` w `.gitignore` (obok `.env`, `backend/.env`) oznacza, że plik onboardingowy nigdy nie trafi do repo. Usunąć tę jedną linię, zostawić `.env` i `backend/.env` zignorowane.
  Plik: `HackerLabAcademy/.gitignore`.
  Zmiana: usunąć linię `backend/.env.example` z sekcji `# Environment`.
  Kryterium akceptacji: `git check-ignore backend/.env.example` zwraca kod wyjścia 1 (plik NIE jest ignorowany); jeśli plik `backend/.env.example` nie istnieje, utworzyć go z aktualną listą zmiennych z `backend/config.py` (`GEMINI_API_KEY`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `AI_PROVIDER`, `DATABASE_URL`) plus nowe z Fazy 5 (`SYSTEM_GLOWNY_URL`, `SYSTEM_GLOWNY_MODULE_KEY`) z wartościami-placeholderami, i dodać go do gita.
  Zależności: brak.

## Faza 1 — Spisanie pivotu w dokumentacji projektu (fundament decyzyjny, ~1-2 h)

- [ ] **F1.1 Napisać ADR pivotu.**
  Opis: udokumentować decyzję pivotu wzorem istniejącego `decisions/DEC-001-docker-multi-stage.md` (kontekst → decyzja → konsekwencje → status).
  Plik nowy: `HackerLabAcademy/decisions/DEC-002-pivot-thm-companion.md`.
  Treść minimalna: kontekst (dlaczego pivot — użytkownik ma subskrypcję THM, MASTER_PLAN §0.6 zakazuje rankingów, DVWA-w-Dockerze to zdublowana funkcja THM), decyzja (lista zostaje/znika/dochodzi — skopiować tabele z sekcji „Pivot” tego planu), konsekwencje (usunięcie `labs.py`/`attack.py` upraszcza problem Dockera z audytu), status: `Accepted`.
  Kryterium akceptacji: plik istnieje, zawiera wszystkie trzy tabele (zostaje/znika/dochodzi) w formie zweryfikowanej wobec aktualnego stanu kodu (nie kopiowanej ślepo z audytu bez re-sprawdzenia).
  Zależności: F0.1.

- [ ] **F1.2 Przepisać `TASKS.md` pod pivot.**
  Opis: sekcja „🔗 PLAN v2 — NEURO + INTEGRACJA” w `TASKS.md` (obecnie linie ok. 9-31) opisuje stary kierunek (własne laby, N-3 „nowy typ podatności = walkthrough” zakłada własne laby). Przepisać:
  - Usunąć/przeformułować `N-3` (HL-2 fading) — fading ma teraz dotyczyć wskazówek Mentora do pokoi THM, nie własnych labów.
  - Usunąć `N-5` (HL-3 productive failure) w kontekście własnych labów — przeformułować na „próba samodzielna w pokoju THM przed podejrzeniem hinta Mentora”.
  - Dodać nową sekcję `PIVOT` z zadaniami THM-tracker (odsyłającą do tego `ACTION_PLAN.md` Fazy 6).
  - Zaktualizować `INT-2` — lista eventów: usunąć `lab_completed`, dodać `thm_room_completed`, `thm_path_progress_updated`.
  - Dodać nagłówek na górze pliku: „Nieaktualność TASKS.md względem kodu rozwiązana — patrz `ACTION_PLAN.md` jako dokument nadrzędny od 2026-08-09”.
  Plik: `HackerLabAcademy/TASKS.md`.
  Kryterium akceptacji: żadna pozycja `TASKS.md` nie odwołuje się do funkcji z tabeli „Znika” bez adnotacji „USUNIĘTE w ramach pivotu, patrz DEC-002”.
  Zależności: F1.1.

- [ ] **F1.3 Zaktualizować `NEURO_PLAN.md` o rozdział pivotu.**
  Opis: dodać na początku pliku sekcję „## Pivot (2026-08-09)” z jednozdaniowym podsumowaniem zmiany roli modułu i odnośnikiem do `DEC-002`. Przejrzeć istniejące punkty HL-1…HL-8 i przy każdym dopisać jednym zdaniem jak się zmienia w nowym kontekście (np. HL-6 „retrieval po labie” → „retrieval po pokoju THM”).
  Plik: `HackerLabAcademy/NEURO_PLAN.md`.
  Kryterium akceptacji: każdy punkt HL-1…HL-8 ma adnotację pivotu; brak sprzecznych stwierdzeń między `NEURO_PLAN.md` a `DEC-002`.
  Zależności: F1.1.

- [ ] **F1.4 Zaktualizować `README.md` i `HackerLabAcademy/CLAUDE.md` (opis produktu).**
  Opis: sekcja opisu projektu w obu plikach nadal opisuje „naucz się hakowania od zera”. Zmienić na opis zgodny z pivotem: „narzędzie do utrwalania wiedzy z TryHackMe”. To wyłącznie zmiana opisowa — techniczne poprawki liczb/tabel routerów są w Fazie 4 (razem z resztą zgodności dokumentacji, żeby nie edytować tych plików trzy razy).
  Pliki: `HackerLabAcademy/README.md` (sekcja wprowadzenia), `HackerLabAcademy/CLAUDE.md` (sekcja „Czym jest ten projekt”).
  Kryterium akceptacji: żadne zdanie w opisie projektu nie sugeruje hostowania własnych podatnych maszyn ani rankingu.
  Zależności: F1.1.

## Faza 2 — Pivot: usunięcie kodu DVWA/labs/attack/leaderboard

- [ ] **F2.1 Usunąć backend labs.**
  Opis: usunąć router, serwis i testy labów.
  Pliki do usunięcia: `backend/routers/labs.py`, `backend/services/lab_service.py`, `backend/tests/test_labs.py`.
  Pliki do zmiany: `backend/main.py` — usunąć linię `import backend.routers.labs as labs` (ok. linia 164) i `app.include_router(labs.router, prefix="/api/v1")` (ok. linia 187).
  Sprawdzić `backend/tests/conftest.py` pod kątem fixture'ów specyficznych dla labów (np. mock Dockera) i usunąć nieużywane.
  Kryterium akceptacji: `grep -rn "lab_service\|routers.labs" backend/` zwraca 0 wyników; `pytest backend/tests -q` przechodzi.
  Zależności: F1.2.

- [ ] **F2.2 Usunąć backend attack scenario.**
  Opis: usunąć kill-chain oparty o własne laby.
  Pliki do usunięcia: `backend/routers/attack.py`, `backend/models/attack_scenario.py`, `backend/tests/test_attack.py`.
  Pliki do zmiany: `backend/main.py` — usunąć `import backend.routers.attack as attack` (ok. linia 178) i `app.include_router(attack.router, prefix="/api/v1")` (ok. linia 201); `backend/models/__init__.py` jeśli re-eksportuje `AttackScenario` — usunąć import.
  Kryterium akceptacji: `grep -rn "attack_scenario\|routers.attack" backend/` zwraca 0 wyników; `python -c "import backend.main"` przechodzi bez błędu; `pytest backend/tests -q` przechodzi.
  Zależności: F2.1 (kolejność usuwania importów w `main.py` w jednym przebiegu, żeby nie zostawić plik w stanie non-importable między commitami).

- [ ] **F2.3 Usunąć ranking CTF (leaderboard).**
  Opis: `GET /api/v1/ctf/leaderboard` w `backend/routers/ctf.py` (ok. linia 138-139, funkcja `get_leaderboard`) narusza zakaz dark patterns (MASTER_PLAN §0.6, własny HL-8). Usunąć endpoint. CTF (rozwiązywanie zagadek, punkty per użytkownik) zostaje — usuwamy wyłącznie widok porównawczy między użytkownikami.
  Pliki: `backend/routers/ctf.py` (usunąć funkcję `get_leaderboard` i jej `@router.get("/leaderboard")`).
  Kryterium akceptacji: `GET /api/v1/ctf/leaderboard` zwraca 404; istniejące testy CTF (jeśli testują leaderboard) zaktualizowane lub usunięte; `pytest backend/tests -q` przechodzi.
  Zależności: F1.2.

- [ ] **F2.4 Usunąć frontend Lab.jsx i trasę `/lab`.**
  Opis: strona i nawigacja do labów.
  Pliki do usunięcia: `frontend/src/pages/Lab.jsx`.
  Pliki do zmiany: `frontend/src/App.jsx` — usunąć `import Lab from './pages/Lab'` i `<Route path="/lab" element={<Lab />} />` (ok. linia 47); `frontend/src/components/Layout.jsx` — usunąć link nawigacyjny do `/lab`; `frontend/src/api/client.js` — usunąć funkcje wołające `backend/routers/labs.py` (np. `startLab`, `stopLab`, `resetLab` — dokładne nazwy sprawdzić w pliku przed usunięciem); strony które linkują do `/lab` (`Dashboard.jsx`, `Topics.jsx`, `Setup.jsx`, `Stats.jsx`, `DailyBrain.jsx` — potwierdzone grepem, zweryfikować każdą i usunąć/zastąpić link).
  Kryterium akceptacji: `grep -rn "'/lab'\|Lab.jsx\|from '../pages/Lab'" frontend/src/` zwraca 0 wyników poza ewentualnym `/api/v1/thm...` niepowiązanym; `npm run build` przechodzi.
  Zależności: F2.1.

- [ ] **F2.5 Usunąć frontend AttackScenario.jsx i trasę `/attack`.**
  Opis: analogicznie do F2.4.
  Pliki do usunięcia: `frontend/src/pages/AttackScenario.jsx`.
  Pliki do zmiany: `frontend/src/App.jsx` — usunąć import i `<Route path="/attack" element={<AttackScenario />} />` (ok. linia 61); `Layout.jsx` — usunąć link nawigacyjny; `client.js` — usunąć funkcje API dla attack scenario.
  Kryterium akceptacji: `grep -rn "AttackScenario\|'/attack'" frontend/src/` zwraca 0 wyników; `npm run build` przechodzi.
  Zależności: F2.2.

- [ ] **F2.6 Usunąć zakładkę Leaderboard z `CTF.jsx`.**
  Opis: `frontend/src/pages/CTF.jsx` ma stan `leaderboard`, funkcję `loadLeaderboard`, import `getLeaderboard` z `client.js`, zakładkę „Leaderboard” (przyciski i render tabeli, ok. linie 15-20, 35-38, 76-79, 162-173). Usunąć cały ten kod, zostawić zakładki „Challenges”/„Solved” (czy jak się nazywają pozostałe).
  Pliki: `frontend/src/pages/CTF.jsx`, `frontend/src/api/client.js` (usunąć `getLeaderboard`).
  Kryterium akceptacji: w UI CTF nie ma żadnego widoku porównującego wyniki między użytkownikami; `npm run build` przechodzi; `npx vitest run` przechodzi.
  Zależności: F2.3.

- [ ] **F2.7 Odczepić generację labów od `lab_type`/DVWA w `topics.py`/`lesson_service.py`.**
  Opis: `backend/routers/topics.py` linia ok. 106-107 woła `generate_lab_instructions(topic.name, topic.slug, topic.lab_type)` gdy `topic.lab_type` jest ustawione (`"dvwa_sqli"` itd. w `TOPICS_SEED`, `backend/main.py` linie 12-86). To generowało instrukcje do własnego DVWA. Zamienić na jedną z dwóch opcji (wybór zostaw jako decyzję w sekcji „Ryzyka i decyzje otwarte” jeśli poniższa domyślna nie pasuje użytkownikowi):
  - **Domyślna:** zamienić `generate_lab_instructions` na `generate_practice_guidance`, która zwraca wskazówkę „poćwicz ten temat w pokoju THM: [nazwa/kategoria]” + link placeholder do wyszukiwarki THM (`https://tryhackme.com/search?searchTerm=<topic.name>`) zamiast instrukcji do własnej appki. Zmienić pole modelu `lab_type` (`backend/models/topic.py` linia 18) na `practice_hint: Column(String, nullable=True)` przez migrację Alembic lub ręczny `ALTER TABLE` (SQLite, brak Alembic w projekcie obecnie — patrz F2.7a).
  - Zaktualizować `TOPICS_SEED` w `backend/main.py` — usunąć wartości `"dvwa_sqli"` itd. z pola `lab_type`/`practice_hint`, zastąpić opisową sugestią kategorii THM.
  Pliki: `backend/routers/topics.py`, `backend/services/lesson_service.py` (funkcja `generate_lab_instructions`), `backend/models/topic.py`, `backend/main.py` (`TOPICS_SEED`).
  Kryterium akceptacji: `grep -rn "dvwa_" backend/` zwraca 0 wyników; `pytest backend/tests -q` przechodzi po aktualizacji testów `topics`.
  Zależności: F2.1, F2.4.

- [ ] **F2.7a Migracja kolumny `lab_type` → `practice_hint` (SQLite, bez Alembic).**
  Opis: projekt nie ma Alembic (potwierdzić: `grep -rn "alembic" backend/requirements.txt` — jeśli brak, użyć ręcznego SQL). Napisać jednorazowy skrypt migracyjny.
  Plik nowy: `backend/scripts/migrate_lab_type_to_practice_hint.py` — otwiera `backend/data/HackerLabAcademy.db` (lub ścieżkę z `DATABASE_URL` po Fazie 3), wykonuje `ALTER TABLE topics RENAME COLUMN lab_type TO practice_hint;` (SQLite 3.25+ wspiera `RENAME COLUMN`). To jest zmiana nazwy kolumny, NIE usunięcie wartości — istniejące wpisy `dvwa_*` zostają zachowane w przemianowanej kolumnie, zgodnie z decyzją użytkownika (patrz „Ryzyka" #4).
  Kryterium akceptacji: po uruchomieniu skryptu `sqlite3 backend/data/HackerLabAcademy.db ".schema topics"` pokazuje kolumnę `practice_hint`, nie `lab_type`; aplikacja startuje bez błędu SQLAlchemy o brakującej kolumnie.
  Zależności: F2.7.

- [ ] **F2.8 Uruchomić pełny regres po Fazie 2.**
  Opis: po usunięciu labs/attack/leaderboard uruchomić cały zestaw testów i build, naprawić wszystko co się posypało (importy krzyżowe, fixture'y w `conftest.py` odwołujące się do usuniętych modeli).
  Komendy: `cd backend && python -m pytest tests -q`, `cd frontend && npm run build && npx vitest run`.
  Kryterium akceptacji: oba zielone; liczba testów backendu udokumentowana w `CHANGELOG.md` (np. „86 → 74 testów, -12 z usunięciem labs/attack, zero regresji w pozostałych”).
  Zależności: F2.1–F2.7a.

## Faza 3 — Naprawa fundamentalnego długu technicznego

- [ ] **F3.1 Naprawić `DATABASE_URL` (martwa konfiguracja).**
  Opis: `backend/database.py` linia 5 ma zahardkodowane `SQLALCHEMY_DATABASE_URL = "sqlite:///./HackerLabAcademy.db"`, ignorując `settings.DATABASE_URL` (`backend/config.py` linia 25) i zmienną środowiskową `DATABASE_URL` z `docker-compose.yml`. Naprawić tak, żeby baza faktycznie trafiała do zamontowanego wolumenu.
  Plik: `backend/database.py`.
  Zmiana:
  ```python
  import os
  from backend.config import settings

  SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)

  engine = create_engine(
      SQLALCHEMY_DATABASE_URL,
      connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {},
  )
  ```
  Zaktualizować `backend/config.py` domyślną wartość `DATABASE_URL` na `sqlite:///./data/HackerLabAcademy.db` (spójne z `docker-compose.yml`) i upewnić się że katalog `data/` istnieje lokalnie (`backend/data/.gitkeep`) oraz jest w `.gitignore` (baza sama, nie katalog).
  Kryterium akceptacji: po `docker compose up --build`, plik bazy pojawia się w wolumenie `backend_data` (sprawdzić `docker compose exec backend ls /app/data`), nie w `/app/HackerLabAcademy.db`; `pytest backend/tests -q` nadal przechodzi (testy używają własnego monkeypatchingu w `conftest.py`, zweryfikować że nie kolidują ze zmianą).
  Zależności: F2.8.

- [ ] **F3.2 Naprawić Dockerfile backendu (brak CMD + niespójność COPY-context/importy).**
  Opis: `backend/Dockerfile` kończy się po komentarzu `# Run with uvicorn` bez `CMD`/`ENTRYPOINT` (działa tylko dzięki `command:` w `docker-compose.yml`, nieuruchamialny samodzielnie). Dodatkowo kontekst builda to `./backend` z `COPY . .` do `WORKDIR /app` — spłaszcza pakiet (`/app/main.py`, nie `/app/backend/main.py`), a 52 pliki w projekcie używają bezwzględnych importów `from backend.X import ...` / `import backend.X`, które w tym layoucie nie zadziałają (potwierdzone w audycie, `decisions/DEC-001-docker-multi-stage.md` linia 169 dokumentuje że kiedyś to naprawiono na importy względne, ale późniejsze commity `3b023dc`/`d085fbc` przywróciły styl `backend.X`).
  **Decyzja architektoniczna (podjęta tu, udokumentować w DEC-002 lub nowym DEC-003):** zamiast migrować 52 pliki z powrotem na importy względne (kruche, łatwo o regres przy każdym nowym pliku), zmienić **kontekst budowania obrazu** tak, żeby pakiet `backend` istniał na ścieżce — budować z katalogu głównego projektu, nie z `./backend`.
  Pliki: `HackerLabAcademy/backend/Dockerfile`, `HackerLabAcademy/docker-compose.yml`.
  Zmiana `docker-compose.yml`:
  ```yaml
  services:
    backend:
      build:
        context: .
        dockerfile: backend/Dockerfile
  ```
  Zmiana `backend/Dockerfile`:
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY backend/requirements.txt backend/requirements.txt
  RUN pip install --no-cache-dir -r backend/requirements.txt
  COPY backend/ backend/
  RUN mkdir -p backend/audio backend/exports backend/data
  EXPOSE 8003
  CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8003"]
  ```
  (Port 8003 zakłada że Faza 4/T4.1 już wykonana — jeśli wykonywane w innej kolejności, użyć aktualnego portu i wrócić tu po Fazie 4.)
  Kryterium akceptacji: `docker build -f backend/Dockerfile -t hackerlab-backend .` (z katalogu `HackerLabAcademy/`) kończy się sukcesem; `docker run --rm -p 8003:8003 hackerlab-backend` odpowiada na `curl http://localhost:8003/api/health` kodem 200 bez podawania `command:` z zewnątrz.
  Zależności: F3.1.

- [ ] **F3.3 Ujednolicić styl importów w całym backendzie na bezwzględny `backend.X`.**
  Opis: skoro F3.2 rozwiązuje problem kontekstu Dockera zachowując `backend.X`, nie trzeba migrować 52 plików — ale `backend/main.py` linia 7 nadal ma `from .database import engine, Base, SessionLocal` (relatywny) obok `import backend.routers.X` (bezwzględny) w tym samym pliku. Ujednolicić na bezwzględny dla spójności.
  Plik: `backend/main.py`.
  Zmiana: `from .database import engine, Base, SessionLocal` → `from backend.database import engine, Base, SessionLocal`.
  Kryterium akceptacji: `python -c "import backend.main"` z katalogu nadrzędnego (`HackerLabAcademy/`) przechodzi; `grep -n "^from \.\|^from \.\." backend/*.py backend/**/*.py` zwraca 0 wyników.
  Zależności: F3.2.

- [ ] **F3.4 Zaktualizować `CHANGELOG.md`/`CODE_MAP.md`/`TASKS.md` po naprawie Dockera.**
  Opis: te pliki twierdzą „✅ COMPLETED, build successful, awaiting manual verification” dla stanu, który audyt wykazał jako zepsuty. Po F3.2/F3.3 zaktualizować status na faktycznie zweryfikowany (z datą i wynikiem komendy `docker build`).
  Pliki: `HackerLabAcademy/CHANGELOG.md`, `HackerLabAcademy/CODE_MAP.md`, `HackerLabAcademy/TASKS.md`.
  Kryterium akceptacji: żaden z tych plików nie twierdzi „awaiting manual verification” dla czegoś już zweryfikowanego w tej fazie.
  Zależności: F3.2.

- [ ] **F3.5 Przenieść sesje Mentora AI z pamięci procesu do bazy danych.**
  Opis: `backend/routers/mentor.py` linia 10, `_sessions: dict = {}` — ginie przy restarcie/reload, niebezpieczne przy >1 workerze uvicorn.
  Plik nowy: `backend/models/mentor_session.py`:
  ```python
  class MentorSession(Base):
      __tablename__ = "mentor_sessions"
      id: Mapped[int] = mapped_column(primary_key=True)
      session_id: Mapped[str] = mapped_column(String, unique=True, index=True)
      user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
      messages: Mapped[str] = mapped_column(Text)  # JSON-encoded list[{role, content}]
      updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
  ```
  Plik: `backend/routers/mentor.py` — zamienić `_sessions[session_id]` na zapytania do `MentorSession` (JSON encode/decode `messages`), zachowując publiczny kontrakt endpointu `/mentor/chat` bez zmian.
  Kryterium akceptacji: nowy test `backend/tests/test_mentor_persistence.py` — wysłać wiadomość, zrestartować proces testowy (nowa sesja `TestClient`), odczytać historię tej samej `session_id`, historia zachowana; `pytest backend/tests -q` przechodzi.
  Zależności: F2.8 (żeby nie mieszać z usuwaniem labs/attack w jednym PR).

## Faza 4 — Zgodność ze standardem ekosystemu

- [ ] **F4.1 Naprawić kolizję portu (8001 → 8003).**
  Opis: `System-Glowny/CLAUDE.md` i `System-Glowny/backend/config.py`/`.env.example` przypisują HackerLabAcademy port **8003**, ale cały kod modułu hardkoduje **8001** (ten sam port co LinguaAI — realna kolizja przy uruchomieniu obu naraz).
  Pliki do zmiany (zamienić `8001` → `8003` wszędzie poza odwołaniami do INNYCH modułów):
  - `docker-compose.yml`: `ports: - "8003:8003"`, `command: uvicorn main:app --host 0.0.0.0 --port 8003` (albo usunąć `command:` całkiem po F3.2, bo `CMD` w Dockerfile już to robi), `healthcheck` URL → `http://127.0.0.1:8003/api/health`.
  - `start.bat`, `start.ps1`: port uruchomienia backendu.
  - `HackerLabAcademy/CLAUDE.md`: wszystkie wzmianki portu 8001 → 8003.
  - `backend/config.py`: jeśli port jest gdzieś zaszyty (sprawdzić `grep -n "8001" backend/config.py`).
  Kryterium akceptacji: `grep -rn "8001" HackerLabAcademy/ --include=*.py --include=*.md --include=*.yml --include=*.bat --include=*.ps1` zwraca 0 wyników (poza plikami historycznymi typu `CHANGELOG.md`, gdzie stary port jest kontekstem historycznym, nie instrukcją); backend startuje na 8003 (`uvicorn backend.main:app --port 8003`), `curl http://localhost:8003/api/health` → 200.
  Zależności: F3.2 (Dockerfile już zaktualizowany do 8003 tam).

- [ ] **F4.2 Naprawić proxy dev frontendu.**
  Opis: `frontend/vite.config.js` linia 9 proxuje `/api` → `http://localhost:8000` (port Systemu Głównego, nie backendu modułu!) i nasłuchuje na porcie `5174`. Po F4.1 backend jest na 8003.
  Plik: `frontend/vite.config.js`.
  Zmiana:
  ```js
  server: {
    port: 5174,
    proxy: {
      '/api': 'http://localhost:8003',
    },
  },
  ```
  Kryterium akceptacji: `npm run dev`, otwarcie `http://localhost:5174`, dowolne wywołanie API z UI (np. lista tematów) trafia do backendu na 8003 i zwraca dane (sprawdzić w devtools Network, nie 404/CORS error).
  Zależności: F4.1.

- [x] **F4.3 [ROZSTRZYGNIĘTE 2026-08-09 — decyzja użytkownika] Wersja React/Router — HackerLabAcademy był już zgodny.**
  Opis: `frontend/package.json` ma `react@^19.2.4` + `react-router-dom@^7.13.1`. Standard ekosystemu
  zaktualizowany 2026-08-09 (LinguaAI jako referencja) na dokładnie te wersje — **żadnego downgrade'u**.
  To `HackerLabAcademy/CLAUDE.md` linia 79 i `README.md` linia 50 były nieaktualne, nie kod.
  Pliki: `HackerLabAcademy/CLAUDE.md`, `HackerLabAcademy/README.md` — zmienić deklarację na `React 19.2 ·
  React Router v7.13` bez żadnej adnotacji o niezgodności (jej już nie ma).
  Kryterium akceptacji: żaden plik `.md` w repo nie podaje wersji frontendu niezgodnej z `frontend/package.json`;
  brak wzmianek o "oczekuje na decyzję" w kontekście React/Router.
  Zależności: brak (niezależne od reszty Fazy 4).

- [ ] **F4.3b [NOWE 2026-08-09] Podnieś backend do Python 3.12.**
  Opis: standard ekosystemu to teraz Python 3.12; HackerLabAcademy deklaruje 3.11.
  Pliki: sprawdzić i zmienić wszystkie wzmianki wersji (`pyproject.toml`/`requirements.txt` jeśli pinują
  wersję, `Dockerfile` backendu — `FROM python:3.11-slim` → `python:3.12-slim`, CI jeśli istnieje, `README.md`,
  `CLAUDE.md`).
  Kryterium akceptacji: `grep -rn "3.11" --include=*.md --include=Dockerfile* --include=*.toml --include=*.yml .`
  w katalogu projektu nie pokazuje już żadnej wzmianki o Pythonie 3.11; `pytest` (86 testów) przechodzi pod
  interpreterem 3.12.
  Zależności: brak.

- [ ] **F4.4 Wyegzekwować karę za hint w CTF (albo usunąć obietnicę).**
  Opis: `backend/routers/ctf.py` `GET /challenges/{id}/hint` zwraca `{"hint": ..., "penalty": "50% points if solved"}`, ale `submit_flag` (komentarz przy zatwierdzaniu flagi, linie ok. 103-104) jawnie nie nalicza kary: „We don't track hint usage in this simple version... simpler: always full points for now.” UI obiecuje karę, backend jej nie stosuje — nieuczciwość wobec użytkownika.
  Wybór (domyślny, prostszy): wyegzekwować karę faktycznie.
  Pliki: `backend/models/ctf.py` (model `UserCtfAttempt`) — dodać kolumnę `hint_used: Mapped[bool] = mapped_column(default=False)`; `backend/routers/ctf.py`:
  - w `get_hint`: ustawić `attempt.hint_used = True` na rekordzie `UserCtfAttempt` (utworzyć jeśli nie istnieje) i zacommitować,
  - w `submit_flag`: `points = challenge.points // 2 if attempt.hint_used else challenge.points`.
  Migracja SQLite: analogicznie do F2.7a, `ALTER TABLE user_ctf_attempts ADD COLUMN hint_used BOOLEAN DEFAULT 0;`.
  Kryterium akceptacji: nowy test `backend/tests/test_ctf_hint_penalty.py` — pobrać hint, zatwierdzić poprawną flagę, sprawdzić że przyznane punkty to `challenge.points // 2`; bez pobrania hinta — pełne punkty. `pytest backend/tests -q` przechodzi.
  Zależności: F2.8.

- [ ] **F4.5 Poprawić liczby i tabelę routerów w dokumentacji.**
  Opis: `README.md` (linie ok. 58-60) podaje „12 modeli / 15 routerów” — faktycznie po Fazie 2 będzie mniej niż audytowe 17/22 (usunięto `labs.py`, `attack.py` z routerów; `attack_scenario.py` z modeli), ale wciąż niezgodne. `HackerLabAcademy/CLAUDE.md` tabela routerów (linie ok. 50-76) wymienia fantomowy `terminal.py → /api/terminal/` (nie istnieje — Terminal Simulator jest czysto frontendowy) i pomija `ai_config.py`.
  Pliki: `README.md`, `HackerLabAcademy/CLAUDE.md`.
  Procedura: policzyć faktyczny stan PO Fazie 2 (`ls backend/routers/*.py | grep -v __init__ | wc -l`, `ls backend/models/*.py | grep -v __init__ | wc -l`), wpisać dokładne liczby, usunąć wiersz `terminal.py` z tabeli, dodać wiersz `ai_config.py → /api/v1/ai-config` (czy jaki jest faktyczny prefix — sprawdzić w pliku).
  Kryterium akceptacji: liczby w `README.md` zgadzają się z `ls`/`wc -l` co do joty; `grep -n "terminal.py" HackerLabAcademy/CLAUDE.md` zwraca 0 wyników.
  Zależności: F2.8 (liczyć PO usunięciu labs/attack, nie przed).

- [ ] **F4.6 Zaktualizować `INTEGRATION_MAP.md` (root) — 4+ miesiące nieaktualny.**
  Opis: datowany 2026-03-28, nadal nazywa moduł „CyberTutor”, odwołuje się do struktury ścieżek `03_Projects/...` niezgodnej z faktyczną `C:/GoogleDriveSync/Projekty/...`, definiuje schemat eventu sprzeczny z aktualnym kontraktem (`{module, event_type, payload, timestamp, severity}` zamiast `{module, user_id, date, summary, events}` + `POST /api/v1/integrations/event` z `X-Module-Key`).
  Plik: `HackerLabAcademy/INTEGRATION_MAP.md`.
  Decyzja: albo przepisać całość zgodnie z sekcją „Architektura docelowa” tego planu, albo skasować plik i zastąpić odnośnikiem do `System-Glowny/docs/INTEGRACJA-MODULOW.md` + sekcji „Architektura docelowa” tego `ACTION_PLAN.md` jako jedynego źródła prawdy (rekomendowane — unika przyszłego dryfu dwóch dokumentów opisujących ten sam kontrakt).
  Kryterium akceptacji: plik nie zawiera nazwy „CyberTutor” ani starego schematu eventu; jeśli zastąpiony odnośnikiem, plik ma ≤10 linii.
  Zależności: F5 (żeby odnośnik prowadził do faktycznie zaimplementowanego kontraktu, nie planowanego) — **wykonać na końcu Fazy 5, nie w Fazie 4** mimo numeracji tutaj (zostawione w tej sekcji tematycznie, ale w kolejności wykonania to zadanie ostatnie w całej Fazie 4+5).

## Faza 5 — Integracja z Systemem Głównym (INT-1, INT-2, INT-3)

- [ ] **F5.1 Zaimplementować `GET /api/v1/summary`.**
  Opis: wzorem `LinguaAI/backend/routers/integration.py` (plik referencyjny, przeczytać przed pisaniem — struktura funkcji `get_ecosystem_summary`, obsługa `_parse_date`, agregacja eventów dnia). Metryki specyficzne dla HackerLabAcademy: liczba ukończonych pokoi THM danego dnia (po Fazie 6 — jeśli F5 robione przed F6, zwrócić `0`/pominąć pole i dopisać w F6.6), liczba fiszek przejrzanych, liczba błędów zalogowanych, liczba zaległych powtórek, XP total, streak (jeśli istnieje pole streak w modelu User — sprawdzić `backend/models/user.py`).
  Plik nowy: `backend/routers/integration.py`.
  Szkielet:
  ```python
  from datetime import date as date_type, datetime
  from fastapi import APIRouter, Depends, HTTPException, Query
  from sqlalchemy import func
  from sqlalchemy.orm import Session
  from backend.database import get_db
  from backend.models.user import User
  from backend.models.flashcard import Flashcard
  from backend.models.error_item import ErrorItem
  # from backend.models.thm_progress import ThmProgress  # po Fazie 6

  router = APIRouter(prefix="/api/v1", tags=["Integration"])
  MODULE_NAME = "hackerlab-academy"

  def _parse_date(raw: str | None) -> date_type:
      if not raw:
          return datetime.utcnow().date()
      try:
          return datetime.strptime(raw, "%Y-%m-%d").date()
      except ValueError:
          raise HTTPException(status_code=422, detail="date must be YYYY-MM-DD")

  @router.get("/summary")
  def get_ecosystem_summary(
      user_id: int = Query(...),
      date: str | None = Query(None),
      db: Session = Depends(get_db),
  ):
      user = db.query(User).filter(User.id == user_id).first()
      if not user:
          raise HTTPException(status_code=404, detail="User not found")
      target = _parse_date(date)
      target_iso = target.isoformat()
      # ... agregacje read-only analogiczne do LinguaAI ...
      return {
          "module": MODULE_NAME,
          "user_id": str(user_id),
          "date": target_iso,
          "summary": {
              "flashcards_reviewed": 0,       # TODO agregacja
              "due_reviews": 0,               # TODO agregacja
              "errors_logged": 0,             # TODO agregacja
              "thm_rooms_completed_today": 0, # TODO po Fazie 6
              "total_xp": user.total_xp or 0,
          },
          "events": [],  # TODO analogicznie do LinguaAI (lista ModuleEvent-owych dictów)
          "wellbeing_contribution": None,
      }
  ```
  Plik: `backend/main.py` — dodać `import backend.routers.integration as integration` i `app.include_router(integration.router, prefix="")` (uwaga: `integration.py` już ma `prefix="/api/v1"` w środku, nie dublować prefiksu — wzorować się dokładnie na tym jak inne routery w `main.py` są rejestrowane z `prefix="/api/v1"` w `include_router` ORAZ swoim wewnętrznym prefiksie; sprawdzić w LinguaAI jak to rozwiązano żeby uniknąć `/api/v1/api/v1/summary`).
  Kryterium akceptacji: `curl "http://localhost:8003/api/v1/summary?user_id=1"` zwraca 200 i JSON zgodny z kontraktem (pole `module` = `"hackerlab-academy"`); nowy test `backend/tests/test_integration_summary.py` (wzorem `LinguaAI/backend/tests/test_integration_summary.py`) przechodzi.
  Zależności: F3.1 (baza poprawna), F4.1 (port).

- [ ] **F5.2 Zaimplementować publisher eventów.**
  Opis: po zdarzeniach `flashcard reviewed`, `error logged`, `thm_room_completed` (po F6) wysłać event do Systemu Głównego. Błąd sieci nie może blokować UX — kolejka + retry.
  Plik nowy: `backend/models/outbound_event.py` (tabela kolejki, analogicznie do `SyncEvent` w LinguaAI, ale dla eventów WYCHODZĄCYCH do huba, nie przychodzących z klienta):
  ```python
  class OutboundEvent(Base):
      __tablename__ = "outbound_events"
      id: Mapped[int] = mapped_column(primary_key=True)
      event_type: Mapped[str] = mapped_column(String)
      user_id: Mapped[str] = mapped_column(String)
      payload_json: Mapped[str] = mapped_column(Text)   # cały ModuleEvent jako JSON
      created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
      sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
      attempts: Mapped[int] = mapped_column(default=0)
  ```
  Plik nowy: `backend/services/hub_publisher.py`:
  ```python
  import httpx, json, os
  from datetime import datetime, timezone
  from sqlalchemy.orm import Session
  from backend.models.outbound_event import OutboundEvent

  HUB_URL = os.getenv("SYSTEM_GLOWNY_URL", "http://localhost:8000")
  HUB_KEY = os.getenv("SYSTEM_GLOWNY_MODULE_KEY", "")
  MODULE_NAME = "hackerlab-academy"

  def queue_event(db: Session, event_type: str, user_id: str, data: dict, **extra) -> None:
      payload = {
          "event_type": event_type, "module": MODULE_NAME, "user_id": str(user_id),
          "timestamp": datetime.now(timezone.utc).isoformat(), "data": data, **extra,
      }
      db.add(OutboundEvent(event_type=event_type, user_id=str(user_id), payload_json=json.dumps(payload)))
      db.commit()

  def flush_pending(db: Session, limit: int = 50) -> int:
      """Best-effort send of unsent events. Never raises — network errors stay queued."""
      pending = db.query(OutboundEvent).filter(OutboundEvent.sent_at.is_(None)).limit(limit).all()
      sent = 0
      for row in pending:
          try:
              resp = httpx.post(
                  f"{HUB_URL}/api/v1/integrations/event",
                  json=json.loads(row.payload_json),
                  headers={"X-Module-Key": HUB_KEY},
                  timeout=5.0,
              )
              if resp.status_code in (200, 201):
                  row.sent_at = datetime.now(timezone.utc)
                  sent += 1
              else:
                  row.attempts += 1
          except httpx.HTTPError:
              row.attempts += 1
          db.commit()
      return sent
  ```
  Punkty wywołania `queue_event(...)` (dodać po istniejącej logice zapisu, NIE zamiast niej): `backend/routers/flashcards.py` po oznaczeniu karty jako przejrzanej (`event_type="flashcard_reviewed"`), `backend/routers/errors.py` po zalogowaniu błędu (`event_type="error_logged"`), `backend/routers/thm_progress.py` po F6 (`event_type="thm_room_completed"`).
  `flush_pending` wołane: (a) przy starcie aplikacji (`lifespan` w `main.py`), (b) opcjonalnie z prostego `APScheduler`/pętli co N minut — jeśli brak już takiej infrastruktury w projekcie, wystarczy wywołanie przy każdym starcie + endpoint administracyjny `POST /api/v1/integrations/flush` do ręcznego triggerowania (test i debug).
  Zmienne środowiskowe: dopisać do `backend/.env.example`: `SYSTEM_GLOWNY_URL=http://localhost:8000`, `SYSTEM_GLOWNY_MODULE_KEY=` (puste — do wypełnienia po koordynacji z sesją System-Głowny, patrz Architektura docelowa punkt 2).
  Kryterium akceptacji: test `backend/tests/test_hub_publisher.py` z `httpx` zamockowanym (np. `respx` lub `unittest.mock.patch`) — sprawdza że `queue_event` zapisuje wiersz, `flush_pending` z mockowaną odpowiedzią 200 oznacza `sent_at`, z mockowanym `ConnectError` zostawia rekord niewysłany i NIE rzuca wyjątku dalej. `pytest backend/tests -q` przechodzi.
  Zależności: F5.1.

- [ ] **F5.3 Zaimplementować `POST /api/v1/directives`.**
  Opis: minimalny endpoint przyjmujący dyrektywy z huba, zapisujący stan lokalnie.
  Plik nowy: `backend/models/directive_state.py` (singleton-per-user tabela: `user_id`, `survival_mode: bool`, `priority_topic: str|None`, `quiet_hours_from: str|None`, `quiet_hours_to: str|None`).
  Plik nowy: `backend/routers/directives.py`:
  ```python
  from fastapi import APIRouter, Depends
  from pydantic import BaseModel
  from sqlalchemy.orm import Session
  from backend.database import get_db
  from backend.models.directive_state import DirectiveState

  router = APIRouter(prefix="/api/v1/directives", tags=["Directives"])

  class DirectivePayload(BaseModel):
      directive: str
      user_id: int = 1  # single-user projekt na dziś; wielu userów = przyszła rozbudowa
      enabled: bool | None = None
      value: str | None = None
      from_: str | None = None
      to: str | None = None

  @router.post("")
  def apply_directive(payload: DirectivePayload, db: Session = Depends(get_db)):
      state = db.query(DirectiveState).filter_by(user_id=payload.user_id).first()
      if not state:
          state = DirectiveState(user_id=payload.user_id)
          db.add(state)
      if payload.directive == "survival_mode":
          state.survival_mode = bool(payload.enabled)
      elif payload.directive == "priority":
          state.priority_topic = payload.value
      elif payload.directive == "quiet_hours":
          state.quiet_hours_from = payload.from_
          state.quiet_hours_to = payload.to
      db.commit()
      return {"status": "applied", "directive": payload.directive}
  ```
  Podłączyć `state.survival_mode` w `backend/routers/brain.py` (algorytm doboru dziennego zadania, `GET /api/v1/brain/...`) — gdy `True`, zwrócić wyłącznie 1 pozycję: sesję fiszek 5 minut, komunikat neutralny bez presji (zgodnie z zasadą feedbacku na poziomie zadania).
  Kryterium akceptacji: test `backend/tests/test_directives.py` — POST `survival_mode: true`, następnie GET z `brain.py` zwraca zredukowany plan; `pytest backend/tests -q` przechodzi.
  Zależności: F5.1.

- [ ] **F5.4 Skoordynować klucz modułu z sesją System-Głowny.**
  Opis: to zadanie wymaga wykonania w DRUGIM repo (`System-Glowny/`), poza zakresem sesji HackerLabAcademy — zapisać tu dokładnie co przekazać.
  Krok 1 (w tej sesji): wygenerować klucz: `python -c "import secrets; print(secrets.token_urlsafe(32))"`, zapisać w `HackerLabAcademy/backend/.env` (NIE commitować) jako `SYSTEM_GLOWNY_MODULE_KEY=<wygenerowany klucz>`.
  Krok 2 (przekazać człowiekowi/następnej sesji System-Głowny): dopisać do `System-Glowny/backend/.env` w zmiennej `MODULE_KEYS` parę `hackerlab-academy=<ten sam klucz>` (format: `MODULE_KEYS=lingua-ai=...,hackerlab-academy=<klucz>`).
  Krok 3: zweryfikować end-to-end: uruchomić oba backendy (`System-Glowny` na 8000, `HackerLabAcademy` na 8003), z HackerLabAcademy wywołać `flush_pending` (np. przez `POST /api/v1/integrations/flush` z F5.2) po wcześniejszym `queue_event`, sprawdzić w `System-Glowny`: `GET /api/v1/integrations/events?module=hackerlab-academy` zwraca opublikowany event.
  Kryterium akceptacji: end-to-end test manualny z kroku 3 przechodzi; `System-Glowny/backend/.env` NIE jest commitowany (weryfikacja: `git status` w `System-Glowny` nie pokazuje `.env`).
  Zależności: F5.2, F5.3.

- [ ] **F5.5 Przepisać/skasować `INTEGRATION_MAP.md` (dokończenie F4.6).**
  Opis: wykonać F4.6 teraz, gdy kontrakt jest faktycznie zaimplementowany, nie tylko planowany.
  Zależności: F5.1–F5.4.

## Faza 6 — Nowe funkcje pivotu: tracker THM i utrwalanie wiedzy

- [ ] **F6.1 Model `ThmProgress`.**
  Opis: ręczny wpis ukończonych pokoi/ścieżek THM (THM nie ma publicznego API do scrapowania postępu — to świadome ograniczenie, nie luka do naprawienia).
  Plik nowy: `backend/models/thm_progress.py`:
  ```python
  class ThmProgress(Base):
      __tablename__ = "thm_progress"
      id: Mapped[int] = mapped_column(primary_key=True)
      user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
      name: Mapped[str] = mapped_column(String)          # nazwa pokoju/ścieżki THM
      kind: Mapped[str] = mapped_column(String)           # "room" | "path"
      category: Mapped[str | None] = mapped_column(String, nullable=True)  # np. "Web", "Network", "Crypto"
      completed_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
      notes: Mapped[str | None] = mapped_column(Text, nullable=True)
      url: Mapped[str | None] = mapped_column(String, nullable=True)
  ```
  Kryterium akceptacji: `python -c "import backend.main"` przechodzi; tabela tworzy się przy starcie (`Base.metadata.create_all` w `database.py`/`main.py` lifespan — sprawdzić wzorzec istniejący w projekcie i podążyć za nim).
  Zależności: F3.1.

- [ ] **F6.2 [ROZSTRZYGNIĘTE 2026-08-09 — decyzja użytkownika: BEZ XP] Router CRUD `thm_progress`.**
  Plik nowy: `backend/routers/thm_progress.py` — `GET /api/v1/thm-progress?user_id=`, `POST /api/v1/thm-progress` (tworzy wpis, wywołuje `queue_event(..., event_type="thm_room_completed", ...)` z F5.2 — **bez systemu XP/punktów**, tylko checklisty ukończenia: pokój/ścieżka oznaczone jako zrobione/niezrobione, data, kategoria), `DELETE /api/v1/thm-progress/{id}`.
  Plik: `backend/main.py` — zarejestrować router.
  Kryterium akceptacji: test `backend/tests/test_thm_progress.py` — POST tworzy wpis, GET go zwraca, event trafia do `outbound_events`; **brak jakiegokolwiek pola `xp`/`points` w schemacie odpowiedzi**.
  Zależności: F6.1, F5.2.

- [ ] **F6.3 Frontend: strona `ThmProgress.jsx`.**
  Opis: formularz dodania wpisu (nazwa, typ pokój/ścieżka, kategoria, notatki, URL) + lista dotychczasowych wpisów + prosty licznik (liczba pokoi w tym miesiącu) — **informacyjny, nie porównawczy z innymi użytkownikami** (zakaz dark patterns, brak jakiegokolwiek rankingu nawet w formie "top categories" porównującej ludzi).
  Plik nowy: `frontend/src/pages/ThmProgress.jsx`.
  Plik: `frontend/src/App.jsx` — dodać `<Route path="/thm-progress" element={<ThmProgress />} />`; `frontend/src/components/Layout.jsx` — dodać link nawigacyjny; `frontend/src/api/client.js` — dodać `getThmProgress`, `createThmProgress`, `deleteThmProgress`.
  Kryterium akceptacji: `npm run build` przechodzi; ręczny test w przeglądarce — dodanie wpisu odświeża listę bez przeładowania strony.
  Zależności: F6.2.

- [ ] **F6.4 Rozszerzyć `quick-create` fiszek o notatki THM jako źródło.**
  Opis: `POST /api/flashcards/quick-create` (obecnie generuje definicję/przykład z gołego terminu przez AI) — dodać opcjonalne pole `source_notes: str | None`, gdy podane, AI generuje fiszkę na bazie wklejonej notatki z pokoju THM zamiast samego terminu.
  Plik: `backend/routers/flashcards.py` (endpoint `quick-create`), `backend/services/ai_service.py` (prompt budujący — dodać branch gdy `source_notes` obecne).
  Kryterium akceptacji: test rozszerzający istniejący test `quick-create` (sprawdzić plik testowy w `backend/tests/` — prawdopodobnie `test_flashcards.py`) — wywołanie z `source_notes` niepustym zwraca fiszkę zawierającą kontekst z notatki (np. mockowana odpowiedź AI, sprawdzić że prompt zawiera przekazany tekst).
  Zależności: F6.2 (żeby UI mogło linkować z `ThmProgress.jsx` do „dodaj fiszkę z tych notatek”, opcjonalnie — nie blokujące funkcjonalnie).

- [ ] **F6.5 Talia powtórkowa składni narzędzi (nmap/burp/metasploit/gobuster).**
  Opis: rozszerzyć istniejący Terminal Simulator o kategorię komend rekonesansu/eksploatacji i wygenerować z niej zestaw fiszek seed (nazwa narzędzia/flaga → co robi).
  Pliki: `frontend/src/data/terminal_scenarios.js` (dodać sceny/komendy), skrypt seed nowy: `backend/scripts/seed_tool_syntax_flashcards.py` (analogiczny do istniejących skryptów seedujących CVE/wideo — sprawdzić wzorzec w `backend/services/cve_service.py` lub podobnym), min. 20 fiszek pokrywających `nmap` (flagi skanowania), `burp` (funkcje Proxy/Repeater/Intruder), `metasploit` (podstawowe komendy `msfconsole`), `gobuster`/`ffuf` (fuzzing).
  Kryterium akceptacji: po uruchomieniu skryptu seed, `GET /api/flashcards?category=tool-syntax` (lub jak nazwana kategoria) zwraca ≥20 fiszek; `pytest backend/tests -q` przechodzi (jeśli dodano test seeda).
  Zależności: F6.2 (kolejność logiczna w fazie, nie twarda zależność techniczna).

- [ ] **F6.6 Domknąć `GET /api/v1/summary` o metryki THM (dokończenie F5.1).**
  Opis: wrócić do `backend/routers/integration.py` (F5.1) i uzupełnić TODO `thm_rooms_completed_today` faktyczną agregacją z `ThmProgress` oraz dodać event `thm_room_completed` do listy `events` zwracanej przez `/summary` dla wpisów z danego dnia.
  Kryterium akceptacji: `curl "http://localhost:8003/api/v1/summary?user_id=1&date=<dzisiaj>"` po dodaniu wpisu THM tego dnia pokazuje `thm_rooms_completed_today >= 1` i odpowiadający event w `events`.
  Zależności: F6.1, F5.1.

## Faza 7 — Nauka: wskazówki stopniowane i technika utrwalania (HL-2, HL-4, HL-5, HL-6, HL-7)

- [ ] **F7.1 Wskazówki stopniowane Mentora AI (HL-4).**
  Opis: `backend/services/lesson_service.py`, funkcja `mentor_chat` (obecnie linie ok. 250-259) nie ma żadnego ograniczenia przed podaniem gotowej odpowiedzi. Zmienić prompt systemowy tak, żeby wymuszał trójstopniową eskalację: (1) kierunek myślenia (pytanie naprowadzające), (2) nazwa techniki/koncepcji bez konkretnych kroków, (3) konkretny krok — tylko jeśli użytkownik explicite poprosi o kolejny poziom wskazówki (np. przez dodatkowe pole w request `hint_level: int` przekazywane z frontendu przy kolejnym kliknięciu „daj mi więcej”).
  Plik: `backend/services/lesson_service.py` (`mentor_chat`), `backend/routers/mentor.py` (`ChatRequest` — dodać opcjonalne pole `hint_level: int = 1`), `frontend/src/pages/Mentor.jsx` (przycisk „poproś o kolejną wskazówkę” inkrementujący `hint_level`).
  Poziom dowodu do zapisania w `NEURO_PLAN.md` przy tej funkcji: **HIPOTEZA** — nie ma badania mierzącego skuteczność tej konkretnej trójstopniowej eskalacji w kontekście cybersecurity; opiera się na ogólnej zasadzie scaffoldingu (Wood, Bruner & Ross 1976) i „productive struggle” — oznaczyć jawnie jako hipotezę do zweryfikowania na własnych danych (czy użytkownicy rzadziej proszą o `hint_level=3` z czasem).
  Kryterium akceptacji: test `backend/tests/test_mentor_hints.py` — `hint_level=1` w odpowiedzi AI (zamockowanej) nie zawiera gotowego rozwiązania (heurystyka testu: prompt do AI zawiera jawny zakaz podania rozwiązania na tym poziomie — testować że prompt jest budowany poprawnie, nie treść realnej odpowiedzi AI, bo to niedeterministyczne).
  Zależności: F1.3 (NEURO_PLAN zaktualizowany o adnotacje pivotu, żeby dopisać tu adnotację dowodu w tym samym miejscu spójnie).

- [ ] **F7.1b [NOWE 2026-08-09 — decyzja użytkownika: powiadomienie przy przekroczeniu progu, nie twardy limit] Licznik wywołań AI Mentora + próg ostrzegawczy.**
  Opis: F7.1 zwiększa liczbę wywołań API do Gemini/OpenRouter (kilka poziomów hinta zamiast jednej odpowiedzi).
  Użytkownik NIE chce twardego cutoffu (funkcja ma dalej działać po przekroczeniu progu), tylko powiadomienie.
  Plik nowy: `backend/services/ai_usage_tracker.py` — licznik wywołań/tokenów per dzień (lub miesiąc, do
  ustalenia — domyślnie dzień, prostsze) w nowej tabeli `ai_usage_log` (kolumny: `date`, `provider`, `calls`,
  `estimated_cost` jeśli dostawca zwraca token count w odpowiedzi).
  Próg: `AI_USAGE_WARN_THRESHOLD` w `.env` (np. domyślnie 100 wywołań/dzień — wartość umowna, użytkownik
  koryguje wg realnego zużycia po tygodniu obserwacji).
  Mechanizm powiadomienia: gdy próg przekroczony, zapisać wpis do logu na poziomie WARNING (`logger.warning(...)`)
  widoczny w konsoli/logach backendu przy najbliższym uruchomieniu — **nie blokować** kolejnych wywołań Mentora.
  Docelowo (poza zakresem tego zadania, zależne od F1.3/INT-6 ekosystemu): gdy System-Główny ma gotowy
  centralny notifier, przełączyć na realne powiadomienie push zamiast logu.
  Kryterium akceptacji: test że po N wywołaniach mockowanych przekraczających próg pojawia się wpis WARNING
  w logu; wywołanie N+1 nadal zwraca poprawną odpowiedź Mentora (brak blokady).
  Zależności: F7.1.

- [ ] **F7.2 Retrieval po pokoju THM (HL-6, adaptacja z „retrieval po labie”).**
  Opis: Defense Mode istnieje jako niezależne ćwiczenie code-fix, niepowiązane z zakończeniem czegokolwiek. Po dodaniu wpisu `ThmProgress` (F6.2), zaproponować użytkownikowi 3 pytania retrieval-practice powiązane z kategorią pokoju (np. kategoria „Web” → pytania o OWASP Top 10 z puli w `backend/routers/exercises.py`).
  Plik: `backend/routers/thm_progress.py` (po `POST`, opcjonalny response field `suggested_retrieval_questions: list[dict]` z 3 pytaniami dobranymi po `category`), `backend/services/exercise_service.py` (funkcja doboru pytań po kategorii, jeśli nie istnieje — dodać).
  Poziom dowodu: retrieval practice ma wsparcie **META** (Roediger & Karpicke 2006; Adesope, Trevisan & Sundararajan 2017 meta-analiza testing effect) — realny efekt, nie hipoteza; zapisać w `NEURO_PLAN.md` z tym odniesieniem.
  Kryterium akceptacji: `POST /api/v1/thm-progress` z `category="Web"` zwraca `suggested_retrieval_questions` niepustą listę; test przechodzi.
  Zależności: F6.2, F1.3.

- [ ] **F7.3 Interleaving w powtórkach (HL-5).**
  Opis: obecna kolejka fiszek (SM-2) najpewniej grupuje po temacie/dacie dodania. Dodać tryb powtórki „mieszany” — losowa kolejność kart z różnych kategorii/tematów w jednej sesji zamiast blokowo po temacie, z pytaniem interleavingowym „który atak tu pasuje?” dla kart typu podatność.
  Plik: `backend/routers/flashcards.py` (nowy query param `mode=interleaved` na endpointzie listy kart do powtórki, tasujący wynik między kategoriami zamiast sortować po kategorii).
  Poziom dowodu: **RCT/META** — interleaving ma solidne wsparcie (Rohrer & Taylor 2007; Rohrer, Dedrick & Stershic 2015 dla kategorii pojęciowych zbliżonych do „typ podatności”) — zapisać z odniesieniem w `NEURO_PLAN.md`.
  Kryterium akceptacji: test sprawdzający że `mode=interleaved` z kartami z ≥2 kategorii nie zwraca ich pogrupowanych blokowo (heurystyka: sprawdzić że w pierwszych N kartach występuje >1 kategoria, gdy dostępne).
  Zależności: F1.3.

- [ ] **F7.4 Adaptacyjna trudność w `brain.py` (HL-7) — HIPOTEZA kalibrowana.**
  Opis: `backend/routers/brain.py` implementuje wyłącznie stałą kolejkę priorytetów (błędy → fiszki → nowy temat → niedokończony lab → najsłabszy temat) — „niedokończony lab” trzeba usunąć/zamienić po Fazie 2 (referencja do labs.py, sprawdzić i poprawić jeśli tam jest). Dodać prosty dobór trudności następnego pytania/fiszki wg trafności w ostatnich N próbach (strefa 70-85% jako punkt startowy — jawnie oznaczony jako hipoteza do kalibracji na własnych danych, nie twardy fakt).
  Plik: `backend/routers/brain.py`, `backend/services/` — nowa funkcja `pick_next_difficulty(recent_accuracy: float) -> int`.
  Kryterium akceptacji: test jednostkowy `pick_next_difficulty` — przy accuracy > 0.85 zwraca wyższy poziom trudności niż przy accuracy < 0.70; `NEURO_PLAN.md` ma wpis HL-7 oznaczony `HIPOTEZA` z planem walidacji (np. „po 4 tygodniach danych sprawdzić czy accuracy użytkownika stabilizuje się w paśmie 70-85%”).
  Zależności: F2.7 (usunięcie referencji do „niedokończony lab” z kolejki priorytetów), F1.3.

## Faza 8 — Silnik FSRS wspólny (zablokowane, dokumentacja przygotowawcza)

- [ ] **F8.1 Udokumentować gotowość do migracji SM-2 → FSRS.**
  Opis: to zadanie jest **zablokowane** przez `System-Glowny` Fazę 3 (`MASTER_PLAN.md` punkt „Faza 3 — Learning Engine”, zadanie 10: „Wydzielenie FSRS z LinguaAI jako usługa wspólna”), która jeszcze nie istnieje. Nie implementować migracji teraz — przygotować grunt.
  Plik: `NEURO_PLAN.md` — dopisać sekcję „## Migracja FSRS (zablokowane przez System-Głowny F3)” z opisem: obecny algorytm to `backend/services/sm2_service.py` (SM-2), docelowy stan to wywołanie wspólnego serwisu Learning Engine (adres/kontrakt nieznany do czasu powstania), cel migracji po pivocie to harmonogram powtórek dla „komend/konceptów THM” (fiszek narzędziowych z F6.5), nie dla dawnej talii tematów deklaratywnych.
  Kryterium akceptacji: sekcja istnieje, jawnie oznaczona jako `BLOCKED` z warunkiem odblokowania.
  Zależności: F1.3, F6.5.

## Faza 9 — Jakość: testy frontendu i uporządkowanie dużych plików

- [ ] **F9.1 Podnieść pokrycie testami frontendu dla modułów, które przetrwały pivot.**
  Opis: obecnie 2 pliki testowe / 4 asercje na 20 stron (po Fazie 2: mniej stron, ale wciąż za mało). Priorytet stron do pokrycia testem (wg audytu, kolejność): Flashcards, Errors, Mentor, Dashboard, nowo dodana ThmProgress (F6.3).
  Pliki nowe: `frontend/src/test/pages/Flashcards.test.jsx`, `frontend/src/test/pages/Errors.test.jsx`, `frontend/src/test/pages/Mentor.test.jsx`, `frontend/src/test/pages/Dashboard.test.jsx`, `frontend/src/test/pages/ThmProgress.test.jsx` — wzorem istniejącego `frontend/src/test/App.test.jsx` (React Testing Library + `vitest`, mockowanie `frontend/src/api/client.js`).
  Kryterium akceptacji: `npx vitest run` pokazuje ≥15 nowych asercji (zamiast obecnych 4), wszystkie zielone; każdy z pięciu plików ma co najmniej: (a) render bez crasha, (b) jedną interakcję użytkownika (klik/input) zmieniającą stan widoczny na ekranie.
  Zależności: F2.8, F6.3, F7.1.

- [ ] **F9.2 Rozbić duże pliki serwisowe (dług samoodnotowany w `IMPROVEMENTS.md`).**
  Opis: `achievement_service.py` (331 LOC), `cve_service.py` (308 LOC), `attack.py` (usunięty w F2.2 — wypada z listy), `cves.py` (288 LOC) — bez akcji od 2026-06-07 wg audytu. Podzielić wg odpowiedzialności (np. `achievement_service.py` → `achievement_rules.py` (definicje progów) + `achievement_service.py` (logika przyznawania) + `achievement_queries.py` (odczyty)).
  Pliki: `backend/services/achievement_service.py`, `backend/services/cve_service.py`, `backend/routers/cves.py`.
  Kryterium akceptacji: żaden z rozbitych plików nie przekracza ok. 200 LOC; `pytest backend/tests -q` przechodzi bez zmian w testach (refaktor musi być behawioralnie neutralny — jeśli test się zmienia, to tylko import path, nie asercje).
  Zależności: F2.8 (nie refaktoryzować równolegle z usuwaniem kodu w tych samych plikach, jeśli jakiś nachodzi — sprawdzić czy `achievement_service.py` odwołuje się do CTF leaderboard przed F2.3; jeśli tak, F2.3 najpierw).

- [ ] **F9.3 Finalny przegląd całościowy i aktualizacja `CHANGELOG.md`.**
  Opis: po wszystkich fazach, jeden wpis podsumowujący w `CHANGELOG.md` z datą, listą wykonanych faz, liczbą testów przed/po, potwierdzeniem `docker compose up --build` działa end-to-end.
  Plik: `HackerLabAcademy/CHANGELOG.md`.
  Kryterium akceptacji: wpis istnieje, wszystkie kryteria sukcesu z sekcji „Cel projektu i mierzalne kryteria sukcesu” tego planu odhaczone i zweryfikowane komendą (nie „powinno działać” — faktyczny output komendy wklejony lub streszczony w wpisie).
  Zależności: wszystkie poprzednie fazy.

---

## Ryzyka i decyzje otwarte

Decyzje wymagające człowieka (nie AI) — wykonawca planu MA ZATRZYMAĆ SIĘ i zapytać / oznaczyć jako `BLOCKED` przy tych punktach, nie decydować samodzielnie:

1. [ROZSTRZYGNIĘTE 2026-08-09 — decyzja użytkownika] **React 19 + Router v7.** Standard ekosystemu podniesiony
   do dokładnie tych wersji (LinguaAI = referencja). HackerLabAcademy nie zmienia nic we frontendzie — patrz F4.3.
2. [ROZSTRZYGNIĘTE 2026-08-09 — decyzja użytkownika] **Brak XP w ogóle (F6.2).** Zamiast punktacji: tylko
   checklisty ukończenia (zrobione/niezrobione) — minimalizuje ryzyko dark pattern.
3. [ROZSTRZYGNIĘTE 2026-08-09 — decyzja użytkownika] **CTF zostaje, leaderboard znika (F2.3).** Mechanika
   rozwiązywania zagadek (punkty per użytkownik, bez porównania z innymi) zostaje jako zgodna z „gamifikacja
   informacyjna” z MASTER_PLAN — praktyka umiejętności, nie rywalizacja.
4. [ROZSTRZYGNIĘTE 2026-08-09 — decyzja użytkownika] **Migracja `lab_type` → `practice_hint` (F2.7): zachować
   historyczne dane `dvwa_*`.** Nie kasować — tylko przemapować pole, dane historyczne zostają w bazie.
5. [ROZSTRZYGNIĘTE 2026-08-09 — decyzja użytkownika, globalna dla całego ekosystemu] **Priorytet czasowy.**
   Kolejność pracy nad modułami: najpierw dociągnąć dojrzałe, już działające moduły (LinguaAI, ForgeBody,
   HackerLabAcademy, LookCoach, Dieta — w tej grupie bez sztywnej podkolejności), dopiero potem moduły od
   zera (Edukacja, Finanse, Mentalność-i-Psychika, memory-forge jako mniej dojrzały prototyp). HackerLabAcademy
   jest w pierwszej grupie — realizować Fazy 0-7 tego planu teraz, nie czekać na Fazę 3 ekosystemu przed
   Fazą 5 (integracja) — integracja i tak jest tylko jedną z 10 faz, reszta nie jest blokowana.
6. [ROZSTRZYGNIĘTE 2026-08-09 — decyzja użytkownika] **Budżet AI dla Mentora (F7.1/F7.1b): powiadomienie
   przy przekroczeniu progu, nie twardy limit.** Wartość progu (domyślnie 100 wywołań/dzień) jest umowna —
   skoryguj po tygodniu realnego użycia.
7. [ROZSTRZYGNIĘTE 2026-08-09 — sprawdzone bezpośrednio] **`HackerLabAcademy.db` w root jest aktywną bazą.**
   Zmierzone 2026-08-09: `root/HackerLabAcademy.db` = 4 575 232 B, modyfikowany dziś (aktywny) vs.
   `backend/HackerLabAcademy.db` = **0 bajtów** (pusty, martwy plik — prawdopodobnie relikt po zmianie CWD
   przy jakimś uruchomieniu). F0.2/F3.1: usunąć/zignorować pusty plik w `backend/`, `DATABASE_URL` ma
   wskazywać na plik w root (albo skopiować root do `backend/data/` jeśli F3.1 tego wymaga — ale ze
   ŹRÓDŁA = root, nigdy odwrotnie).

---

## Definition of Done całego planu

Plan jest ukończony, gdy WSZYSTKIE poniższe są prawdą jednocześnie (weryfikowalne komendą, nie deklaracją):

1. `git status` w `HackerLabAcademy/` jest czysty; wszystkie zmiany z Faz 0-9 są w historii commitów z konwencją `<type>: co i dlaczego`.
2. `pytest backend/tests -q` przechodzi w 100%, liczba testów udokumentowana w `CHANGELOG.md` z uzasadnieniem każdej zmiany liczby.
3. `npm run build && npx vitest run` w `frontend/` przechodzi w 100%.
4. `docker compose up --build` z katalogu `HackerLabAcademy/` uruchamia działający stack: `curl http://localhost:8003/api/health` → 200, `curl http://localhost/` → 200 (frontend).
5. Zero endpointów/UI zawiera ranking porównujący użytkowników; kara za hint w CTF jest faktycznie naliczana.
6. `GET http://localhost:8003/api/v1/summary?user_id=1` zwraca poprawny JSON zgodny z kontraktem opisanym w sekcji „Architektura docelowa”; `POST http://localhost:8000/api/v1/integrations/event` z `X-Module-Key` modułu przyjmuje event opublikowany przez `hub_publisher.py` (zweryfikowane end-to-end z uruchomionym `System-Glowny`).
7. `NEURO_PLAN.md` ma przy każdej funkcji wpływającej na naukę poziom dowodu (META/RCT/OBS/HIPOTEZA), zgodny z tym co faktycznie zaimplementowano (nie z popularnym uproszczeniem badania).
8. `README.md`, `HackerLabAcademy/CLAUDE.md`, `TASKS.md`, `INTEGRATION_MAP.md` nie zawierają twierdzeń sprzecznych z aktualnym stanem kodu (liczby routerów/modeli, wersje frontendu, port, opis produktu).
9. Zero plików `cyber_tutor.db`, `Zmiany_CyberTutor.txt`, `test.db`, `backend/routers/labs.py`, `backend/routers/attack.py` w drzewie roboczym.
10. Wszystkie punkty z sekcji „Ryzyka i decyzje otwarte” mają jawną decyzję człowieka zapisaną (np. w `decisions/DEC-00X.md`) — plan nie uznaje się za ukończony, jeśli AI podjęło którąkolwiek z tych decyzji samodzielnie zamiast eskalować.
