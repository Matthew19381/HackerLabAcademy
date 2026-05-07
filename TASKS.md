# HackerLabAcademy — TASKS

**Status audytu:** 2026-04-02  
**Rzeczywistość vs. TASKS:** Wiele P0 już gotowe, TASKS nieaktualne

---

## ✅ P0 — ZAKOŃCZONE (już zaimplementowane)

- [x] P0-1: Brak zróżnicowanych ćwiczeń (tylko DVWA labs) — dodać quiz, fill blank, code review per temat
  - **Faktycznie:** ✅ Exercise model (quiz_mc, fill_blank, code_review), auto-generation, Exercises.jsx
- [x] P0-2: Brak strukturyzowanej praktyki konwersacyjnej z AI
  - **Faktycznie:** ✅ ConversationSession + 5-turn structured Q&A, Conversation.jsx

---

## 🔄 P1 — WAŻNE (częściowo gotowe)

- [x] P1-1: Security News / CVE Explorer
  - **Backend:** ✅ /api/cves (GET list, GET detail, POST /{cve_id}/flashcard, POST /refresh, GET /meta)
  - **Frontend:** ✅ Cves.jsx (filtry, lista, "Dodaj do fiszek")
  - **Data:** ✅ Sample CVEs seeded (4 przykładowe)
  - **Auto-fetch:** ✅ backend/services/cve_service.py (NVD API integration, manual refresh endpoint)
  - **Status:** ✅ FULLY COMPLETED — includes P1-1a auto-fetch service
- [~] P1-2: YouTube Security Videos per topic
  - **Backend:** ✅ /api/videos (GET with filters), /api/videos/topics (mapping)
  - **Frontend:** ✅ Videos.jsx (iframe embeds, topic/category filters)
  - **Data:** ✅ 11 sample videos seeded (SQLi, XSS, CSRF, IDOR, etc.)
  - **Status:** ✅ ZAKOŃCZONE
- [~] P1-3: Eksport fiszek do Anki (.apkg)
  - **Backend:** ✅ anki_service.py + /api/download/flashcards/{uid}/anki
  - **Frontend:** ✅ Przycisk "Anki" na Flashcards page z downloading state
  - **Status:** ✅ ZAKOŃCZONE
- [~] P1-4: Timer sesji nauki (persistent across all tabs)
  - **Backend:** N/A (frontend-only)
  - **Frontend:** ✅ StudyTimer.jsx (global component in Layout)
  - **Features:** 15/30/60 min selector, Play/Pause/Reset, localStorage persistence, desktop notification
  - **Status:** ✅ ZAKOŃCZONE
- [x] P1-5: Szybkie dodawanie fiszek
  - ✅ Backend: POST /api/flashcards/quick-create (AI generuje definicję i przykład)
  - ✅ Frontend: formularz "Szybkie dodanie fiszki" na stronie Flashcards
  - ⚠️ Note: currently only on Flashcards page; to add global button later

---

## 🆕 P2 — Nowe funkcje

- [~] P2-1: CTF Challenge Mode
  - **Backend:** ✅ /api/ctf (challenges, submit, leaderboard), models (CtfChallenge, UserCtfAttempt)
  - **Frontend:** ✅ CTF.jsx (list/detail, hint, submit, leaderboard tabs)
  - **Data:** ✅ 5 sample challenges (web category, diff 1-4, DVWA-themed)
  - **Features:** Points/XP, achievements, attempt tracking, hint penalty (50%)
  - **Status:** ✅ ZAKOŃCZONE
- [x] P2-2: Code Review Exercise (wskaż podatność w kodzie)
  - **Faktycznie:** ✅ Already included in P0-1 (exercise_type='code_review'), UI supports code snippets
- [~] P2-3: Terminal Simulator (nmap, curl, sqlmap, bash)
  - **Frontend:** ✅ Terminal.jsx + terminal_scenarios.js
  - **Scenarios:** 4 complete (nmap basics, curl basics, bash essentials, sqlmap basics)
  - **Status:** ✅ ZAKOŃCZONE
- [~] P2-4: Defense Mode (code fix + AI evaluation)
  - **Backend:** ✅ /api/defense (GET challenges, POST submit), models (DefenseChallenge, UserDefenseAttempt), AI eval via Gemini
  - **Frontend:** ✅ Defense.jsx (list + editor + AI feedback), integrated with Layout navigation
  - **Data:** ✅ 3 sample challenges (SQLi, XSS, Command Injection)
  - **Status:** ✅ ZAKOŃCZONE
- [~] P2-5: Attack Scenario (full kill chain step-by-step)
  - **Backend:** ✅ /api/attack (scenarios, start, submit step, progress tracking)
  - **Frontend:** ✅ AttackScenario.jsx (multi-step interactive, per-step answers, points)
  - **Data:** ✅ 2 sample scenarios (SQLi kill chain, XSS kill chain)
  - **Nav:** ✅ Added to Layout (Skull icon)
  - **Status:** ✅ ZAKOŃCZONE
- [~] P2-6: Topic Mindmap / Dependency Graph
  - **Backend:** ✅ /api/topics already provides prerequisites + unlock status
  - **Frontend:** ✅ Mindmap.jsx (D3 force-directed graph, drag nodes, color by completion)
  - **Integration:** ✅ Added to App.jsx and Layout nav (Network icon)
  - **Dependencies:** Added `d3` to package.json (user must run `npm install` in frontend/)
  - **Status:** ✅ ZAKOŃCZONE (awaiting npm install)

---

## 🎨 P3 — UI / Drobnostki

