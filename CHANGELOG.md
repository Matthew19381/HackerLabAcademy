# HackerLabAcademy — Changelog

---

## [Unreleased] — 2026-09-27
### Naprawione (przejście aplikacji w przeglądarce)
- **Każde wysłanie quizu kończyło się 500**: osiągnięcia odwoływały się do nieistniejących pól
  (`UserDefenseAttempt.completed`, `ConversationSession.completed`) — teraz `is_correct` / `ended_at`; test.
- Analiza AI quizu zawsze padała: domyślny model OpenRouter `gemini-2.0-flash-001` wycofany (404) — domyślnie
  `gemini-2.5-flash`, a przy 404 automatyczne ponowienie z aktualnym modelem.
- Informacja zwrotna po quizie oceniała osobę („uczeń zgadywał”, „brak wiedzy”) — prompt i etykiety opisują
  pojęcie („nowe pojęcie”, „do utrwalenia”).
- Mindmap: brak importu d3 wywracał całą aplikację (pusta strona); do tego podwójne `JSON.parse`. Dodany
  ErrorBoundary — błąd jednej strony nie gasi menu.
- `start.bat`/`start.ps1` uruchamiały backend na :8001 (port LinguaAI), a frontend proxował na :8003 — API nie
  działało przy starcie skryptem. Ścieżka bazy bezwzględna (względna tworzyła pustą bazę przy starcie z `backend/`);
  `DATABASE_URL` z env.
- Testy mogły wysłać prawdziwe, płatne zapytanie do AI, gdy klucz był w środowisku — klucze AI zerowane w `conftest`.
- Literówki: „Przepełnij kill chain” → „Przejdź”, „Skryptowa Dziecię” → „Skryptowe dziecko”.
### Dodane
- **Integracja z System-Głównym (F5.1–F5.3)**: `GET /api/v1/summary` (fiszki przejrzane/zaległe, błędy
  zalogowane/otwarte, XP; bez streaku), kolejka eventów wychodzących `outbound_events` + `services/hub_publisher.py`
  (`flashcard_reviewed`, `quiz_completed`, `error_resolved`; wysyłka w tle, przy starcie i ręcznie
  `POST /api/v1/integrations/flush`; hub niedostępny = event czeka), `POST /api/v1/directives`
  (survival_mode → plan dnia skrócony do 5 minut fiszek, priority, quiet_hours). Testy `tests/test_hub_integration.py`.
### Naprawione
- **Artykuły**: `POST /articles/{slug}/read` i `/quiz/submit` wołane przez UI nie istniały (404); lista artykułów
  wracała jako `{items}`, a strona oczekiwała tablicy (crash); szczegóły nie zwracały `quiz_questions`. Test kontraktu
  `tests/test_frontend_contract.py`.
- **51 filtrów SQLAlchemy z `Model.pole is True/False/None`** (porównanie tożsamości w Pythonie → stałe False,
  nie SQL): puste listy CVE, scenariuszy ataku, wyzwań obrony, certyfikatów, wideo, writeupów, statystyk błędów,
  osiągnięć; „Napraw N błędów” nigdy nie pojawiało się w planie dnia. Teraz `.is_(...)`/`.isnot(None)`, test
  regresyjny + skan kodu (`tests/test_sql_boolean_filters.py`).
- `fsrs` brakował w `requirements.txt` — świeża instalacja nie startowała (`ModuleNotFoundError`).

## [2026-04-06] — Docker Production Deployment (nginx + multi-stage)

### Deployment & Infrastructure
- ✅ **Frontend:** Multi-stage Docker build (Node 20 → nginx:alpine)
- ✅ **Nginx:** Static file serving with SPA fallback, API reverse proxy
- ✅ **Docker Compose:** Production-ready config (frontend:80 → nginx, backend:8001)
- ✅ **Healthcheck:** Backend timeout increased to 40s for reliability
- ✅ **CORS:** Nginx proxy eliminates CORS issues (no browser config needed)

