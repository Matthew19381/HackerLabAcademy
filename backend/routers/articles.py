import logging
from fastapi import APIRouter, Depends
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
