def calculate_heat(engagement: float, rivalry: float, cluster: float, phase: float, novelty: float) -> float:
    hi = (
        0.40 * engagement +
        0.25 * rivalry +
        0.20 * cluster +
        0.10 * phase +
        0.05 * novelty
    ) * 5
    return round(hi, 3)

def calculate_ces(revenue: float, heat_index: float) -> float:
    if heat_index == 0:
        return 0
    return round(revenue / heat_index, 3)

def predict_heat(current_heat: float, heat_history: list[float], alpha: float = 0.6) -> float:
    """
    Exponential smoothing forecast for heat
    """
    if len(heat_history) < 2:
        return current_heat

    recent_trend = heat_history[-1] - heat_history[-2]
    projected = current_heat + (alpha * recent_trend)

    return round(projected, 3)

def compute_engagement_velocity(heat_history: list[float]) -> float:
    if len(heat_history) < 2:
        return 0.0
    return round(heat_history[-1] - heat_history[-2], 3)
