from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas
import uuid
from typing import List

router = APIRouter(prefix="/api/v1", tags=["Matches"])

@router.post("/matches", response_model=schemas.MatchResponse)
def create_match(data: schemas.MatchCreate, db: Session = Depends(get_db)):
    match = models.Match(
        title=data.title,
        phase=data.phase
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match

@router.get("/matches", response_model=List[schemas.MatchResponse])
def get_matches(db: Session = Depends(get_db)):
    return db.query(models.Match).all()
