# HackerLabAcademy

Nauka cyberbezpieczeństwa: teoria, laby Docker, CTF, CVE, fiszki. Moduł ekosystemu System-Główny.

## Najpierw mapa, nie dokumenty
- Porty, uruchamianie, API, zależności: `C:\Projects\KB\mapa\INDEX.md` (w chmurze: repo `Matthew19381/KB`, katalog `mapa/`);
  ten moduł: `mapa/moduly/HackerLabAcademy.md`. Czytaj tylko potrzebną sekcję.
- Mapa kodu: `CODE_MAP.md`; plan: `ACTION_PLAN.md` (71 KB, czytaj fragmentami).
- Pełna dawna wersja tego pliku (tabela 22 routerów, liczby XP, Docker): `docs/archiwum/CLAUDE-do-2026-11-06.md`.

## Zasady (Mateusz)
- Moduł nie jest dziś uruchamiany przez starter i jest wyłączony w hubie (`MODULE_DISABLED`). Usługi ekosystemu uruchamiaj tylko przez
  `Start-ScheduledTask -TaskName Ekosystem-Start`.
- Push i scalanie tylko po zgodzie Mateusza (dawna reguła „push po każdej zmianie” nie obowiązuje).
- Repo jest **publiczne**: przed push skan sekretów. Nie zmieniaj plików `.env`.

## Pułapki
- Backend z korzenia repo (`backend.main:app`), frontend z `frontend/` (proxy `/api` na backend).
- Baza `HackerLabAcademy.db` w korzeniu repo (`backend/database.py`), schemat przez `Base.metadata.create_all()` w lifespan
  (bez Alembica): nowy model importuj w bloku lifespan w `main.py`.
- AI tylko przez `backend/services/gemini_service.py` (`generate_json`, `generate_text`); każde wywołanie ma fallback. Prompty w `services/lesson_generator.py`.
- Frontend: wywołania w `frontend/src/api/client.js` (interceptor zwraca `response.data`); `userId` w `localStorage`.
- Fiszki: FSRS przez `backend/services/fsrs_service.py` (biblioteka `fsrs`); dawne pola SM-2 w modelu zostały dla zgodności.

## Konwencje
Commity `<typ>: co i dlaczego` z listą plików (feat, fix, refactor, style, docs, chore).
