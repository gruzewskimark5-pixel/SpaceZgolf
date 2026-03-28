import logging
from typing import List

logger = logging.getLogger(__name__)

# The V1 Cluster Multiplier Matrix
# Defines how different roles interact non-linearly to spike attention
# PRESTIGE (Validate) | ANCHOR (Stabilize) | DISRUPTOR (Spike) | CONVERTER (Monetize) | AMPLIFIER (Noise)

CLUSTER_MATRIX = {
    # Extreme Heat
    ("PRESTIGE", "DISRUPTOR"): 1.90,  # e.g., Nelly Korda + Alexis Miestowski (Top Force Event)
    ("ANCHOR", "DISRUPTOR"): 1.65,    # e.g., Kai Trump + Alyssa Lamoureux (Narrative Chaos)
    ("PRESTIGE", "ANCHOR"): 1.50,     # Huge authority validation, but slow burn

    # High Heat
    ("ANCHOR", "ANCHOR"): 1.40,       # Clash of titans (Rivalry)
    ("DISRUPTOR", "DISRUPTOR"): 1.35, # Unpredictable volatility
    ("CONVERTER", "PRESTIGE"): 1.30,  # Extreme monetization opportunity

    # Medium Heat
    ("ANCHOR", "CONVERTER"): 1.25,
    ("DISRUPTOR", "CONVERTER"): 1.20,
    ("AMPLIFIER", "DISRUPTOR"): 1.15,
    ("PRESTIGE", "AMPLIFIER"): 1.10,
    ("ANCHOR", "AMPLIFIER"): 1.05,

    # Base/Negative Heat
    ("CONVERTER", "CONVERTER"): 0.95, # Too commercial
    ("AMPLIFIER", "AMPLIFIER"): 0.85  # Pure noise
}

def get_pair_multiplier(role_a: str, role_b: str) -> float:
    pair1 = (role_a.upper(), role_b.upper())
    pair2 = (role_b.upper(), role_a.upper())

    if pair1 in CLUSTER_MATRIX:
        return CLUSTER_MATRIX[pair1]
    if pair2 in CLUSTER_MATRIX:
        return CLUSTER_MATRIX[pair2]

    return 1.0 # Default neutral multiplier

def calculate_cluster_multiplier(roles_in_scene: List[str]) -> float:
    """
    Computes the total non-linear cluster multiplier for a group of players.
    Base multiplier starts at 1.0. Evaluates all unique pairs in the scene.
    """
    if not roles_in_scene or len(roles_in_scene) < 2:
        return 1.0

    multiplier = 1.0
    # Evaluate all unique pairs
    for i in range(len(roles_in_scene)):
        for j in range(i + 1, len(roles_in_scene)):
            pair_mult = get_pair_multiplier(roles_in_scene[i], roles_in_scene[j])

            # Dampen additional pairs to avoid exponential explosions in large groups
            if multiplier == 1.0:
                multiplier *= pair_mult
            else:
                # Add 20% of the pair's effect on top of existing multiplier
                multiplier += (pair_mult - 1.0) * 0.2

    return round(multiplier, 3)
