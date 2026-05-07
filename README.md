# HackerLabAcademy

Platforma treningowa do nauki cybersecurity (Web Security) z AI (Google Gemini).

## Funkcje

- **Teoria**: 9 tematów (Fundamentals → OWASP Top 10 → Advanced) z lekcjami generowanymi przez AI
- **Labs**: Praktyka na DVWA (Damn Vulnerable Web Application) w Dockerze
- **Ćwiczenia**: Quiz MC, Fill-in-the-blank, Code Review — 10 per temat
- **CTF Challenge Mode**: Zadania z flagami, punktacją i rankingiem
- **Defense Mode**: Napraw podatny kod, oceń AI
- **Attack Scenarios**: Wielokrokowe symulacje ataków (kill chain)
- **Terminal Simulator**: nmap, curl, sqlmap, bash — 4 scenariusze
- **CVE Explorer**: Newsy bezpieczeństwa (NVD API), dodawanie do fiszek
- **YouTube Videos**: Filmy edukacyjne per temat
- **AI Mentor**: Rozmowy Q&A, wolne czaty
- **Fiszki**: SM-2 spaced repetition + TTS (edge-tts) + eksport do Anki
- **Write-up Templates**: Raporty z labów i CTFów (PDF)
- **Mindmap**: Wizualizacja grafu zależności między tematami (D3.js)
- **Certyfikaty**: PDF po ukończeniu kategorii
- **Statystyki**: XP, poziomy (50), osiągnięcia (35), analytics

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
# Backend API: http://localhost:8001/docs
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
