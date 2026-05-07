"""
Vocabulary Engine — technical cybersecurity glossary with PL↔EN.
Resources Engine — curated learning resources per topic.
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.topic import Topic
from services.ai_service import generate_json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/vocabulary", tags=["vocabulary"])


@router.get("/topic/{slug}")
async def get_topic_vocabulary(slug: str, db: Session = Depends(get_db)):
    """Get full vocabulary for a topic — auto-extracted from theory content."""
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    if not topic.theory_content:
        raise HTTPException(status_code=400, detail="Lekcja nie jest jeszcze wygenerowana")

    content = json.loads(topic.theory_content)
    concepts = content.get("key_concepts", [])
    flashcards = content.get("flashcards", [])

    # Build vocabulary from key concepts + flashcards
    vocab = []
    seen = set()
    for c in concepts:
        term = c.get("term", "")
        if term and term not in seen:
            seen.add(term)
            vocab.append({
                "term_en": term,
                "term_pl": term,
                "definition": c.get("definition", ""),
                "example": None,
                "category": topic.category,
            })

    for fc in flashcards[:10]:
        front = fc.get("front", "")
        if front and front not in seen:
            seen.add(front)
            vocab.append({
                "term_en": front,
                "term_pl": front,
                "definition": fc.get("back", ""),
                "example": fc.get("example"),
                "category": topic.category,
            })

    return {"topic": topic.name, "vocabulary": vocab}


@router.get("/topic/{slug}/resources")
async def get_topic_resources(slug: str, db: Session = Depends(get_db)):
    """Get curated learning resources for a topic (AI-generated, cached)."""
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Cache resources in a JSON column — reuse theory_content pattern via separate attribute
    # For simplicity, we generate on demand (no cache for resources)
    prompt = f"""Jesteś ekspertem cyberbezpieczeństwa. Podaj najlepsze bezpłatne zasoby edukacyjne dla POCZĄTKUJĄCEGO chcącego nauczyć się: {topic.name}

Podaj KONKRETNE zasoby (prawdziwe nazwy kanałów, stron, narzędzi).

Zwróć JSON:
{{
    "youtube_channels": [
        {{"name": "Nazwa kanału", "url_hint": "youtube.com/...", "why": "Dlaczego polecany"}}
    ],
    "websites": [
        {{"name": "Nazwa strony", "url_hint": "adres.com", "why": "Do czego służy"}}
    ],
    "practice_platforms": [
        {{"name": "Platforma", "url_hint": "adres.com", "why": "Jak pomaga w nauce"}}
    ],
    "tools": [
        {{"name": "Narzędzie", "description": "Do czego służy w kontekście {topic.name}"}}
    ],
    "tip": "Jedna konkretna rada jak najefektywniej nauczyć się tego tematu"
}}"""

    try:
        resources = await generate_json(prompt)
    except Exception as e:
        logger.error(f"Resources generation failed for {slug}: {e}")
        resources = {
            "youtube_channels": [],
            "websites": [{"name": "OWASP", "url_hint": "owasp.org", "why": "Oficjalna dokumentacja bezpieczeństwa webowego"}],
            "practice_platforms": [{"name": "DVWA", "url_hint": "localhost:8080", "why": "Lokalne środowisko do ćwiczeń"}],
            "tools": [],
            "tip": f"Najlepszy sposób nauki {topic.name} to praktyka — uruchom lab i próbuj."
        }

    return {"topic": topic.name, "resources": resources}
