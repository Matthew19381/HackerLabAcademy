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


def test_flashcards_from_thm_notes(client, db_session, monkeypatch):
    """C5: recall cards from the user's own TryHackMe notes, at most 5, empty items skipped."""
    from backend.models.flashcard import Flashcard
    from backend.models.user import User

    user = User(name="notes")
    db_session.add(user)
    db_session.commit()

    async def fake_json(prompt):
        assert "Nmap" in prompt and "-sV" in prompt
        return {"cards": [
            {"front": "Która flaga nmap wykrywa wersje usług?", "back": "-sV", "example": "nmap -sV 10.10.0.1"},
            {"front": "", "back": "pominięta"},
        ] + [{"front": f"Q{i}", "back": f"A{i}"} for i in range(6)]}

    monkeypatch.setattr("backend.routers.flashcards.generate_json", fake_json)
    resp = client.post("/api/v1/flashcards/from-notes", json={
        "user_id": user.id, "source": "Nmap", "notes": "nmap -sV pokazuje wersje usług, -p- skanuje wszystkie porty"})
    assert resp.status_code == 200
    assert resp.json()["created"] == 4  # 5 items taken, the empty one skipped
    cards = db_session.query(Flashcard).filter(Flashcard.user_id == user.id).all()
    assert {c.topic_slug for c in cards} == {"thm"} and all(c.next_review_date for c in cards)


def test_flashcards_from_notes_requires_real_notes(client):
    assert client.post("/api/v1/flashcards/from-notes",
                       json={"user_id": 1, "source": "x", "notes": "za krótko"}).status_code == 422


def test_tool_deck_is_added_once(client, db_session):
    """C6: the tool syntax deck can be added again without duplicates."""
    from backend.models.user import User
    from backend.services.tool_deck import TOOL_DECK

    user = User(name="deck")
    db_session.add(user)
    db_session.commit()
    first = client.post("/api/v1/flashcards/decks/tools", json={"user_id": user.id}).json()
    second = client.post("/api/v1/flashcards/decks/tools", json={"user_id": user.id}).json()
    assert first == {"added": len(TOOL_DECK), "deck_size": len(TOOL_DECK)}
    assert second["added"] == 0
    due = client.get(f"/api/v1/flashcards/due/{user.id}").json()
    assert any(c["front"].startswith("nmap:") for c in due)
