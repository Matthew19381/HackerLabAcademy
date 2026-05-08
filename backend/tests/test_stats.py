import pytest
from backend.services.achievement_service import calculate_level_from_xp


def test_calculate_level_from_xp_zero():
    result = calculate_level_from_xp(0)
    assert result["level"] == 1
    assert result["level_name"] == "Skryptowa Dziecię"
    assert result["xp"] == 0


def test_calculate_level_from_xp_level_2():
    # Level 2 requires (2-1)^2 * 20 = 20 XP
    result = calculate_level_from_xp(20)
    assert result["level"] == 2
    assert result["level_name"] == "Skryptowa Dziecię"  # Level 2 is in 1-5 range


def test_calculate_level_from_xp_level_5():
    # Level 5 requires (5-1)^2 * 20 = 320 XP
    result = calculate_level_from_xp(320)
    assert result["level"] == 5
    assert result["level_name"] == "Skryptowa Dziecię"  # Level 5 is in 1-5 range


def test_calculate_level_from_xp_level_10():
    # Level 10 requires (10-1)^2 * 20 = 1620 XP
    result = calculate_level_from_xp(1620)
    assert result["level"] == 10
    assert result["level_name"] == "Nowy Haker"


def test_calculate_level_from_xp_level_25():
    # Level 25 requires (25-1)^2 * 20 = 11520 XP
    result = calculate_level_from_xp(11520)
    assert result["level"] == 25
    assert result["level_name"] == "Łowca Bugów"  # Level 25 is in 21-25 range


def test_calculate_level_from_xp_max_level():
    # Level 50+ should cap at 50
    result = calculate_level_from_xp(50000)
    assert result["level"] == 50
    assert result["progress_percent"] == 100.0


def test_calculate_level_from_xp_progress():
    # At 10 XP: level is 1 (because 10 < 20 required for level 2)
    result = calculate_level_from_xp(10)
    assert result["level"] == 1
    assert result["current_level_xp"] == 0  # Level 1 requires 0 XP
    assert result["next_level_xp"] == 20  # Level 2 requires 20 XP
    assert result["progress_percent"] == 50.0


def test_calculate_level_from_xp_progress_75():
    # At 15 XP: level is 1, progress to level 2 (15/20 = 75%)
    result = calculate_level_from_xp(15)
    assert result["level"] == 1
    assert result["progress_percent"] == 75.0


def test_get_stats_nonexistent_user(client):
    response = client.get("/api/v1/stats/9999")
    assert response.status_code == 404


def test_get_stats_new_user(client):
    create_resp = client.post("/api/v1/placement/user", json={"name": "Bob"})
    user_id = create_resp.json()["user_id"]

    response = client.get(f"/api/v1/stats/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "level_info" in data
    assert "progress" in data
    assert data["user"]["id"] == user_id
    assert data["level_info"]["level"] == 1
