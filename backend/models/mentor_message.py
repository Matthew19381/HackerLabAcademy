from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from backend.database import Base


class MentorMessage(Base):
    """AI Mentor conversation (plan B3, 2026-11-03) - was a dict in process memory, lost on restart."""

    __tablename__ = "mentor_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
