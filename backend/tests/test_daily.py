def test_daily_status_no_user(client):
    # Endpoint doesn't check if user exists, returns 200 with empty data
    response = client.get("/api/v1/daily/status?user_id=9999")
    assert response.status_code == 200
    data = response.json()
    assert "lab_done" in data


def test_daily_status_new_user(client):
    user_resp = client.post("/api/v1/placement/user", json={"name": "Daily User"})
    user_id = user_resp.json()["user_id"]

    response = client.get(f"/api/v1/daily/status?user_id={user_id}")
    assert response.status_code == 200
    data = response.json()
    assert "lab_done" in data
    assert "quiz_done" in data
    assert "flashcard_done" in data
    assert "article_done" in data
