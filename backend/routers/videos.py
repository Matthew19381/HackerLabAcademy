import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.youtube_video import YouTubeVideo

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/videos", tags=["videos"])


@router.get("/")
def get_videos(
    topic_slug: str = None,
    category: str = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List YouTube videos, optionally filtered by topic or category."""
    from backend.models.topic import Topic
    query = db.query(YouTubeVideo).filter(YouTubeVideo.is_active == True)

    if topic_slug:
        # Verify topic exists (optional)
        topic = db.query(Topic).filter(Topic.slug == topic_slug).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        query = query.filter(YouTubeVideo.topic_slug == topic_slug)
    if category:
        query = query.filter(YouTubeVideo.category == category)

    videos = query.order_by(YouTubeVideo.created_at.desc()).limit(limit).all()

    return [
        {
            "id": v.id,
            "video_id": v.video_id,
            "title": v.title,
            "description": v.description,
            "channel": v.channel,
            "topic_slug": v.topic_slug,
            "category": v.category,
            "duration": v.duration,
            "published_at": v.published_at.isoformat() if v.published_at else None,
            "url": f"https://www.youtube.com/embed/{v.video_id}",
        }
        for v in videos
    ]


@router.get("/topics")
def get_videos_by_topic(db: Session = Depends(get_db)):
    """Return mapping: topic_slug -> list of videos."""
    from backend.models.topic import Topic
    topics = db.query(Topic).all()
    result = {}
    for t in topics:
        videos = db.query(YouTubeVideo).filter(
            YouTubeVideo.topic_slug == t.slug,
            YouTubeVideo.is_active == True
        ).all()
        result[t.slug] = [
            {
                "video_id": v.video_id,
                "title": v.title,
                "category": v.category,
                "url": f"https://www.youtube.com/embed/{v.video_id}",
            }
            for v in videos
        ]
    return result


def seed_sample_videos(db: Session):
    """Seed database with sample educational YouTube videos per topic."""
    samples = [
        # SQL Injection
        {"topic_slug": "sql-injection", "video_id": "M_aVTz77Da4", "title": "SQL Injection Explained", "channel": "NetworkChuck", "category": "tutorial", "description": "Complete beginner guide to SQL injection."},
        {"topic_slug": "sql-injection", "video_id": "9Q8GmLk用", "title": "SQL Injection - How to prevent", "channel": "The Cyber Mentor", "category": "defense", "description": "How to protect your apps from SQLi."},
        # XSS
        {"topic_slug": "xss", "video_id": "5XNrXR4UXDM", "title": "Cross-Site Scripting (XSS) Explained", "channel": "Frasercorbin", "category": "tutorial", "description": "XSS attack explained with examples."},
        {"topic_slug": "xss", "video_id": "Hpx_hPPdnQ", "title": "XSS Attack Demo", "channel": " bug bounty", "category": "demo", "description": "Live XSS exploitation demonstration."},
        # CSRF
        {"topic_slug": "csrf", "video_id": "3pWmyU2VoXo", "title": "CSRF (Cross-Site Request Forgery)", "channel": "David Bombal", "category": "tutorial", "description": "What is CSRF and how it works."},
        # IDOR
        {"topic_slug": "idor", "video_id": "qVQR abbreviation?", "title": "IDOR Vulnerabilities", "channel": "InsiderPhD", "category": "demo", "description": "Finding and exploiting IDOR."},
        # File Upload
        {"topic_slug": "file-upload", "video_id": "5kN0euTHbBg", "title": "File Upload Vulnerabilities", "channel": "LiveOverflow", "category": "tutorial", "description": "Uploading malicious files to webshell."},
        # Command Injection
        {"topic_slug": "command-injection", "video_id": "I7KzHYqY3do", "title": "Command Injection Explained", "channel": "The Cyber Mentor", "category": "tutorial", "description": "OS command injection in web apps."},
        # Blind SQLi
        {"topic_slug": "blind-sqli", "video_id": "yhuNnaf2JQ", "title": "Blind SQL Injection", "channel": "NahamSec", "category": "tutorial", "description": "Time-based and boolean-based blind SQLi."},
        # Stored XSS
        {"topic_slug": "stored-xss", "video_id": "Rw_kJqbKF9g", "title": "Stored XSS Attack", "channel": "HackerOne", "category": "demo", "description": "Stored XSS in the wild."},
        # File Inclusion
        {"topic_slug": "file-inclusion", "video_id": "3nG__z8w4zM", "title": "LFI/RFI Vulnerabilities", "channel": "Cybersecurity", "category": "tutorial", "description": "Local and Remote File Inclusion."},
        # Additional videos
        {"topic_slug": "sql-injection", "video_id": "0lHJsgVsrGg", "title": "SQL Injection - UNION Based", "channel": "The Cyber Mentor", "category": "tutorial", "description": "Advanced SQLi with UNION attacks."},
        {"topic_slug": "xss", "video_id": "bEZo0VazT08", "title": "XSS - DOM Based Attacks", "channel": "PwnFunction", "category": "tutorial", "description": "DOM-based XSS explained."},
        {"topic_slug": "csrf", "video_id": "1nYz_aVURnc", "title": "CSRF Protection - SameSite Cookies", "channel": "Web Security", "category": "defense", "description": "How SameSite cookies protect against CSRF."},
        {"topic_slug": "idor", "video_id": "XEcI5kwzFbw", "title": "IDOR - How to Find and Exploit", "channel": "NahamSec", "category": "demo", "description": "Real-world IDOR examples."},
        {"topic_slug": "auth-bypass", "video_id": "2eQv2yDO0EA", "title": "Broken Authentication - OWASP", "channel": "OWASP", "category": "tutorial", "description": "Password attacks and session management."},
        {"topic_slug": "blind-sqli", "video_id": "8ZcOJIherPo", "title": "Blind SQLi - Time Based", "channel": "SecurityId", "category": "tutorial", "description": "Using sleep() and benchmarking."},
        {"topic_slug": "stored-xss", "video_id": "zSLdDKirx1Y", "title": "Stored XSS - Cookie Stealing", "channel": "LiveOverflow", "category": "demo", "description": "Stealing session cookies via stored XSS."},
        {"topic_slug": "command-injection", "video_id": "kEeT8x_Cr0", "title": "Command Inj - Netcat Reverse Shell", "channel": "Hackersploit", "category": "demo", "description": "Getting a reverse shell via command injection."},
    ]

    added = 0
    for vdata in samples:
        existing = db.query(YouTubeVideo).filter(YouTubeVideo.video_id == vdata["video_id"]).first()
        if not existing:
            video = YouTubeVideo(
                video_id=vdata["video_id"],
                title=vdata["title"],
                description=vdata.get("description"),
                channel=vdata.get("channel"),
                topic_slug=vdata["topic_slug"],
                category=vdata.get("category", "tutorial"),
                is_active=True,
            )
            db.add(video)
            added += 1
    if added:
        db.commit()
        logger.info(f"Seeded {added} sample YouTube videos")
