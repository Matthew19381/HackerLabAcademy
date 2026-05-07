"""
Defense Challenge model for HackerLabAcademy.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class DefenseChallenge(Base):
    __tablename__ = "defense_challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    vulnerable_code = Column(Text, nullable=False)  # code snippet with vulnerability
    solution_code = Column(Text, nullable=False)    # expected fixed code (or pattern)
    test_cases = Column(Text, nullable=True)        # JSON list of test cases (optional)
    points = Column(Integer, default=100)
    difficulty = Column(Integer, default=2)  # 1-5 scale
    topic_slug = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserDefenseAttempt(Base):
    __tablename__ = "user_defense_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    challenge_id = Column(Integer, ForeignKey("defense_challenges.id"))
    submitted_code = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    points_earned = Column(Integer, default=0)
    ai_feedback = Column(Text, nullable=True)  # explanation from AI
    solved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    challenge = relationship("DefenseChallenge")
    user = relationship("User")
