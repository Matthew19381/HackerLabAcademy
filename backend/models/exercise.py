from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    exercise_type = Column(String, nullable=False)  # "quiz_mc", "fill_blank", "code_review"
    question = Column(Text, nullable=False)
    options = Column(Text, nullable=True)  # JSON list: ["A", "B", "C", "D"] for quiz_mc; NULL for others
    correct_answer = Column(Text, nullable=False)  # for quiz_mc: index (0-3) as string; for fill: exact text; for code: line number or "line:X"
    explanation = Column(Text, nullable=True)
    code_snippet = Column(Text, nullable=True)  # for code_review exercises
    difficulty = Column(Integer, default=1)  # 1-5
    generated_by_ai = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    topic = relationship("Topic", back_populates="exercises")
    attempts = relationship("UserExerciseAttempt", back_populates="exercise", cascade="all, delete-orphan")


class UserExerciseAttempt(Base):
    __tablename__ = "user_exercise_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    attempted_at = Column(DateTime, default=datetime.utcnow)
    xp_awarded = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="exercise_attempts")
    exercise = relationship("Exercise", back_populates="attempts")
