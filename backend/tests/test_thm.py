"""TryHackMe tracker (plan C4, C7)."""
from backend.models.user import User
from backend.services import hub_publisher


def _user(db):
    u = User(name="thm")
    db.add(u)
    db.commit()
    return u


def test_crud_and_counts(client, db_session):
    u = _user(db_session)
    created = client.post("/api/v1/thm", json={"user_id": u.id, "name": "OWASP Top 10", "category": "Web"})
    assert created.status_code == 201 and created.json()["done"] is False
    client.post("/api/v1/thm", json={"user_id": u.id, "kind": "path", "name": "Jr Penetration Tester"})

    entry_id = created.json()["id"]
    updated = client.patch(f"/api/v1/thm/{entry_id}", json={"done": True, "notes": "IDOR w parametrze id"}).json()
    assert updated["done"] is True and updated["completed_at"] and updated["notes"] == "IDOR w parametrze id"

    listing = client.get("/api/v1/thm", params={"user_id": u.id}).json()
    assert listing["counts"] == {"done": 1, "todo": 1}
    assert [e["name"] for e in listing["entries"]] == ["Jr Penetration Tester", "OWASP Top 10"]  # todo first

    undone = client.patch(f"/api/v1/thm/{entry_id}", json={"done": False}).json()
    assert undone["completed_at"] is None
    assert client.delete(f"/api/v1/thm/{entry_id}").json() == {"success": True}
    assert client.patch(f"/api/v1/thm/{entry_id}", json={"done": True}).status_code == 404


def test_no_xp_for_tracker(client, db_session):
    """Decision 2 of 2026-08-09: done / not done, no points."""
    u = _user(db_session)
    entry = client.post("/api/v1/thm", json={"user_id": u.id, "name": "Nmap"}).json()
    client.patch(f"/api/v1/thm/{entry['id']}", json={"done": True})
    db_session.refresh(u)
    assert (u.total_xp or 0) == 0


def test_done_queues_one_hub_event_and_counts_in_summary(client, db_session, monkeypatch):
    monkeypatch.setattr(hub_publisher.hub_settings, "SYSTEM_GLOWNY_MODULE_KEY", "")
    u = _user(db_session)
    entry = client.post("/api/v1/thm", json={"user_id": u.id, "name": "Burp Suite: The Basics"}).json()
    client.patch(f"/api/v1/thm/{entry['id']}", json={"done": True})
    client.patch(f"/api/v1/thm/{entry['id']}", json={"notes": "repeater"})  # not a second completion

    body = client.get("/api/v1/summary", params={"user_id": u.id}).json()
    assert body["summary"]["thm_completed"] == 1
    assert [e["event_type"] for e in body["events"]] == ["thm_room_completed"]
    assert body["events"][0]["data"]["name"] == "Burp Suite: The Basics"


def test_unknown_user_and_bad_kind(client):
    assert client.post("/api/v1/thm", json={"user_id": 999, "name": "x"}).status_code == 404
    assert client.post("/api/v1/thm", json={"user_id": 1, "name": "x", "kind": "badge"}).status_code == 422