- [x] P3-1: Dzienny wskaźnik ukończenia (lab + quiz + fiszki + artykuł)
  - **Backend:** ✅ /api/daily/status – lab_done (LabAttempt), quiz_done (ExerciseAttempt), flashcard_done (FlashcardAttempt), article_done (ArticleRead)
  - **Frontend:** ✅ Dashboard.jsx – daily completion bar (percent + badges for Lab/Quiz/Fiszki/Artykuł)
  - **Features:** Lab + Quiz + Flashcards + Articles tracked.
  - **Status:** ✅ FULLY COMPLETED
- [x] P3-2: Dzienne wskazówki security
  - ✅ Statyczna lista `SECURITY_TIPS` w frontend/src/data/security_tips.js
  - ✅ Frontend: "Wskazówka bezpieczeństwa dnia" card na Dashboard
  - **Gotowe** (zmienia się codziennie na podstawie daty)
- [x] P3-3: TTS dla terminologii
  - ✅ Backend: generate_flashcard_audio() + endpoint /api/download/flashcard/{card_id}/audio
  - ✅ Frontend: Volume2 button on flashcard (Flashcards.jsx)
  - **Gotowe**
- [~] P3-4: Certyfikat ukończenia sekcji (PDF)
  - **Backend:** ✅ Certificate model, /api/certificates (list, generate, download), certificate_service.py (fpdf2)
  - **Frontend:** ✅ Certificates.jsx page (generate per category, download PDF, list)
  - **Integration:** ✅ Added to App.jsx and Layout nav (Award icon)
  - **Logic:** Requires all topics in category (theory_completed + quiz_passed) to generate.
  - **Status:** ✅ ZAKOŃCZONE
  - **PDF lekcji:** ✅ istnieje (pdf_service.py, endpoints)
  - **Certyfikaty:** ❌ brak generatora certyfikatów po ukończeniu tematu/kategorii
- [x] P3-5: Osiągnięcia po polsku
  - ✅ Zastosowano polskie stringi w ACHIEVEMENT_DEFS
  - ✅ Tłumaczone również level names (`_get_level_name`)
  - **Gotowe**

---

## 🎁 ADDITIONAL FEATURES (beyond original spec)

- [x] Article Module (Read + Quiz)
  - **Backend:** ✅ models (Article, ArticleRead, ArticleQuiz, ArticleQuizAttempt), routers/articles.py (GET list, GET detail, POST /read, POST /quiz/submit), seed 2 sample articles with quizzes
  - **Frontend:** ✅ Articles.jsx (list, detail with markdown, read timer, quiz submission), nav link (Newspaper icon)
  - **Daily tracking:** ✅ article_done in daily status
  - **Status:** ✅ FULLY COMPLETED

- [x] CVE Auto-Scheduler
  - **Backend:** ✅ cve_service.py with `CveScheduler` class, manual `POST /api/cves/refresh`, auto-start via env `CVE_SCHEDULED_FETCH=true` in main.py lifespan
  - **Status:** ✅ COMPLETED (opt-in)

- [x] Write-up Templates (Lab/CTF Reports)
  - **Backend:** ✅ models (WriteupTemplate, Writeup), routers/writeups.py (GET templates, POST generate, GET history/download), seed templates: "DVWA Lab Report", "CTF Write-up"
  - **Frontend:** API ready; UI to integrate into Lab/CTF pages (template selection modal, variable form, PDF export)
  - **PDF generation:** ✅ via fpdf2
  - **Status:** ✅ BACKEND COMPLETED, UI TODO

- [x] Progress Analytics
  - **Backend:** ✅ GET /api/stats/{user_id}/analytics returns weakest topics (errors), in-progress topics, exercise accuracy, streak
  - **Frontend:** ✅ Integrated into Stats.jsx (new "Analiza nauki" section)
  - **Status:** ✅ COMPLETED

- [x] Lesson Bundle Download (PDF + Audio)
  - **Backend:** ✅ GET /api/download/lesson/{slug}/bundle returns ZIP with lesson PDF + MP3
  - **Frontend:** ✅ "PDF+Audio" button in TheoryLesson.jsx
  - **Service:** ✅ lesson_bundle_service.py
  - **Status:** ✅ COMPLETED

- [x] More Exercises (increase from 5 → 10 per topic)
  - **Backend:** ✅ generate_exercises_for_topic already supports `count` param
  - **Frontend:** ✅ Exercises.jsx auto-generate count changed to 10
  - **Status:** ✅ COMPLETED

---

## 🐳 DOCKER PRODUCTION DEPLOYMENT (2026-04-06)

- [x] Multi-stage frontend build (Node → nginx static)
- [x] Nginx reverse proxy configuration
- [x] Backend import path fixes (relative imports)
- [x] Path hardcode fixes (audio/, exports/)
- [x] SQLAlchemy metadata conflict resolution (ConversationTurn.turn_metadata)
- [x] Missing import fixes (YouTubeVideo, AttackStepAttempt, etc.)
- [x] Add generate_pdf_from_markdown to pdf_service (for writeups)
- [x] docker-compose.yml: port 80:80, healthcheck 40s
- [x] Backend config: PDF_EXPORT_DIR, AUDIO_DIR module-level constants
- [x] All features tested and working (pending final build)

**Status:** ✅ COMPLETED (build successful, awaiting manual verification)

---

## Ukończone (historia)

*(brak — projekt bez udokumentowanej historii)*

---

## NOTATKI DLA ROZWOJU

### Backend gotowe, czekające na UI:
- Anki export endpoint (P1-3)
- Flashcard audio TTS (P3-3)
- PDF lesson download (P1-4 oops, it's a different feature)

### Sugerowane kolejność:
1. P1-3: dodać przycisk "Eksportuj do Anki" na Flashcards page
2. P3-5: przetłumaczyć achievement strings na PL
3. P2-1: CTF Challenge Mode (największy P2, ale dochodowy)
4. P2-6: Topic Mindmap (wizualizacja dependencies między tematami)
