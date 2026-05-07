import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.user import User
from models.flashcard import Flashcard
from models.flashcard_attempt import FlashcardAttempt
from services.sm2_service import sm2_update
from services.ai_service import generate_json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


@router.get("/due/{user_id}")
def get_due_flashcards(user_id: int, db: Session = Depends(get_db)):
    """Return flashcards due for review today."""
    now = datetime.utcnow()
    cards = db.query(Flashcard).filter(
        Flashcard.user_id == user_id,
        Flashcard.is_active == True,
        Flashcard.next_review_date <= now
    ).all()

    return [
        {
            "id": c.id,
            "front": c.front,
            "back": c.back,
            "example": c.example,
            "topic_slug": c.topic_slug,
            "interval_days": c.interval_days,
            "repetitions": c.repetitions,
        }
        for c in cards
    ]


@router.get("/all/{user_id}")
def get_all_flashcards(user_id: int, db: Session = Depends(get_db)):
    cards = db.query(Flashcard).filter(
        Flashcard.user_id == user_id,
        Flashcard.is_active == True
    ).order_by(Flashcard.next_review_date).all()

    return [
        {
            "id": c.id,
            "front": c.front,
            "back": c.back,
            "example": c.example,
            "topic_slug": c.topic_slug,
            "next_review_date": c.next_review_date.isoformat(),
            "interval_days": c.interval_days,
        }
        for c in cards
    ]


class ReviewRequest(BaseModel):
    rating: int  # 1 (didn't know) | 2 (hard) | 3 (good) | 4 (easy)


@router.post("/{card_id}/review")
def review_flashcard(card_id: int, req: ReviewRequest, db: Session = Depends(get_db)):
    """Apply SM-2 update after review."""
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    if req.rating not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="Rating must be 1-4")

    updated = sm2_update(card.ease_factor, card.interval_days, card.repetitions, req.rating)
    card.ease_factor = updated["ease_factor"]
    card.interval_days = updated["interval_days"]
    card.repetitions = updated["repetitions"]
    card.next_review_date = updated["next_review_date"]
    db.commit()

    # Log the review attempt
    attempt = FlashcardAttempt(
        user_id=card.user_id,
        flashcard_id=card.id,
        rating=req.rating,
        reviewed_at=datetime.utcnow(),
        is_active=True
    )
    db.add(attempt)
    db.commit()

    return {
        "next_review_date": card.next_review_date.isoformat(),
        "interval_days": card.interval_days,
        "ease_factor": card.ease_factor,
    }


@router.delete("/{card_id}")
def delete_flashcard(card_id: int, db: Session = Depends(get_db)):
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    card.is_active = False
    # Also deactivate attempts for this card
    db.query(FlashcardAttempt).filter(
        FlashcardAttempt.flashcard_id == card_id
    ).update({"is_active": False})
    db.commit()
    return {"success": True}


class QuickCreateRequest(BaseModel):
    user_id: int
    term: str


@router.post("/quick-create")
async def quick_create_flashcard(req: QuickCreateRequest, db: Session = Depends(get_db)):
    """Create a flashcard with AI-generated definition and example."""
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    prompt = f"""Jesteś ekspertem cyberbezpieczeństwa. Stwórz fiszkę edukacyjną.

Termin (front): {req.term}

Zwróć JSON:
{{
  "back": "Definicja po polsku, zrozumiała dla początkującego (1-2 zdania)",
  "example": "Konkretny przykład kodu/payloadu/scenariusza (może być null jeśli nie dotyczy)"
}}

Uwagi:
- Definicja powinna być klarowna i krótka.
- Przykład powinien być realistyczny i związany z bezpieczeństwem.
- Jeśli termin nie jest związany z cyberbezpieczeństwem, nadaj ogólną definicję edukacyjną.
"""

    try:
        result = await generate_json(prompt)
        back = result.get("back", "")
        example = result.get("example")
    except Exception as e:
        logger.error(f"Gemini flashcard generation failed: {e}")
        raise HTTPException(status_code=503, detail="Nie udało się wygenerować definicji")

    card = Flashcard(
        user_id=req.user_id,
        front=req.term,
        back=back,
        example=example,
        ease_factor=2.5,
        interval_days=1,
        repetitions=0,
        next_review_date=datetime.utcnow(),
        is_active=True,
    )
    db.add(card)
    db.commit()
    db.refresh(card)

    return {
        "id": card.id,
        "front": card.front,
        "back": card.back,
        "example": card.example,
        "next_review_date": card.next_review_date.isoformat(),
    }
