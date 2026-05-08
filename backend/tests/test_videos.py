def test_list_videos(client):
    response = client.get("/api/v1/videos/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_videos_with_category_filter(client):
    response = client.get("/api/v1/videos/?category=OWASP Top 10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_video_topics(client):
    response = client.get("/api/v1/videos/topics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
