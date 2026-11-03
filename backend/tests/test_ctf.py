"""CTF restored without a leaderboard (2026-11-03)."""
import sqlite3

from backend.migrations_runner import upgrade_database
from backend.models.user import User
from backend.routers.ctf import seed_challenges
from backend.services.ctf_challenges import CHALLENGES


def _setup(db):
    seed_challenges(db)
    user = User(name="ctf", total_xp=0)
    db.add(user)
    db.commit()
    return user


def _by_title(client, user_id, title):
    return next(c for c in client.get("/api/v1/ctf/challenges", params={"user_id": user_id}).json() if c["title"] == title)


def test_solve_gives_points_once_and_reveals_solution(client, db_session):
    user = _setup(db_session)
    ch = _by_title(client, user.id, "Ciasteczko w Base64")
    assert ch["solved"] is False and ch["solution"] is None and "flag" not in ch

    wrong = client.post(f"/api/v1/ctf/challenges/{ch['id']}/submit", json={"user_id": user.id, "flag": "FLAG{nie}"}).json()
    assert wrong["correct"] is False
    ok = client.post(f"/api/v1/ctf/challenges/{ch['id']}/submit",
                     json={"user_id": user.id, "flag": " FLAG{CIASTECZKO_ODKODOWANE} "}).json()
    assert ok["correct"] is True and ok["points_earned"] == 50 and ok["solution"]
    again = client.post(f"/api/v1/ctf/challenges/{ch['id']}/submit",
                        json={"user_id": user.id, "flag": "FLAG{CIASTECZKO_ODKODOWANE}"}).json()
    assert again["points_earned"] == 0
    db_session.refresh(user)
    assert user.total_xp == 50
    assert _by_title(client, user.id, "Ciasteczko w Base64")["solved"] is True


def test_hint_halves_the_points(client, db_session):
    """The penalty was promised in the UI before 2026-11-03 but never applied."""
    user = _setup(db_session)
    ch = _by_title(client, user.id, "Token bez podpisu")
    hint = client.post(f"/api/v1/ctf/challenges/{ch['id']}/hint", json={"user_id": user.id}).json()
    assert hint["points_if_solved"] == 50 and hint["hint"]
    ok = client.post(f"/api/v1/ctf/challenges/{ch['id']}/submit",
                     json={"user_id": user.id, "flag": "FLAG{JWT_TO_NIE_SZYFR}"}).json()
    assert ok["points_earned"] == 50


def test_no_leaderboard(client):
    assert client.get("/api/v1/ctf/leaderboard").status_code == 404


def test_every_flag_follows_from_its_description():
    """Guard against the old made-up flags: each encoded payload in the text decodes to the flag."""
    import base64
    import codecs
    import hashlib
    import urllib.parse

    by_title = {c["title"]: c for c in CHALLENGES}
    assert base64.b64decode("RkxBR3tDSUFTVEVDWktPX09ES09ET1dBTkV9").decode() == by_title["Ciasteczko w Base64"]["flag"]
    assert codecs.decode("SYNT{XBZRAGNEMR_FN_CHOYVPMAR}", "rot13") == by_title["Komentarz w HTML"]["flag"]
    assert hashlib.md5(b"password").hexdigest() == "5f4dcc3b5aa765d61d8327deb882cf99"
    url = "%46%4C%41%47%7B%55%52%4C%5F%45%4E%43%4F%44%49%4E%47%7D"
    assert urllib.parse.unquote(url) == by_title["Zakodowany parametr"]["flag"]
    assert bytes.fromhex("464c41477b4845585f544f5f54454b53547d").decode() == by_title["Zrzut pamięci"]["flag"]
    payload = "eyJ1c2VyIjoiamFuIiwicm9sZSI6InVzZXIiLCJmbGFnIjoiRkxBR3tKV1RfVE9fTklFX1NaWUZSfSJ9"
    assert by_title["Token bez podpisu"]["flag"] in base64.urlsafe_b64decode(payload + "==").decode()
    for c in CHALLENGES:
        if c["title"] not in ("Wyciek hasha", "Kto próbował SQL Injection?"):
            assert any(part in c["description"] for part in ("RkxB", "SYNT", "eyJ", "%46", "464c"))
        assert "DVWA" not in c["description"]


def test_old_dvwa_challenges_are_deactivated(tmp_path):
    from sqlalchemy import create_engine

    path = tmp_path / "old.db"
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE ctf_challenges (id INTEGER PRIMARY KEY, title TEXT, description TEXT, flag TEXT,"
                " points INTEGER, difficulty INTEGER, category TEXT, hint TEXT, solution TEXT, is_active BOOLEAN,"
                " created_at DATETIME)")
    con.execute("CREATE TABLE user_ctf_attempts (id INTEGER PRIMARY KEY, user_id INTEGER, challenge_id INTEGER,"
                " solved BOOLEAN, solved_at DATETIME, attempts_count INTEGER, points_earned INTEGER)")
    con.execute("INSERT INTO ctf_challenges (id, title, description, flag, category, is_active)"
                " VALUES (1, 'Cookie Monster', 'DVWA', 'FLAG{COOKIE_MASTER}', 'web', 1)")
    con.execute("INSERT INTO user_ctf_attempts VALUES (1, 1, 1, 1, NULL, 2, 150)")
    con.commit()
    con.close()

    upgrade_database(create_engine(f"sqlite:///{path}"))

    con = sqlite3.connect(path)
    assert con.execute("SELECT is_active FROM ctf_challenges WHERE id = 1").fetchone() == (0,)
    assert con.execute("SELECT points_earned, hint_used FROM user_ctf_attempts").fetchone() == (150, None)
    con.close()
