import logging
from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.lesson_service import mentor_chat

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/mentor", tags=["mentor"])

# In-memory sessions: {session_id: [messages]}
_sessions: dict = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str
    topic_context: str = None


@router.post("/chat")
async def chat(req: ChatRequest):
    history = _sessions.get(req.session_id, [])
    response = await mentor_chat(req.message, history, req.topic_context)

    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": response})
    _sessions[req.session_id] = history[-20:]  # keep last 20 messages

    return {"response": response, "history_length": len(history)}


@router.delete("/session/{session_id}")
def clear_session(session_id: str):
    _sessions.pop(session_id, None)
    return {"success": True}
