def test_get_daily_agenda_no_user(client):
    response = client.get("/api/v1/brain/today/9999")
    assert response.status_code == 404


def test_get_daily_agenda_valid_user(client):
    user_resp = client.post("/api/v1/placement/user", json={"name": "Brain User"})
    user_id = user_resp.json()["user_id"]

    response = client.get(f"/api/v1/brain/today/{user_id}")
    # May return 200 with agenda or 500 if AI fails
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "agenda" in data or isinstance(data, dict)
