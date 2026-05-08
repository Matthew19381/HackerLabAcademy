import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.exercise import Exercise, UserExerciseAttempt
from backend.models.topic import Topic
from backend.models.user import User
from backend.services.ai_service import generate_json
from backend.services.achievement_service import check_and_award_achievements

logger = logging.getLogger(__name__)


async def generate_exercises_for_topic(topic_id: int, db: Session, count: int = 5) -> list[Exercise]:
    """Generate exercises for a given topic using Gemini."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise ValueError(f"Topic ID {topic_id} not found")

    prompt = f"""Jesteś ekspertem cyberbezpieczeństwa i nauczycielem. Wygeneruj {count} zróżnicowanych ćwiczenia na temat:

    Temat: {topic.name}
    Kategoria: {topic.category}
    Poziom trudności: {topic.difficulty}/5

    Zwróć JSON:
    {{
      "exercises": [
        {{
          "type": "quiz_mc" | "fill_blank" | "code_review" | "defense_write",
          "question": "Treść pytania lub polecenie",
          "options": ["A. ...", "B. ...", "C. ...", "D. ..."],  // TYLKO dla quiz_mc
          "correct_answer": "0" | "1" | "2" | "3" | "dokładny tekst" | "line:N",
          "explanation": "Dlaczego ta odpowiedź jest poprawna, edukacyjne wyjaśnienie",
          "code_snippet": "kod do analizy (dla code_review i defense_write, w innych null)"
        }}
      ]
    }}

    WYMAGANIA:
    - Język polski
    - Mix typów ćwiczeń: quiz_mc, fill_blank, code_review, defense_write
    - defense_write: podaj fragment podatnego kodu (Python/PHP/JS/SQL), question: "Napraw ten kod — popraw podatność", correct_answer: poprawiony fragment kodu (pełna linijka lub kompletny fragment, case-sensitive); code_snippet: oryginalny, podatny kod
    - Inne wymagania jak wyżej
    - Używaj prawdziwych przykładów
    """

    try:
        result = await generate_json(prompt)
        exercises_data = result.get("exercises", [])

        created = []
        for ex_data in exercises_data[:count]:
            ex = Exercise(
                topic_id=topic.id,
                exercise_type=ex_data["type"],
                question=ex_data["question"],
                options=json.dumps(ex_data.get("options")) if ex_data.get("options") else None,
                correct_answer=ex_data["correct_answer"],
                explanation=ex_data.get("explanation"),
                code_snippet=ex_data.get("code_snippet"),
                difficulty=topic.difficulty,
                generated_by_ai=True,
            )
            db.add(ex)
            created.append(ex)

        db.commit()
        for ex in created:
            db.refresh(ex)
        return created

    except Exception as e:
        logger.error(f"Failed to generate exercises for {topic_slug}: {e}")
        raise


def get_exercises_for_topic(topic_id: int, db: Session) -> list[Exercise]:
    """Get all exercises for a topic."""
    return db.query(Exercise).filter(Exercise.topic_id == topic_id).order_by(Exercise.id).all()


def submit_exercise_answer(
    user_id: int, exercise_id: int, user_answer: str, db: Session
) -> dict:
    """Check user's answer, award XP, and record attempt."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise ValueError("Exercise not found")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    # Normalize answers for comparison
    is_correct = False
    if exercise.exercise_type == "quiz_mc":
        # correct_answer is index as string "0"-"3"
        ans = user_answer.strip().upper()
        # Accept both letter (A-D) and index (0-3)
        if ans in "ABCD":
            ans = str(ord(ans) - ord("A"))  # 'A'->'0', 'B'->'1', ...
        is_correct = ans == exercise.correct_answer.strip()
    elif exercise.exercise_type == "fill_blank":
        # Case-sensitive exact match (could normalize later)
        is_correct = user_answer.strip() == exercise.correct_answer.strip()
    elif exercise.exercise_type == "code_review":
        # Accept "line:3" or "3" depending on prompt
        correct = exercise.correct_answer.strip()
        # User might answer "3" or "line:3"
        if user_answer.strip() == correct or user_answer.strip().replace("line:", "") == correct.replace("line:", ""):
            is_correct = True
    elif exercise.exercise_type == "defense_write":
        # Exact match for fixed code snippet
        is_correct = user_answer.strip() == exercise.correct_answer.strip()

    # XP award: base 10, modified by difficulty (1.0x to 2.0x)
    base_xp = 10
    xp_awarded = int(base_xp * (0.8 + 0.4 * (exercise.difficulty / 5))) if is_correct else 0

    # Create attempt record
    attempt = UserExerciseAttempt(
        user_id=user_id,
        exercise_id=exercise_id,
        user_answer=user_answer,
        is_correct=is_correct,
        xp_awarded=xp_awarded,
    )
    db.add(attempt)

    # Update user XP
    if is_correct:
        user.total_xp += xp_awarded
        # Update last activity
        user.last_activity_date = datetime.utcnow()

    db.commit()
    db.refresh(attempt)

    # Check achievements
    newly_awarded = check_and_award_achievements(user, db)

    return {
        "correct": is_correct,
        "xp_awarded": xp_awarded,
        "explanation": exercise.explanation,
        "total_xp": user.total_xp,
        "achievements": newly_awarded,
    }
