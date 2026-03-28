from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

CLUSTERS = ["Chaos", "Stability", "Prestige", "Narrative-Commerce", "Noise"]

class Player(BaseModel):
    id: str
    name: str
    cluster: str
    base_heat: float
    volatility: float
    authority: float
    last_activity_date: Optional[datetime] = None
    momentum_score: float = 0.0   # -1.0 to 1.0
    trend_direction: str = "→"     # ↑ ↓ →
    decay_rate: float = 0.05

    def current_heat(self) -> float:
        # Temporal adjustment
        recency_boost = 1.0 + (self.momentum_score * 0.3)
        return round(self.base_heat * recency_boost, 3)
