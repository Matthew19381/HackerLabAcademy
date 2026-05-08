import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend.models.error_item import ErrorItem

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/errors", tags=["errors"])


@router.get("/due/{user_id}")
def get_due_errors(user_id: int, db: Session = Depends(get_db)):
    """Return error items due for review."""
    now = datetime.utcnow()
    items = db.query(ErrorItem).filter(
        ErrorItem.user_id == user_id,
        ErrorItem.resolved == False,
        ErrorItem.next_review <= now
    ).order_by(ErrorItem.created_at).all()

    return [
        {
            "id": e.id,
            "question": e.question,
            "correct_answer": e.correct_answer,
            "user_answer": e.user_answer,
            "error_type": e.error_type,
            "explanation": e.explanation,
            "topic_slug": e.topic_slug,
            "correct_streak": e.correct_streak,
        }
        for e in items
    ]


@router.get("/stats/{user_id}")
def get_error_stats(user_id: int, db: Session = Depends(get_db)):
    total = db.query(ErrorItem).filter(ErrorItem.user_id == user_id).count()
    resolved = db.query(ErrorItem).filter(ErrorItem.user_id == user_id, ErrorItem.resolved == True).count()
    pending = db.query(ErrorItem).filter(
        ErrorItem.user_id == user_id,
        ErrorItem.resolved == False,
        ErrorItem.next_review <= datetime.utcnow()
    ).count()
    return {"total": total, "resolved": resolved, "pending": pending}


class ErrorReviewRequest(BaseModel):
    correct: bool


@router.post("/{error_id}/review")
def review_error(error_id: int, req: ErrorReviewRequest, db: Session = Depends(get_db)):
    """
    Review an error item.
    Must answer correctly 3 times in a row to resolve it.
    Retry schedule: 24h → 3 days → 7 days
    """
    item = db.query(ErrorItem).filter(ErrorItem.id == error_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Error item not found")

    if req.correct:
        item.correct_streak += 1
        if item.correct_streak >= 3:
            item.resolved = True
        else:
            # Schedule next review: 1d, 3d after streak 1, 2
            days = [1, 3, 7][min(item.correct_streak - 1, 2)]
            item.next_review = datetime.utcnow() + timedelta(days=days)
    else:
        item.correct_streak = 0
        item.next_review = datetime.utcnow() + timedelta(days=1)

    db.commit()
    return {"resolved": item.resolved, "correct_streak": item.correct_streak}
