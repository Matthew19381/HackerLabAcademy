from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_type = Column(String, nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    notified = Column(Boolean, default=False)

    user = relationship("User", back_populates="achievements")
