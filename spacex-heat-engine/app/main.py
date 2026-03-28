from fastapi import FastAPI
from .db import Base, engine
from .routers import events, players, matches

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SpaceZ Heat Engine", description="Attention Economics OS for Live Golf")

app.include_router(players.router)
app.include_router(matches.router)
app.include_router(events.router)

@app.get("/")
def read_root():
    return {"message": "SpaceZ Heat Engine API is online"}
