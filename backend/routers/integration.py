"""INT-1 (ACTION_PLAN F5.1): GET /api/v1/summary for the System-Główny hub, plus
POST /api/v1/integrations/flush to push queued events by hand (F5.2)."""

import json
from datetime import date as date_type
from datetime import datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.error_item import ErrorItem
from backend.models.flashcard import Flashcard
from backend.models.flashcard_attempt import FlashcardAttempt
from backend.models.outbound_event import OutboundEvent
from backend.models.user import User
from backend.services.hub_publisher import MODULE_NAME, flush_pending

router = APIRouter(tags=["Integration"])


def _parse_date(raw: str | None) -> date_type:
    if not raw:
        return datetime.utcnow().date()
    try:
        return date_type.fromisoformat(raw)
    except ValueError as e:
        raise HTTPException(status_code=422, detail="date must be YYYY-MM-DD") from e


@router.get("/summary")
def get_ecosystem_summary(
    user_id: int = Query(...),
    date: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """Read-only, no AI calls; no streaks (hub standard: no shaming counters)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    day = _parse_date(date)
    start, end = datetime.combine(day, time.min), datetime.combine(day + timedelta(days=1), time.min)

    reviewed = (
        db.query(FlashcardAttempt)
        .filter(FlashcardAttempt.user_id == user_id, FlashcardAttempt.reviewed_at >= start, FlashcardAttempt.reviewed_at < end)
        .count()
    )
    due = (
        db.query(Flashcard)
        .filter(Flashcard.user_id == user_id, Flashcard.is_active.is_(True), Flashcard.next_review_date < end)
        .count()
    )
    errors_logged = (
        db.query(ErrorItem)
        .filter(ErrorItem.user_id == user_id, ErrorItem.created_at >= start, ErrorItem.created_at < end)
        .count()
    )
    errors_open = db.query(ErrorItem).filter(ErrorItem.user_id == user_id, ErrorItem.resolved.is_(False)).count()
    events = [
        json.loads(e.payload_json)
        for e in db.query(OutboundEvent)
        .filter(OutboundEvent.user_id == str(user_id), OutboundEvent.created_at >= start, OutboundEvent.created_at < end)
        .order_by(OutboundEvent.id)
        .limit(100)
    ]
    return {
        "module": MODULE_NAME,
        "user_id": str(user_id),
        "date": day.isoformat(),
        "summary": {
            "flashcards_reviewed": reviewed,
            "flashcards_due": due,
            "errors_logged": errors_logged,
            "errors_open": errors_open,
            "total_xp": user.total_xp or 0,
        },
        "events": events,
        "wellbeing_contribution": None,
    }


@router.post("/integrations/flush")
def flush(db: Session = Depends(get_db)):
    return {"sent": flush_pending(db)}
