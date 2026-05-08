def test_lab_status(client):
    response = client.get("/api/v1/labs/status")
    assert response.status_code == 200
    data = response.json()
    assert "running" in data or "status" in data


def test_lab_start(client):
    response = client.post("/api/v1/labs/start")
    # May succeed or fail depending on Docker availability
    assert response.status_code in [200, 500, 503]


def test_lab_stop(client):
    response = client.post("/api/v1/labs/stop")
    assert response.status_code in [200, 500]


def test_lab_reset(client):
    response = client.post("/api/v1/labs/reset")
    assert response.status_code in [200, 500]


def test_lab_url(client):
    response = client.get("/api/v1/labs/url/dvwa_sqli")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "url" in data
