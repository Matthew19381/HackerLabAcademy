from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Cve(Base):
    __tablename__ = "cves"

    id = Column(Integer, primary_key=True, index=True)
    cve_id = Column(String, unique=True, nullable=False)  # e.g. "CVE-2021-44228"
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String, nullable=False)  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    published_date = Column(DateTime, nullable=False)
    affected_products = Column(Text, nullable=True)  # JSON list or comma-separated
    references = Column(Text, nullable=True)  # JSON list of URLs
    topic_slug = Column(String, nullable=True)  # link to HackerLab topic (optional)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    flashcards = relationship("Flashcard", back_populates="cve", cascade="all, delete-orphan")
