def test_get_writeup_templates(client):
    response = client.get("/api/v1/writeups/templates")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_generate_writeup_invalid_template(client):
    user_resp = client.post("/api/v1/placement/user", json={"name": "Writeup User"})
    user_id = user_resp.json()["user_id"]

    response = client.post(
        "/api/v1/writeups/generate",
        json={"user_id": user_id, "template_id": 9999, "variables": {}}
    )
    assert response.status_code in [404, 500]


def test_get_writeup_history_no_user(client):
    # Endpoint returns 200 with empty list if user not found
    response = client.get("/api/v1/writeups/history/9999")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_download_nonexistent_writeup(client):
    response = client.get("/api/v1/writeups/download/9999")
    assert response.status_code in [404, 500]
