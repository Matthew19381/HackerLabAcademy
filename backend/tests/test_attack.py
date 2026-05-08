def test_list_scenarios(client):
    response = client.get("/api/v1/attack/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_nonexistent_scenario(client):
    response = client.get("/api/v1/attack/scenarios/9999")
    assert response.status_code == 404


def test_get_scenario_valid(client):
    # Get list first to find a valid ID
    response = client.get("/api/v1/attack/scenarios")
    scenarios = response.json()
    if len(scenarios) > 0:
        scenario_id = scenarios[0]["id"]
        response = client.get(f"/api/v1/attack/scenarios/{scenario_id}")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "steps" in data


def test_start_scenario_invalid_user(client):
    # Try to start with non-existent user
    response = client.post(
        "/api/v1/attack/scenarios/1/start",
        params={"user_id": 9999}
    )
    assert response.status_code == 404


def test_submit_step_invalid_session(client):
    response = client.post(
        "/api/v1/attack/scenarios/9999/submit",
        json={"user_id": 1, "answer": "test"}
    )
    # Returns 422 (validation) or 404 if session not found
    assert response.status_code in [404, 422, 500]
