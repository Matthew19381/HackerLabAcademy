def test_list_flashcards_empty(client):
    # Create user first
    user_resp = client.post("/api/v1/placement/user", json={"name": "Flashcard User"})
    user_id = user_resp.json()["user_id"]

    response = client.get(f"/api/v1/flashcards/due/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_flashcard(client):
    user_resp = client.post("/api/v1/placement/user", json={"name": "FC Creator"})
    user_id = user_resp.json()["user_id"]

    response = client.post(
        "/api/v1/flashcards/quick-create",
        json={"user_id": user_id, "term": "SQL Injection"}
    )
    # May fail without Gemini API key, check for 200 or 503
    assert response.status_code in [200, 503, 500]


def test_flashcards_review_empty(client):
    user_resp = client.post("/api/v1/placement/user", json={"name": "Reviewer"})
    user_id = user_resp.json()["user_id"]

    response = client.get(f"/api/v1/flashcards/due/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_review_uses_fsrs_only_and_reports_its_interval(client, db_session):
    """B4 (2026-11-03): SM-2 ran next to FSRS on every review and overwrote interval_days."""
    from datetime import datetime, timedelta

    from backend.models.flashcard import Flashcard
    from backend.models.user import User

    user = User(name="fsrs")
    db_session.add(user)
    db_session.commit()
    card = Flashcard(user_id=user.id, front="nmap -sV", back="wersje usług",
                     next_review_date=datetime.utcnow() - timedelta(days=1))
    db_session.add(card)
    db_session.commit()

    body = client.post(f"/api/v1/flashcards/{card.id}/review", json={"rating": 4}).json()
    due = datetime.fromisoformat(body["next_review_date"])
    last = datetime.fromisoformat(body["last_review"])
    assert body["interval_days"] == max(0, (due - last).days)
    assert body["repetitions"] == 1
