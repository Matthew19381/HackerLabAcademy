import logging
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend.models.user import User
from backend.models.flashcard import Flashcard
from backend.models.flashcard_attempt import FlashcardAttempt
from backend.services.fsrs_service import fsrs_update, initialize_new_card
from backend.services.ai_service import generate_json
from backend.services.hub_publisher import flush_in_background, queue_event

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/flashcards", tags=["flashcards"])


@router.get("/due/{user_id}")
def get_due_flashcards(user_id: int, db: Session = Depends(get_db)):
    """Return flashcards due for review today."""
    now = datetime.utcnow()
    cards = db.query(Flashcard).filter(
        Flashcard.user_id == user_id,
        Flashcard.is_active.is_(True),
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
            "ease_factor": c.ease_factor,
            # FSRS fields (optional for frontend)
            "stability": c.stability,
            "difficulty": c.difficulty,
            "state": c.state,
            "step": c.step,
            "last_review": c.last_review.isoformat() if c.last_review else None,
        }
        for c in cards
    ]


@router.get("/all/{user_id}")
def get_all_flashcards(user_id: int, db: Session = Depends(get_db)):
    cards = db.query(Flashcard).filter(
        Flashcard.user_id == user_id,
        Flashcard.is_active.is_(True)
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
            "repetitions": c.repetitions,
            "ease_factor": c.ease_factor,
            # FSRS fields
            "stability": c.stability,
            "difficulty": c.difficulty,
            "state": c.state,
            "step": c.step,
            "last_review": c.last_review.isoformat() if c.last_review else None,
        }
        for c in cards
    ]


class ReviewRequest(BaseModel):
    rating: int  # 1 (didn't know) | 2 (hard) | 3 (good) | 4 (easy)


@router.post("/{card_id}/review")
def review_flashcard(
    card_id: int, req: ReviewRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """Apply FSRS update after review."""
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    if req.rating not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="Rating must be 1-4")

    # Prepare current state for FSRS update
    card_data = {
        'stability': card.stability,
        'difficulty': card.difficulty,
        'due': card.next_review_date,
        'last_review': card.last_review,
        'state': card.state,
        'step': card.step,
        'card_id': card.card_id if hasattr(card, 'card_id') else None,
        'interval_days': card.interval_days,  # for fallback
        'repetitions': card.repetitions,
        'ease_factor': card.ease_factor
    }

    # Apply FSRS update
    updated = fsrs_update(card_data, req.rating)

    # Update the card with new values
    card.stability = updated['stability']
    card.difficulty = updated['difficulty']
    card.next_review_date = updated['due']
    card.last_review = updated['last_review']
    card.state = updated['state']
    card.step = updated['step']

    # Keep SM-2 fields updated for backward compatibility (approximate)
    # We can compute approximate SM-2 values from FSRS state or keep them as is.
    # For now, we'll update them based on the rating as in the original SM-2, but note: this is not accurate.
    # Alternatively, we can leave the SM-2 fields as they are and only use FSRS for scheduling.
    # Since we are keeping both, let's update the SM-2 fields in a way that is consistent with the rating.
    # We'll use the same SM-2 update function for the SM-2 fields to keep them updated (even though we don't use them for scheduling).
    from backend.services.sm2_service import sm2_update
    sm2_updated = sm2_update(card.ease_factor, card.interval_days, card.repetitions, req.rating)
    card.ease_factor = sm2_updated["ease_factor"]
    card.interval_days = sm2_updated["interval_days"]
    card.repetitions = sm2_updated["repetitions"]
    # Note: next_review_date is already set by FSRS, so we don't overwrite it with SM-2.

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
    queue_event(db, "flashcard_reviewed", card.user_id, {"flashcard_id": card.id, "rating": req.rating,
                                                          "topic_slug": card.topic_slug})
    db.commit()
    background_tasks.add_task(flush_in_background)

    return {
        "next_review_date": card.next_review_date.isoformat(),
        "interval_days": card.interval_days,
        "repetitions": card.repetitions,
        "ease_factor": card.ease_factor,
        # FSRS fields
        "stability": card.stability,
        "difficulty": card.difficulty,
        "state": card.state,
        "step": card.step,
        "last_review": card.last_review.isoformat() if card.last_review else None,
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

    # Initialize a new card with FSRS state
    fsrs_initial = initialize_new_card()

    card = Flashcard(
        user_id=req.user_id,
        front=req.term,
        back=back,
        example=example,
        # SM-2 fields (initial values)
        ease_factor=2.5,
        interval_days=1,
        repetitions=0,
        next_review_date=fsrs_initial['due'],
        # FSRS fields
        stability=fsrs_initial['stability'],
        difficulty=fsrs_initial['difficulty'],
        state=fsrs_initial['state'],
        step=fsrs_initial['step'],
        last_review=fsrs_initial['last_review'],
        card_id=fsrs_initial.get('card_id'),  # Note: we don't have card_id in initialize_new_card, but we can set it to None or generate
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
        "interval_days": card.interval_days,
        "repetitions": card.repetitions,
        "ease_factor": card.ease_factor,
        # FSRS fields
        "stability": card.stability,
        "difficulty": card.difficulty,
        "state": card.state,
        "step": card.step,
        "last_review": card.last_review.isoformat() if card.last_review else None,
    }