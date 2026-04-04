from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Miakka DI Engine")

# Mock Course Data (since the formula requires specific hole_data properties)
MIAKKA_COURSE_DATA = {
    1: {
        "par": 4,
        "geometry_penalty": 60,
        "hazard_pressure": 40,
        "wind_exposure": {
            "strength_typical": 50,
            "cross_quartering_ratio": 0.4
        },
        "decision_complexity": 2.0,
        "di_baseline": {
            "tour_avg_di": 65.0
        }
    },
    2: {
        "par": 5,
        "geometry_penalty": 70,
        "hazard_pressure": 50,
        "wind_exposure": {
            "strength_typical": 60,
            "cross_quartering_ratio": 0.6
        },
        "decision_complexity": 2.5,
        "di_baseline": {
            "tour_avg_di": 70.0
        }
    },
    # Default hole data for remaining holes 3-18
    **{i: {
        "par": 4,
        "geometry_penalty": 50,
        "hazard_pressure": 50,
        "wind_exposure": {
            "strength_typical": 50,
            "cross_quartering_ratio": 0.5
        },
        "decision_complexity": 2.0,
        "di_baseline": {
            "tour_avg_di": 60.0
        }
    } for i in range(3, 19)}
}

class ScoreEntry(BaseModel):
    hole: int
    score: int

class DICalculationRequest(BaseModel):
    course_id: str
    scores: List[ScoreEntry]

def calculate_di(hole_data, player_score):
    """
    DI = Execution_Complexity × 0.65 + normalize(Decision_Zone) × 0.35
    Returns 0-100 score
    """

    # Execution Complexity (EC) - physical difficulty
    ec = (
        hole_data["geometry_penalty"] * 0.4 +
        hole_data["hazard_pressure"] * 0.3 +
        hole_data["wind_exposure"]["strength_typical"] * 0.3
    )
    ec = min(max(ec, 0), 100)  # cap 0-100

    # Decision Zone (Z) - mental complexity
    z_raw = (
        hole_data["decision_complexity"] * 25 +
        (1 - hole_data["wind_exposure"]["cross_quartering_ratio"]) * 25
    )
    z = min(max(z_raw, 0), 100)  # normalize and cap

    # Final DI score (0-100)
    di = (ec * 0.65) + (z * 0.35)
    di = round(di, 2)

    # Bonus: vs baseline comparison
    baseline_delta = di - hole_data["di_baseline"]["tour_avg_di"]

    return {
        "hole_di": di,
        "vs_baseline": round(baseline_delta, 2),
        "execution_component": round(ec * 0.65, 2),
        "decision_component": round(z * 0.35, 2),
        "player_score": player_score,
        "par": hole_data["par"]
    }

@app.post("/api/rounds/calculate-di")
async def calculate_round_di(request: DICalculationRequest):
    if request.course_id.lower() != "miakka":
        raise HTTPException(status_code=400, detail="Only 'miakka' course_id is currently supported.")

    hole_breakdowns = []
    total_di = 0.0

    for score_entry in request.scores:
        hole_num = score_entry.hole
        if hole_num not in MIAKKA_COURSE_DATA:
            raise HTTPException(status_code=400, detail=f"Invalid hole number: {hole_num}")

        hole_data = MIAKKA_COURSE_DATA[hole_num]
        result = calculate_di(hole_data, score_entry.score)

        total_di += result["hole_di"]

        hole_breakdowns.append({
            "hole": hole_num,
            "di": result["hole_di"],
            "vs_baseline": result["vs_baseline"],
            "execution_component": result["execution_component"],
            "decision_component": result["decision_component"],
            "score": result["player_score"],
            "par": result["par"]
        })

    overall_di = 0.0
    if request.scores:
        overall_di = round(total_di / len(request.scores), 2)

    return {
        "overall_di": overall_di,
        "hole_breakdown": hole_breakdowns
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