### Backend Refactoring
- ✅ **Import paths:** All `from backend.` → relative imports (`from database`, `from models`, etc.)
- ✅ **Path fixes:** `backend/audio` → `audio`, `backend/exports` → `exports`
- ✅ **SQLAlchemy fix:** `ConversationTurn.metadata` → `turn_metadata` (reserved name conflict)
- ✅ **Model imports:** `YoutubeVideo` → `YouTubeVideo`, `AttackStepAttempt` → `UserAttackProgress`
- ✅ **Config module:** Added `PDF_EXPORT_DIR` and `AUDIO_DIR` as module-level constants
- ✅ **API fixes:**
  - `routers/exercises.py` — syntax error fix (HTTPException detail)
  - `routers/certificates.py` — import from `certificate_service` (not `pdf_service`)
- ✅ **Writeups support:** Added `generate_pdf_from_markdown()` to `pdf_service.py`

### Post-Deployment Notes
- First build: ~2-3 minutes (downloads base images, npm install, pip install)
- Hot reload disabled — rebuild required for code changes (`docker-compose up --build`)
- Volumes: `backend_data`, `backend_audio`, `backend_exports` (persistent)
- Access:
  - Frontend: http://localhost
  - Backend API: http://localhost:8001/docs
  - Health: http://localhost:8001/api/health

---

## [2026-04-02] — Complete Feature Parity Implementation

### Zakończone zadania (P1, P2, P3)
- ✅ **P1-1:** CVE Explorer (backend + frontend, 4 sample CVEs, add to flashcards)
- ✅ **P1-2:** YouTube Security Videos per Topic (11 sample videos, category filters)
- ✅ **P1-4:** Study Timer (global, 15/30/60 min, persistent, desktop notifications)
- ✅ **P2-1:** CTF Challenge Mode (5 challenges, leaderboard, points)
- ✅ **P2-3:** Terminal Simulator (4 scenarios: nmap, curl, bash, sqlmap)
- ✅ **P2-4:** Defense Mode (code fix challenges, AI evaluation via Gemini)
- ✅ **P2-5:** Attack Scenario (multi-step kill chain: SQLi, XSS)
- ✅ **P2-6:** Topic Mindmap (D3 force-directed graph, drag nodes, unlock visualization)
- ✅ **P3-1:** Daily Completion Indicator (lab + quiz, Dashboard bar)
- ✅ **P3-4:** Certificates PDF (generation per completed category, fpdf2)

### Nowe pliki
- Backend models: `defense.py`, `certificate.py`
- Backend routers: `defense.py`, `certificates.py`, `daily.py`
- Backend services: `certificate_service.py`
- Frontend pages: `Defense.jsx`, `Mindmap.jsx`, `Certificates.jsx`
- Frontend API: defense, daily, certificates endpoints
- Layout navigation: Defense (Shield), Attack (Skull), Mindmap (Network), Certificates (Award)
- Data: `terminal_scenarios.js` expanded with sqlmap

### Wymagane kroki post-deployment
1. `cd frontend && npm install` (dodano `d3`)
2. Restart backend (nowe tabele utworzą się automatycznie)
3. Verify: `/defense`, `/mindmap`, `/attack`, `/certificates`, daily bar on Dashboard


## [Nieznana wersja] — przed 2026-03-28

### Zaimplementowane (odtworzone ze struktury kodu)
- Placement test poziomujący
- Baza tematów z prerekvizytami i poziomami (Fundamentals → OWASP Top 10 → Advanced)
- Integracja z DVWA (10 typów labów)
- System fiszek
- AI Mentor (Gemini)
- Error tracking
- Statystyki
- Brain (adaptacyjny silnik nauki)
- Vocabulary (słownik terminów)
- Downloads (eksport notatek)
- Achievements
- TTS audio service
- Anki service
