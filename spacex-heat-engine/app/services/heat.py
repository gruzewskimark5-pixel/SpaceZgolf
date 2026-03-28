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
