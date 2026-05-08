import logging
from backend.services.ai_service import generate_json, generate_text

logger = logging.getLogger(__name__)


async def generate_theory_lesson(topic_name: str, topic_slug: str, difficulty: int, prerequisites: list) -> dict:
    prereq_str = ", ".join(prerequisites) if prerequisites else "brak"
    prompt = f"""Jesteś ekspertem cyberbezpieczeństwa i nauczycielem. Napisz kompletną lekcję teorii dla POCZĄTKUJĄCEGO na temat:

Temat: {topic_name}
Poziom trudności: {difficulty}/5
Wymagana wiedza: {prereq_str}

Lekcja musi być w języku polskim, praktyczna i skierowana do kogoś kto nie ma doświadczenia w cyberbezpieczeństwie.

Zwróć JSON:
{{
    "title": "{topic_name}",
    "intro": "Wstęp — dlaczego ten temat jest ważny (2-3 zdania)",
    "sections": [
        {{
            "heading": "Nagłówek sekcji",
            "content": "Treść sekcji z wyjaśnieniami",
            "code_example": "Przykład kodu lub payloadu (opcjonalnie, może być null)"
        }}
    ],
    "key_concepts": [
        {{"term": "Termin", "definition": "Definicja po polsku"}}
    ],
    "how_attack_works": "Krok po kroku jak działa ten atak (po polsku)",
    "how_to_defend": "Jak się bronić przed tym atakiem (po polsku)",
    "real_world_example": "Przykład z prawdziwego życia (znany incydent lub scenariusz)",
    "quiz": [
        {{
            "question": "Pytanie testowe",
            "options": ["A. opcja", "B. opcja", "C. opcja", "D. opcja"],
            "correct": "A",
            "explanation": "Dlaczego ta odpowiedź jest poprawna"
        }}
    ],
    "flashcards": [
        {{
            "front": "Pytanie lub termin",
            "back": "Odpowiedź lub definicja",
            "example": "Przykład użycia (kod, payload, scenario)"
        }}
    ]
}}

Uwzględnij:
- Minimum 4 sekcje
- Minimum 5 kluczowych pojęć
- Minimum 5 pytań quizu
- Minimum 8 fiszek
- Konkretne przykłady payloadów/kodów gdzie to możliwe"""

    return await generate_json(prompt)


async def _generate_theory_lesson_UNUSED(topic_name, topic_slug):
    # kept for reference only — fallbacks removed intentionally
    return {
            "flashcards": [
                {"front": topic_name, "back": f"Typ ataku/podatności w cyberbezpieczeństwie", "example": None}
            ]
        }


async def generate_lab_instructions(topic_name: str, topic_slug: str, lab_type: str) -> dict:
    prompt = f"""Jesteś instruktorem cyberbezpieczeństwa. Napisz instrukcje do laboratorium praktycznego dla POCZĄTKUJĄCEGO.

Temat: {topic_name}
Typ labu: {lab_type}
Środowisko: DVWA (Damn Vulnerable Web Application) działające lokalnie

Napisz w języku polskim, krok po kroku, bardzo szczegółowo.

Zwróć JSON:
{{
    "title": "Tytuł laboratorium",
    "objective": "Cel laboratorium — czego się nauczysz",
    "tools_needed": ["narzędzie 1", "narzędzie 2"],
    "setup_steps": [
        "Krok 1: ...",
        "Krok 2: ..."
    ],
    "tasks": [
        {{
            "id": 1,
            "title": "Zadanie 1",
            "description": "Opis co zrobić",
            "hint": "Wskazówka jeśli utkniesz",
            "solution": "Rozwiązanie (payload/komenda)"
        }}
    ],
    "verification_question": "Pytanie sprawdzające — co znalazłeś w bazie danych / jaki payload zadziałał",
    "writeup_template": {{
        "reconnaissance": "Co sprawdziłeś przed atakiem?",
        "exploitation": "Jaki payload/technikę użyłeś?",
        "result": "Co udało Ci się osiągnąć?",
        "lesson": "Czego się nauczyłeś?"
    }}
}}"""

    try:
        return await generate_json(prompt)
    except Exception as e:
        logger.error(f"Error generating lab instructions for {topic_slug}: {e}")
        return {
            "title": f"Lab: {topic_name}",
            "objective": f"Praktyczne ćwiczenie z {topic_name}",
            "tools_needed": ["Przeglądarka", "DVWA"],
            "setup_steps": ["Uruchom DVWA przez Docker", "Zaloguj się (admin/password)", "Ustaw poziom trudności na Low"],
            "tasks": [
                {
                    "id": 1,
                    "title": f"Podstawowe {topic_name}",
                    "description": f"Wykonaj podstawowy atak {topic_name} na formularz.",
                    "hint": "Zacznij od prostego testu.",
                    "solution": "Patrz dokumentacja DVWA"
                }
            ],
            "verification_question": "Jaki wynik uzyskałeś?",
            "writeup_template": {
                "reconnaissance": "Co sprawdziłeś?",
                "exploitation": "Co zrobiłeś?",
                "result": "Co osiągnąłeś?",
                "lesson": "Czego się nauczyłeś?"
            }
        }


