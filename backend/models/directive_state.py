from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from backend.database import Base


class DirectiveState(Base):
    """Latest hub directives per user (INT-3, ACTION_PLAN F5.3)."""

    __tablename__ = "directive_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    survival_mode = Column(Boolean, default=False)
    priority_topic = Column(String, nullable=True)
    quiet_hours_from = Column(String, nullable=True)
    quiet_hours_to = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
