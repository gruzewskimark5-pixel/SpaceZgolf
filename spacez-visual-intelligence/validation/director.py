from __future__ import annotations

from dataclasses import dataclass

from .models import DirectorDecision, ShotEvent


@dataclass(frozen=True)
class DirectorConfig:
    # V1/V2-style scoring is deliberately deterministic for validation.
    heat_weight: float = 0.40
    momentum_weight: float = 0.25
    impact_weight: float = 0.25
    comeback_weight: float = 0.10
    major_threshold: float = 0.72
    prediction_window: int = 3


class DirectorBrain:
    """Pure decision function: no network, clock, randomness, or mutable state."""

    def __init__(self, config: DirectorConfig | None = None) -> None:
        self.config = config or DirectorConfig()

    def priority(self, event: ShotEvent) -> float:
        comeback = min(1.0, abs(event.win_probability - 0.5) * 2.0)
        score = (
            event.heat / 100.0 * self.config.heat_weight
            + abs(event.momentum) / 100.0 * self.config.momentum_weight
            + event.impact * self.config.impact_weight
            + comeback * self.config.comeback_weight
        )
        return max(0.0, min(1.0, score))

    def decide(self, event: ShotEvent, future_events: list[ShotEvent] | None = None) -> DirectorDecision:
        future_events = future_events or []
        current = self.priority(event)
        future_best = max((self.priority(e) for e in future_events), default=0.0)

        # Predictive focus: flag an approaching major event before it happens.
        predicted = future_best >= self.config.major_threshold and future_best > current + 0.08
        if predicted:
            decision = "PREPARE_FOCUS"
            reason = "future_major_event"
        elif current >= self.config.major_threshold:
            decision = "FOCUS_NOW"
            reason = event.kind
        else:
            decision = "MONITOR"
            reason = "below_focus_threshold"

        return DirectorDecision(
            event_id=event.event_id,
            match_id=event.match_id,
            priority=current,
            predicted=predicted,
            decision=decision,
            reason=reason,
        )
