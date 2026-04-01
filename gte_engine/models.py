from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid

class EventState(BaseModel):
    biometrics: Dict[str, float] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)

class EventDecision(BaseModel):
    latency_ms: float
    choice: str = ""
    confidence: Optional[float] = None
    complexity: Optional[float] = None

class EventCausality(BaseModel):
    factors: List[Dict[str, Any]] = Field(default_factory=list)

class EventOutcome(BaseModel):
    performance_delta: float = 0.0
    accuracy: float = 0.0
    latency: float = 0.0
    raw_metrics: Dict[str, Any] = Field(default_factory=dict)

class EventScoring(BaseModel):
    performance_score: float
    integrity_score: float
    components: Dict[str, float] = Field(default_factory=dict)

class EventLeaderboard(BaseModel):
    delta_rank: int
    current_rank: int

class EventIntegrity(BaseModel):
    score: float
    flags: List[str] = Field(default_factory=list)
    factors: Dict[str, float] = Field(default_factory=dict)

class UnifiedCognitiveEvent(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    entity_id: str

    state: EventState
    decision: EventDecision
    causality: EventCausality
    outcome: EventOutcome

    scoring: Optional[EventScoring] = None
    leaderboard: Optional[EventLeaderboard] = None
    integrity: Optional[EventIntegrity] = None
