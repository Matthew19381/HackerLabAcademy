import logging
from datetime import datetime
from sqlalchemy.orm import Session
from models.achievement import Achievement

logger = logging.getLogger(__name__)

ACHIEVEMENT_DEFS = {
    # Topic progression
    "first_theory": ("Pierwszy Krok", "Ukończyłeś pierwszą lekcję teorii", "📖"),
    "theory_5": ("Badacz", "Ukończyłeś 5 lekcji teorii", "🔬"),
    "theory_10": ("Uczony", "Ukończyłeś 10 lekcji teorii", "🎓"),
    # Lab completions
    "first_lab": ("Szczur Labowy", "Ukończyłeś swój pierwszy lab", "🧪"),
    "labs_3": ("Cząstka Hakerska", "Ukończyłeś 3 laby", "⚡"),
    "labs_10": ("Dev Eksploitów", "Ukończyłeś 10 labów", "💀"),
    # Error loop
    "first_fix": ("Śmierć Błędów", "Naprawiłeś swój pierwszy błąd", "🐛"),
    "fix_10": ("Debugger", "Naprawiłeś 10 błędów", "🔧"),
    # Streak
    "streak_3": ("Rozkręcenie", "3-dniowa seria nauki", "🔥"),
    "streak_7": ("Wojownik Tygodniowy", "7-dniowa seria nauki", "⚡"),
    "streak_14": ("Oddany", "14-dniowa seria nauki", "💪"),
    "streak_30": ("Cyber Mnich", "30-dniowa seria nauki", "👑"),
    # XP milestones
    "xp_100": ("Kolekcjoner XP", "Zdobyłeś 100 XP", "✨"),
    "xp_500": ("Łowca XP", "Zdobyłeś 500 XP", "💫"),
    "xp_1000": ("Legenda XP", "Zdobyłeś 1000 XP", "🌟"),
    "xp_5000": ("Elitarny Haker", "Zdobyłeś 5000 XP", "🏆"),
    # Level milestones
    "level_5": ("Początkujący Haker", "Osiągnąłeś poziom 5", "🚀"),
    "level_10": ("Uczeń", "Osiągnąłeś poziom 10", "🎊"),
    "level_25": ("Członek Cechu", "Osiągnąłeś poziom 25", "🏹"),
    # OWASP mastery
    "owasp_sqli": ("Mistrz SQL", "Opanowałeś SQL Injection", "💉"),
    "owasp_xss": ("Łowca XSS", "Opanowałeś Cross-Site Scripting", "🕷️"),
    "owasp_complete": ("Wojownik OWASP", "Ukończyłeś wszystkie tematy OWASP Top 10", "🛡️"),
}


def calculate_level_from_xp(xp: int) -> dict:
    """50 levels, quadratic curve: level n requires (n-1)^2 * 20 XP."""
    level = 1
    for n in range(1, 51):
        required = (n - 1) ** 2 * 20
        if xp >= required:
            level = n
        else:
            break

    current_xp_req = (level - 1) ** 2 * 20
    next_xp_req = level ** 2 * 20 if level < 50 else current_xp_req + 1000

    if level < 50:
        progress = ((xp - current_xp_req) / (next_xp_req - current_xp_req)) * 100
    else:
        progress = 100.0

    return {
        "level": level,
        "level_name": _get_level_name(level),
        "xp": xp,
        "current_level_xp": current_xp_req,
        "next_level_xp": next_xp_req,
        "progress_percent": min(100.0, max(0.0, progress)),
        "max_level": 50,
    }


def _get_level_name(level: int) -> str:
    if level <= 5:
        return "Skryptowa Dziecię"
    elif level <= 10:
        return "Nowy Haker"
    elif level <= 15:
        return "Uczeń"
    elif level <= 20:
        return "Pentester"
    elif level <= 25:
        return "Łowca Bugów"
    elif level <= 30:
        return "Dev Eksploitów"
    elif level <= 35:
        return "Czerwona Drużyna"
    elif level <= 40:
        return "Elitarny Haker"
    elif level <= 45:
        return "Badacz 0day"
    else:
        return "Cyber Bóg"


