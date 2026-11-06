# CLAUDE.md

This file provides guidance to Claude Code when working with the HackerLabAcademy repository.

## Starting the App

Run from the **project root** (`HackerLabAcademy/`):

```bash
# Windows CMD
start.bat

# PowerShell
.\start.ps1

# Manual — backend (from HackerLabAcademy/)
uvicorn backend.main:app --reload --port 8003

# Manual — frontend (from HackerLabAcademy/frontend/)
npm run dev
```

Frontend dev server runs on `:5174` and proxies `/api` to `http://localhost:8003` (configured in `frontend/vite.config.js`).

## Environment

Copy `backend/.env.example` → `backend/.env` and set `GEMINI_API_KEY` (or `OPENROUTER_API_KEY` + `AI_PROVIDER=openrouter`).
The SQLite database is `HackerLabAcademy.db` in the **project root** (`backend/database.py`, independent of CWD;
override with `DATABASE_URL`).

**Schema = Alembic** (since 2026-11-03). The lifespan calls `backend/migrations_runner.upgrade_database()`
(`alembic upgrade head`). Revision `0001` is an idempotent baseline: it creates missing tables and adds missing
columns to databases created by the old `create_all`, keeping data. New model → import it in
`backend/models/__init__.py`, then from the project root:
`alembic -c backend/alembic.ini revision --autogenerate -m "opis"` and make the migration idempotent
(check `sa.inspect(op.get_bind())` before creating). Never `create_all` in app code.

## Architecture

### Backend

**Stack**: FastAPI · SQLAlchemy 2 + Alembic (SQLite) · Gemini 2.5 Flash / OpenRouter / Ollama · FSRS · edge-tts · fpdf · httpx (NVD API) · genanki

**Request flow**:
```
Router → Service → SQLAlchemy Session (get_db dependency)
```

**`backend/services/ai_service.py`** routes AI calls by `AI_PROVIDER` (Gemini, OpenRouter, Ollama) with fallbacks;
`gemini_service.py` is the Gemini client. Two functions:
- `generate_json(prompt)` — appends "Respond ONLY with valid JSON" and strips markdown fences
- `generate_text(prompt)` — raw string response

Every function calling Gemini has a hardcoded fallback dict/string for graceful degradation when the API fails.

**`backend/services/lesson_service.py`** — all AI prompt logic: theory lessons, quizzes, exercises, flashcards, CVE explanations, conversation questions.

### Key Routers (`backend/routers/`, all under `/api/v1`)

| File | Prefix | Responsibility |
|------|--------|-----------------|
| `thm.py` | `/thm` | TryHackMe tracker: rooms/paths, done, notes (no XP); `thm_*_completed` events |
| `topics.py` | `/topics` | Topics, theory generation, quiz submit, practice step (`/{slug}/lab/complete`, `practice_hint`) |
| `flashcards.py` | `/flashcards` | FSRS only, interleaved due queue, quick-create, `/from-notes`, `/decks/tools`, Anki export |
| `ctf.py` | `/ctf` | CTF puzzles solvable from their text, hint = half points (`hint_used`), **no leaderboard** |
| `mentor.py` | `/mentor` | AI mentor; conversation in DB (`mentor_messages`), modes guide/hint/answer, daily usage notice |
| `exercises.py` | `/exercises` | Exercises CRUD, AI generation, submit |
| `conversation.py` | `/conversation` | Structured AI Q&A sessions |
| `defense.py` | `/defense` | Defense challenges, code fix, AI evaluation |
| `cves.py` | `/cves` | CVE Explorer, NVD API |
| `videos.py` | `/videos` | YouTube videos per topic |
| `writeups.py` | `/writeups` | Write-up templates, PDF |
| `certificates.py` | `/certificates` | PDF certificates per category |
| `stats.py` | `/stats` | XP/level, achievements (informational, no ranking) |
| `daily.py`, `brain.py` | `/daily`, `/brain` | Daily status, adaptive agenda |
| `articles.py`, `errors.py`, `vocabulary.py` | … | Articles + quizzes, error tracking, terminology |
| `downloads.py` | `/download` | PDF, audio, Anki, bundle exports |
| `placement.py`, `ai_config.py` | … | User creation / level test, AI provider config |
| `integration.py` | — | Hub contract: `GET /summary`, `POST /integrations/flush` |
| `directives.py` | `/directives` | Hub directives (survival_mode, priority, quiet_hours) |

Removed in the THM pivot (2026-11-03): `labs.py` (DVWA containers), `attack.py` (kill chain), the CTF leaderboard.
CTF itself was restored 2026-11-03 (removed by mistake in `1b1f2ff`); the 5 old DVWA challenges are deactivated.

### Frontend

**Stack**: React 19 · React Router 7 · Axios · Tailwind CSS · Vite 8 · Vitest · lucide-react · D3.js

**`frontend/src/api/client.js`** — all API calls. The `api` Axios instance has a response interceptor that unwraps `response.data`.

**State**: no global state manager. Each page fetches its own data on mount. `userId` is stored in `localStorage` and read via `getUserId()` from `client.js`.

**`frontend/src/components/Layout.jsx`** — sidebar nav, study timer, achievement toasts.

### Docker Deployment

```bash
cd HackerLabAcademy
docker-compose up --build
```

- Build context of the backend is the project root (`backend/Dockerfile`, `CMD uvicorn backend.main:app`)
- Frontend: http://localhost (nginx, multi-stage build)
- Backend API docs: http://localhost:8003/docs
- API proxy: nginx proxies `/api` → `http://backend:8003`

## Key Numbers

| Constant | Value | Location |
|----------|-------|----------|
| Practice step XP | +50 | `routers/topics.py` (`XP_LAB`) |
| Exercise submission XP | `score × 0.5` (max 50) | `services/exercise_service.py` |
| Defense completion XP | +25 | `services/defense_service.py` |
| Level curve | `(n-1)² × 20` XP, 50 levels | `services/achievement_service.py` |
| CTF solve | challenge points (50–100), half after a hint | `routers/ctf.py` |
| TryHackMe tracker XP | **none** (decision 2026-08-09) | `routers/thm.py` |
| Mentor daily notice threshold | 100 calls (`MENTOR_DAILY_WARN`) | `config.py` |
| Cards from notes | max 5 | `routers/flashcards.py` |
| API timeout (frontend) | 120 s | `api/client.js` |

## Quality

- Tests: `python -m pytest backend/tests -q` (from the project root); frontend `cd frontend && npx vitest run`.
- Lint: `ruff check .` (config in `pyproject.toml`), `cd frontend && npx eslint . --max-warnings 0`.
- CI: `.github/workflows/ci.yml` (ruff, pytest, ESLint, vitest, build). Pre-commit: `.pre-commit-config.yaml`.
- Tests never reach paid AI or the real hub (keys blanked in `backend/tests/conftest.py`).
- Plan: `decisions/ACTION_PLAN_2026-11-03.md`.

## Git — Mandatory Push Policy

**Push to GitHub after every meaningful change.**

### When to commit and push
- Any new file created (router, service, component, page)
- Any bug fixed
- Any feature completed or partially completed
- Any refactor, even small
- Any CLAUDE.md update
- Before ending a work session

### Commit message format
```
<type>: <what changed and why>

- Detail 1 (which file, what exactly)
- Detail 2
```

**Types**: `feat`, `fix`, `refactor`, `style`, `docs`, `chore`

### Commands
All git commands run from `HackerLabAcademy/` (the repo root):
```bash
git add -A
git commit -m "feat: description

- file.py: what changed"
git push
```
