from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.conversation_service import (
    start_conversation_session,
    generate_question,
    evaluate_answer,
    end_conversation_session,
)
from backend.models.conversation import ConversationSession

router = APIRouter(prefix="/api/conversation", tags=["conversation"])


@router.post("/sessions/start")
async def start_session(
    user_id: int,
    topic_slug: str = None,
    db: Session = Depends(get_db)
):
    """Start a new conversation practice session."""
    try:
        session = await start_conversation_session(user_id, topic_slug, db)
        return {
            "session_id": session.id,
            "topic_slug": topic_slug,
            "started_at": session.started_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/question")
async def get_next_question(session_id: int, db: Session = Depends(get_db)):
    """Generate and return the next question for the current session."""
    session = db.query(ConversationSession).filter(ConversationSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.total_turns >= 5:
        raise HTTPException(status_code=400, detail="Session already completed max turns")

    try:
        question = await generate_question(session, db)
        return {
            "session_id": session.id,
            "turn": session.total_turns + 1,
            "question": question["question"],
            "type": question["type"],
            "options": question.get("options"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/answer")
def submit_answer(
    session_id: int,
    user_answer: str,
    db: Session = Depends(get_db)
):
    """Submit user's answer and get evaluation."""
    try:
        session = db.query(ConversationSession).filter(ConversationSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        result = evaluate_answer(session, user_answer, db)

        return {
            "correct": result["correct"],
            "feedback": result["feedback"],
            "xp_awarded": result["xp_awarded"],
            "turns_completed": session.total_turns,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/end")
def end_session(session_id: int, db: Session = Depends(get_db)):
    """End the conversation session."""
    try:
        result = end_conversation_session(session_id, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/user/{user_id}")
def list_user_sessions(user_id: int, db: Session = Depends(get_db)):
    """List all conversation sessions for a user."""
    sessions = db.query(ConversationSession).filter(ConversationSession.user_id == user_id).order_by(ConversationSession.started_at.desc()).all()
    return [
        {
            "id": s.id,
            "topic_slug": s.topic_slug,
            "started_at": s.started_at.isoformat(),
            "ended_at": s.ended_at.isoformat() if s.ended_at else None,
            "total_turns": s.total_turns,
            "correct_answers": s.correct_answers,
            "xp_awarded": s.xp_awarded,
        }
        for s in sessions
    ]
