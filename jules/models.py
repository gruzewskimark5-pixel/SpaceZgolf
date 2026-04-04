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
