from datetime import timezone
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

class EventState(BaseModel):
    biometrics: Dict[str, Any] = Field(default_factory=dict)
    environment: Dict[str, Any] = Field(default_factory=dict)

class EventDecision(BaseModel):
    latency_ms: Optional[int] = None
    option_selected: str
    confidence: float

class EventCausality(BaseModel):
    factors: Dict[str, float] = Field(default_factory=dict)

class EventOutcome(BaseModel):
    performance_delta: float
    accuracy_delta: Optional[float] = None
    latency_delta: Optional[float] = None
    accuracy: float
    latency_ms: Optional[int] = None

class IntegrityDetails(BaseModel):
    score: float
    flags: List[str] = Field(default_factory=list)
    factors: Dict[str, float] = Field(default_factory=dict)

class ScoringDetails(BaseModel):
    performance_score: float
    integrity_score: float
    components: Dict[str, float] = Field(default_factory=dict)

class LeaderboardDetails(BaseModel):
    delta_rank: int
    current_rank: int

class UnifiedCognitiveEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    entity_id: str

    state: EventState
    decision: EventDecision
    causality: EventCausality
    outcome: EventOutcome

    integrity: Optional[IntegrityDetails] = None
    scoring: Optional[ScoringDetails] = None
    leaderboard: Optional[LeaderboardDetails] = None
