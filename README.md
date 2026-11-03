# HackerLabAcademy

Narzędzie do utrwalania wiedzy z cybersecurity zdobywanej na **TryHackMe** (pivot z 2026-08-09,
dokończony 2026-11-03): aplikacja nie hostuje już własnych podatnych maszyn — praktyka odbywa się na THM,
a tutaj notujesz, powtarzasz i sprawdzasz, co pamiętasz. Moduł ekosystemu System-Główny (port `:8003`).

## Funkcje

- **TryHackMe**: ręczny tracker pokoi i ścieżek (zrobione / do zrobienia, notatki, link — bez punktów),
  z notatek AI robi 3–5 pytań do powtórek
- **Teoria**: tematy (Fundamentals → OWASP Top 10 → Advanced) z lekcjami generowanymi przez AI
- **Praktyka**: krok tematu po teorii — link do pokoi THM, writeup własnymi słowami (PDF)
- **Ćwiczenia**: quiz MC, uzupełnianie luk, code review
- **Defense Mode**: napraw podatny kod, ocena AI
- **Terminal Simulator**: nmap, curl, sqlmap, bash
- **CVE Explorer**: bieżące podatności (NVD API), dodawanie do fiszek
- **Filmy**: YouTube per temat
- **AI Mentor**: rozmowa zapisywana w bazie; tryby pomocy „Naprowadź / Podpowiedź / Wyjaśnij”;
  informacja po przekroczeniu dziennego progu wywołań (bez blokady)
- **Fiszki**: FSRS, przeplatanie kategorii w kolejce, talia składni narzędzi (nmap, gobuster, hydra,
  msfconsole, Burp, netcat), TTS (edge-tts), eksport do Anki
- **Mindmap**: graf zależności między tematami (D3.js)
- **Certyfikaty**: PDF po ukończeniu kategorii
- **Statystyki**: XP, poziomy, osiągnięcia (informacyjnie, bez rankingu)

## Szybki start

```bash
# 1. Skopiuj konfigurację
cp backend/.env.example backend/.env
# Edytuj backend/.env i ustaw GEMINI_API_KEY

# 2. Uruchom (Windows)
start.bat        # CMD
.\start.ps1      # PowerShell

# 3. Otwórz przeglądarkę
# Frontend: http://localhost:5174
# Backend API: http://localhost:8003/docs
```

## Docker (produkcja)

```bash
docker-compose up --build
# Frontend: http://localhost (nginx)
# Backend API: http://localhost:8001/docs
```

## Stack technologiczny

**Backend**: FastAPI · SQLAlchemy · SQLite · Google Gemini 2.0 Flash · edge-tts · fpdf2 · httpx · genanki  
**Frontend**: React 18 · React Router v6 · Axios · Tailwind CSS · Vite · D3.js · lucide-react

## Struktura

```
HackerLabAcademy/
├── backend/
│   ├── main.py          # FastAPI app
│   ├── models/          # SQLAlchemy (12 modeli)
│   ├── routers/         # 15 routerów (API endpoints)
│   ├── services/        # Logika biznesowa + AI
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/      # 20 stron (React)
│   │   ├── components/  # Layout, StudyTimer
│   │   └── api/        # client.js (Axios)
│   └── package.json
├── docker-compose.yml
├── start.bat / start.ps1
└── README.md
```

## Repozytorium

https://github.com/Matthew19381/HackerLabAcademy
