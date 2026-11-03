# Plan działania HackerLabAcademy — 2026-11-03

Przegląd całego systemu (sesja w chmurze, 2026-11-03) i konkretny plan z polami do odhaczania.
Uzupełnia `ACTION_PLAN.md` (pivot THM z 2026-08-09) — tamten plan jest w większości **niewykonany**,
a jego checkboxy nie odpowiadają stanowi kodu. Ten plik weryfikuje każdy punkt w kodzie i dokłada
nowe znaleziska. Po wykonaniu punktu: `[x]` + data.

Gałąź robocza: `claude/przeglad-2026-11` (PR do `master`, merge decyduje właściciel).
Lokalnie i na GitHubie `master` = `ea7190d` (sprawdzone 2026-11-03, brak niewysłanych zmian).

---

## 1. Ocena stanu (zmierzone 2026-11-03)

| Obszar | Wynik |
|---|---|
| Testy backendu | **100 passed** (Python 3.13, venv) |
| Testy frontendu | 4 passed (2 pliki) — prawie brak pokrycia 20 stron |
| Build frontendu | przechodzi |
| `npm ci` | **pada** — `package-lock.json` niezgodny z `package.json` (ajv, json-schema-traverse) |
| ruff backend | 278 błędów (71 nieposortowane importy, 64 B008 `Depends` — do wyciszenia w configu, 57 `except Exception`, 40 `utcnow`) |
| ESLint frontend | 22 błędy, 9 ostrzeżeń (nieużywane zmienne, setState w efekcie, funkcje nieczyste w renderze) |
| CI / pre-commit | **brak** (`.github/workflows` nie istnieje) |
| Integracja z hubem | `/api/v1/summary`, kolejka eventów, `/api/v1/directives` — zrobione 2026-09-27 |
| Pivot THM (ACTION_PLAN 2026-08-09) | Fazy 0–4, 6–9: **niewykonane** (poza portem 8003 i usunięciem CTF) |

### Najważniejsze problemy

1. **Pivot w połowie.** Laby DVWA (`labs.py`, `lab_service.py` z `subprocess docker`), Attack Scenario
   (`attack.py`, `AttackScenario.jsx`) i trasy `/lab`, `/attack` nadal działają. Trackera THM (Faza 6) nie ma.
2. **CTF usunięty w całości** (`1b1f2ff`), choć decyzja nr 3 z 2026-08-09 brzmiała: *CTF zostaje, znika
   tylko leaderboard*. Do decyzji (D-HLA-1).
3. **Docker nie działa**: `backend/Dockerfile` nie ma `CMD`, kontekst `./backend` + `COPY . .` nie daje
   pakietu `backend.*`, Python 3.11 zamiast 3.12.
4. **Brak migracji**: `create_all` przy starcie nie dodaje kolumn do istniejących tabel (już raz
   potrzebne były ręczne skrypty `migrate_flashcards.py`, `update_flashcard_schema.py` w roocie).
5. **Śmieci w repo (publicznym)**: 2 kopie bazy `HackerLabAcademy.db.backup.*` (po 11 MB, dane
   testowe „AuditBot” + 10 130 CVE — nic prywatnego), 3 pliki `.bak`, skrypty jednorazowe w roocie
   (`check_*.py`, `final_verification.py`, `migrate_flashcards.py`, `update_flashcard_schema.py`,
   `test_api_migration.py`), `Zmiany_CyberTutor.txt`.
6. **Mentor AI trzyma rozmowy w pamięci procesu** (`_sessions: dict` w `routers/mentor.py`) — restart = utrata.
7. **Dwa silniki powtórek**: fiszki na FSRS, ale `flashcards.py:125` nadal importuje `sm2_service`.
8. **Dokumentacja nieaktualna**: `CLAUDE.md` (prefiks `/api/` zamiast `/api/v1/`, router `ctf.py`,
   React 18/Router v6, Gemini 2.0), `README.md` (CTF z rankingiem).