def check_and_award_achievements(user, db: Session) -> list:
    from models.topic import UserTopicProgress
    from models.lab_attempt import LabAttempt
    from models.error_item import ErrorItem

    theory_done = db.query(UserTopicProgress).filter(
        UserTopicProgress.user_id == user.id,
        UserTopicProgress.theory_completed == True
    ).count()

    labs_done = db.query(LabAttempt).filter(
        LabAttempt.user_id == user.id,
        LabAttempt.completed == True
    ).count()

    errors_fixed = db.query(ErrorItem).filter(
        ErrorItem.user_id == user.id,
        ErrorItem.resolved == True
    ).count()

    xp = user.total_xp
    streak = user.streak_days or 0
    level_info = calculate_level_from_xp(xp)
    current_level = level_info["level"]

    existing = {a.achievement_type for a in db.query(Achievement).filter(
        Achievement.user_id == user.id
    ).all()}

    candidates = []

    def maybe(ach_type):
        if ach_type not in existing and ach_type in ACHIEVEMENT_DEFS:
            candidates.append(ach_type)

    if theory_done >= 1: maybe("first_theory")
    if theory_done >= 5: maybe("theory_5")
    if theory_done >= 10: maybe("theory_10")

    if labs_done >= 1: maybe("first_lab")
    if labs_done >= 3: maybe("labs_3")
    if labs_done >= 10: maybe("labs_10")

    if errors_fixed >= 1: maybe("first_fix")
    if errors_fixed >= 10: maybe("fix_10")

    if streak >= 3: maybe("streak_3")
    if streak >= 7: maybe("streak_7")
    if streak >= 14: maybe("streak_14")
    if streak >= 30: maybe("streak_30")

    if xp >= 100: maybe("xp_100")
    if xp >= 500: maybe("xp_500")
    if xp >= 1000: maybe("xp_1000")
    if xp >= 5000: maybe("xp_5000")

    if current_level >= 5: maybe("level_5")
    if current_level >= 10: maybe("level_10")
    if current_level >= 25: maybe("level_25")

    # Check OWASP topic mastery
    _check_owasp_achievements(user.id, db, existing, candidates)

    newly_awarded = []
    for ach_type in candidates:
        ach = Achievement(
            user_id=user.id,
            achievement_type=ach_type,
            unlocked_at=datetime.utcnow(),
            notified=False
        )
        db.add(ach)
        title, description, icon = ACHIEVEMENT_DEFS[ach_type]
        newly_awarded.append({"type": ach_type, "title": title, "description": description, "icon": icon})

    if newly_awarded:
        db.commit()

    return newly_awarded


def _check_owasp_achievements(user_id: int, db: Session, existing: set, candidates: list):
    from models.topic import UserTopicProgress, Topic

    def maybe(ach_type):
        if ach_type not in existing and ach_type in ACHIEVEMENT_DEFS:
            candidates.append(ach_type)

    sqli_topic = db.query(Topic).filter(Topic.slug == "sql-injection").first()
    if sqli_topic:
        progress = db.query(UserTopicProgress).filter(
            UserTopicProgress.user_id == user_id,
            UserTopicProgress.topic_id == sqli_topic.id,
            UserTopicProgress.lab_completed == True
        ).first()
        if progress:
            maybe("owasp_sqli")

    xss_topic = db.query(Topic).filter(Topic.slug == "xss").first()
    if xss_topic:
        progress = db.query(UserTopicProgress).filter(
            UserTopicProgress.user_id == user_id,
            UserTopicProgress.topic_id == xss_topic.id,
            UserTopicProgress.lab_completed == True
        ).first()
        if progress:
            maybe("owasp_xss")

    owasp_slugs = ["sql-injection", "xss", "csrf", "idor", "auth-bypass", "file-upload",
                   "security-misconfiguration", "sensitive-data", "xxe", "insecure-deserialization"]
    owasp_topics = db.query(Topic).filter(Topic.slug.in_(owasp_slugs)).all()
    if len(owasp_topics) >= 5:
        all_completed = all(
            db.query(UserTopicProgress).filter(
                UserTopicProgress.user_id == user_id,
                UserTopicProgress.topic_id == t.id,
                UserTopicProgress.lab_completed == True
            ).first() for t in owasp_topics
        )
        if all_completed:
            maybe("owasp_complete")


def get_unnotified_achievements(user_id: int, db: Session) -> list:
    unnotified = db.query(Achievement).filter(
        Achievement.user_id == user_id,
        Achievement.notified == False
    ).all()

    result = []
    for a in unnotified:
        if a.achievement_type in ACHIEVEMENT_DEFS:
            title, description, icon = ACHIEVEMENT_DEFS[a.achievement_type]
            result.append({
                "type": a.achievement_type,
                "title": title,
                "description": description,
                "icon": icon,
                "unlocked_at": a.unlocked_at.isoformat(),
            })
        a.notified = True

    if result:
        db.commit()

    return result


def get_all_achievements_for_user(user_id: int, db: Session) -> dict:
    earned_records = db.query(Achievement).filter(Achievement.user_id == user_id).all()
    earned_types = {a.achievement_type: a for a in earned_records}

    all_achievements = []
    for ach_type, (title, description, icon) in ACHIEVEMENT_DEFS.items():
        record = earned_types.get(ach_type)
        all_achievements.append({
            "type": ach_type,
            "title": title,
            "description": description,
            "icon": icon,
            "earned": record is not None,
            "unlocked_at": record.unlocked_at.isoformat() if record else None,
        })

    return {
        "total": len(ACHIEVEMENT_DEFS),
        "earned": len(earned_types),
        "achievements": all_achievements,
    }
