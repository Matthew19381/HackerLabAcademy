import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from models.conversation import ConversationSession, ConversationTurn
from models.topic import Topic
from models.user import User
from services.ai_service import generate_json
from services.achievement_service import check_and_award_achievements

logger = logging.getLogger(__name__)

# Max turns per session (5 questions)
MAX_TURNS = 5
XP_PER_CORRECT = 15


async def start_conversation_session(user_id: int, topic_slug: str = None, db: Session = None) -> ConversationSession:
    """Create a new conversation session."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    session = ConversationSession(
        user_id=user_id,
        topic_slug=topic_slug,
        started_at=datetime.utcnow(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


async def generate_question(session: ConversationSession, db: Session) -> dict:
    """Generate the next question using Gemini based on topic and turn number."""
    topic = None
    if session.topic_slug:
        topic = db.query(Topic).filter(Topic.slug == session.topic_slug).first()

    turn_number = session.total_turns + 1

    prompt = f"""Jesteś ekspertem cyberbezpieczeństwa i nauczycielem. Zadaj pytanietestujące zrozumienie użytkownika.

    Kontekst:
    - Temat: {topic.name if topic else 'Ogólne bezpieczeństwo IT'}
    - Kategoria: {topic.category if topic else 'Security Fundamentals'}
    - Poziom trudności: {topic.difficulty if topic else 2}/5
    - numer pytania w sesji: {turn_number} z {MAX_TURNS}

    Zwróć JSON:
    {{
      "question": "Treść pytania po polsku",
      "type": "multiple_choice" | "open_ended" | "scenario",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],  // dla multiple_choice, w open_ended null
      "correct_answer": "A" | "B" | "C" | "D" | "tekst dokładny",
      "explanation": "Krótkie wyjaśnienie poprawnej odpowiedzi (2-3 zdania)"
    }}

    Wymagania:
    - Język polski, prosty ale precyzyjny
    - Pytania progresywnie trudniejsze (turn 1 = łatwe, turn 5 = trudne)
    - Mix typów: 2 multiple_choice, 2 open_ended, 1 scenario (case study)
    - Temat powiązany z kontekstem (topic)
    - Opcje MC: 4 opcje, tylko jedna poprawna
    - Open-ended: konkretne pytanie wymagające krótkiej odpowiedzi (1-2 zdania)
    - Scenario: krótki opis sytuacji + pytanie o action/reaction
    - Avoid trivial yes/no questions
    """

    result = await generate_json(prompt)

    # Save assistant message (question) with full metadata
    turn = ConversationTurn(
        session_id=session.id,
        role="assistant",
        content=result['question'],
        turn_metadata=json.dumps({
            "type": result['type'],
            "options": result.get('options'),
            "correct_answer": result['correct_answer'],
            "explanation": result['explanation']
        }, ensure_ascii=False),
        created_at=datetime.utcnow(),
    )
    db.add(turn)
    db.commit()

    return result


def evaluate_answer(session: ConversationSession, user_answer: str, db: Session) -> dict:
    """Evaluate user's answer and provide feedback."""
    # Get the latest assistant turn (the question)
    assistant_turn = db.query(ConversationTurn).filter(
        ConversationTurn.session_id == session.id,
        ConversationTurn.role == "assistant"
    ).order_by(ConversationTurn.id.desc()).first()

    if not assistant_turn or not assistant_turn.turn_metadata:
        raise ValueError("No question found for this session")

    meta = json.loads(assistant_turn.turn_metadata)
    correct_answer = meta['correct_answer']
    question_type = meta['type']
    explanation = meta['explanation']
    question_text = assistant_turn.content

    is_correct = False
    if question_type == 'multiple_choice':
        is_correct = user_answer.strip().upper() == correct_answer.strip().upper()
    elif question_type in ('open_ended', 'scenario'):
        is_correct = _semantic_match_open_ended(user_answer, correct_answer, question_text)

    # Save user turn
    turn = ConversationTurn(
        session_id=session.id,
        role="user",
        content=user_answer,
        is_correct=is_correct,
        feedback=explanation if is_correct else "Niestety, to nie do końca poprawne. " + explanation,
        created_at=datetime.utcnow(),
    )
    db.add(turn)

    # Update session stats
    session.total_turns += 1
    if is_correct:
        session.correct_answers += 1
    db.commit()

    # Award XP if correct
    if is_correct:
        user = db.query(User).filter(User.id == session.user_id).first()
        user.total_xp += XP_PER_CORRECT
        session.xp_awarded += XP_PER_CORRECT
        db.commit()

    return {
        "correct": is_correct,
        "feedback": turn.feedback,
        "xp_awarded": XP_PER_CORRECT if is_correct else 0,
    }


def _semantic_match_open_ended(user_answer: str, correct_answer: str, question: str) -> bool:
    """Simple keyword matching for open-ended (can be upgraded to Gemini embedding)."""
    # Normalize
    user_norm = user_answer.lower().strip()
    correct_norm = correct_answer.lower().strip()

    # Exact match
    if user_norm == correct_norm:
        return True

    # Keyword inclusion: check if key terms from correct answer appear in user answer
    correct_keywords = set(correct_norm.replace('?', '').replace('.', '').split())
    user_words = set(user_norm.split())

    # If >70% of keywords present, consider correct
    if len(correct_keywords) > 0:
        overlap = len(correct_keywords & user_words) / len(correct_keywords)
        if overlap >= 0.7:
            return True

    return False


async def end_conversation_session(session_id: int, db: Session) -> dict:
    """End a session and finalize awards."""
    session = db.query(ConversationSession).filter(ConversationSession.id == session_id).first()
    if not session:
        raise ValueError("Session not found")

    session.ended_at = datetime.utcnow()
    db.commit()

    user = db.query(User).filter(User.id == session.user_id).first()
    new_achievements = check_and_award_achievements(user, db)

    return {
        "session_id": session.id,
        "total_turns": session.total_turns,
        "correct_answers": session.correct_answers,
        "xp_awarded": session.xp_awarded,
        "total_xp": user.total_xp,
        "new_achievements": new_achievements,
    }
