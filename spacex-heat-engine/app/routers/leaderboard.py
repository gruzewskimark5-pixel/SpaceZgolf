from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..db import get_db
from .. import models

router = APIRouter(tags=["Leaderboard"])

@router.get("/api/v1/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    # Calculate average Heat Index and Total/Avg CES per player
    # A player is linked to events via event_players

    results = (
        db.query(
            models.Player.id,
            models.Player.name,
            models.Player.role,
            func.avg(models.HeatScore.heat_index).label('avg_hi'),
            func.avg(models.CESScore.ces).label('avg_ces')
        )
        .outerjoin(models.EventPlayer, models.Player.id == models.EventPlayer.player_id)
        .outerjoin(models.HeatScore, models.EventPlayer.event_id == models.HeatScore.event_id)
        .outerjoin(models.CESScore, models.EventPlayer.event_id == models.CESScore.event_id)
        .group_by(models.Player.id, models.Player.name, models.Player.role)
        .all()
    )

    leaderboard = []
    for row in results:
        leaderboard.append({
            "id": str(row.id),
            "name": row.name,
            "role": row.role,
            "hi": round(row.avg_hi, 2) if row.avg_hi else 0.0,
            "ces": round(row.avg_ces, 2) if row.avg_ces else 0.0
        })

    # Sort by HI descending
    leaderboard.sort(key=lambda x: x["hi"], reverse=True)
    return leaderboard
