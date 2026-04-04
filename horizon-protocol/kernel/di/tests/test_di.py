import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from ..router import router
from ..schemas import HoleData
from ..service import calculate_hole_di

app = FastAPI()
app.include_router(router, prefix="/api/rounds")
client = TestClient(app)

def test_calculate_hole_di():
    hole = HoleData(
        id=1, course_id="miakka", number=1, par=4, yards_champion=450,
        geometry_penalty=1.1, hazard_pressure="medium", wind_strength=10.0,
        decision_complexity="medium", cross_quartering_ratio=0.5, tour_avg_di=50.0
    )
    result = calculate_hole_di(hole, 4)

    # Check bounds and basic math
    assert 0 <= result.hole_di <= 100
    assert result.player_score == 4
    assert result.par == 4
    assert result.number == 1

    # Check EC formula
    # ec = 1.1 * 0.4 + 1 * 0.3 + (10.0/20.0) * 0.3 = 0.44 + 0.3 + 0.15 = 0.89 -> 89.0
    # ec_component = 89.0 * 0.65 = 57.85
    assert result.execution_component == 57.85

    # Check Z formula
    # z_raw = 50 + (1.0 - 0.5) * 25.0 = 50 + 12.5 = 62.5
    # z_component = 62.5 * 0.35 = 21.875 -> 21.88
    assert result.decision_component == 21.88

    # Check final DI
    # di = 57.85 + 21.875 = 79.725 -> 79.72 (python round-half-to-even)
    assert result.hole_di == 79.72

    # Check vs baseline
    # vs_baseline = 79.72 - 50.0 = 29.72
    assert result.vs_baseline == 29.72

def test_calculate_di_endpoint():
    request_data = {
        "course_id": "miakka",
        "scores": {
            1: 4,
            2: 3,
            3: 5
        }
    }
    response = client.post("/api/rounds/calculate-di", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "overall_di" in data
    assert "hole_breakdown" in data
    assert len(data["hole_breakdown"]) == 3

    assert data["hole_breakdown"][0]["number"] == 1
    assert data["hole_breakdown"][1]["number"] == 2
    assert data["hole_breakdown"][2]["number"] == 3

def test_calculate_di_endpoint_not_found():
    request_data = {
        "course_id": "unknown_course",
        "scores": {1: 4}
    }
    response = client.post("/api/rounds/calculate-di", json=request_data)
    assert response.status_code == 404
