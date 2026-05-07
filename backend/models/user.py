from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_xp = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    last_activity_date = Column(DateTime, nullable=True)

    # Relationships
    topic_progress = relationship("UserTopicProgress", back_populates="user", cascade="all, delete-orphan")
    flashcards = relationship("Flashcard", back_populates="user", cascade="all, delete-orphan")
    error_items = relationship("ErrorItem", back_populates="user", cascade="all, delete-orphan")
    lab_attempts = relationship("LabAttempt", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
    exercise_attempts = relationship("UserExerciseAttempt", back_populates="user", cascade="all, delete-orphan")
    conversation_sessions = relationship("ConversationSession", back_populates="user", cascade="all, delete-orphan")
    attack_progress = relationship("UserAttackProgress", back_populates="user", cascade="all, delete-orphan")
    ctf_attempts = relationship("UserCtfAttempt", back_populates="user", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="user", cascade="all, delete-orphan")
