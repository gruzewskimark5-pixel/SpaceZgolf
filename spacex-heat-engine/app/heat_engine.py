import random
from typing import Tuple, Dict

# Cluster Compatibility Matrix (numerical multipliers)
COMPATIBILITY_MATRIX: Dict[str, Dict[str, float]] = {
    "Chaos": {
        "Chaos": 1.4, "Stability": 0.7, "Prestige": 1.9, "Narrative-Commerce": 2.1, "Noise": 1.6
    },
    "Stability": {
        "Chaos": 0.7, "Stability": 0.9, "Prestige": 1.3, "Narrative-Commerce": 1.1, "Noise": 0.8
    },
    "Prestige": {
        "Chaos": 1.9, "Stability": 1.3, "Prestige": 1.0, "Narrative-Commerce": 2.3, "Noise": 1.2
    },
    "Narrative-Commerce": {
        "Chaos": 2.1, "Stability": 1.1, "Prestige": 2.3, "Narrative-Commerce": 1.8, "Noise": 1.4
    },
    "Noise": {
        "Chaos": 1.6, "Stability": 0.8, "Prestige": 1.2, "Narrative-Commerce": 1.4, "Noise": 1.3
    }
}

def calculate_interaction_score(player_a, player_b, context_modifier: float = 1.0) -> Dict:
    h1 = player_a.current_heat()
    h2 = player_b.current_heat()

    base_interaction = h1 * h2
    compatibility = COMPATIBILITY_MATRIX[player_a.cluster][player_b.cluster]

    interaction_score = round(base_interaction * compatibility * context_modifier, 3)

    # Outcome predictions
    spike_prob = min(100, round(interaction_score * 22, 1))   # tuned to real-world feel
    narrative_potential = "Viral" if interaction_score > 8.5 else "High" if interaction_score > 6.0 else "Medium"

    volatility = round((player_a.volatility + player_b.volatility) / 2 * (compatibility / 1.5), 2)

    conversion_potential = round(interaction_score * 0.45, 2)   # ties to CES

    return {
        "interaction_score": interaction_score,
        "spike_probability": f"{spike_prob}%",
        "narrative_potential": narrative_potential,
        "volatility_index": volatility,
        "conversion_potential": conversion_potential,
        "top_force_event": interaction_score > 9.0
    }
