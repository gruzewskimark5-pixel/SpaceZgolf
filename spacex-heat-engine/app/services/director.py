from typing import List

class DirectorBrain:
    def __init__(self):
        self.thresholds = {
            "high_heat": 3.5,
            "mid_heat": 2.0,
            "fatigue_drop": -0.15,
            "dominance_plateau": 0.08
        }

    def evaluate(self,
                 heat_index: float,
                 projected_heat_30s: float,
                 engagement_velocity: float,
                 anchor_presence: bool,
                 ces_score: float,
                 global_avg_ces: float = 1.0) -> List[dict]:

        actions = []

        if projected_heat_30s > 3.8:
            actions.append({
                "policy": "PRIORITIZE_CAMERA",
                "actions": ["elevate_camera_priority", "enable_multi_angle", "trigger_overlay_boost"]
            })

        if anchor_presence and heat_index > 3.0:
            actions.append({
                "policy": "ANCHOR_AMPLIFICATION",
                "actions": ["increase_commentary_intensity", "highlight_anchor_graphics", "clip_auto_generate"]
            })

        if engagement_velocity < self.thresholds["fatigue_drop"]:
            actions.append({
                "policy": "CHAOS_INJECTION",
                "actions": ["inject_chaos_event", "escalate_cluster_interaction", "introduce_new_matchup"]
            })

        # Simplification for prestige check
        if heat_index < 2.0 and not anchor_presence:
            actions.append({
                "policy": "PRESTIGE_GATEKEEP",
                "actions": ["restrict_prestige_access", "route_to_development_matches"]
            })

        if ces_score < global_avg_ces and ces_score > 0:
             actions.append({
                "policy": "CES_OPTIMIZATION",
                "actions": ["deprioritize_broadcast_slot", "route_to_growth_content"]
            })

        return actions

director_brain = DirectorBrain()
