# HackerLabAcademy — Mapa Kodu i Architektura

## 🐳 Docker Architecture (2026-04-06)

### Overview
Production-ready deployment using **multi-stage builds** and **nginx reverse proxy**.

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Host (Windows)                    │
│  Port 80  →  Frontend (nginx)                              │
│  Port 8001 → Backend (FastAPI)                             │
└─────────────────────────────────────────────────────────────┘
                         │
                    Docker Network (hackerlabacademy_default)
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
  ┌─────────┐                     ┌─────────┐
  │ frontend│  /api → proxy       │ backend │
  │  nginx  │ ──────────────────→ │ FastAPI │
  │  port 80│                     │ port8001│
  └─────────┘                     └─────────┘
```

### Components

**Frontend (nginx + static build)**
- **Stage 1 (builder):** Node 20-alpine → `npm ci` + `npm run build` → `/app/dist`
- **Stage 2 (runtime):** nginx:alpine → copies `/app/dist` → `/usr/share/nginx/html`
- **Nginx config:**
  - SPA fallback: `try_files $uri $uri/ /index.html`
  - API proxy: `/api` → `http://backend:8001`
  - Static caching: `expires 1y` for assets
- **Port mapping:** `80:80` (host:container)
- **No environment variables** (proxy handles API routing)

**Backend (FastAPI)**
- **Base image:** Python 3.11-slim
- **Dependencies:** `requirements.txt` (fastapi, uvicorn, sqlalchemy, google-genai, httpx, fpdf, edge-tts, genanki)
- **Working directory:** `/app`
- **Code structure:** Relative imports (no `backend.` prefix)
  ```python
  from database import engine, Base, SessionLocal
  from models.user import User
  from routers.topics import router as topics_router
  ```
- **Volumes:**
  - `backend_data` → `/app/data` (SQLite DB: `HackerLabAcademy.db`)
  - `backend_audio` → `/app/audio` (TTS outputs)
  - `backend_exports` → `/app/exports` (PDFs, Anki decks)
- **Healthcheck:** `GET /api/health` every 30s, timeout 40s
- **Port:** `8001:8001`
- **Lifespan:** Auto-creates tables, seeds topics/CVEs/videos/CTF/defense/articles

**Docker Compose**
```yaml
version: '3.8'  # (obsolete but harmless)
services:
  backend:
    build: ./backend
    ports: ["8001:8001"]
    volumes: [backend_data:/app/data, backend_audio:/app/audio, backend_exports:/app/exports]
    environment: [GEMINI_API_KEY, AI_PROVIDER, OLLAMA_*, CVE_SCHEDULED_FETCH]
    healthcheck: {test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/api/health').read()"], timeout: 40s}
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports: ["80:80"]
    depends_on: {backend: {condition: service_healthy}}
    restart: unless-stopped

volumes: [backend_data, backend_audio, backend_exports]
```

### Key Files

| File | Purpose |
|------|---------|
| `frontend/Dockerfile` | Multi-stage (node:20-alpine → nginx:alpine) |
| `frontend/nginx.conf` | SPA fallback + API reverse proxy + caching |
| `backend/Dockerfile` | Python 3.11-slim, pip install, uvicorn |
| `docker-compose.yml` | Orchestration (frontend + backend) |
| `.dockerignore` | Exclude node_modules, __pycache__, .git, etc. |

### Build & Run

```bash
cd 03_Projects/HackerLabAcademy
docker-compose down -v   # optional cleanup
docker-compose up --build
```

**Access:**
- Frontend: http://localhost
- Backend API docs: http://localhost:8001/docs
- Health: http://localhost:8001/api/health

### Post-Deployment Steps

1. **Create user:** Open http://localhost → `/setup` → enter name + user_id
2. **Test topics:** Generate first lesson (AI call, ~5-10 seconds)
3. **Verify features:** Quiz, flashcards, CTF, Defense, Mindmap, Certificates
4. **Check logs:** `docker-compose logs -f backend` for errors

### Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Backend import errors on startup | Old cached image | `docker-compose down -v && docker-compose up --build` |
| 502 Bad Gateway from nginx | Backend not healthy yet | Wait 30s, check `docker-compose logs backend` |
| Gemini AI fails | GEMINI_API_KEY not set | Edit `.env`, restart `docker-compose up --build` |
| Port 80 already in use | IIS/Apache/nginx on host | Change frontend port to `8080:80` in compose, then use http://localhost:8080 |

---

## Struktura projektu

## Kluczowe API Endpoints

| Endpoint | Metoda | Purpose |
|----------|--------|---------|
| `/api/topics/` | GET | List topics with unlock status |
| `/api/topics/{slug}/theory` | GET | (Generate) lesson theory + quiz + flashcards |
| `/api/topics/{slug}/quiz` | POST | Submit quiz, save errors, award XP |
| `/api/topics/{slug}/lab/complete` | POST | Submit lab writeup, mark complete |
| `/api/exercises/topics/{topic_id}` | GET | List exercises for topic |
| `/api/exercises/topics/{topic_id}/generate` | POST | Generate 5 exercises via AI |
| `/api/exercises/submit` | POST | Submit answer, get XP |
| `/api/conversation/sessions/start` | POST | Start structured Q&A session |
| `/api/conversation/sessions/{id}/question` | POST | Get next AI question |
| `/api/conversation/sessions/{id}/answer` | POST | Submit answer, get feedback |
| `/api/conversation/sessions/{id}/end` | POST | End session, finalize XP |
| `/api/conversation/sessions/user/{uid}` | GET | History |
| `/api/mentor/chat` | POST | Free-form AI mentor chat |
| `/api/flashcards/due/{user_id}` | GET | Due cards (SM-2) |
| `/api/flashcards/{card_id}/review` | POST | Submit rating (again/hard/good/easy) |
| `/api/download/lesson/{slug}/pdf` | GET | Download lesson PDF |
| `/api/download/lesson/{slug}/audio` | GET | Download lesson MP3 |
| `/api/download/flashcards/{user_id}/anki` | GET | Export .apkg |
| `/api/stats/{user_id}` | GET | Stats + new achievements |
| `/api/stats/{user_id}/achievements` | GET | All achievements |

