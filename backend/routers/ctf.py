"""CTF (restored 2026-11-03; decision 3 of 2026-08-09: puzzles and per-user points, NO leaderboard).

Before its removal the hint "consumes 50% of points" was promised but never applied; the attempt now
records hint_used and a solve after a hint earns half the points.
"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.ctf import CtfChallenge, UserCtfAttempt
from backend.models.user import User
from backend.services.achievement_service import check_and_award_achievements
from backend.services.ctf_challenges import CHALLENGES

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ctf", tags=["ctf"])


class FlagSubmit(BaseModel):
    user_id: int
    flag: str = Field(min_length=1, max_length=200)


class HintRequest(BaseModel):
    user_id: int


def _active(db: Session, challenge_id: int) -> CtfChallenge:
    challenge = db.query(CtfChallenge).filter(CtfChallenge.id == challenge_id, CtfChallenge.is_active.is_(True)).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Nie ma takiego zadania")
    return challenge


def _attempt(db: Session, user_id: int, challenge_id: int) -> UserCtfAttempt:
    attempt = db.query(UserCtfAttempt).filter(
        UserCtfAttempt.user_id == user_id, UserCtfAttempt.challenge_id == challenge_id
    ).first()
    if not attempt:
        attempt = UserCtfAttempt(user_id=user_id, challenge_id=challenge_id, attempts_count=0,
                                 solved=False, hint_used=False, points_earned=0)
        db.add(attempt)
    return attempt


@router.get("/challenges")
def list_challenges(user_id: int | None = Query(None), db: Session = Depends(get_db)):
    challenges = (
        db.query(CtfChallenge).filter(CtfChallenge.is_active.is_(True))
        .order_by(CtfChallenge.difficulty, CtfChallenge.points, CtfChallenge.id).all()
    )
    mine = {}
    if user_id is not None:
        mine = {a.challenge_id: a for a in db.query(UserCtfAttempt).filter(UserCtfAttempt.user_id == user_id)}
    out = []
    for c in challenges:
        attempt = mine.get(c.id)
        solved = bool(attempt and attempt.solved)
        out.append({
            "id": c.id, "title": c.title, "description": c.description, "points": c.points,
            "difficulty": c.difficulty, "category": c.category, "has_hint": bool(c.hint),
            "solved": solved,
            "points_earned": attempt.points_earned if solved else 0,
            "hint": c.hint if attempt and attempt.hint_used else None,
            "solution": c.solution if solved else None,
        })
    return out


@router.post("/challenges/{challenge_id}/hint")
def take_hint(challenge_id: int, req: HintRequest, db: Session = Depends(get_db)):
    challenge = _active(db, challenge_id)
    if not challenge.hint:
        raise HTTPException(status_code=404, detail="To zadanie nie ma podpowiedzi")
    attempt = _attempt(db, req.user_id, challenge_id)
    if not attempt.solved:
        attempt.hint_used = True
    db.commit()
    return {"hint": challenge.hint, "points_if_solved": challenge.points // 2 if attempt.hint_used else challenge.points}


@router.post("/challenges/{challenge_id}/submit")
def submit_flag(challenge_id: int, req: FlagSubmit, db: Session = Depends(get_db)):
    challenge = _active(db, challenge_id)
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    attempt = _attempt(db, user.id, challenge_id)
    attempt.attempts_count = (attempt.attempts_count or 0) + 1

    if req.flag.strip() != challenge.flag:
        db.commit()
        return {"correct": False, "points_earned": 0, "message": "To nie ta flaga. Spróbuj jeszcze raz."}
    if attempt.solved:
        db.commit()
        return {"correct": True, "points_earned": 0, "message": "To zadanie jest już rozwiązane.",
                "solution": challenge.solution}

    points = challenge.points // 2 if attempt.hint_used else challenge.points
    attempt.solved = True
    attempt.solved_at = datetime.utcnow()
    attempt.points_earned = points
    user.total_xp = (user.total_xp or 0) + points
    db.commit()
    return {
        "correct": True,
        "points_earned": points,
        "message": f"Flaga przyjęta! +{points} XP" + (" (połowa za podpowiedź)" if attempt.hint_used else ""),
        "solution": challenge.solution,
        "new_achievements": check_and_award_achievements(user, db),
    }


def seed_challenges(db: Session) -> None:
    existing = {title for (title,) in db.query(CtfChallenge.title)}
    added = 0
    for data in CHALLENGES:
        if data["title"] not in existing:
            db.add(CtfChallenge(**data, is_active=True))
            added += 1
    if added:
        db.commit()
        logger.info("Seeded %s CTF challenges", added)
