from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routers import events, players, matches, leaderboard, stream, simulate, digital_twin, markos_routes
from .interaction_predictor import router as apex_router

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
app.include_router(digital_twin.router)
app.include_router(markos_routes.router) # The new Mark OS router
app.include_router(apex_router) # The new Heat Engine v1 router

@app.get("/")
def read_root():
    return {"message": "SpaceZ Heat Engine API is online"}
