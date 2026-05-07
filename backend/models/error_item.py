from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class ErrorItem(Base):
    __tablename__ = "error_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_slug = Column(String, nullable=True)

    question = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=False)
    error_type = Column(String, default="unknown")  # "no_knowledge" | "misunderstanding" | "guessing"
    explanation = Column(Text, nullable=True)       # AI explanation of why it was wrong

    # Fix loop tracking: must answer correctly 3 times in a row to clear
    correct_streak = Column(Integer, default=0)
    resolved = Column(Boolean, default=False)
    next_review = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="error_items")
