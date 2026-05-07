# HackerLabAcademy — Lista Funkcji

HackerLabAcademy to aplikacja do nauki cyberbezpieczeństwa. Prowadzi użytkownika przez tematy od podstaw (HTTP, HTML) przez OWASP Top 10 do zaawansowanych technik, łącząc teorię z praktyką w laboratoriach.

---

## Ścieżka Nauki

### Placement Test
Test poziomujący przy pierwszym uruchomieniu. Określa punkt startowy nauki na podstawie wiedzy użytkownika.

### Topics (Tematy)
Baza tematów z systemem prerekvizytów i poziomami trudności (1-4). Kategorie: Fundamentals, OWASP Top 10, Advanced.

**Dostępne tematy:**
- Poziom 1: HTTP Basics, HTML i JavaScript, SQL Basics
- Poziom 2: SQL Injection, XSS, Broken Authentication
- Poziom 3: CSRF, IDOR, File Upload, Command Injection
- Poziom 4: Blind SQLi, Stored XSS, File Inclusion (LFI/RFI)

### Brain (Silnik Nauki)
Adaptacyjny silnik uczenia. Dobiera kolejność i trudność materiału na podstawie postępów użytkownika.

---

## Praktyka

### Labs (DVWA)
Interaktywne laboratoria na bazie DVWA (Damn Vulnerable Web Application). Praktyczne ćwiczenia podatności: sqli, xss_reflected, xss_stored, brute_force, csrf, idor, file_upload, command_injection, file_inclusion, sqli_blind.

### Lab Attempts
Śledzenie prób rozwiązania laboratoriów. Historia podejść, wskazówki przy niepowodzeniu.

---

## Słownictwo i Fiszki

### Vocabulary (Słownik)
Baza terminów cyberbezpieczeństwa z definicjami i przykładami użycia.

### Flashcards (Fiszki)
System fiszek dla terminologii security. Tworzenie manualne i automatyczne.

---

## AI Wsparcie

### Mentor AI
Asystent AI do zadawania pytań, wyjaśniania konceptów, analizy błędów użytkownika. Kontekst aktualnego tematu i poziomu.

---

## Śledzenie Postępów

### Error Tracking
Rejestrowanie błędnych odpowiedzi i nieudanych lab attempts. Baza do powtórek.

### Stats (Statystyki)
Postęp per temat, ukończone laboratoria, liczba błędów, czas nauki, osiągnięcia.

### Achievements (Osiągnięcia)
System gamifikacji: odznaki za ukończenie tematów, serii, laboratoriów.

---

## Eksport

### Downloads
Pobieranie notatek i materiałów z tematów. Eksport do lokalnego pliku.

---

## Infrastruktura

**Stack:** FastAPI + SQLite + React/Vite
**Port:** Backend 8000, Frontend 5173
**AI:** Gemini (generowanie treści, mentor)
**Audio:** TTS service
