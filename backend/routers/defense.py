"""
Defense Mode: Submit code fixes for vulnerable snippets.
"""
import logging
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend.models.defense import DefenseChallenge, UserDefenseAttempt
from backend.models.user import User
from backend.services.ai_service import generate_json
from backend.services.achievement_service import check_and_award_achievements

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/defense", tags=["defense"])


class DefenseSubmitRequest(BaseModel):
    user_id: int
    challenge_id: int
    submitted_code: str


@router.get("/challenges")
def list_defense_challenges(
    topic_slug: str = None,
    difficulty: int = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List defense challenges (vulnerable code to fix)."""
    query = db.query(DefenseChallenge).filter(DefenseChallenge.is_active == True)
    if topic_slug:
        query = query.filter(DefenseChallenge.topic_slug == topic_slug)
    if difficulty:
        query = query.filter(DefenseChallenge.difficulty == difficulty)
    challenges = query.order_by(DefenseChallenge.difficulty, DefenseChallenge.points).limit(limit).all()

    return [
        {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "vulnerable_code": c.vulnerable_code,
            "points": c.points,
            "difficulty": c.difficulty,
            "topic_slug": c.topic_slug,
        }
        for c in challenges
    ]


@router.get("/challenges/{challenge_id}")
def get_defense_challenge(challenge_id: int, db: Session = Depends(get_db)):
    """Get full challenge including vulnerable code."""
    challenge = db.query(DefenseChallenge).filter(DefenseChallenge.id == challenge_id, DefenseChallenge.is_active == True).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return {
        "id": challenge.id,
        "title": challenge.title,
        "description": challenge.description,
        "vulnerable_code": challenge.vulnerable_code,
        "points": challenge.points,
        "difficulty": challenge.difficulty,
        "topic_slug": challenge.topic_slug,
    }


@router.post("/submit")
def submit_defense_fix(
    req: DefenseSubmitRequest,
    db: Session = Depends(get_db)
):
    """Submit a code fix. AI evaluates correctness and awards XP."""
    challenge = db.query(DefenseChallenge).filter(DefenseChallenge.id == req.challenge_id, DefenseChallenge.is_active == True).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already solved by this user (optional: allow multiple attempts but only reward once)
    attempt = db.query(UserDefenseAttempt).filter(
        UserDefenseAttempt.user_id == req.user_id,
        UserDefenseAttempt.challenge_id == req.challenge_id
    ).first()
    if attempt and attempt.is_correct:
        return {
            "correct": True,
            "points_earned": 0,
            "total_xp": user.total_xp,
            "message": "You already solved this challenge.",
            "feedback": attempt.ai_feedback,
        }

    # Evaluate with AI
    prompt = f"""
You are a security code review expert. Evaluate if the submitted code fix correctly addresses the vulnerability.

Vulnerable code (original):
{challenge.vulnerable_code}

Expected solution (reference):
{challenge.solution_code}

User's submitted fix:
{req.submitted_code}

Instructions:
- Determine if the user's fix correctly patches the vulnerability
- Consider both functionality preservation and security improvement
- Provide a brief explanation (1-2 sentences) of whether it's correct or what's missing

Respond ONLY with valid JSON:
{{
  "correct": boolean,
  "score": integer (0-100, with 100 being perfect match),
  "explanation": "string"
}}
"""
    try:
        eval_result = generate_json(prompt, default={"correct": False, "score": 0, "explanation": "AI evaluation failed"})
        is_correct = eval_result.get("correct", False)
        score = eval_result.get("score", 0)
        explanation = eval_result.get("explanation", "No explanation provided.")
    except Exception as e:
        logger.error(f"Gemini eval error: {e}")
        is_correct = False
        score = 0
        explanation = "Evaluation failed due to server error."

    # Award points proportional to score if correct (threshold 70)
    points_earned = 0
    if is_correct and score >= 70:
        points_earned = challenge.points
        user.total_xp += points_earned

    # Save attempt
    if attempt:
        attempt.submitted_code = req.submitted_code
        attempt.is_correct = is_correct
        attempt.points_earned = points_earned
        attempt.ai_feedback = explanation
        if is_correct:
            attempt.solved_at = datetime.utcnow()
    else:
        attempt = UserDefenseAttempt(
            user_id=req.user_id,
            challenge_id=req.challenge_id,
            submitted_code=req.submitted_code,
            is_correct=is_correct,
            points_earned=points_earned,
            ai_feedback=explanation,
            solved_at=datetime.utcnow() if is_correct else None,
        )
        db.add(attempt)
    db.commit()

    # Award achievements if earned
    new_achievements = []
    if is_correct:
        new_achievements = check_and_award_achievements(user, db)

    return {
        "correct": is_correct,
        "points_earned": points_earned,
        "total_xp": user.total_xp,
        "score": score,
        "message": f"{'Correct!' if is_correct else 'Not quite right.'} {explanation}",
        "new_achievements": new_achievements,
        "feedback": explanation,
    }


def seed_sample_defense_challenges(db: Session):
    """Seed database with sample defense challenges."""
    samples = [
        {
            "title": "Fix SQL Injection in Python",
            "description": "The following code is vulnerable to SQL injection. Rewrite the query using parameterized statements.",
            "vulnerable_code": '''query = "SELECT * FROM users WHERE id = " + user_id_str
cursor.execute(query)''',
            "solution_code": '''query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id_str,))''',
            "points": 100,
            "difficulty": 2,
            "topic_slug": "sql-injection",
        },
        {
            "title": "Fix XSS in PHP",
            "description": "The PHP code directly echoes user input. Fix it by properly escaping output.",
            "vulnerable_code": '''<?php
$name = $_GET['name'];
echo "<div>Hello, " . $name . "!</div>";
?>''',
            "solution_code": '''<?php
$name = htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8');
echo "<div>Hello, " . $name . "!</div>";
?>''',
            "points": 150,
            "difficulty": 2,
            "topic_slug": "xss",
        },
        {
            "title": "Fix Command Injection in Node.js",
            "description": "The code uses user input in a shell command. Fix it by using parameterized exec or escaping.",
            "vulnerable_code": '''const { exec } = require('child_process');
const hostname = req.body.hostname;
exec(`ping -c 1 ${hostname}`, (err, stdout) => {
  res.send(stdout);
});''',
            "solution_code": '''const { execFile } = require('child_process');
const hostname = req.body.hostname;
execFile('ping', ['-c', '1', hostname], (err, stdout) => {
  res.send(stdout);
});''',
            "points": 200,
            "difficulty": 3,
            "topic_slug": "command-injection",
        },
    ]

    added = 0
    for cdata in samples:
        existing = db.query(DefenseChallenge).filter(DefenseChallenge.title == cdata["title"]).first()
        if not existing:
            ch = DefenseChallenge(
                title=cdata["title"],
                description=cdata["description"],
                vulnerable_code=cdata["vulnerable_code"],
                solution_code=cdata["solution_code"],
                points=cdata["points"],
                difficulty=cdata["difficulty"],
                topic_slug=cdata["topic_slug"],
                is_active=True,
            )
            db.add(ch)
            added += 1
    if added:
        db.commit()
        logger.info(f"Seeded {added} defense challenges")
