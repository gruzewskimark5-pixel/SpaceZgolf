from fastapi import APIRouter, HTTPException
from .schemas import DICalculationRequest, DICalculationResult
from .service import get_holes_by_course, calculate_hole_di

router = APIRouter()

@router.post("/calculate-di", response_model=DICalculationResult)
async def calculate_di_endpoint(request: DICalculationRequest):
    holes = get_holes_by_course(request.course_id)
    if not holes:
        raise HTTPException(status_code=404, detail="Course not found")

    hole_breakdown = []
    total_di = 0.0
    calculated_holes = 0

    for hole in holes:
        score = request.scores.get(hole.number)
        if score is not None:
            di_result = calculate_hole_di(hole, score)
            hole_breakdown.append(di_result)
            total_di += di_result.hole_di
            calculated_holes += 1

    overall_di = total_di / calculated_holes if calculated_holes > 0 else 0.0

    return DICalculationResult(
        overall_di=round(overall_di, 2),
        hole_breakdown=hole_breakdown
    )
