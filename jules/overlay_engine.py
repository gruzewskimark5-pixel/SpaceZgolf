import time
import uuid
from typing import List, Dict, Tuple
from .overlay_models import Overlay, RivalryEvent, RhiSnapshot, Context

class OverlayEngine:
    def __init__(self, min_priority: float = 0.4, cooldown_seconds: int = 5, max_overlays_per_window: int = 2):
        self.min_priority = min_priority
        self.cooldown_seconds = cooldown_seconds
        self.max_overlays_per_window = max_overlays_per_window

        self.last_shown: Dict[str, float] = {}
        self.active_overlays: List[Overlay] = []
        self.recent_keys: Dict[str, float] = {}

    def _now(self) -> float:
        return time.time()

    def _prune(self, now: float):
        """Remove expired overlays from active list and recent keys"""
        self.active_overlays = [
            o for o in self.active_overlays
            if (now - o.created_at) * 1000 < o.ttl_ms
        ]

        # Prune recent keys (deduplication cache of 3s)
        self.recent_keys = {
            k: v for k, v in self.recent_keys.items()
            if (now - v) < 3.0
        }

    def build_overlays(
        self,
        event: RivalryEvent,
        rhi: RhiSnapshot,
        ctx: Context,
    ) -> List[Overlay]:
        now = self._now()
        self._prune(now)

        # 0. Gate on confidence
        if rhi.confidence < 0.5:
            return []

        candidates: List[Overlay] = []

        # 1. Compute scores
        rivalry_score = rhi.rhi * abs(rhi.momentum) * rhi.confidence
        di_score = ctx.hole_di
        proximity = ctx.proximity
        event_boost = ctx.event_boost

        priority = (
            0.4 * rivalry_score
            + 0.3 * di_score
            + 0.2 * proximity
            + 0.1 * event_boost
        )

        # Base debug info
        debug_trace = {
            "rhi": rhi.rhi,
            "momentum": rhi.momentum,
            "hole_di": ctx.hole_di,
            "proximity": ctx.proximity,
            "event_boost": ctx.event_boost
        }

        # Example: Rivalry Badge
        if rhi.rhi > 0.6 and proximity > 0.5:
            candidates.append(
                Overlay(
                    overlay_id=str(uuid.uuid4()),
                    type="RIVALRY_BADGE",
                    players=[event.player_a_id, event.player_b_id],
                    priority=priority,
                    ttl_ms=4000,
                    payload={
                        "label": f"{event.player_a_id} vs {event.player_b_id}",
                        "rhi": rhi.rhi,
                        "band": "Volatile" if rhi.volatility > 0.3 else "Stable",
                        "_debug": debug_trace
                    },
                    reason="RHI>0.6 AND proximity>0.5",
                    created_at=now,
                )
            )

        # Filter by priority, deduplication, and cooldown
        filtered: List[Overlay] = []

        candidates.sort(key=lambda o: o.priority, reverse=True)

        for o in candidates:
            if o.priority < self.min_priority:
                continue

            dedup_key = f"{o.type}:{','.join(sorted(o.players))}"
            if dedup_key in self.recent_keys:
                continue

            last = self.last_shown.get(o.type)
            if last and (now - last) < self.cooldown_seconds:
                continue

            filtered.append(o)

            # State updates
            self.last_shown[o.type] = now
            self.recent_keys[dedup_key] = now
            self.active_overlays.append(o)

            if len(filtered) >= self.max_overlays_per_window:
                break

        return filtered
