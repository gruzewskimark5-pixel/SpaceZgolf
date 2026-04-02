from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal

class HoleData(BaseModel):
    id: int
    course_id: str
    number: int
    par: int
    yards_champion: Optional[int] = None
    yards_blue: Optional[int] = None
    yards_white: Optional[int] = None
    fairway_width_avg: Optional[float] = None
    green_depth: Optional[float] = None
    green_width: Optional[float] = None
    primary_angle: Optional[str] = None
    hazard_pressure: Optional[Literal["extreme", "high", "medium", "low", "none"]] = "none"
    wind_direction: Optional[str] = None
    wind_strength: Optional[float] = 0.0
    cross_quartering_ratio: Optional[float] = 0.0
    tour_avg_di: Optional[float] = 0.0
    amateur_avg_di: Optional[float] = 0.0
    geometry_penalty: Optional[float] = 1.0
    decision_complexity: Optional[Literal["complex", "medium", "simple"]] = "simple"
    signature_test: Optional[str] = None

class HoleDIResult(BaseModel):
    hole_di: float
    vs_baseline: float
    execution_component: float
    decision_component: float
    player_score: int
    par: int
    number: int

class DICalculationRequest(BaseModel):
    course_id: str
    scores: Dict[int, int] = Field(..., description="A mapping of hole number to player score")

class DICalculationResult(BaseModel):
    overall_di: float
    hole_breakdown: List[HoleDIResult]
