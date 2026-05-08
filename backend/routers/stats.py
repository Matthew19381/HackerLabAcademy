import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.topic import UserTopicProgress, Topic
from backend.models.lab_attempt import LabAttempt
from backend.models.error_item import ErrorItem
from backend.models.exercise import UserExerciseAttempt
from backend.services.achievement_service import (
    calculate_level_from_xp,
    get_all_achievements_for_user,
    get_unnotified_achievements
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/{user_id}")
def get_stats(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    level_info = calculate_level_from_xp(user.total_xp)

    topics_total = db.query(Topic).count()
    theory_done = db.query(UserTopicProgress).filter(
        UserTopicProgress.user_id == user_id,
        UserTopicProgress.theory_completed == True
    ).count()
    labs_done = db.query(UserTopicProgress).filter(
        UserTopicProgress.user_id == user_id,
        UserTopicProgress.lab_completed == True
    ).count()
    errors_pending = db.query(ErrorItem).filter(
        ErrorItem.user_id == user_id,
        ErrorItem.resolved == False
    ).count()

    new_achievements = get_unnotified_achievements(user_id, db)

    return {
        "user": {"id": user.id, "name": user.name, "streak_days": user.streak_days},
        "level_info": level_info,
        "progress": {
            "topics_total": topics_total,
            "theory_completed": theory_done,
            "labs_completed": labs_done,
            "errors_pending": errors_pending,
        },
        "new_achievements": new_achievements,
    }


@router.get("/{user_id}/achievements")
def get_achievements(user_id: int, db: Session = Depends(get_db)):
    return get_all_achievements_for_user(user_id, db)


@router.get("/{user_id}/analytics")
def get_analytics(user_id: int, db: Session = Depends(get_db)):
    """Get learning analytics: weakest topics, in-progress topics, accuracy."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Weakest topics by unresolved errors (top 5)
    error_topics = db.query(
        ErrorItem.topic_slug,
        func.count(ErrorItem.id).label("count")
    ).filter(
        ErrorItem.user_id == user_id,
        ErrorItem.resolved == False,
        ErrorItem.topic_slug != None
    ).group_by(ErrorItem.topic_slug).order_by(func.count(ErrorItem.id).desc()).limit(5).all()

    # Topics in progress: theory completed but lab not done
    in_progress = db.query(Topic).join(
        UserTopicProgress, Topic.id == UserTopicProgress.topic_id
    ).filter(
        UserTopicProgress.user_id == user_id,
        UserTopicProgress.theory_completed == True,
        UserTopicProgress.lab_completed == False
    ).all()

    # Overall exercise accuracy
    total_exercises = db.query(UserExerciseAttempt).filter(
        UserExerciseAttempt.user_id == user_id
    ).count()
    correct_exercises = db.query(UserExerciseAttempt).filter(
        UserExerciseAttempt.user_id == user_id,
        UserExerciseAttempt.is_correct == True
    ).count()
    accuracy = round((correct_exercises / total_exercises) * 100) if total_exercises > 0 else 0

    # Study streak already in user.streak_days

    return {
        "weakest_topics": [
            {"topic_slug": t[0], "unresolved_errors": t[1]}
            for t in error_topics
        ],
        "in_progress_topics": [
            {"slug": t.slug, "name": t.name, "category": t.category}
            for t in in_progress
        ],
        "overall_accuracy": accuracy,
        "total_exercises": total_exercises,
        "correct_exercises": correct_exercises,
        "streak_days": user.streak_days,
    }
