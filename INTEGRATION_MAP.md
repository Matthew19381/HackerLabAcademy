# Personal AI OS — Mapa Integracji

Data: 2026-03-28

Wszystkie projekty są częścią jednego ekosystemu. System Główny orkiestruje przepływ danych.

---

## Moduły systemu

| Projekt | Folder | Status | Rola |
|---------|--------|--------|------|
| TradeVision | `03_Projects/tradevision` | Aktywny | Trading autonomiczny |
| AutoLogic/AlphaForge | `03_Projects/AutoLogic` | W budowie | Strategie tradingowe |
| Language Tutor | `03_Projects/language-tutor` | Aktywny | Nauka języków |
| CyberTutor | `03_Projects/cyber-tutor` | Aktywny | Nauka cybersecurity |
| Trening | `03_Projects/Trening` | Faza 1 | Aplikacja treningowa |
| Dieta | `03_Projects/Dieta` | Planowanie | System diety AI |
| Wygląd | `03_Projects/Wyglad` | Planowanie | Looks optimizer |
| Edukacja | `03_Projects/Edukacja` | Planowanie | Tracker edukacji |
| Finanse | `03_Projects/Finanse` | Planowanie | Portfel i inwestycje |
| Mentalność i Psychika | `03_Projects/Mentalnosc-i-Psychika` | Planowanie | System wsparcia |
| System Główny | `03_Projects/System-Glowny` | Planowanie (OSTATNI) | Dashboard + orkiestrator |

---

## Kluczowe integracje

```
Trening ──────┬──→ Dieta (zmęczenie → kalorie/makro)
              ├──→ Wygląd (sylwetka → priorytet ćwiczeń)
              └──→ Mentalność (pominięcia → check-in)

Wygląd ───────┬──→ Trening (cel estetyczny → plan)
              └──→ Dieta (skóra/retencja → żywienie)

Dieta ────────┬──→ Trening (energia → intensywność)
              └──→ Wygląd (trądzik/woda → produkty)

TradeVision ──┬──→ Finanse (P&L)
AutoLogic ────┘

Finanse ──────→ Mentalność (drawdown → wsparcie)

Edukacja ─────→ Mentalność (pominięcia → check-in)

Mentalność ───→ Wszystkie (wellbeing score, tryb kryzysowy)

Wszystkie ────→ System Główny (eventy, widgety, raporty)
```

---

## Standaryzowany format eventu

```json
{
  "module": "trening",
  "event_type": "session_skipped",
  "payload": { "reason": null, "streak_broken": true },
  "timestamp": "2026-03-28T18:00:00Z",
  "severity": "warning"
}
```

---

## Zalecana kolejność budowania

1. Trening (fundament — fizyczność)
2. Dieta (ścisły związek z treningiem)
3. Wygląd (korzysta z danych Trening + Dieta)
4. Mentalność (korzysta z eventów wszystkich powyższych)
5. Finanse (niezależny, ale korzysta z TradeVision/AutoLogic)
6. Edukacja (niezależny)
7. System Główny (OSTATNI — spinający wszystko)
