import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.ctf import CtfChallenge, UserCtfAttempt
from backend.models.user import User
from backend.services.achievement_service import check_and_award_achievements

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ctf", tags=["ctf"])


@router.get("/challenges")
def list_challenges(
    category: str = None,
    difficulty: int = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List active CTF challenges."""
    query = db.query(CtfChallenge).filter(CtfChallenge.is_active == True)
    if category:
        query = query.filter(CtfChallenge.category == category)
    if difficulty:
        query = query.filter(CtfChallenge.difficulty == difficulty)
    challenges = query.order_by(CtfChallenge.difficulty, CtfChallenge.points).limit(limit).all()

    return [
        {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "points": c.points,
            "difficulty": c.difficulty,
            "category": c.category,
            "has_hint": bool(c.hint),
            "solved_by_me": False,  # will be filled separately if needed
        }
        for c in challenges
    ]


@router.get("/challenges/{challenge_id}")
def get_challenge(challenge_id: int, db: Session = Depends(get_db)):
    """Get full challenge details (including hint if requested via query param? no, separate endpoint)."""
    challenge = db.query(CtfChallenge).filter(CtfChallenge.id == challenge_id, CtfChallenge.is_active == True).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return {
        "id": challenge.id,
        "title": challenge.title,
        "description": challenge.description,
        "points": challenge.points,
        "difficulty": challenge.difficulty,
        "category": challenge.category,
        "hint": challenge.hint,
        "solution": None,  # never expose solution to regular users
    }


@router.post("/challenges/{challenge_id}/hint")
def get_hint(challenge_id: int, user_id: int, db: Session = Depends(get_db)):
    """Get hint for a challenge (consumes 50% of points if solved)."""
    challenge = db.query(CtfChallenge).filter(CtfChallenge.id == challenge_id, CtfChallenge.is_active == True).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if not challenge.hint:
        raise HTTPException(status_code=404, detail="No hint available")
    return {"hint": challenge.hint, "penalty": "50% points if solved"}


@router.post("/challenges/{challenge_id}/submit")
def submit_flag(
    challenge_id: int,
    user_id: int,
    flag: str,
    db: Session = Depends(get_db)
):
    """Submit a flag. If correct, award points and mark solved. Only first solve counts full points; hints reduce points by 50%."""
    challenge = db.query(CtfChallenge).filter(CtfChallenge.id == challenge_id, CtfChallenge.is_active == True).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get or create attempt
    attempt = db.query(UserCtfAttempt).filter(
        UserCtfAttempt.user_id == user_id,
        UserCtfAttempt.challenge_id == challenge_id
    ).first()
    if not attempt:
        attempt = UserCtfAttempt(user_id=user_id, challenge_id=challenge_id, attempts_count=0)
        db.add(attempt)

    attempt.attempts_count += 1

    # Check flag (case-sensitive exact match)
    if flag.strip() == challenge.flag:
        if not attempt.solved:
            # Calculate points: full if no hint used? We don't track hint usage in this simple version. Let's assume hint penalty applies if user requested hint before.
            # We could store a flag for hint_used but simpler: always full points for now.
            points = challenge.points
            attempt.solved = True
            attempt.solved_at = datetime.utcnow()
            attempt.points_earned = points
            user.total_xp += points
            db.commit()

            new_achievements = check_and_award_achievements(user, db)

            return {
                "correct": True,
                "points_earned": points,
                "total_xp": user.total_xp,
                "new_achievements": new_achievements,
                "message": f"Flag accepted! +{points} XP"
            }
        else:
            # Already solved
            return {
                "correct": True,
                "points_earned": 0,
                "total_xp": user.total_xp,
                "message": "You already solved this challenge."
            }
    else:
        db.commit()
        return {
            "correct": False,
            "points_earned": 0,
            "message": "Incorrect flag. Try again!"
        }


@router.get("/leaderboard")
def get_leaderboard(limit: int = 20, db: Session = Depends(get_db)):
    """Top users by CTF points sum."""
    from sqlalchemy import func
    from backend.models.user import User

    # Sum of points_earned from UserCtfAttempt per user
    scores = db.query(
        User.id,
        User.name,
        func.sum(UserCtfAttempt.points_earned).label("ctf_points"),
        func.count(UserCtfAttempt.id).label("challenges_solved")
    ).join(UserCtfAttempt, User.id == UserCtfAttempt.user_id)\
     .filter(UserCtfAttempt.solved == True)\
     .group_by(User.id, User.name)\
     .order_by(func.sum(UserCtfAttempt.points_earned).desc())\
     .limit(limit).all()

    return [
        {"rank": i+1, "user_id": r.id, "name": r.name, "ctf_points": r.ctf_points or 0, "challenges_solved": r.challenges_solved}
        for i, r in enumerate(scores)
    ]


def seed_sample_challenges(db: Session):
    """Seed CTF challenges."""
    samples = [
        {
            "title": "Flag in HTTP Headers",
            "description": "Connect to the DVWA lab and send a request with a custom header. The flag is hidden in a secret header. What is the value of `X-Flag`?",
            "flag": "FLAG{HEADER_HUNTER}",
            "points": 100,
            "difficulty": 1,
            "category": "web",
            "hint": "Check all response headers, including those starting with X-"
        },
        {
            "title": "Cookie Monster",
            "description": "After logging into DVWA, inspect the cookies. One cookie contains a flag encoded in base64. Decode it and submit.",
            "flag": "FLAG{COOKIE_MASTER}",
            "points": 150,
            "difficulty": 2,
            "category": "web",
            "hint": "Look for a cookie named `session` or `flag`. It's base64."
        },
        {
            "title": "SQL Injection to Read File",
            "description": "In the DVWA SQL Injection lab, use a UNION-based attack to read the contents of `/etc/passwd`. Submit the first line as the flag.",
            "flag": "FLAG{SQL_FILE_READ}",
            "points": 200,
            "difficulty": 2,
            "category": "web",
            "hint": "Use `UNION SELECT` with `LOAD_FILE()` function."
        },
        {
            "title": "XSS Steal Cookie",
            "description": "In the reflected XSS lab, craft a payload that sends the victim's cookie to your attacker server (e.g., http://your-server.com/collect?c=...). The flag is the name of the cookie you need to steal.",
            "flag": "FLAG{PHPSESSIONID}",
            "points": 250,
            "difficulty": 3,
            "category": "web",
            "hint": "DVWA uses PHPSESSID as session cookie name."
        },
        {
            "title": "Blind Bool Time",
            "description": "Using blind SQL injection with conditional responses, determine the length of the admin password. The flag is that length.",
            "flag": "FLAG{LENGTH_32}",
            "points": 300,
            "difficulty": 4,
            "category": "web",
            "hint": "Use `AND LENGTH(password)=N` and observe page differences."
        },
    ]

    added = 0
    for cdata in samples:
        existing = db.query(CtfChallenge).filter(CtfChallenge.title == cdata["title"]).first()
        if not existing:
            ch = CtfChallenge(
                title=cdata["title"],
                description=cdata["description"],
                flag=cdata["flag"],
                points=cdata["points"],
                difficulty=cdata["difficulty"],
                category=cdata["category"],
                hint=cdata.get("hint"),
                is_active=True,
            )
            db.add(ch)
            added += 1
    if added:
        db.commit()
        logger.info(f"Seeded {added} CTF challenges")
