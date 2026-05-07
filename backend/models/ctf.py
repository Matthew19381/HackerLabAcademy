from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class CtfChallenge(Base):
    __tablename__ = "ctf_challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)  # Markdown supported
    flag = Column(String, nullable=False)  # plaintext flag (could hash later)
    points = Column(Integer, default=100)  # base points
    difficulty = Column(Integer, default=1)  # 1-5
    category = Column(String, nullable=False)  # "web", "forensics", "crypto", "pwn", "reversing"
    hint = Column(Text, nullable=True)
    solution = Column(Text, nullable=True)  # for admins
    is_active = Column(Boolean, default=True)
    created_at = DateTime = Column(DateTime, default=datetime.utcnow)

    # Relationships
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

    # Relationships
    user = relationship("User", back_populates="ctf_attempts")
    challenge = relationship("CtfChallenge", back_populates="attempts")
