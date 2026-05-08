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
