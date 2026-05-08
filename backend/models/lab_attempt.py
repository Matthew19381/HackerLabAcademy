from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class LabAttempt(Base):
    __tablename__ = "lab_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_slug = Column(String, nullable=False)
    lab_type = Column(String, nullable=False)   # "dvwa_sqli", "dvwa_xss", etc.

    completed = Column(Boolean, default=False)
    flag_captured = Column(Boolean, default=False)
    score = Column(Float, default=0.0)          # 0-100

    # Writeup generated after completion
    writeup = Column(Text, nullable=True)       # JSON: {steps, tools, lesson}

    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    xp_awarded = Column(Integer, default=0)

    user = relationship("User", back_populates="lab_attempts")
