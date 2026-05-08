"""
Download endpoints: PDF lesson, MP3 audio, Anki deck.
"""
import json
import logging
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.topic import Topic
from backend.models.flashcard import Flashcard
from backend.services.pdf_service import generate_lesson_pdf
from backend.services.audio_service import generate_lesson_audio, generate_flashcard_audio
from backend.services.anki_service import export_flashcards_to_anki
from backend.services.lesson_bundle_service import create_lesson_bundle
from backend.models.flashcard import Flashcard

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/download", tags=["downloads"])


@router.get("/lesson/{slug}/pdf")
def download_lesson_pdf(slug: str, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic or not topic.theory_content:
        raise HTTPException(status_code=404, detail="Lekcja nie jest jeszcze wygenerowana")

    content = json.loads(topic.theory_content)
    try:
        path = generate_lesson_pdf(slug, content)
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        raise HTTPException(status_code=500, detail="Błąd generowania PDF")

    filename = f"cybertutor_{slug}.pdf"
    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/lesson/{slug}/audio")
async def download_lesson_audio(slug: str, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic or not topic.theory_content:
        raise HTTPException(status_code=404, detail="Lekcja nie jest jeszcze wygenerowana")

    content = json.loads(topic.theory_content)
    try:
        path = await generate_lesson_audio(slug, content)
    except Exception as e:
        logger.error(f"Audio generation error: {e}")
        raise HTTPException(status_code=500, detail="Błąd generowania audio")

    filename = f"cybertutor_{slug}.mp3"
    return FileResponse(
        path=path,
        media_type="audio/mpeg",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/flashcard/{card_id}/audio")
async def download_flashcard_audio(card_id: int, db: Session = Depends(get_db)):
    """Generate and serve audio for a single flashcard front."""
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    try:
        path = await generate_flashcard_audio(card.front, card.id)
    except Exception as e:
        logger.error(f"Flashcard audio generation error: {e}")
        raise HTTPException(status_code=500, detail="Błąd generowania audio")

    filename = f"flashcard_{card_id}.mp3"
    return FileResponse(
        path=path,
        media_type="audio/mpeg",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/flashcards/{user_id}/anki")
def download_anki(user_id: int, db: Session = Depends(get_db)):
    cards = db.query(Flashcard).filter(
        Flashcard.user_id == user_id,
        Flashcard.is_active == True
    ).all()

    if not cards:
        raise HTTPException(status_code=404, detail="Brak fiszek do eksportu")

    flashcard_dicts = [
        {"front": c.front, "back": c.back, "example": c.example or ""}
        for c in cards
    ]

    try:
        path = export_flashcards_to_anki(user_id, flashcard_dicts)
    except Exception as e:
        logger.error(f"Anki export error: {e}")
        raise HTTPException(status_code=500, detail="Błąd eksportu Anki")

    return FileResponse(
        path=path,
        media_type="application/octet-stream",
        filename="cybertutor_flashcards.apkg",
        headers={"Content-Disposition": 'attachment; filename="cybertutor_flashcards.apkg"'},
    )


@router.get("/lesson/{slug}/bundle")
async def download_lesson_bundle(slug: str, db: Session = Depends(get_db)):
    """Download ZIP bundle containing lesson PDF + audio MP3."""
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic or not topic.theory_content:
        raise HTTPException(status_code=404, detail="Lekcja nie istnieje")

    try:
        # Ensure PDF and audio exist
        content = json.loads(topic.theory_content)
        pdf_path = generate_lesson_pdf(slug, content)
        audio_path = await generate_lesson_audio(slug, content)
    except Exception as e:
        logger.error(f"Lesson bundle generation error: {e}")
        raise HTTPException(status_code=500, detail="Błąd generowania plików lekcji")

    try:
        zip_path = create_lesson_bundle(slug, pdf_path, audio_path)
    except FileNotFoundError as e:
        logger.error(f"Bundle missing files: {e}")
        raise HTTPException(status_code=500, detail="Brak wygenerowanych plików")
    except Exception as e:
        logger.error(f"Bundle creation error: {e}")
        raise HTTPException(status_code=500, detail="Błąd tworzenia archiwum")

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=f"hackerlab_{slug}_lesson.zip",
        headers={"Content-Disposition": f'attachment; filename="hackerlab_{slug}_lesson.zip"'},
    )
