from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.database import Base


class CtfChallenge(Base):
    """CTF puzzles (restored 2026-11-03, decision 3 of 2026-08-09: CTF stays, no leaderboard).
    Every active challenge must be solvable from its own description - no external lab."""

    __tablename__ = "ctf_challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)  # Markdown supported
    flag = Column(String, nullable=False)
    points = Column(Integer, default=100)
    difficulty = Column(Integer, default=1)  # 1-5
    category = Column(String, nullable=False)  # web, forensics, crypto
    hint = Column(Text, nullable=True)
    solution = Column(Text, nullable=True)  # explanation shown after solving
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    attempts = relationship("UserCtfAttempt", back_populates="challenge", cascade="all, delete-orphan")


class UserCtfAttempt(Base):
    __tablename__ = "user_ctf_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("ctf_challenges.id"), nullable=False)
    solved = Column(Boolean, default=False)
    solved_at = Column(DateTime, nullable=True)
    attempts_count = Column(Integer, default=0)
    points_earned = Column(Integer, default=0)
    hint_used = Column(Boolean, default=False)  # hint halves the points (enforced since 2026-11-03)

    user = relationship("User", back_populates="ctf_attempts")
    challenge = relationship("CtfChallenge", back_populates="attempts")
