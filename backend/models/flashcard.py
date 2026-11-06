from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.database import Base


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_slug = Column(String, nullable=True)
    cve_id = Column(Integer, ForeignKey("cves.id"), nullable=True)

    front = Column(Text, nullable=False)    # question / term
    back = Column(Text, nullable=False)     # answer / definition
    example = Column(Text, nullable=True)  # code/payload example

    # SM-2 fields (kept for backward compatibility during transition)
    ease_factor = Column(Float, default=2.5)
    interval_days = Column(Integer, default=1)
    repetitions = Column(Integer, default=0)
    next_review_date = Column(DateTime, default=datetime.utcnow)

    # FSRS fields
    stability = Column(Float, nullable=True)        # Core parameter for future scheduling
    difficulty = Column(Float, nullable=True)       # Core parameter for future scheduling
    state = Column(Integer, default=1)              # FSRS State: 1=Learning, 2=Review, 3=Relearning
    step = Column(Integer, nullable=True)           # Current step in learning/relearning
    last_review = Column(DateTime, nullable=True)   # Last review timestamp
    card_id = Column(BigInteger, nullable=True)     # FSRS card identifier (epoch ms)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="flashcards")
    cve = relationship("Cve", back_populates="flashcards")
    attempts = relationship("FlashcardAttempt", back_populates="flashcard")