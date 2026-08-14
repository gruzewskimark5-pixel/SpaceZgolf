from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

EventKind = Literal[
    "routine",
    "heat_spike",
    "momentum_shift",
    "lead_change",
    "clutch",
    "meltdown",
]


@dataclass(frozen=True)
class ShotEvent:
    event_id: str
    match_id: str
    shot_index: int
    player_id: str
    hole: int
    score_diff: float
    heat: float
    momentum: float
    win_probability: float
    kind: EventKind
    impact: float
    timestamp_ms: int


@dataclass(frozen=True)
class DirectorDecision:
    event_id: str
    match_id: str
    priority: float
    predicted: bool
    decision: str
    reason: str


@dataclass
class MatchResult:
    match_id: str
    events: list[ShotEvent] = field(default_factory=list)
    true_major_event_ids: set[str] = field(default_factory=set)
    decisions: list[DirectorDecision] = field(default_factory=list)


@dataclass(frozen=True)
class ValidationMetrics:
    precision_at_k: float
    recall_at_k: float
    predictive_precision: float
    predictive_recall: float
    mean_lead_time_ms: float
    false_focus_rate: float
    event_integrity: float
    replay_recall: float

    def as_dict(self) -> dict[str, float]:
        return {
            "precision_at_k": round(self.precision_at_k, 4),
            "recall_at_k": round(self.recall_at_k, 4),
            "predictive_precision": round(self.predictive_precision, 4),
            "predictive_recall": round(self.predictive_recall, 4),
            "mean_lead_time_ms": round(self.mean_lead_time_ms, 2),
            "false_focus_rate": round(self.false_focus_rate, 4),
            "event_integrity": round(self.event_integrity, 4),
            "replay_recall": round(self.replay_recall, 4),
        }
