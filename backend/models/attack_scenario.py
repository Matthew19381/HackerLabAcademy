from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class AttackScenario(Base):
    __tablename__ = "attack_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)  # narrative intro
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # steps stored as JSON array:
    # [{ "step": 1, "question": "...", "expected_answer": "...", "explanation": "...", "points": 50 }, ...]
    steps_data = Column(Text, nullable=False)  # JSON string

    # Relationships
    progress_entries = relationship("UserAttackProgress", back_populates="scenario", cascade="all, delete-orphan")


class UserAttackProgress(Base):
    __tablename__ = "user_attack_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scenario_id = Column(Integer, ForeignKey("attack_scenarios.id"), nullable=False)
    current_step = Column(Integer, default=0)  # 0 means not started, 1 means step 1 done, etc.
    completed = Column(Boolean, default=False)
    total_points_earned = Column(Integer, default=0)
    last_attempt_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="attack_progress")
    scenario = relationship("AttackScenario", back_populates="progress_entries")
