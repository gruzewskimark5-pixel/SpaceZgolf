from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/v1/digital-twin", tags=["Digital Twin"])

# --- Models ---
class ContextInfo(BaseModel):
    format: str
    stakes: str
    hole: int
    par: int
    yardage: int
    wind: str

class SwingInfo(BaseModel):
    club: str
    ball_speed: float
    club_speed: float
    launch: float
    spin: int
    attack_angle: float
    face_to_path: float

class OutcomeInfo(BaseModel):
    carry: int
    total: int
    fairway: bool
    miss_pattern: str

class DigitalTwinEvent(BaseModel):
    event_id: str
    player_id: str
    timestamp: datetime
    context: ContextInfo
    swing: SwingInfo
    outcome: OutcomeInfo

    # Enrichment fields
    cluster: Optional[str] = None
    heat_at_time: Optional[float] = None
    momentum: Optional[float] = None

class DigitalTwinPlayerState(BaseModel):
    player_id: str
    name: str
    cluster: str
    current_heat: float
    base_heat: float
    momentum: float
    trend_direction: str  # "↑", "↓", "→"
    total_events: int
    avg_ball_speed: float
    fairway_percentage: float
    last_event_id: Optional[str] = None
    last_activity_date: Optional[datetime] = None

# --- In-Memory Stores for MVP ---
TWIN_EVENTS_DB: Dict[str, DigitalTwinEvent] = {}
TWIN_PLAYER_STATES: Dict[str, DigitalTwinPlayerState] = {}

# --- APIs ---
@router.post("/ingest", response_model=DigitalTwinEvent)
async def ingest_event(event: DigitalTwinEvent):
    if not event.event_id:
        event.event_id = str(uuid.uuid4())

    from ..apex_roster import ROSTER
    from ..aggregates import update_player_state_from_events

    player = ROSTER.get(event.player_id)

    if event.player_id not in TWIN_PLAYER_STATES:
        TWIN_PLAYER_STATES[event.player_id] = DigitalTwinPlayerState(
            player_id=event.player_id,
            name=player.name if player else event.player_id,
            cluster=player.cluster if player else "Unknown",
            base_heat=player.base_heat if player else 1.0,
            current_heat=player.base_heat if player else 1.0,
            momentum=player.momentum_score if player else 0.0,
            trend_direction="→",
            total_events=0,
            avg_ball_speed=0.0,
            fairway_percentage=0.0
        )

    # 1. Persist Event First
    TWIN_EVENTS_DB[event.event_id] = event

    # 2. Get All Player Events for Aggregate Updating
    state = TWIN_PLAYER_STATES[event.player_id]
    player_events = [e for e in TWIN_EVENTS_DB.values() if e.player_id == event.player_id]

    # 3. Update Aggregates (Momentum, Heat, Trend) via external logic
    state = update_player_state_from_events(state, player_events)

    # Update Basic Stats
    total = state.total_events
    state.avg_ball_speed = ((state.avg_ball_speed * total) + event.swing.ball_speed) / (total + 1)

    fairway_hits = int((state.fairway_percentage / 100.0) * total) if total > 0 else 0
    if event.outcome.fairway: fairway_hits += 1
    state.fairway_percentage = (fairway_hits / (total + 1)) * 100.0

    state.total_events += 1
    state.last_event_id = event.event_id
    state.last_activity_date = event.timestamp

    # Enrich Event with the newly computed state
    event.cluster = state.cluster
    event.heat_at_time = state.current_heat
    event.momentum = state.momentum

    return event

@router.get("/player/{player_id}", response_model=Dict)
async def get_player_twin(player_id: str):
    state = TWIN_PLAYER_STATES.get(player_id)
    if not state:
        raise HTTPException(404, "Digital Twin for player not found")

    recent_events = [e for e in TWIN_EVENTS_DB.values() if e.player_id == player_id]
    recent_events.sort(key=lambda x: x.timestamp, reverse=True)

    return {
        "state": state.model_dump(),
        "recent_events": [e.model_dump() for e in recent_events[:5]]
    }

@router.get("/event/{event_id}", response_model=DigitalTwinEvent)
async def get_event_twin(event_id: str):
    event = TWIN_EVENTS_DB.get(event_id)
    if not event:
        raise HTTPException(404, "Event not found")
    return event