9. **Ekosystem**: HackerLabAcademy (:8003) nie jest w `System-Glowny/scripts/start-ekosystem.ps1`
   ani w `backup_baz.py` — nie startuje z resztą i nie ma kopii bazy.

---

## 2. Decyzje do podjęcia przez właściciela

- [ ] **D-HLA-1 CTF** (2026-11-03: właściciel poprosił o wyjaśnienie — czeka): (a) zostawić usunięty, (b) przywrócić zagadki CTF bez rankingu (zgodnie z decyzją z 2026-08-09).
- [x] **D-HLA-2 Kopie bazy w historii git** — 2026-11-03: wybrane (a) tylko `git rm` (zostają w historii, dane nieprywatne — zalecane),
      (b) przepisanie historii (force push — zmienia hashe wszystkich commitów).
- [x] **D-HLA-3 Start i kopie w ekosystemie** — 2026-11-03: NIE TERAZ (sesja lokalna): dopisać HackerLabAcademy (i Edukację) do `start-ekosystem.ps1`
      i `backup_baz.py` w System-Glowny (zmiana w innym repo, osobny PR).

Punkty niezależne od decyzji wykonuję od razu po akceptacji planu.

---

## 3. Plan

### Faza A — Higiena i jakość (bez zmiany zachowania)

- [x] **A1** (2026-11-03) Zregenerować `frontend/package-lock.json` (`npm install`), sprawdzić `npm ci` + build.
- [x] **A2** (2026-11-03) Usunąć z repo: `HackerLabAcademy.db.backup.*` (wg D-HLA-2), `*.py.bak` (3), `Zmiany_CyberTutor.txt`,
      jednorazowe skrypty z roota (`check_backend.py`, `check_db_schema.py`, `check_flashcard_schema.py`,
      `check_schema.py`, `final_verification.py`, `migrate_flashcards.py`, `update_flashcard_schema.py`,
      `test_api_migration.py`) — wcześniej `grep`, że nic ich nie importuje; `.gitignore`: `*.db.backup.*`, `*.bak`.
- [x] **A3** (2026-11-03) `.gitignore`: usunąć regułę `backend/.env.example` (ACTION_PLAN F0.3); `.env.example` aktualny
      względem `config.py` (w tym `SYSTEM_GLOWNY_URL`, `SYSTEM_GLOWNY_MODULE_KEY`).
- [x] **A4** (2026-11-03; `utcnow()` zostawione — zamiana na strefowe daty zmieniłaby porównania z bazą) ruff: konfiguracja w `pyproject.toml` (ignore B008 dla FastAPI `Depends`), `ruff check --fix`
      dla bezpiecznych reguł (importy, f-stringi), `utcnow()` → `now(UTC)`; cel: 0 błędów lub udokumentowane wyjątki.
- [x] **A5** (2026-11-03) ESLint: naprawić 22 błędy i 9 ostrzeżeń (`--max-warnings 0`).
- [x] **A6** (2026-11-03) CI `.github/workflows/ci.yml`: ruff, pytest, eslint, vitest, build (wzór: LookCoach). `.pre-commit-config.yaml`.

### Faza B — Fundamenty techniczne

- [x] **B1** (2026-11-03) Alembic: baseline z obecnego schematu + `alembic upgrade head` w lifespan (baza sprzed Alembica
      oznaczana na baseline), migracje idempotentne. Usuwa potrzebę ręcznych skryptów schematu.
- [x] **B2** (2026-11-03; obraz niezbudowany w chmurze — brak demona Dockera, do sprawdzenia lokalnie) Docker: `Dockerfile` z kontekstem roota (pakiet `backend.*`), `CMD uvicorn backend.main:app --port 8003`,
      Python 3.12, wolumen na bazę; test `test_ports.py` rozszerzony o sprawdzenie `CMD`.
- [x] **B3** (2026-11-03) Mentor AI: rozmowy w bazie (model `MentorMessage`, ostatnie 20 na sesję) zamiast `_sessions: dict`.
- [x] **B4** (2026-11-03) Jeden silnik powtórek: usunąć ścieżkę SM-2 z `flashcards.py:125` (i `sm2_service.py`, jeśli nic
      innego nie używa) — FSRS wszędzie; test na ocenę karty po migracji.

