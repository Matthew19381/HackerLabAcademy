import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base, SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOPICS_SEED = [
    # ── Level 1: Fundamentals ──────────────────────────────────────────────
    {"slug": "http-basics", "name": "Podstawy HTTP", "category": "Fundamentals",
     "difficulty": 1, "prerequisites": [],
     "description": "Jak działają żądania i odpowiedzi HTTP — fundament web security.",
     "lab_type": None, "order_index": 1},
    {"slug": "html-js-basics", "name": "HTML i JavaScript", "category": "Fundamentals",
     "difficulty": 1, "prerequisites": ["http-basics"],
     "description": "DOM, formularze, skrypty — co atakujemy w XSS.",
     "lab_type": None, "order_index": 2},
    {"slug": "sql-basics", "name": "Podstawy SQL", "category": "Fundamentals",
     "difficulty": 1, "prerequisites": ["http-basics"],
     "description": "SELECT, WHERE, UNION — co musisz znać przed SQL injection.",
     "lab_type": None, "order_index": 3},
    # ── Level 2: OWASP Core ────────────────────────────────────────────────
    {"slug": "sql-injection", "name": "SQL Injection", "category": "OWASP Top 10",
     "difficulty": 2, "prerequisites": ["http-basics", "sql-basics"],
     "description": "Wstrzykiwanie kodu SQL do zapytań bazy danych — jedna z najstarszych i najgroźniejszych podatności.",
     "lab_type": "dvwa_sqli", "order_index": 10},
    {"slug": "xss", "name": "Cross-Site Scripting (XSS)", "category": "OWASP Top 10",
     "difficulty": 2, "prerequisites": ["http-basics", "html-js-basics"],
     "description": "Wstrzykiwanie kodu JavaScript do stron — kradzież sesji, phishing.",
     "lab_type": "dvwa_xss_reflected", "order_index": 11},
    {"slug": "auth-bypass", "name": "Broken Authentication", "category": "OWASP Top 10",
     "difficulty": 2, "prerequisites": ["http-basics"],
     "description": "Słabe uwierzytelnianie — brute force, domyślne hasła, słabe sesje.",
     "lab_type": "dvwa_brute_force", "order_index": 12},
    # ── Level 3: Intermediate ──────────────────────────────────────────────
    {"slug": "csrf", "name": "CSRF (Cross-Site Request Forgery)", "category": "OWASP Top 10",
     "difficulty": 3, "prerequisites": ["xss", "auth-bypass"],
     "description": "Zmuszanie użytkownika do wykonania akcji bez jego wiedzy.",
     "lab_type": "dvwa_csrf", "order_index": 20},
    {"slug": "idor", "name": "IDOR (Insecure Direct Object Reference)", "category": "OWASP Top 10",
     "difficulty": 3, "prerequisites": ["auth-bypass"],
     "description": "Dostęp do zasobów innych użytkowników przez manipulację ID.",
     "lab_type": "dvwa_idor", "order_index": 21},
    {"slug": "file-upload", "name": "File Upload Vulnerabilities", "category": "OWASP Top 10",
     "difficulty": 3, "prerequisites": ["http-basics"],
     "description": "Przesyłanie złośliwych plików — web shells, RCE.",
     "lab_type": "dvwa_file_upload", "order_index": 22},
    {"slug": "command-injection", "name": "Command Injection", "category": "OWASP Top 10",
     "difficulty": 3, "prerequisites": ["http-basics", "sql-basics"],
     "description": "Wstrzykiwanie komend systemowych — przejęcie serwera.",
     "lab_type": "dvwa_command_injection", "order_index": 23},
    # ── Level 4: Advanced ──────────────────────────────────────────────────
    {"slug": "blind-sqli", "name": "Blind SQL Injection", "category": "Advanced",
     "difficulty": 4, "prerequisites": ["sql-injection"],
     "description": "SQLi bez widocznych wyników — time-based i boolean-based.",
     "lab_type": "dvwa_sqli_blind", "order_index": 30},
    {"slug": "stored-xss", "name": "Stored XSS", "category": "Advanced",
     "difficulty": 4, "prerequisites": ["xss"],
     "description": "XSS zapisany w bazie danych — trwalszy i groźniejszy.",
     "lab_type": "dvwa_xss_stored", "order_index": 31},
    {"slug": "file-inclusion", "name": "File Inclusion (LFI/RFI)", "category": "Advanced",
     "difficulty": 4, "prerequisites": ["file-upload"],
     "description": "Dołączanie lokalnych i zdalnych plików — LFI i RFI.",
     "lab_type": "dvwa_file_inclusion", "order_index": 32},
    # ── Level 5: Expert ──────────────────────────────────────────────
    {"slug": "java-security", "name": "Java Security", "category": "Expert",
     "difficulty": 5, "prerequisites": ["blind-sqli", "stored-xss"],
     "description": "Podatności w aplikacjach Java: deserializacja, SpEL, SSTI, JNDI.",
     "lab_type": None, "order_index": 40},
    {"slug": "api-security", "name": "API Security", "category": "Expert",
     "difficulty": 5, "prerequisites": ["blind-sqli", "stored-xss"],
     "description": "Ataki na REST/GraphQL: BOLA, mass assignment, improper rate limiting.",
     "lab_type": None, "order_index": 41},
    {"slug": "crypto-basics", "name": "Cryptography Basics", "category": "Expert",
     "difficulty": 5, "prerequisites": ["http-basics"],
     "description": "Słabe generatory liczb, padding attacks, słabe hashowanie, JWT attacks.",
     "lab_type": None, "order_index": 42},
    {"slug": "privilege-escalation", "name": "Privilege Escalation", "category": "Expert",
     "difficulty": 5, "prerequisites": ["command-injection"],
     "description": "Linux/Windows escalation: SUID, cron, sudo, kernel exploits.",
     "lab_type": None, "order_index": 43},
]


