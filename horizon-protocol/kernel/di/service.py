from typing import Dict, List
from .schemas import HoleData, HoleDIResult

# Mock database of Miakka holes to avoid needing a full DB just yet
MIAKKA_HOLES = [
    HoleData(
        id=1, course_id="miakka", number=1, par=4, yards_champion=450,
        geometry_penalty=1.1, hazard_pressure="medium", wind_strength=10.0,
        decision_complexity="medium", cross_quartering_ratio=0.5, tour_avg_di=50.0
    ),
    HoleData(
        id=2, course_id="miakka", number=2, par=3, yards_champion=180,
        geometry_penalty=1.2, hazard_pressure="high", wind_strength=15.0,
        decision_complexity="complex", cross_quartering_ratio=0.8, tour_avg_di=65.0
    ),
    HoleData(
        id=3, course_id="miakka", number=3, par=5, yards_champion=560,
        geometry_penalty=1.0, hazard_pressure="low", wind_strength=5.0,
        decision_complexity="simple", cross_quartering_ratio=0.2, tour_avg_di=40.0
    ),
    HoleData(
        id=4, course_id="miakka", number=4, par=4, yards_champion=410,
        geometry_penalty=1.1, hazard_pressure="medium", wind_strength=12.0,
        decision_complexity="medium", cross_quartering_ratio=0.4, tour_avg_di=55.0
    ),
    HoleData(
        id=5, course_id="miakka", number=5, par=4, yards_champion=480,
        geometry_penalty=1.3, hazard_pressure="extreme", wind_strength=20.0,
        decision_complexity="complex", cross_quartering_ratio=0.9, tour_avg_di=80.0
    ),
    HoleData(
        id=6, course_id="miakka", number=6, par=3, yards_champion=210,
        geometry_penalty=1.2, hazard_pressure="high", wind_strength=18.0,
        decision_complexity="medium", cross_quartering_ratio=0.7, tour_avg_di=70.0
    ),
    HoleData(
        id=7, course_id="miakka", number=7, par=4, yards_champion=380,
        geometry_penalty=1.0, hazard_pressure="medium", wind_strength=8.0,
        decision_complexity="complex", cross_quartering_ratio=0.3, tour_avg_di=45.0
    ),
    HoleData(
        id=8, course_id="miakka", number=8, par=5, yards_champion=600,
        geometry_penalty=1.1, hazard_pressure="low", wind_strength=10.0,
        decision_complexity="simple", cross_quartering_ratio=0.5, tour_avg_di=42.0
    ),
    HoleData(
        id=9, course_id="miakka", number=9, par=4, yards_champion=460,
        geometry_penalty=1.2, hazard_pressure="high", wind_strength=15.0,
        decision_complexity="complex", cross_quartering_ratio=0.6, tour_avg_di=68.0
    ),
    HoleData(
        id=10, course_id="miakka", number=10, par=4, yards_champion=420,
        geometry_penalty=1.1, hazard_pressure="medium", wind_strength=10.0,
        decision_complexity="medium", cross_quartering_ratio=0.4, tour_avg_di=52.0
    ),
    HoleData(
        id=11, course_id="miakka", number=11, par=3, yards_champion=160,
        geometry_penalty=1.0, hazard_pressure="low", wind_strength=5.0,
        decision_complexity="simple", cross_quartering_ratio=0.2, tour_avg_di=35.0
    ),
    HoleData(
        id=12, course_id="miakka", number=12, par=5, yards_champion=580,
        geometry_penalty=1.1, hazard_pressure="medium", wind_strength=12.0,
        decision_complexity="complex", cross_quartering_ratio=0.5, tour_avg_di=60.0
    ),
    HoleData(
        id=13, course_id="miakka", number=13, par=4, yards_champion=440,
        geometry_penalty=1.2, hazard_pressure="high", wind_strength=15.0,
        decision_complexity="medium", cross_quartering_ratio=0.6, tour_avg_di=62.0
    ),
    HoleData(
        id=14, course_id="miakka", number=14, par=4, yards_champion=390,
        geometry_penalty=1.0, hazard_pressure="medium", wind_strength=8.0,
        decision_complexity="complex", cross_quartering_ratio=0.3, tour_avg_di=48.0
    ),
    HoleData(
        id=15, course_id="miakka", number=15, par=5, yards_champion=540,
        geometry_penalty=1.1, hazard_pressure="low", wind_strength=10.0,
        decision_complexity="simple", cross_quartering_ratio=0.4, tour_avg_di=45.0
    ),
    HoleData(
        id=16, course_id="miakka", number=16, par=3, yards_champion=230,
        geometry_penalty=1.3, hazard_pressure="extreme", wind_strength=20.0,
        decision_complexity="complex", cross_quartering_ratio=0.8, tour_avg_di=85.0
    ),
    HoleData(
        id=17, course_id="miakka", number=17, par=4, yards_champion=470,
        geometry_penalty=1.2, hazard_pressure="high", wind_strength=18.0,
        decision_complexity="medium", cross_quartering_ratio=0.7, tour_avg_di=72.0
    ),
    HoleData(
        id=18, course_id="miakka", number=18, par=4, yards_champion=490,
        geometry_penalty=1.3, hazard_pressure="extreme", wind_strength=25.0,
        decision_complexity="complex", cross_quartering_ratio=0.9, tour_avg_di=88.0
    )
]

def get_holes_by_course(course_id: str) -> List[HoleData]:
    if course_id == "miakka":
        return MIAKKA_HOLES
    return []

def calculate_hole_di(hole_data: HoleData, player_score: int) -> HoleDIResult:
    # Execution Complexity (EC) - how physically demanding the hole is
    geometry_penalty = hole_data.geometry_penalty or 1.0
    hazard_pressure_val = 0
    if hole_data.hazard_pressure == "extreme":
        hazard_pressure_val = 3
    elif hole_data.hazard_pressure == "high":
        hazard_pressure_val = 2
    elif hole_data.hazard_pressure == "medium":
        hazard_pressure_val = 1

    wind_strength = hole_data.wind_strength or 0.0

    ec = (
        geometry_penalty * 0.4 +
        hazard_pressure_val * 0.3 +
        (wind_strength / 20.0) * 0.3
    )
    ec = max(min(ec * 100.0, 100.0), 0.0)  # Scale to 0-100 roughly

    # Decision Zone (Z) - how mentally complex the hole is
    decision_complexity_val = 25
    if hole_data.decision_complexity == "complex":
        decision_complexity_val = 75
    elif hole_data.decision_complexity == "medium":
        decision_complexity_val = 50

    cross_quartering_ratio = hole_data.cross_quartering_ratio or 0.0

    z_raw = (
        decision_complexity_val +
        (1.0 - cross_quartering_ratio) * 25.0
    )
    z = max(min(z_raw, 100.0), 0.0)

    # Final DI score (0-100)
    di = (ec * 0.65) + (z * 0.35)
    di = round(di, 2)

    # Bonus: vs baseline comparison
    tour_avg_di = hole_data.tour_avg_di or 0.0
    baseline_delta = di - tour_avg_di

    return HoleDIResult(
        hole_di=di,
        vs_baseline=round(baseline_delta, 2),
        execution_component=round(ec * 0.65, 2),
        decision_component=round(z * 0.35, 2),
        player_score=player_score,
        par=hole_data.par,
        number=hole_data.number
    )
