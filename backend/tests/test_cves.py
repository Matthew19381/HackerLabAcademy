def test_list_cves(client):
    response = client.get("/api/v1/cves/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_nonexistent_cve(client):
    response = client.get("/api/v1/cves/nonexistent-cve-12345")
    assert response.status_code == 404


def test_refresh_cves(client):
    # POST to refresh (may fail without API key, check for 200 or 503)
    response = client.post("/api/v1/cves/refresh")
    assert response.status_code in [200, 503]
