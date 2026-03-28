from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Players
class PlayerCreate(BaseModel):
    name: str
    role: str

class PlayerResponse(PlayerCreate):
    id: UUID
    authority_score: float
    narrative_weight: float
    volatility_score: float
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# Matches
class MatchCreate(BaseModel):
    title: str
    phase: str

class MatchResponse(MatchCreate):
    id: UUID
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# Events
class EventCreate(BaseModel):
    match_id: UUID
    phase_multiplier: float = 1.0
    novelty_bonus: float = 0.0
    players: Optional[List[UUID]] = []

class EventResponse(BaseModel):
    id: UUID
    match_id: UUID
    timestamp: datetime
    phase_multiplier: float
    novelty_bonus: float
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# Metrics
class EngagementCreate(BaseModel):
    views: int
    retention: float
    interactions: int
    peak_concurrent: int

class RevenueCreate(BaseModel):
    revenue: float
    source: Optional[str] = "unknown"
