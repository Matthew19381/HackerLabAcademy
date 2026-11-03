import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.mentor_message import MentorMessage
from backend.services.lesson_service import mentor_chat

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mentor", tags=["mentor"])

HISTORY_LIMIT = 20  # messages sent back to the model as context


class ChatRequest(BaseModel):
    session_id: str
    message: str
    topic_context: str | None = None


def _history(db: Session, session_id: str, limit: int | None = None) -> list[dict]:
    query = db.query(MentorMessage).filter(MentorMessage.session_id == session_id).order_by(MentorMessage.id.desc())
    if limit:
        query = query.limit(limit)
    return [{"role": m.role, "content": m.content} for m in reversed(query.all())]


@router.post("/chat")
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    history = _history(db, req.session_id, HISTORY_LIMIT)
    response = await mentor_chat(req.message, history, req.topic_context)

    db.add(MentorMessage(session_id=req.session_id, role="user", content=req.message))
    db.add(MentorMessage(session_id=req.session_id, role="assistant", content=response))
    db.commit()
    return {"response": response, "history_length": len(history) + 2}


@router.get("/session/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    return {"session_id": session_id, "messages": _history(db, session_id)}


@router.delete("/session/{session_id}")
def clear_session(session_id: str, db: Session = Depends(get_db)):
    db.query(MentorMessage).filter(MentorMessage.session_id == session_id).delete()
    db.commit()
    return {"success": True}
