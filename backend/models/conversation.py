from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_slug = Column(String, nullable=True)  # optional: tied to a topic
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    total_turns = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    xp_awarded = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="conversation_sessions")
    turns = relationship("ConversationTurn", back_populates="session", cascade="all, delete-orphan")


class ConversationTurn(Base):
    __tablename__ = "conversation_turns"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("conversation_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # "assistant" (question) or "user" (answer)
    content = Column(Text, nullable=False)  # user answer or assistant question text
    is_correct = Column(Boolean, nullable=True)  # only for user answers
    feedback = Column(Text, nullable=True)  # AI feedback after user answer
    turn_metadata = Column('metadata', Text, nullable=True)  # JSON: for assistant: {question, type, options, correct_answer, explanation}; for user: optional
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("ConversationSession", back_populates="turns")
