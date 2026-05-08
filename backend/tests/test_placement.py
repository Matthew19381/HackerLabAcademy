def test_create_user(client):
    response = client.post("/api/v1/placement/user", json={"name": "Test User"})
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["name"] == "Test User"


def test_get_user(client):
    create_resp = client.post("/api/v1/placement/user", json={"name": "Alice"})
    user_id = create_resp.json()["user_id"]

    response = client.get(f"/api/v1/placement/user/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["name"] == "Alice"
    assert data["total_xp"] == 0
    assert data["streak_days"] == 0


def test_get_nonexistent_user(client):
    response = client.get("/api/v1/placement/user/9999")
    assert response.status_code == 404
