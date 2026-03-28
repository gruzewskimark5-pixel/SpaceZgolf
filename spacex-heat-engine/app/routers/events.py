from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas
from ..services.heat import calculate_heat, calculate_ces
from .stream import broadcast_leaderboard_update
import uuid

router = APIRouter(prefix="/api/v1", tags=["Events"])

@router.post("/events", response_model=schemas.EventResponse)
def create_event(data: schemas.EventCreate, db: Session = Depends(get_db)):
    event = models.Event(
        match_id=data.match_id,
        phase_multiplier=data.phase_multiplier,
        novelty_bonus=data.novelty_bonus
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Associate players if provided
    if data.players:
        for p_id in data.players:
            ep = models.EventPlayer(event_id=event.id, player_id=p_id)
            db.add(ep)
        db.commit()

    return event

@router.post("/events/{event_id}/engagement")
def add_engagement(event_id: uuid.UUID, data: schemas.EngagementCreate, db: Session = Depends(get_db)):
    normalized = (
        0.4 * min(data.views / 100000.0, 1.0) +
        0.3 * min(data.retention, 1.0) +
        0.2 * min(data.interactions / 10000.0, 1.0) +
        0.1 * min(data.peak_concurrent / 50000.0, 1.0)
    )

    metric = models.EngagementMetric(
        event_id=event_id,
        views=data.views,
        retention=data.retention,
        interactions=data.interactions,
        peak_concurrent=data.peak_concurrent,
        normalized_engagement=normalized
    )

    db.add(metric)
    db.commit()
    return {"normalized_engagement": normalized}

@router.post("/events/{event_id}/calculate-heat")
def compute_heat(event_id: uuid.UUID, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    metric = db.query(models.EngagementMetric).filter_by(event_id=event_id).first()
    if not metric:
        raise HTTPException(status_code=400, detail="No engagement metrics found for this event")

    event = db.query(models.Event).filter_by(id=event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    rivalry = 0.8
    cluster = 0.7

    hi = calculate_heat(
        engagement=metric.normalized_engagement,
        rivalry=rivalry,
        cluster=cluster,
        phase=event.phase_multiplier,
        novelty=event.novelty_bonus
    )

    heat = models.HeatScore(
        event_id=event_id,
        engagement=metric.normalized_engagement,
        rivalry=rivalry,
        cluster=cluster,
        phase=event.phase_multiplier,
        novelty=event.novelty_bonus,
        heat_index=hi
    )

    db.add(heat)
    db.commit()

    # Trigger broadcast in background
    background_tasks.add_task(broadcast_leaderboard_update)

    return {"heat_index": hi}

@router.post("/events/{event_id}/revenue")
def add_revenue(event_id: uuid.UUID, data: schemas.RevenueCreate, db: Session = Depends(get_db)):
    revenue = models.RevenueEvent(
        event_id=event_id,
        revenue=data.revenue,
        source=data.source
    )

    db.add(revenue)
    db.commit()
    return {"status": "ok", "revenue_added": data.revenue}

@router.post("/events/{event_id}/calculate-ces")
def compute_ces(event_id: uuid.UUID, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    heat = db.query(models.HeatScore).filter_by(event_id=event_id).first()
    if not heat:
        raise HTTPException(status_code=400, detail="No heat score found for this event. Calculate heat first.")

    revenue = db.query(models.RevenueEvent).filter_by(event_id=event_id).first()
    if not revenue:
        raise HTTPException(status_code=400, detail="No revenue events found for this event.")

    ces_value = calculate_ces(revenue.revenue, heat.heat_index)

    ces = models.CESScore(
        event_id=event_id,
        heat_index=heat.heat_index,
        revenue=revenue.revenue,
        ces=ces_value
    )

    db.add(ces)
    db.commit()

    # Trigger broadcast in background
    background_tasks.add_task(broadcast_leaderboard_update)

    return {"ces": ces_value}
