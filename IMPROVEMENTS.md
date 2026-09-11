# HackerLabAcademy — Usprawnienia

> Ostatnia aktualizacja: 2026-06-07

## ✅ Zrobione

- [x] **CLAUDE.md** — dokumentacja projektu istnieje
- [x] **.gitignore** — reguły VCS istnieją
- [x] **Testy** — 25 plików testowych w `backend/tests/`, dobre pokrycie modułów
- [x] **Type hints** — dobre pokrycie w serwisach i routerach

## 📋 Do zrobienia

### Wysoki priorytet
- [ ] **Dodaj pyproject.toml** — brak metadanych pakietu
- [ ] **Dodaj .pre-commit-config.yaml** — ruff lint+format, trailing whitespace

### Średni priorytet
- [ ] **Rozważ refaktoryzację dużych plików**:
  - `achievement_service.py` (331 LOC)
  - `cve_service.py` (308 LOC)
  - `attack.py` (291 LOC)
  - `cves.py` (288 LOC)
- [ ] **Sprawdź .gitignore** — czy `__pycache__` jest ignorowane? (znaleziono 5 katalogów)

### Niski priorytet
- [ ] **Dodaj README.md** — opis projektu, stack, quick start

---

## 📁 Struktura

```
HackerLabAcademy/
├── backend/
│   ├── routers/       # API endpoints (CTF, attacks, defense, labs, etc.)
│   ├── services/      # Logika biznesowa (achievement, cve, lesson, etc.)
│   ├── models/        # SQLAlchemy models
│   ├── tests/         # 25 plików testowych ✅
│   └── main.py        # FastAPI app (211 LOC)
├── audio/             # Pliki audio
├── decisions/         # ADR docs
└── CLAUDE.md          # ✅ Dokumentacja
```

## 🔗 Linki

- [CLAUDE.md](CLAUDE.md)
- [CHANGELOG](CHANGELOG.md)
- [CHANGES_PROPOSED](CHANGES_PROPOSED.md)
