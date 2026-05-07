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
uvicorn backend.main:app --reload --port 8001

# Manual — frontend (from HackerLabAcademy/frontend/)
npm run dev
```

Frontend dev server runs on `:5174` and proxies `/api` to `http://localhost:8001` (configured in `frontend/vite.config.js`).

## Environment

Copy `backend/.env.example` → `backend/.env` and set `GEMINI_API_KEY`. The SQLite database (`HackerLabAcademy.db`) is created automatically in `backend/data/` on first startup via `Base.metadata.create_all()` in `main.py`'s lifespan handler.

**When adding a new SQLAlchemy model**: import it inside the lifespan block in `main.py` so it registers with `Base` before `create_all` runs.

## Architecture

### Backend

**Stack**: FastAPI · SQLAlchemy (SQLite) · Google Gemini 2.0 Flash · edge-tts · fpdf2 · httpx (NVD API) · genanki

**Request flow**:
```
Router → Service → SQLAlchemy Session (get_db dependency)
```

**`backend/services/gemini_service.py`** is the single point of contact with Gemini. Two functions:
- `generate_json(prompt)` — appends "Respond ONLY with valid JSON" and strips markdown fences
- `generate_text(prompt)` — raw string response

Every function calling Gemini has a hardcoded fallback dict/string for graceful degradation when the API fails.

**`backend/services/lesson_generator.py`** — all AI prompt logic: theory lessons, quizzes, exercises, flashcards, CVE explanations, conversation questions.

### Key Routers (`backend/routers/`)

| File | API prefix | Responsibility |
|------|------------|-----------------|
| `topics.py` | `/api/topics/` | Topics list, theory generation, quiz submit, prerequisites |
| `labs.py` | `/api/labs/` | Docker lab control (start/stop/reset), DVWA integration |
| `exercises.py` | `/api/exercises/` | Exercises CRUD, AI generation, submit answers |
| `flashcards.py` | `/api/flashcards/` | SM-2 spaced repetition, quick-create, Anki export |
| `conversation.py` | `/api/conversation/` | Structured AI Q&A sessions (5 turns) |
| `mentor.py` | `/api/mentor/` | Free-form AI mentor chat |
| `ctf.py` | `/api/ctf/` | CTF challenges, flag submission, leaderboard |
| `defense.py` | `/api/defense/` | Defense challenges, code fix, AI evaluation |
| `attack.py` | `/api/attack/` | Multi-step attack scenarios (kill chain) |
| `cves.py` | `/api/cves/` | CVE Explorer, NVD API integration, refresh |
| `videos.py` | `/api/videos/` | YouTube security videos per topic |
| `writeups.py` | `/api/writeups/` | Write-up templates, PDF generation |
| `certificates.py` | `/api/certificates/` | PDF certificates per category |
| `stats.py` | `/api/stats/` | XP/level, achievements, analytics |
| `daily.py` | `/api/daily/` | Daily completion status |
| `articles.py` | `/api/articles/` | Security articles + quizzes |
| `errors.py` | `/api/errors/` | Error tracking from quiz mistakes |
| `brain.py` | `/api/brain/` | Adaptive learning agenda |
| `downloads.py` | `/api/download/` | PDF, audio, Anki, bundle exports |
| `vocabulary.py` | `/api/vocabulary/` | Topic terminology |
| `terminal.py` | `/api/terminal/` | Terminal simulator scenarios |
| `placement.py` | `/api/placement/` | User creation, level test |

### Frontend

**Stack**: React 18 · React Router v6 · Axios · Tailwind CSS · Vite · lucide-react · D3.js

**`frontend/src/api/client.js`** — all API calls. The `api` Axios instance has a response interceptor that unwraps `response.data`.

**State**: no global state manager. Each page fetches its own data on mount. `userId` is stored in `localStorage` and read via `getUserId()` from `client.js`.

**`frontend/src/components/Layout.jsx`** — sidebar nav, study timer, achievement toasts.

### Docker Deployment

```bash
cd HackerLabAcademy
docker-compose up --build
```

- Frontend: http://localhost (nginx, multi-stage build)
- Backend API docs: http://localhost:8001/docs
- API proxy: nginx proxies `/api` → `http://backend:8001`

## Key Numbers

| Constant | Value | Location |
|----------|-------|----------|
| Lab completion XP | +30 | `routers/labs.py` |
| Exercise submission XP | `score × 0.5` (max 50) | `services/exercise_service.py` |
| CTF flag XP | points (10-50) | `routers/ctf.py` |
| Defense completion XP | +25 | `services/defense_service.py` |
| Level curve | `(n-1)² × 20` XP, 50 levels | `services/achievement_service.py` |
| Gemini model | `gemini-2.0-flash` | `services/gemini_service.py` |
| API timeout (frontend) | 120 s | `api/client.js` |

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
