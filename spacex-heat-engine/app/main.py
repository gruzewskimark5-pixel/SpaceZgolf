from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routers import events, players, matches, leaderboard, stream, simulate

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SpaceZ Heat Engine", description="Attention Economics OS for Live Golf")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router)
app.include_router(matches.router)
app.include_router(events.router)
app.include_router(leaderboard.router)
app.include_router(stream.router)
app.include_router(simulate.router)

@app.get("/")
def read_root():
    return {"message": "SpaceZ Heat Engine API is online"}
