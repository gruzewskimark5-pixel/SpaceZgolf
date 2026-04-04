import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_calculate_di_valid_request():
    payload = {
        "course_id": "miakka",
        "scores": [
            {"hole": 1, "score": 4},
            {"hole": 2, "score": 5}
        ]
    }
    response = client.post("/api/rounds/calculate-di", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "overall_di" in data
    assert "hole_breakdown" in data
    assert len(data["hole_breakdown"]) == 2

    hole_1 = data["hole_breakdown"][0]
    assert hole_1["hole"] == 1
    assert "di" in hole_1
    assert hole_1["score"] == 4
    assert hole_1["par"] == 4
    assert "vs_baseline" in hole_1
    assert "execution_component" in hole_1
    assert "decision_component" in hole_1

def test_calculate_di_invalid_course():
    payload = {
        "course_id": "augusta",
        "scores": [
            {"hole": 1, "score": 4}
        ]
    }
    response = client.post("/api/rounds/calculate-di", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Only 'miakka' course_id is currently supported."

def test_calculate_di_invalid_hole():
    payload = {
        "course_id": "miakka",
        "scores": [
            {"hole": 19, "score": 4}
        ]
    }
    response = client.post("/api/rounds/calculate-di", json=payload)
    assert response.status_code == 400
    assert "Invalid hole number" in response.json()["detail"]
