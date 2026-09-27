"""ACTION_PLAN F5.1-F5.3: /summary contract, outbound event queue, hub directives."""

import json
from datetime import datetime, timedelta

import httpx

from backend.models.error_item import ErrorItem
from backend.models.flashcard import Flashcard
from backend.models.outbound_event import OutboundEvent
from backend.models.user import User
from backend.services import hub_publisher


def _user(db):
    u = User(name="u", total_xp=120)
    db.add(u)
    db.commit()
    return u


def test_summary_contract(client, db_session):
    u = _user(db_session)
    r = client.get("/api/v1/summary", params={"user_id": u.id, "date": "2026-09-27"})
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"module", "user_id", "date", "summary", "events", "wellbeing_contribution"}
    assert body["module"] == "hackerlab-academy" and body["user_id"] == str(u.id)
    assert body["summary"]["total_xp"] == 120 and "streak" not in body["summary"]
    assert body["wellbeing_contribution"] is None
    assert client.get("/api/v1/summary", params={"user_id": u.id, "date": "x"}).status_code == 422
    assert client.get("/api/v1/summary", params={"user_id": 9999}).status_code == 404


def test_review_queues_event_and_summary_counts_it(client, db_session, monkeypatch):
    monkeypatch.setattr(hub_publisher.hub_settings, "SYSTEM_GLOWNY_MODULE_KEY", "")  # no network in tests
    u = _user(db_session)
    card = Flashcard(user_id=u.id, front="f", back="b", next_review_date=datetime.utcnow() - timedelta(days=1))
    db_session.add(card)
    db_session.commit()

    assert client.post(f"/api/v1/flashcards/{card.id}/review", json={"rating": 3}).status_code == 200
    body = client.get("/api/v1/summary", params={"user_id": u.id}).json()
    assert body["summary"]["flashcards_reviewed"] == 1
    assert [e["event_type"] for e in body["events"]] == ["flashcard_reviewed"]
    assert body["events"][0]["module"] == "hackerlab-academy"


def test_error_resolved_only_once(client, db_session, monkeypatch):
    monkeypatch.setattr(hub_publisher.hub_settings, "SYSTEM_GLOWNY_MODULE_KEY", "")
    u = _user(db_session)
    e = ErrorItem(user_id=u.id, question="q", correct_answer="a", user_answer="b")
    db_session.add(e)
    db_session.commit()
    for _ in range(5):
        client.post(f"/api/v1/errors/{e.id}/review", json={"correct": True})
    from backend import database

    s = database.SessionLocal()
    assert s.query(OutboundEvent).filter_by(event_type="error_resolved").count() == 1
    s.close()


def test_flush_marks_sent_and_survives_hub_down(db_session, monkeypatch):
    monkeypatch.setattr(hub_publisher.hub_settings, "SYSTEM_GLOWNY_MODULE_KEY", "k")
    hub_publisher.queue_event(db_session, "quiz_completed", 1, {"score": 80})
    db_session.commit()

    def down(*a, **k):
        raise httpx.ConnectError("down")

    monkeypatch.setattr(hub_publisher.httpx, "post", down)
    assert hub_publisher.flush_pending(db_session) == 0
    row = db_session.query(OutboundEvent).one()
    assert row.sent_at is None and row.attempts == 1

    sent = []

    def ok(url, json, headers, timeout):
        sent.append((url, json, headers))
        return httpx.Response(201)

    monkeypatch.setattr(hub_publisher.httpx, "post", ok)
    assert hub_publisher.flush_pending(db_session) == 1
    assert sent[0][2] == {"X-Module-Key": "k"} and sent[0][1]["event_type"] == "quiz_completed"
    db_session.refresh(row)
    assert row.sent_at is not None


def test_survival_mode_shrinks_agenda(client, db_session):
    u = _user(db_session)
    r = client.post("/api/v1/directives", json={"directive": "survival_mode", "enabled": True, "user_id": u.id})
    assert r.status_code == 200
    agenda = client.get(f"/api/v1/brain/today/{u.id}").json()
    assert agenda["survival_mode"] is True and len(agenda["agenda"]) == 1
    assert agenda["agenda"][0]["minutes"] == 5

    client.post("/api/v1/directives", json={"directive": "survival_mode", "enabled": False, "user_id": u.id})
    assert "survival_mode" not in client.get(f"/api/v1/brain/today/{u.id}").json()


def test_quiet_hours_uses_hub_field_names(client, db_session):
    u = _user(db_session)
    client.post("/api/v1/directives", json={"directive": "quiet_hours", "from": "22:00", "to": "07:00", "user_id": u.id})
    assert client.get(f"/api/v1/directives/{u.id}").json()["quiet_hours"] == {"from": "22:00", "to": "07:00"}
    assert client.post("/api/v1/directives", json={"directive": "nope"}).status_code == 422
