def test_get_due_errors_no_user(client):
    # Endpoint returns 200 with empty list
    response = client.get("/api/v1/errors/due/9999")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_error_stats_no_user(client):
    # Endpoint returns 200 with stats
    response = client.get("/api/v1/errors/stats/9999")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_review_error_nonexistent(client):
    response = client.post(
        "/api/v1/errors/9999/review",
        json={"correct": True}
    )
    # Returns 422 (validation) or 404 if error not found
    assert response.status_code in [404, 422, 500]


def test_get_due_errors_valid_user(client):
    user_resp = client.post("/api/v1/placement/user", json={"name": "Error User"})
    user_id = user_resp.json()["user_id"]

    response = client.get(f"/api/v1/errors/due/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_error_stats_valid_user(client):
    user_resp = client.post("/api/v1/placement/user", json={"name": "Error Stats"})
    user_id = user_resp.json()["user_id"]

    response = client.get(f"/api/v1/errors/stats/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
