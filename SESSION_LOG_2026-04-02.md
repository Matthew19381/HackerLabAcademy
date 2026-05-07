# CHANGELOG — HackerLabAcademy

**Data:** 2026-04-02  
**Operator:** Claude Code (autonomiczny)  
**Tryb:** TRAINING出炉

---

## ✅ EXECUTED TASKS (this session)

### Bug fix (P0)
- Fixed `quiz_mc` answer matching: now accepts both letters (A-D) and indices (0-3)

### Feature: P1-3 Anki export UI
- Added "Anki" export button to Flashcards page
- Backend endpoint already existed (`/api/download/flashcards/{user_id}/anki`)
- Button status: downloading state

### Feature: P3-5 Polish achievements
- Translated all achievement titles & descriptions to Polish in `achievement_service.py`
- Translated level names (`_get_level_name`) to Polish
- Applied at runtime in Stats page and achievements list

### Feature: P3-3 TTS for flashcards
- Backend: New endpoint `/api/download/flashcard/{card_id}/audio` uses `generate_flashcard_audio()`
- Frontend: Volume2 button on each flashcard in Flashcards page to play term audio (Polish TTS)
- Uses `edge-tts` (pl-PL-ZofiaNeural)

### Feature: P3-2 Daily security tips
- Created `frontend/src/data/security_tips.js` with 30 Polish security tips
- Dashboard: shows "Wskazówka bezpieczeństwa dnia" card
- Tip changes daily based on date hash

### Feature: P1-5 Quick flashcard add
- Backend: `POST /api/flashcards/quick-create` accepts `user_id` + `term`
  - Calls Gemini to generate `back` (definition) and `example`
  - Creates Flashcard with SM-2 defaults
- Frontend: quick-add form at top of Flashcards page
  - Input + "Dodaj fiszkę" button
  - AI auto-fills definition/example
- Note: currently only on Flashcards page (global button TBD)

---

## 📝 UPDATED FILES

### Backend
- `backend/services/achievement_service.py` (Polish strings)
- `backend/routers/downloads.py` (flashcard audio endpoint)
- `backend/routers/flashcards.py` (quick-create endpoint + gemini import)
- `backend/services/exercise_service.py` (bug fix: letter→index conversion)

### Frontend
- `frontend/src/pages/Flashcards.jsx` (Anki button, Volume2 audio, quick-add form)
- `frontend/src/pages/Dashboard.jsx` (daily tip card + Lightbulb icon import)
- `frontend/src/api/client.js` (quickCreateFlashcard function)
- `frontend/src/data/security_tips.js` (new: list + getTipOfTheDay)

### Project
- `03_Projects/HackerLabAcademy/TASKS.md` (status updates)
- `03_Projects/HackerLabAcademy/CODE_MAP.md` (new: architecture doc)

---

## 🎯 REMAINING TASKS (from TASKS.md)

**P1:** CVE Explorer, YouTube videos, Timer sesji  
**P2:** CTF Challenge, Terminal Sim, Defense Mode, Attack Scenario, Mindmap/Graph  
**P3:** Dzienny wskaźnik ukończenia, Certyfikaty PDF  

All P0 and many P1/P3 features are now complete.

---

## 💾 DEPLOYMENT NOTES

- No database migrations required
- New endpoints: `/api/download/flashcard/{card_id}/audio`, `/api/flashcards/quick-create`
- Ensure `genanki` installed for Anki export (already present)
- `edge-tts` required for TTS (already in imports)
- Frontend Vite dev server: restart to pick up changes

---

**Koniec sesji pracy autonomicznej.**
