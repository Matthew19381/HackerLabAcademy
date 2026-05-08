def test_list_defense_challenges(client):
    response = client.get("/api/v1/defense/challenges/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_nonexistent_defense_challenge(client):
    response = client.get("/api/v1/defense/challenges/9999")
    assert response.status_code == 404


def test_submit_defense_invalid_challenge(client):
    user_resp = client.post("/api/v1/placement/user", json={"name": "Defense User"})
    user_id = user_resp.json()["user_id"]

    response = client.post(
        "/api/v1/defense/submit",
        json={"challenge_id": 9999, "user_id": user_id, "submitted_code": "test"}
    )
    assert response.status_code in [404, 500]
