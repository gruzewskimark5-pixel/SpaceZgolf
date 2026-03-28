from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas
import uuid
from typing import List

router = APIRouter(prefix="/api/v1", tags=["Players"])

@router.post("/players", response_model=schemas.PlayerResponse)
def create_player(data: schemas.PlayerCreate, db: Session = Depends(get_db)):
    player = models.Player(
        name=data.name,
        role=data.role
    )
    db.add(player)
    db.commit()
    db.refresh(player)
    return player

@router.get("/players", response_model=List[schemas.PlayerResponse])
def get_players(db: Session = Depends(get_db)):
    return db.query(models.Player).all()
