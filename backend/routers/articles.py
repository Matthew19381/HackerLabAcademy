import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("/")
def list_articles(page: int = 1, page_size: int = 10, topic_slug: str = None, db: Session = Depends(get_db)):
    from backend.models.article import Article
    query = db.query(Article)
    if topic_slug:
        query = query.filter(Article.topic_slug == topic_slug)
    total = query.count()
    articles = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [
            {
                "id": a.id,
                "title": a.title,
                "slug": a.slug,
                "topic_slug": a.topic_slug,
                "read_time_minutes": a.read_time_minutes,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in articles
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }

@router.get("/{slug}")
def get_article(slug: str, db: Session = Depends(get_db)):
    from backend.models.article import Article
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Article not found")
    return {
        "id": article.id,
        "title": article.title,
        "slug": article.slug,
        "topic_slug": article.topic_slug,
        "content_md": article.content_md,
        "read_time_minutes": article.read_time_minutes,
        "created_at": article.created_at.isoformat() if article.created_at else None,
        # correct_index stays on the server - graded in POST /{slug}/quiz/submit
        "quiz_questions": [
            {"id": q.id, "question": q.question, "options": json.loads(q.options)}
            for q in _quizzes(db, article.id)
        ],
    }


XP_PER_CORRECT = 5


class ReadRequest(BaseModel):
    user_id: int
    read_time_seconds: int | None = None


class QuizSubmitRequest(BaseModel):
    user_id: int
    answers: dict[int, int]  # question id -> chosen option index


def _quizzes(db: Session, article_id: int):
    from backend.models.article import ArticleQuiz

    return (
        db.query(ArticleQuiz)
        .filter(ArticleQuiz.article_id == article_id)
        .order_by(ArticleQuiz.question_order, ArticleQuiz.id)
        .all()
    )


def _article_or_404(db: Session, slug: str):
    from backend.models.article import Article

    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


# The frontend called both endpoints below, but they did not exist (404) until 2026-09-27.
@router.post("/{slug}/read")
def mark_read(slug: str, req: ReadRequest, db: Session = Depends(get_db)):
    from backend.models.article import ArticleRead

    article = _article_or_404(db, slug)
    row = (
        db.query(ArticleRead)
        .filter(ArticleRead.user_id == req.user_id, ArticleRead.article_id == article.id)
        .first()
    )
    if row:
        if req.read_time_seconds:
            row.read_time_seconds = (row.read_time_seconds or 0) + req.read_time_seconds
    else:
        row = ArticleRead(user_id=req.user_id, article_id=article.id, read_time_seconds=req.read_time_seconds)
        db.add(row)
    db.commit()
    return {"status": "read", "article_id": article.id, "read_time_seconds": row.read_time_seconds}


@router.post("/{slug}/quiz/submit")
def submit_quiz(slug: str, req: QuizSubmitRequest, db: Session = Depends(get_db)):
    from backend.models.article import ArticleQuizAttempt
    from backend.models.user import User

    article = _article_or_404(db, slug)
    questions = _quizzes(db, article.id)
    if not questions:
        raise HTTPException(status_code=404, detail="This article has no quiz")
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ids = [q.id for q in questions]
    first_time = (
        db.query(ArticleQuizAttempt)
        .filter(ArticleQuizAttempt.user_id == user.id, ArticleQuizAttempt.article_quiz_id.in_(ids))
        .count()
        == 0
    )
    results = []
    for q in questions:
        chosen = req.answers.get(q.id)
        correct = chosen is not None and chosen == q.correct_index
        if chosen is not None:
            db.add(ArticleQuizAttempt(user_id=user.id, article_quiz_id=q.id, user_answer=chosen, is_correct=correct))
        results.append({"id": q.id, "correct": correct, "correct_index": q.correct_index,
                        "explanation": q.explanation})
    n_correct = sum(r["correct"] for r in results)
    xp = n_correct * XP_PER_CORRECT if first_time else 0  # XP only for the first attempt
    user.total_xp = (user.total_xp or 0) + xp
    db.commit()
    return {
        "correct": n_correct,
        "total": len(questions),
        "score_percent": round(n_correct / len(questions) * 100),
        "xp_awarded": xp,
        "results": results,
    }


def seed_sample_articles(db: Session):
    from backend.models.article import Article
    existing_slugs = {a.slug for a in db.query(Article).all()}
    sample_articles = [
        {
            "slug": "sql-injection-deep-dive",
            "title": "SQL Injection - Deep Dive",
            "topic_slug": "sql-injection",
            "content_md": "# SQL Injection\n\nDetailed article about SQL injection...",
            "read_time_minutes": 8,
        },
        {
            "slug": "idor-explained",
            "title": "IDOR - Insecure Direct Object Reference",
            "topic_slug": "idor",
            "content_md": "# IDOR\n\nDetailed article about IDOR...",
            "read_time_minutes": 6,
        },
        {
            "slug": "file-upload-security",
            "title": "File Upload Vulnerabilities",
            "topic_slug": "file-upload",
            "content_md": "# File Upload\n\nDetailed article about file upload attacks...",
            "read_time_minutes": 7,
        },
        {
            "slug": "command-injection-basics",
            "title": "Command Injection Basics",
            "topic_slug": "command-injection",
            "content_md": "# Command Injection\n\nDetailed article about command injection...",
            "read_time_minutes": 5,
        },
        {
            "slug": "privilege-escalation-linux",
            "title": "Linux Privilege Escalation",
            "topic_slug": "privilege-escalation",
            "content_md": "# Privilege Escalation\n\nDetailed article about Linux privilege escalation...",
            "read_time_minutes": 10,
        },
        {
            "slug": "java-deserialization",
            "title": "Java Deserialization Attacks",
            "topic_slug": "java-security",
            "content_md": "# Java Deserialization\n\nDetailed article about Java deserialization...",
            "read_time_minutes": 12,
        },
        {
            "slug": "api-security-basics",
            "title": "API Security Fundamentals",
            "topic_slug": "api-security",
            "content_md": "# API Security\n\nDetailed article about API security...",
            "read_time_minutes": 9,
        },
    ]
    added = 0
    for data in sample_articles:
        if data["slug"] not in existing_slugs:
            article = Article(
                slug=data["slug"],
                title=data["title"],
                topic_slug=data["topic_slug"],
                content_md=data["content_md"],
                read_time_minutes=data["read_time_minutes"],
            )
            db.add(article)
            added += 1
    if added:
        db.commit()
        logger.info(f"Seeded {added} sample articles")
