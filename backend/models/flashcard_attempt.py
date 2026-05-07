from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class FlashcardAttempt(Base):
    __tablename__ = "flashcard_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    flashcard_id = Column(Integer, ForeignKey("flashcards.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-4 (again, hard, good, easy)
    reviewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    flashcard = relationship("Flashcard", back_populates="attempts")
