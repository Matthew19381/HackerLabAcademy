import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend.models.error_item import ErrorItem
from backend.services.hub_publisher import flush_in_background, queue_event

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/errors", tags=["errors"])


@router.get("/due/{user_id}")
def get_due_errors(user_id: int, db: Session = Depends(get_db)):
    """Return error items due for review."""
    now = datetime.utcnow()
    items = db.query(ErrorItem).filter(
        ErrorItem.user_id == user_id,
        ErrorItem.resolved.is_(False),
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
    resolved = db.query(ErrorItem).filter(ErrorItem.user_id == user_id, ErrorItem.resolved.is_(True)).count()
    pending = db.query(ErrorItem).filter(
        ErrorItem.user_id == user_id,
        ErrorItem.resolved.is_(False),
        ErrorItem.next_review <= datetime.utcnow()
    ).count()
    return {"total": total, "resolved": resolved, "pending": pending}


class ErrorReviewRequest(BaseModel):
    correct: bool


@router.post("/{error_id}/review")
def review_error(
    error_id: int, req: ErrorReviewRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """
    Review an error item.
    Must answer correctly 3 times in a row to resolve it.
    Retry schedule: 24h → 3 days → 7 days
    """
    item = db.query(ErrorItem).filter(ErrorItem.id == error_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Error item not found")

    was_resolved = item.resolved
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

    newly_resolved = item.resolved and not was_resolved
    if newly_resolved:
        queue_event(db, "error_resolved", item.user_id, {"error_id": item.id, "topic_slug": item.topic_slug})
    db.commit()
    if newly_resolved:
        background_tasks.add_task(flush_in_background)
    return {"resolved": item.resolved, "correct_streak": item.correct_streak}
