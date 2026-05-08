"""
Certificate model for HackerLabAcademy.
Certificates awarded when a user completes all topics in a category.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)  # "Fundamentals", "OWASP Top 10", "Advanced"
    topic_slugs = Column(Text, nullable=False)  # JSON array of topic slugs completed
    issued_at = Column(DateTime, default=datetime.utcnow)
    certificate_code = Column(String, unique=True, nullable=False)  # e.g., HLA-FUN-20260402-USER1
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="certificates")
