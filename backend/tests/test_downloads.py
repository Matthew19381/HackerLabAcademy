def test_download_lesson_pdf_nonexistent(client):
    response = client.get("/api/v1/download/lesson/nonexistent-slug/pdf")
    assert response.status_code in [404, 500]


def test_download_lesson_audio_nonexistent(client):
    response = client.get("/api/v1/download/lesson/nonexistent-slug/audio")
    assert response.status_code in [404, 500]


def test_download_lesson_bundle_nonexistent(client):
    response = client.get("/api/v1/download/lesson/nonexistent-slug/bundle")
    assert response.status_code in [404, 500]


def test_download_anki_no_user(client):
    response = client.get("/api/v1/download/flashcards/9999/anki")
    assert response.status_code in [404, 500]


def test_download_writeup_pdf_nonexistent(client):
    response = client.get("/api/v1/download/writeups/download/9999")
    assert response.status_code in [404, 500]
