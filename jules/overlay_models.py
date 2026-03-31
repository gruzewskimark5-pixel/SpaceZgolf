from pydantic import BaseModel
from typing import List, Literal, Dict, Any

OverlayType = Literal[
    "RIVALRY_BADGE",
    "SHOT_CONTEXT",
    "EDGE_INDICATOR",
    "MOMENTUM_SPIKE",
    "CLOSING_PRESSURE",
]

class RivalryEvent(BaseModel):
    source_event_id: str
    player_a_id: str
    player_b_id: str
    round_id: str
    hole_number: int
    di: float
    event_type: str
    event_ts: float

class RhiSnapshot(BaseModel):
    rhi: float
    momentum: float
    confidence: float
    volatility: float
    priority: float

class Context(BaseModel):
    hole_di: float
    proximity: float  # 0 to 1, e.g., closeness to hole end or score gap
    event_boost: float  # 0 to 1, multiplier for impactful events

class Overlay(BaseModel):
    overlay_id: str
    type: OverlayType
    players: List[str]
    priority: float
    ttl_ms: int
    payload: Dict[str, Any]
    reason: str
    created_at: float
