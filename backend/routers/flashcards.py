import logging
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.flashcard import Flashcard
from backend.models.flashcard_attempt import FlashcardAttempt
from backend.models.user import User
from backend.services.ai_service import generate_json
from backend.services.fsrs_service import fsrs_update, initialize_new_card
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

    # FSRS is the only scheduler (plan B4, 2026-11-03). The legacy SM-2 columns are kept in the table
    # and in the response, but derived from the FSRS result instead of a second, competing algorithm.
    card.interval_days = max(0, (card.next_review_date - card.last_review).days) if card.last_review else 0
    card.repetitions = (card.repetitions or 0) + 1

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


def _new_card(user_id: int, front: str, back: str, example: str | None = None,
              topic_slug: str | None = None) -> Flashcard:
    """A new card in the FSRS initial state (legacy SM-2 columns at their defaults)."""
    fsrs_initial = initialize_new_card()
    return Flashcard(
        user_id=user_id,
        topic_slug=topic_slug,
        front=front,
        back=back,
        example=example,
        ease_factor=2.5,
        interval_days=1,
        repetitions=0,
        next_review_date=fsrs_initial["due"],
        stability=fsrs_initial["stability"],
        difficulty=fsrs_initial["difficulty"],
        state=fsrs_initial["state"],
        step=fsrs_initial["step"],
        last_review=fsrs_initial["last_review"],
        card_id=fsrs_initial.get("card_id"),
        is_active=True,
    )


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

    card = _new_card(req.user_id, req.term, back, example)
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

MAX_NOTE_CARDS = 5


class FromNotesRequest(BaseModel):
    user_id: int
    notes: str = Field(min_length=20, max_length=8000)
    source: str = Field(min_length=1, max_length=200)  # e.g. TryHackMe room name


@router.post("/from-notes")
async def flashcards_from_notes(req: FromNotesRequest, db: Session = Depends(get_db)):
    """Plan C5: 3-5 recall questions from the user's own TryHackMe notes (not from a bare term)."""
    if not db.query(User).filter(User.id == req.user_id).first():
        raise HTTPException(status_code=404, detail="User not found")

    prompt = f"""Jesteś ekspertem cyberbezpieczeństwa. Na podstawie NOTATEK ucznia z pokoju TryHackMe
"{req.source}" przygotuj od 3 do {MAX_NOTE_CARDS} fiszek do powtórek.

Zasady:
- Front to pytanie wymagające przypomnienia (komenda, flaga narzędzia, pojęcie), nie zdanie do rozpoznania.
- Back to krótka, poprawna odpowiedź po polsku. Używaj tylko tego, co wynika z notatek; popraw oczywiste błędy.
- Example to konkretna komenda lub payload z notatek albo null.

NOTATKI:
{req.notes}

Zwróć JSON: {{"cards": [{{"front": "...", "back": "...", "example": "..." }}]}}"""

    try:
        result = await generate_json(prompt)
        raw_cards = (result or {}).get("cards") or []
    except Exception as e:
        logger.error(f"Flashcards from notes failed: {e}")
        raise HTTPException(status_code=503, detail="Nie udało się wygenerować fiszek")

    cards = []
    for item in raw_cards[:MAX_NOTE_CARDS]:
        front, back = (item.get("front") or "").strip(), (item.get("back") or "").strip()
        if front and back:
            card = _new_card(req.user_id, front, back, item.get("example"), topic_slug="thm")
            db.add(card)
            cards.append(card)
    if not cards:
        raise HTTPException(status_code=503, detail="Model nie zwrócił żadnej fiszki")
    db.commit()
    return {"created": len(cards), "cards": [{"id": c.id, "front": c.front, "back": c.back} for c in cards]}


class DeckRequest(BaseModel):
    user_id: int


@router.post("/decks/tools")
def add_tool_deck(req: DeckRequest, db: Session = Depends(get_db)):
    """Plan C6: tool syntax deck (nmap, gobuster, hydra, msfconsole, Burp, netcat); idempotent."""
    from backend.services.tool_deck import TOOL_DECK

    if not db.query(User).filter(User.id == req.user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    existing = {front for (front,) in db.query(Flashcard.front).filter(Flashcard.user_id == req.user_id)}
    added = 0
    for front, back, example in TOOL_DECK:
        if front not in existing:
            db.add(_new_card(req.user_id, front, back, example, topic_slug="tools"))
            added += 1
    db.commit()
    return {"added": added, "deck_size": len(TOOL_DECK)}
