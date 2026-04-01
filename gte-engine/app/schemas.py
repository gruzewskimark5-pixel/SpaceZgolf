from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime, timezone

class RawTelemetryEvent(BaseModel):
    event_id: str
    entity_id: str
    ts: int = Field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp() * 1000))
    activity: str
    environment: str
    raw_metrics: Dict[str, float]

class BaselineContext(BaseModel):
    window: str
    context: str

class NormalizedMetrics(BaseModel):
    accuracy: float
    efficiency_score: float

class Outcome(BaseModel):
    delta: Dict[str, float]
    normalized: NormalizedMetrics
    confidence: float
    baseline: BaselineContext

class UnifiedCognitiveEvent(BaseModel):
    event_id: str
    entity_id: str
    ts: int
    raw_payload: RawTelemetryEvent
    outcome: Outcome
    integrity_score: float
    gte_score: float
    version: str = "1.0.0"
