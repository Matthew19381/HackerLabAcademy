"""
Daily completion status (simple).
"""
import logging
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models.lab_attempt import LabAttempt
from models.exercise import UserExerciseAttempt
from models.flashcard_attempt import FlashcardAttempt
from models.article import ArticleRead

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/daily", tags=["daily"])


@router.get("/status")
def get_daily_status(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Return today's completion flags for lab and quiz."""
    # Today in UTC (start of day)
    today_dt = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_dt = today_dt + timedelta(days=1)

    # Lab: any completed LabAttempt today
    lab_done = db.query(LabAttempt).filter(
        LabAttempt.user_id == user_id,
        LabAttempt.completed == True,
        LabAttempt.completed_at >= today_dt,
        LabAttempt.completed_at < tomorrow_dt
    ).first() is not None

    # Quiz: any correct ExerciseAttempt today (or any attempt)
    quiz_done = db.query(UserExerciseAttempt).filter(
        UserExerciseAttempt.user_id == user_id,
        UserExerciseAttempt.attempted_at >= today_dt,
        UserExerciseAttempt.attempted_at < tomorrow_dt
    ).first() is not None

    # Flashcard: any review today
    flashcard_done = db.query(FlashcardAttempt).filter(
        FlashcardAttempt.user_id == user_id,
        FlashcardAttempt.is_active == True,
        FlashcardAttempt.reviewed_at >= today_dt,
        FlashcardAttempt.reviewed_at < tomorrow_dt
    ).first() is not None

    # Article: any read today
    article_done = db.query(ArticleRead).filter(
        ArticleRead.user_id == user_id,
        ArticleRead.is_active == True,
        ArticleRead.read_at >= today_dt,
        ArticleRead.read_at < tomorrow_dt
    ).first() is not None

    # Overall completion %: (lab + quiz + flashcard + article) / 4 * 100
    completed_tasks = (1 if lab_done else 0) + (1 if quiz_done else 0) + (1 if flashcard_done else 0) + (1 if article_done else 0)
    total_tasks = 4
    completion_pct = round((completed_tasks / total_tasks) * 100)

    return {
        "date": today_dt.date().isoformat(),
        "lab_done": lab_done,
        "quiz_done": quiz_done,
        "flashcard_done": flashcard_done,
        "article_done": article_done,
        "completion_percent": completion_pct,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
    }