def seed_topics(db):
    import json
    from backend.models.topic import Topic
    existing_slugs = {t.slug for t in db.query(Topic).all()}
    added = 0
    for t in TOPICS_SEED:
        if t["slug"] not in existing_slugs:
            topic = Topic(
                slug=t["slug"],
                name=t["name"],
                category=t["category"],
                difficulty=t["difficulty"],
                description=t["description"],
                prerequisites=json.dumps(t["prerequisites"]),
                lab_type=t.get("lab_type"),
                order_index=t["order_index"],
            )
            db.add(topic)
            added += 1
    if added:
        db.commit()
        logger.info(f"Seeded {added} topics")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import all models so create_all picks them up
    from .models import user, topic, flashcard, flashcard_attempt, error_item, lab_attempt, achievement, exercise, conversation, cve, youtube_video, ctf, attack_scenario, defense, certificate, article  # noqa

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    for d in ["audio", "exports"]:
        os.makedirs(d, exist_ok=True)

    db = SessionLocal()
    try:
        seed_topics(db)
        from backend.routers.cves import seed_sample_cves
        seed_sample_cves(db)
        from backend.routers.videos import seed_sample_videos
        seed_sample_videos(db)
        from backend.routers.ctf import seed_sample_challenges
        seed_sample_challenges(db)
        from backend.routers.defense import seed_sample_defense_challenges
        seed_sample_defense_challenges(db)
        from backend.routers.articles import seed_sample_articles
        seed_sample_articles(db)
        from backend.routers.writeups import seed_sample_templates
        seed_sample_templates(db)
    finally:
        db.close()

    # Start CVE auto-fetch scheduler if enabled
    if os.getenv("CVE_SCHEDULED_FETCH", "false").lower() == "true":
        from .services.cve_service import start_scheduler
        start_scheduler(interval_hours=24)
        logger.info("CVE auto-scheduler started (every 24h)")

    yield
    logger.info("Shutting down")


app = FastAPI(title="HackerLabAcademy API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "http://localhost", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import backend.routers.placement as placement
import backend.routers.topics as topics
import backend.routers.labs as labs
import backend.routers.flashcards as flashcards
import backend.routers.mentor as mentor
import backend.routers.errors as errors
import backend.routers.stats as stats
import backend.routers.brain as brain
import backend.routers.downloads as downloads
import backend.routers.vocabulary as vocabulary
import backend.routers.exercises as exercises
import backend.routers.conversation as conversation
import backend.routers.cves as cves
import backend.routers.videos as videos
import backend.routers.ctf as ctf
import backend.routers.defense as defense
import backend.routers.attack as attack
import backend.routers.certificates as certificates
import backend.routers.daily as daily
import backend.routers.articles as articles
import backend.routers.writeups as writeups

app.include_router(placement.router, prefix="/api/v1")
app.include_router(topics.router, prefix="/api/v1")
app.include_router(labs.router, prefix="/api/v1")
app.include_router(flashcards.router, prefix="/api/v1")
app.include_router(mentor.router, prefix="/api/v1")
app.include_router(errors.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
app.include_router(brain.router, prefix="/api/v1")
app.include_router(downloads.router, prefix="/api/v1")
app.include_router(vocabulary.router, prefix="/api/v1")
app.include_router(exercises.router, prefix="/api/v1")
app.include_router(conversation.router, prefix="/api/v1")
app.include_router(cves.router, prefix="/api/v1")
app.include_router(videos.router, prefix="/api/v1")
app.include_router(ctf.router, prefix="/api/v1")
app.include_router(defense.router, prefix="/api/v1")
app.include_router(attack.router, prefix="/api/v1")
app.include_router(certificates.router, prefix="/api/v1")
app.include_router(daily.router, prefix="/api/v1")
app.include_router(articles.router, prefix="/api/v1")
app.include_router(writeups.router, prefix="/api/v1")


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "HackerLabAcademy"}
