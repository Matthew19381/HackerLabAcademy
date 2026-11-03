from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from backend.database import Base


class ThmProgress(Base):
    """Manual TryHackMe tracker (plan C4, ACTION_PLAN F6.1). TryHackMe has no public progress API,
    so rooms and paths are entered by hand. No XP - done / not done only (decision 2 of 2026-08-09)."""

    __tablename__ = "thm_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    kind = Column(String, nullable=False, default="room")  # "room" | "path"
    name = Column(String, nullable=False)
    url = Column(String, nullable=True)
    category = Column(String, nullable=True)  # e.g. "Web", "Network", "Linux"
    done = Column(Boolean, nullable=False, default=False)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
