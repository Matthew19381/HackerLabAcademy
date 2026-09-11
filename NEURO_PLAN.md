# NEURO_PLAN — HackerLabAcademy (v1.0)

> Część ekosystemu: `System-Glowny/MASTER_PLAN.md` (standard naukowy: sekcja 0).

## 1. Rola w ekosystemie
Nauka umiejętności złożonej (cybersecurity) = wiedza deklaratywna (terminy,
koncepty) + proceduralna (laby). Nauka deklaratywna idzie przez wspólny
Learning Engine; proceduralna przez zasady cognitive load theory i deliberate
practice.

## 2. Fundament naukowy
| Obszar | Co pokazują badania | Źródło | Poziom |
|---|---|---|---|
| Worked examples | dla nowicjuszy przykłady rozwiązane > samodzielne odkrywanie; przewaga znika z ekspertyzą (expertise reversal) | Sweller (CLT); Kalyuga et al. 2003 | META |
| Guided instruction | minimalne prowadzenie u początkujących zawodzi | Kirschner, Sweller & Clark 2006 | przegląd |
| Productive failure | próba PRZED instrukcją pomaga, jeśli po niej następuje konsolidacja | Kapur 2008/2016 | RCT |
| Deliberate practice | ćwiczenie celowane w słabości z natychmiastowym feedbackiem | Ericsson et al. 1993 | OBS/przegląd |
| Testing effect / spacing | jak w całym ekosystemie | Roediger & Karpicke 2006; Cepeda 2006 | META |
| Errorful learning | błędy + feedback korekcyjny = lepsza pamięć niż unikanie błędów | Metcalfe 2017 | META |

## 3. Funkcje
| ID | Funkcja | Podstawa | Poziom |
|---|---|---|---|
| HL-1 | Fiszki terminologii przez **wspólny Learning Engine (FSRS)**; error tracking zasila kolejkę powtórek (błąd → fiszka) | Cepeda 2006; Metcalfe 2017 | META |
| HL-2 | **Faded worked examples w labach**: nowy typ podatności zaczyna się od pełnego przejścia (walkthrough), kolejne laby stopniowo usuwają kroki aż do samodzielności | Sweller; Renkl & Atkinson 2003 (fading) | RCT |
| HL-3 | **Productive failure mode** (dla tematów poziomu 2+): najpierw 10-15 min własnych prób na labie, potem instrukcja — nie odwrotnie; przy poziomie 1 odwrotnie (HL-2) | Kapur 2016; Kalyuga 2003 (expertise reversal) | RCT |
| HL-4 | **Wskazówki stopniowane zamiast rozwiązań**: hint 1 (kierunek) → hint 2 (technika) → hint 3 (krok). Mentor AI nie podaje payloadu od razu | deliberate practice: feedback bez wyręczania; Ericsson 1993 | OBS |
| HL-5 | Interleaving typów podatności w powtórkach ("który atak tu pasuje?") — trening ROZPOZNAWANIA, nie tylko wykonania | Rohrer & Taylor 2007; discrimination learning | RCT |
| HL-6 | **Retrieval po labie**: po ukończeniu 3 pytania "wyjaśnij czemu działało / jak się bronić" (free recall + transfer do defensywy) | testing effect + self-explanation | META |
| HL-7 | Brain (silnik adaptacyjny): dobór trudności wg accuracy — utrzymanie w strefie ~70-85% poprawności; poza nią nuda/frustracja. Konkretny próg = HIPOTEZA do kalibracji na danych | trening adaptacyjny (analogia: N-back adaptacyjny); próg liczbowy bez twardych dowodów | HIPOTEZA |
| HL-8 | Osiągnięcia tylko informacyjne (opanowane tematy), bez lig i rankingów | Deci, Koestner & Ryan 1999 (META) | META |

## 4. Anty-wzorce
- Zakaz "wrzucenia na głęboką wodę" nowicjusza (Kirschner 2006) — placement test
  decyduje o trybie HL-2 vs HL-3.
- Mentor AI nie może dawać gotowych rozwiązań przy pierwszej prośbie (HL-4).
- Streak bez mechaniki karzącej: przerwa nie zeruje postępu opanowania.

## 5. Integracje
- Publikuje: sesje, błędy (typ podatności), ukończone laby, zaległe powtórki.
- Subskrybuje: plan dnia, tryb przetrwania (minimalny cel: 1 sesja fiszek),
  Edukacja (umiejętność "web security" w profilu kompetencji).

## 6. Fazy
1. HL-1 (wspólny FSRS + błędy→fiszki), HL-4 (hinty stopniowane).
2. HL-2 (fading), HL-6 (retrieval po labie).
3. HL-3, HL-5, HL-7 (po zebraniu danych accuracy).
