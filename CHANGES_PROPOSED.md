# HackerLabAcademy — Proponowane Zmiany i Nowe Funkcje

Data: 2026-03-28
Status: Do oceny przez użytkownika przed implementacją

---

## PROBLEMY KRYTYCZNE (P0)

### P0-1: Brak zróżnicowanych ćwiczeń
**Problem:** Praktyka ograniczona wyłącznie do labów DVWA. Brak ćwiczeń tekstowych, quizów, zadań kodowania.
**Propozycja:** Dodać do każdego tematu minimum 3 typy ćwiczeń:
- Quiz (Multiple Choice) z obsługą klawiszy numerycznych
- Fill Blank (uzupełnij payload/komendę)
- Code Review (wskaż podatność w kodzie)

### P0-2: Brak interaktywnej praktyki konwersacyjnej z AI
**Problem:** Mentor AI istnieje, ale nie ma strukturyzowanej rozmowy ćwiczeniowej.
**Propozycja:** Tryb "Rozmowa z AI Mentorem" — ustrukturyzowane sesje Q&A na temat bezpieczeństwa. AI zadaje pytania, ocenia odpowiedzi, wyjaśnia błędy.

---

## ZMIANY WAŻNE (P1)

### P1-1: Security News (CVE Explorer)
Inspiracja: Newsy w Language Tutor.
Dzienne/tygodniowe wiadomości o nowych CVE i incydentach bezpieczeństwa. Klikalne terminy → dodanie do fiszek. Wyjaśnienie mechanizmu ataku dla każdego CVE. Powiązanie z odpowiednim tematem kursu.

### P1-2: YouTube Security Videos per Topic
Inspiracja: Filmy w Language Tutor.
Przy każdym temacie: lista filmów edukacyjnych z YouTube. Kategorie: tutorial, demo ataku, obrona. Ładowane raz przy generowaniu treści tematu.

### P1-3: Eksport Fiszek do Anki
Inspiracja: Eksport Anki w Language Tutor.
Eksport fiszek z terminologią security do formatu .apkg. Filtr po dacie dodania (nie pobieraj za każdym razem wszystkich).

### P1-4: Timer Sesji Nauki
Inspiracja: Timer 15 min w Language Tutor.
Widoczny timer nauki we wszystkich zakładkach. Nie zatrzymuje się przy zmianie zakładki. Własny czas (15/30/60 min). Ostatnie 5 sekund: powiększenie + czerwone miganie.

### P1-5: Szybkie Dodawanie Fiszek
Inspiracja: Szybkie fiszki w Language Tutor.
Widoczny przycisk w każdej zakładce. Wpisanie terminu → AI uzupełnia definicję i przykład automatycznie.

---

## NOWE FUNKCJE (P2)

### P2-1: CTF Challenge Mode
Zadania w stylu Capture The Flag. Stopniowane trudności. Znajdź flagę ukrytą w podatnej aplikacji. Ranking i punktacja. Historia ukończonych CTF.

### P2-2: Code Review Exercise
Pokaż podatny kod (Python/PHP/JS/SQL). Użytkownik wskazuje linię z podatnością. AI ocenia i wyjaśnia. Stopniowane: od oczywistych błędów do subtelnych.

### P2-3: Terminal Simulator
Interaktywny symulator terminala. Ćwiczenie komend: nmap, curl, sqlmap (edukacyjne), podstawy bash. Scenariusze z zadaniami.

### P2-4: Defense Mode
Odwrócenie: zamiast atakować — napraw podatny kod. Wyświetl podatny snippet, użytkownik pisze poprawkę. AI ocenia poprawność i wyjaśnia best practices.

### P2-5: Attack Scenario
Krok po kroku symulacja pełnego ataku na przykładową aplikację. Każdy krok = nowe ćwiczenie. Rozumienie całego kill chain'a, nie tylko pojedynczej podatności.

### P2-6: Topic Mindmap / Graph
Wizualizacja grafu zależności między tematami. Pokazuje prerekvizty i co odblokujesz po ukończeniu tematu. Motywuje do nauki.

---

## POPRAWKI UI (P3)

### P3-1: Dzienny wskaźnik ukończenia
Pasek postępu wypełniający się w miarę ukończenia: lab, quiz, fiszki, artykuł. Synchronizacja z przyciskami "Oznacz jako ukończone".

### P3-2: Dzienne Wskazówki Security
Codzienne porady bezpieczeństwa poparte badaniami/best practices. Generowane raz dziennie.

### P3-3: Audio dla Terminologii
TTS dla nowych terminów i definicji. Poprawna wymowa angielskich terminów security.

### P3-4: Certyfikat Ukończenia Sekcji
Po ukończeniu wszystkich tematów w kategorii (Fundamentals, OWASP Top 10, Advanced) — wygenerowany certyfikat PDF.

### P3-5: Osiągnięcia po Polsku
Zmiana wszystkich achievement stringów na język polski.

---

## INSPIRACJE Z LANGUAGE TUTOR — PODSUMOWANIE

| Language Tutor | CyberTutor Odpowiednik |
|----------------|------------------------|
| Newsy | CVE/Security News Explorer |
| Filmy (YouTube) | Security Video Library per temat |
| Mów (rozmowa AI) | AI Mentor Session (Q&A strukturyzowane) |
| i+1 Czytanie | Security Write-ups / Artykuły na poziomie |
| Fiszki + Anki | Fiszki + Eksport Anki |
| Timer 15 min | Timer Sesji |
| Szybkie fiszki | Szybkie terminy |
| Dzienne wskazówki | Dzienny tip security |
| Wskaźnik ukończenia | Wskaźnik ukończenia tematu/dnia |