### Faza C — Dokończenie pivotu THM (decyzje z 2026-08-09 już podjęte)

- [x] **C1** (2026-11-03) Usunąć laby DVWA: `routers/labs.py`, `services/lab_service.py`, `tests/test_labs.py`, `pages/Lab.jsx`,
      trasa `/lab`, link w menu. Model `lab_attempt` zostaje w bazie (dane historyczne), bez routera.
- [x] **C2** (2026-11-03) Usunąć Attack Scenario: `routers/attack.py`, `pages/AttackScenario.jsx`, trasa `/attack`
      (model zostaje w bazie tylko jeśli ma dane — inaczej usunąć i migracją dropnąć tabelę).
- [x] **C3** (2026-11-03) `lab_type` → `practice_hint` (migracja Alembic, dane `dvwa_*` zachowane — decyzja nr 4)
      i odpięcie generacji labów od DVWA w `lesson_service.py`.
- [x] **C4** (2026-11-03) Tracker THM: model `ThmProgress` (pokój/ścieżka, kategoria, status zrobione/niezrobione — **bez XP**,
      decyzja nr 2, data, notatki, link), router CRUD `/api/v1/thm`, strona `ThmProgress.jsx`, testy.
- [x] **C5** (2026-11-03) Fiszki z notatek THM: `quick-create` przyjmuje `source_notes` + nazwę pokoju jako źródło.
- [x] **C6** (2026-11-03) Talia składni narzędzi (nmap, gobuster, burp, metasploit, hydra) — seed fiszek w osobnej kategorii.
- [x] **C7** (2026-11-03) `/api/v1/summary` + eventy: pokoje THM ukończone danego dnia (`thm_room_completed`).
- [ ] **C8** CTF wg D-HLA-1.

### Faza D — Nauka (ACTION_PLAN Faza 7)

- [x] **D1** (2026-11-03) Mentor: wskazówki stopniowane (najpierw pytanie naprowadzające, potem podpowiedź, na końcu odpowiedź).
- [x] **D2** (2026-11-03) Licznik wywołań AI Mentora + powiadomienie po progu (domyślnie 100/dzień, nie twarda blokada — decyzja nr 6).
- [x] **D3** (2026-11-03) Retrieval po pokoju THM: po oznaczeniu pokoju jako ukończony — 3 pytania z notatek (bez oceny osoby).
- [x] **D4** (2026-11-03) Interleaving w powtórkach (mieszanie kategorii w kolejce due).

### Faza E — Dokumentacja i testy frontendu

- [x] **E1** (2026-11-03) `CLAUDE.md`, `README.md`, `CODE_MAP.md`, `INTEGRATION_MAP.md` zgodne z kodem (prefiks `/api/v1`, lista
      routerów, React 19/Router 7, model AI, brak CTF/labów, tracker THM).
- [x] **E2** (2026-11-03: Mentor, ThmProgress, Flashcards, Practice; Dashboard/Errors/Brain bez zmian — testy przy następnej zmianie) Testy vitest dla stron, które zostają (Dashboard, Flashcards, Errors, Mentor, ThmProgress, Brain).
- [x] **E3** (2026-11-03) `ACTION_PLAN.md` (2026-08-09): odhaczyć wykonane punkty z odnośnikiem do tego planu; `CHANGELOG.md`.

---

## 4. Kryteria zakończenia

- `pytest backend/tests -q` 100% zielone; `npm ci && npm run build && npx vitest run` zielone; ruff i ESLint 0 błędów; CI zielone.
- `docker compose up --build` → `curl :8003/api/health` 200 i frontend 200 (sprawdza właściciel lokalnie — w chmurze brak Dockera).
- Brak tras `/lab`, `/attack` i kodu uruchamiającego kontenery; tracker THM działa end-to-end.
