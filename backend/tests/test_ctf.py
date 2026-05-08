def test_list_ctf_challenges(client):
    response = client.get("/api/v1/ctf/challenges")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_ctf_leaderboard(client):
    response = client.get("/api/v1/ctf/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_nonexistent_ctf(client):
    response = client.get("/api/v1/ctf/challenges/9999")
    assert response.status_code == 404