async def generate_writeup(
    topic_name: str,
    user_steps: dict,
    lab_instructions: dict
) -> dict:
    prompt = f"""Jesteś mentorem cyberbezpieczeństwa. Na podstawie kroków ucznia wygeneruj profesjonalny writeup CTF-style.

Temat labu: {topic_name}
Kroki ucznia:
- Rekonesans: {user_steps.get('reconnaissance', 'brak')}
- Eksploitacja: {user_steps.get('exploitation', 'brak')}
- Wynik: {user_steps.get('result', 'brak')}
- Lekcja: {user_steps.get('lesson', 'brak')}

Napisz writeup w języku polskim. Zwróć JSON:
{{
    "title": "Tytuł writeupa",
    "summary": "Podsumowanie (2-3 zdania co osiągnął uczeń)",
    "attack_narrative": "Narracja ataku krok po kroku",
    "technical_details": "Szczegóły techniczne użytych technik",
    "defense_notes": "Jak deweloper mógł temu zapobiec",
    "key_lessons": ["Lekcja 1", "Lekcja 2", "Lekcja 3"],
    "difficulty_rating": 3,
    "xp_commentary": "Dlaczego ten lab jest wartościowy"
}}"""

    try:
        return await generate_json(prompt)
    except Exception as e:
        logger.error(f"Error generating writeup: {e}")
        return {
            "title": f"Writeup: {topic_name}",
            "summary": f"Uczeń ukończył lab z {topic_name}.",
            "attack_narrative": "Atak został przeprowadzony pomyślnie.",
            "technical_details": user_steps.get("exploitation", ""),
            "defense_notes": "Walidacja danych wejściowych zapobiega temu atakowi.",
            "key_lessons": ["Waliduj dane wejściowe", "Stosuj prepared statements", "Zasada najmniejszych uprawnień"],
            "difficulty_rating": 3,
            "xp_commentary": "Lab pokazuje realne zagrożenie."
        }


async def analyze_quiz_errors(questions: list, user_answers: dict, topic_name: str, response_times: dict = None) -> dict:
    results = []
    for q in questions:
        q_id = str(q.get("id", questions.index(q)))
        user_ans = user_answers.get(q_id, "")
        correct = q.get("correct", "")
        is_correct = str(user_ans).upper().strip() == str(correct).upper().strip()
        results.append({
            "question": q.get("question", ""),
            "user_answer": user_ans,
            "correct_answer": correct,
            "is_correct": is_correct,
            "explanation": q.get("explanation", "")
        })

    wrong = [r for r in results if not r["is_correct"]]
    score = (sum(1 for r in results if r["is_correct"]) / len(results) * 100) if results else 0

    # Confidence detection: fast wrong answer (<3000ms) = guessing
    if response_times:
        for r in wrong:
            idx = str(results.index(r))
            ms = response_times.get(idx, 9999)
            if ms < 3000:
                r["confidence_hint"] = "guessing"
            elif ms > 15000:
                r["confidence_hint"] = "no_knowledge"
            else:
                r["confidence_hint"] = "misunderstanding"

    wrong_with_hints = wrong
    prompt = f"""Przeanalizuj błędy ucznia w quizie z {topic_name} i zaklasyfikuj każdy błąd.

Błędne odpowiedzi: {wrong_with_hints}

Dla każdego błędu określ typ (uwzględnij "confidence_hint" jeśli dostępny):
- "no_knowledge" — uczeń nie miał pojęcia o temacie
- "misunderstanding" — mylne rozumienie pojęcia
- "guessing" — odpowiedź losowa, bez wiedzy

Zwróć JSON:
{{
    "score": {score:.1f},
    "errors": [
        {{
            "question": "treść pytania",
            "user_answer": "co odpowiedział",
            "correct_answer": "poprawna odpowiedź",
            "error_type": "no_knowledge|misunderstanding|guessing",
            "explanation": "krótkie wyjaśnienie błędu po polsku"
        }}
    ],
    "summary": "Ogólna ocena po polsku"
}}"""

    try:
        result = await generate_json(prompt)
        result["score"] = score
        return result
    except Exception as e:
        logger.error(f"Error analyzing quiz errors: {e}")
        return {
            "score": score,
            "errors": [{"question": r["question"], "user_answer": r["user_answer"],
                        "correct_answer": r["correct_answer"], "error_type": "unknown",
                        "explanation": r["explanation"]} for r in wrong],
            "summary": f"Wynik: {score:.0f}%. Przejrzyj błędy."
        }


async def mentor_chat(message: str, history: list, topic_context: str = None) -> str:
    context = f"Kontekst tematu: {topic_context}\n\n" if topic_context else ""
    history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history[-6:]])

    prompt = f"""Jesteś AI Mentorem cyberbezpieczeństwa. Pomagasz początkującemu uczniowi zrozumieć tematy z web security.
Odpowiadaj po polsku, prosto i zrozumiale. Używaj analogii i przykładów z życia codziennego.
Jeśli pytanie dotyczy ataków — zawsze tłumacz w kontekście EDUKACYJNYM i etycznym pentestingu.

{context}Historia rozmowy:
{history_str}

Uczeń: {message}

Odpowiedź:"""

    try:
        return await generate_text(prompt)
    except Exception as e:
        logger.error(f"Error in mentor chat: {e}")
        return "Przepraszam, mam chwilowy problem. Spróbuj ponownie za chwilę."