## Modele danych

### Topic (tematy)
- Seeded w `main.py` (9 tematów: Fundamentals, OWASP Top 10, Advanced)
- Prerequisites: JSON list of slugs
- theory_content: JSON blob z lekcją
- lab_type: dvwa_* typ

### Exercise (ćwiczenia)
- exercise_type: `quiz_mc`, `fill_blank`, `code_review`
- options: JSON list (dla MC)
- correct_answer: string (indeks dla MC, tekst dla fill, "line:N" dla code_review)
- difficulty 1-5

### ConversationSession/Turn
- 5 turns max per session
- Turn types: multiple_choice, open_ended, scenario
- Metadata przechowuje correct_answer i explanation

### Flashcard (SM-2)
- ease_factor, interval_days, repetitions, next_review_date

### UserTopicProgress
- theory_completed, lab_completed, quiz_score

### Achievement
- achievement_type + notified flag

## Przepływy użytkownika

### 1. Teoria → Quiz → Lab (main flow)
```
Topics page (unlocks based on prerequisites)
  ↓ click topic
TheoryLesson page
  ├─ Teoria (z key concepts, attack/defend, real-world)
  ├─ Quiz (multiple choice, 5+ questions)
  │     ↓ submit → errors saved to ErrorItem, XP if >=70%
  ├─ Ćwiczenia (auto-generated: MC, fill, code review)
  └─ Konwersacja (structured Q&A, 5 turns)
       ↓ complete quiz ≥70% → theory_completed = True
       ↓ complete lab → lab_completed = True (writeup generated)
Lab page (DVWA integration)
```

### 2. Fiszki SM-2
```
Flashcards page
  → getDueFlashcards()
  → review (Again/Hard/Good/Easy)
  → SM-2 update interval
```

### 3. Error Loop
```
Errors page
  → from quiz mistakes (saved automatically)
  → review error, mark as resolved/fixed
  → XP awarded
```

### 4. Stats & Achievements
```
Stats page → get_stats() + get_achievements()
  Level calculation: (n-1)^2 * 20 XP per level (50 levels)
  Achievements: 35 types tracked (theory, labs, errors, streak, XP, OWASP mastery)
```

## Generowanie treści (Gemini)

- `generate_theory_lesson()`: full lesson JSON (sections, quiz, flashcards)
- `generate_lab_instructions()`: DVWA lab step-by-step
- `generate_writeup()`: CTF-style report from student writeup
- `generate_exercises_for_topic()`: 5 exercises (mix types)
- `generate_question()` (conversation_service): AI question based on topic + turn number
- `analyze_quiz_errors()`: classify errors (no_knowledge, misunderstanding, guessing)

## P0/P1 Status (po audycie)

### P0 — BLOCKING ✅ DONE
- P0-1:多样化 exercises (quiz_mc, fill_blank, code_review) ✅
- P0-2: Structured conversation practice ✅

### P1 — IMPORTANT
- P1-1: CVE Explorer ❌
- P1-2: YouTube videos per topic ❌
- P1-3: Anki export ✅ backend, ❌ missing UI button
- P1-4: Learning timer ❌
- P1-5: Quick flashcard add ❌

### P2 — NEW FEATURES
- P2-1: CTF mode ❌
- P2-2: Code review exercise ✅ (already in P0-1)
- P2-3: Terminal simulator ❌
- P2-4: Defense mode ❌
- P2-5: Attack scenario ❌
- P2-6: Topic mindmap/graph ❌

### P3 — UI/POLISH
- P3-1: Daily completion indicator ❌
- P3-2: Daily security tips ❌
- P3-3: TTS for terminology ⚠️ (audio_service exists for flashcards but unused)
- P3-4: PDF certificates ⚠️ (PDF lessons exist, certs missing)
- P3-5: Polish achievements ❌ (all English strings)

## Błędy vs. Language Tutor

Language Tutor ma:
- Newsy (dzienne) → HackerLab: missing
- YouTube videos → HackerLab: missing
- Mów (conversation) → HackerLab: ✅ (conversation_service)
- i+1 reading → HackerLab: N/A
- Fiszki + Anki → HackerLab: ✅ SM-2 + Anki export backend
- Timer 15 min → HackerLab: ❌
- Szybkie fiszki → HackerLab: ❌
- Daily tips → HackerLab: ❌
- Completion indicator → HackerLab: ❌

## Rekomendacje

1. **Zaktualizować TASKS.md** — usunąć P0 (already done), oznaczyć które P1/P2 gotowe
2. **Dodać UI przycisk Anki** w Flashcards page
3. **Przetłumaczyć achievements** na polski (P3-5)
4. **Synchronizować FEEDBACK.md** z nowymi features
5. **Wybrać 1-2 P2 do implementacji** (np. CTF Challenge lub Mindmap)

---

**Wygenerowano:** 2026-04-02  
**Wersja audytu:** 1.0
