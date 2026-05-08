"""
Learning Brain — daily agenda engine.
Decides: what to do today, in what order, and why.
"""
import json
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.topic import Topic, UserTopicProgress
from backend.models.error_item import ErrorItem
from backend.models.flashcard import Flashcard
from backend.services.achievement_service import calculate_level_from_xp

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/brain", tags=["brain"])


@router.get("/today/{user_id}")
def get_daily_agenda(user_id: int, db: Session = Depends(get_db)):
    """
    Learning Brain: generates a prioritized daily agenda.
    Priority order:
      1. Error Loop items due for review
      2. Flashcards due for review
      3. Next unlocked topic (theory not started)
      4. Incomplete topic (theory done but no quiz/lab)
      5. Review suggestion (weakest quiz score)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.utcnow()
    agenda = []

    # 1. Due error items
    due_errors = db.query(ErrorItem).filter(
        ErrorItem.user_id == user_id,
        ErrorItem.resolved == False,
        ErrorItem.next_review <= now
    ).count()

    if due_errors > 0:
        agenda.append({
            "type": "fix_errors",
            "priority": 1,
            "title": f"Napraw {due_errors} błędów",
            "description": "Błędy z poprzednich quizów czekają na powtórkę.",
            "action_url": "/errors",
            "count": due_errors,
            "xp_potential": due_errors * 5,
            "icon": "🐛",
        })

    # 2. Due flashcards
    due_cards = db.query(Flashcard).filter(
        Flashcard.user_id == user_id,
        Flashcard.is_active == True,
        Flashcard.next_review_date <= now
    ).count()

    if due_cards > 0:
        agenda.append({
            "type": "flashcards",
            "priority": 2,
            "title": f"Powtórz {due_cards} fiszek",
            "description": "Algorytm SM-2 mówi: czas na powtórkę.",
            "action_url": "/flashcards",
            "count": due_cards,
            "xp_potential": due_cards * 2,
            "icon": "🃏",
        })

    # 3. Next new topic to start
    all_topics = db.query(Topic).order_by(Topic.order_index).all()
    progress_map = {
        p.topic_id: p for p in
        db.query(UserTopicProgress).filter(UserTopicProgress.user_id == user_id).all()
    }

    next_topic = None
    incomplete_topic = None
    weakest_topic = None
    weakest_score = 101.0

    for t in all_topics:
        prereqs = json.loads(t.prerequisites or "[]")
        unlocked = _check_unlocked(t, prereqs, progress_map, db)
        if not unlocked:
            continue

        prog = progress_map.get(t.id)

        if prog is None or not prog.theory_completed:
            if next_topic is None:
                next_topic = t
        elif prog.theory_completed and not prog.lab_completed and t.lab_type:
            if incomplete_topic is None:
                incomplete_topic = t
        elif prog.quiz_score is not None and prog.quiz_score < weakest_score:
            weakest_score = prog.quiz_score
            weakest_topic = t

    if next_topic:
        agenda.append({
            "type": "new_topic",
            "priority": 3,
            "title": f"Nowy temat: {next_topic.name}",
            "description": next_topic.description or "",
            "action_url": f"/topics/{next_topic.slug}",
            "topic_slug": next_topic.slug,
            "topic_name": next_topic.name,
            "xp_potential": 50,
            "icon": "📖",
        })

    if incomplete_topic:
        agenda.append({
            "type": "complete_lab",
            "priority": 4,
            "title": f"Lab do ukończenia: {incomplete_topic.name}",
            "description": "Teoria zaliczona — czas na praktykę w Docker labie.",
            "action_url": "/lab",
            "topic_slug": incomplete_topic.slug,
            "topic_name": incomplete_topic.name,
            "xp_potential": 50,
            "icon": "🧪",
        })

    if weakest_topic and (weakest_score < 80):
        agenda.append({
            "type": "review_topic",
            "priority": 5,
            "title": f"Powtórz: {weakest_topic.name}",
            "description": f"Twój wynik: {weakest_score:.0f}%. Warto utrwalić.",
            "action_url": f"/topics/{weakest_topic.slug}",
            "topic_slug": weakest_topic.slug,
            "topic_name": weakest_topic.name,
            "xp_potential": 20,
            "icon": "🔄",
        })

    # Compute totals
    topics_done = sum(1 for p in progress_map.values() if p.theory_completed)
    labs_done = sum(1 for p in progress_map.values() if p.lab_completed)
    level_info = calculate_level_from_xp(user.total_xp or 0)

    return {
        "agenda": agenda,
        "summary": _build_summary(agenda),
        "stats": {
            "topics_done": topics_done,
            "labs_done": labs_done,
            "errors_pending": due_errors,
            "flashcards_due": due_cards,
            "streak": user.streak_days or 0,
        },
        "level_info": level_info,
    }


def _check_unlocked(topic, prereqs, progress_map, db) -> bool:
    for prereq_slug in prereqs:
        prereq_topic = db.query(Topic).filter(Topic.slug == prereq_slug).first()
        if prereq_topic:
            prog = progress_map.get(prereq_topic.id)
            if not prog or not prog.theory_completed:
                return False
    return True


def _build_summary(agenda: list) -> str:
    if not agenda:
        return "Wszystko na dziś zrobione! Wróć jutro po nowe zadania."
    parts = []
    for item in agenda[:2]:
        parts.append(item["title"])
    if len(agenda) > 2:
        parts.append(f"i {len(agenda) - 2} więcej")
    return "Dziś: " + ", ".join(parts) + "."
