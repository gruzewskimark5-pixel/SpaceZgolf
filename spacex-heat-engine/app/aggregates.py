from datetime import datetime, timedelta, timezone
from typing import List
from .apex_models import Player
from .routers.digital_twin import DigitalTwinEvent, DigitalTwinPlayerState

def compute_momentum(events: List[DigitalTwinEvent]) -> float:
    """
    Returns momentum in [-1.0, 1.0] based on last 30 days of events.
    Simple heuristic: more recent + better outcomes -> higher momentum.
    """
    if not events:
        return 0.0

    now = datetime.now(timezone.utc)
    # Be robust to naive vs aware datetimes for MVP
    window_start = now - timedelta(days=30)

    recent = []
    for e in events:
        evt_time = e.timestamp.replace(tzinfo=timezone.utc) if e.timestamp.tzinfo is None else e.timestamp
        if evt_time >= window_start:
            recent.append(e)

    if not recent:
        return -0.2  # stale

    score = 0.0
    for e in recent:
        evt_time = e.timestamp.replace(tzinfo=timezone.utc) if e.timestamp.tzinfo is None else e.timestamp
        age_days = (now - evt_time).days + 1
        recency_weight = 1.0 / age_days

        carry = e.outcome.carry
        fairway = 1.0 if e.outcome.fairway else 0.0

        local = (carry / 300.0) + fairway  # ~0-2
        score += local * recency_weight

    # Normalize
    # typical range ~0-3 -> map to [-1, 1]
    norm = max(0.0, min(score / 2.0, 2.0))  # clamp 0-2
    momentum = (norm - 1.0)  # -1 to +1
    return round(momentum, 3)

def trend_from_momentum(momentum: float) -> str:
    if momentum > 0.15:
        return "↑"
    if momentum < -0.15:
        return "↓"
    return "→"

def update_player_state_from_events(state: DigitalTwinPlayerState, events: List[DigitalTwinEvent]) -> DigitalTwinPlayerState:
    momentum = compute_momentum(events)
    trend = trend_from_momentum(momentum)

    state.momentum = momentum
    state.trend_direction = trend

    # Recalculate Heat Based on Momentum (Base Heat * (1.0 + momentum * 0.3))
    recency_boost = 1.0 + (state.momentum * 0.3)
    state.current_heat = round(state.base_heat * recency_boost, 3)

    return state
