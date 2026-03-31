from dataclasses import dataclass
from typing import List, Any, Dict


@dataclass
class Round:
    id: str
    score: int
    status: str

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Round":
        return Round(
            id=d["id"],
            score=d["score"],
            status=d["status"],
        )


@dataclass
class EventInput:
    player_id: str
    action: str
    value: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "action": self.action,
            "value": self.value,
        }


@dataclass
class EventResponse:
    event_id: str
    status: str

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "EventResponse":
        return EventResponse(
            event_id=d["event_id"],
            status=d["status"],
        )


@dataclass
class LeaderboardEntry:
    player_id: str
    score: int

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "LeaderboardEntry":
        return LeaderboardEntry(
            player_id=d["player_id"],
            score=d["score"],
        )


@dataclass
class Leaderboard:
    entries: List[LeaderboardEntry]

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Leaderboard":
        return Leaderboard(
            entries=[LeaderboardEntry.from_dict(e) for e in d.get("entries", [])]
        )

from datetime import datetime

@dataclass
class RivalryEvent:
    source_event_id: str
    player_a_id: str
    player_b_id: str
    round_id: str
    hole_number: int
    di: float
    event_type: str
    base_weight: float
    event_ts: datetime

    def to_dict(self) -> Dict[str, Any]:
        """
        Normalize payload keys to match sync client.
        """
        return {
            "source_event_id": self.source_event_id,
            "player_a_id": self.player_a_id,
            "player_b_id": self.player_b_id,
            "round_id": self.round_id,
            "hole_number": self.hole_number,
            "di": self.di,
            "event_type": self.event_type,
            "base_weight": self.base_weight,
            "event_ts": self.event_ts.isoformat(),
        }
