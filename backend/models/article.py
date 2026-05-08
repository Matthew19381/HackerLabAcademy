from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    content_md = Column(Text, nullable=False)  # Markdown content
    read_time_minutes = Column(Integer, default=15)
    difficulty = Column(Integer, default=2)  # 1-5
    topic_slug = Column(String, nullable=True)  # link to topic
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reads = relationship("ArticleRead", back_populates="article", cascade="all, delete-orphan")
    quizzes = relationship("ArticleQuiz", back_populates="article", cascade="all, delete-orphan")


class ArticleRead(Base):
    __tablename__ = "article_reads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    read_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_time_seconds = Column(Integer, nullable=True)  # actual time spent
    is_active = Column(Boolean, default=True)

    # Relationships
    article = relationship("Article", back_populates="reads")


class ArticleQuiz(Base):
    __tablename__ = "article_quizzes"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # JSON list
    correct_index = Column(Integer, nullable=False)  # 0-3
    explanation = Column(Text, nullable=True)
    question_order = Column(Integer, default=0)

    # Relationships
    article = relationship("Article", back_populates="quizzes")


class ArticleQuizAttempt(Base):
    __tablename__ = "article_quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    article_quiz_id = Column(Integer, ForeignKey("article_quizzes.id"), nullable=False)
    user_answer = Column(Integer, nullable=False)  # 0-3
    is_correct = Column(Boolean, nullable=False)
    attempted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True)
