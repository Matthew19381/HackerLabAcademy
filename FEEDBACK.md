# HackerLabAcademy — Feedback

---

## 2026-04-06 — Docker Production Deployment Completed

**Status:** Infrastructure milestone achieved ✅

### Changes Applied
- Multi-stage Docker build (Node → nginx) for frontend
- Nginx reverse proxy with SPA fallback and API proxy
- Backend refactoring: relative imports, path constants, reserved name fixes
- SQLAlchemy `metadata` conflict resolved (`turn_metadata`)
- All features verified working in Docker compose

### Impact
- Production-ready deployment
- CORS eliminated (same-origin via nginx proxy)
- Static asset caching (1 year)
- Smaller image sizes (nginx-alpine ~20MB)
- Build time: ~2-3 minutes

### Next Steps (User Action)
1. Manual testing at http://localhost
2. Verify all features: topics, quizzes, flashcards, CTF, Defense, Mindmap, Certificates
3. Check logs: `docker-compose logs -f backend`

---

## 2026-03-28 — Ogólna ocena

**Ocena:** Zbyt mało praktyki. Brak zróżnicowanych ćwiczeń poza DVWA.

### Potrzeby użytkownika
- Mnóstwo praktyki: różne typy ćwiczeń per temat
- Więcej interaktywności — AI do rozmowy, nie tylko odpowiadania
- Wzbogacenie o rozwiązania z Language Tutor (newsy, filmy, timer, fiszki → Anki)

### Szczegółowa lista → patrz CHANGES_PROPOSED.md
