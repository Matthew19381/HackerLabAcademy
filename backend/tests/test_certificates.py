def test_list_certificates_no_user(client):
    # Endpoint returns 200 with empty list if user not found
    response = client.get("/api/v1/certificates/list", params={"user_id": 9999})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_certificates_valid_user(client):
    user_resp = client.post("/api/v1/placement/user", json={"name": "Cert User"})
    user_id = user_resp.json()["user_id"]

    response = client.get("/api/v1/certificates/list", params={"user_id": user_id})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_generate_certificate_invalid_category(client):
    user_resp = client.post("/api/v1/placement/user", json={"name": "Cert Gen"})
    user_id = user_resp.json()["user_id"]

    response = client.get(
        "/api/v1/certificates/generate",
        params={"category": "InvalidCategory", "user_id": user_id}
    )
    assert response.status_code == 400


def test_download_nonexistent_certificate(client):
    response = client.get("/api/v1/certificates/download/nonexistent-code")
    assert response.status_code in [404, 500]
