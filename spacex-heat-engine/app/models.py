from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import TypeDecorator, CHAR
import uuid
from .db import Base
from sqlalchemy.sql import func

# Custom UUID type to work with SQLite and Postgres
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class Player(Base):
    __tablename__ = "players"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    role = Column(String)
    authority_score = Column(Float, default=0.0)
    narrative_weight = Column(Float, default=0.0)
    volatility_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())


class Match(Base):
    __tablename__ = "matches"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    title = Column(String)
    phase = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=func.now())


class MatchPlayer(Base):
    __tablename__ = "match_players"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    match_id = Column(GUID(), ForeignKey("matches.id"))
    player_id = Column(GUID(), ForeignKey("players.id"))


class Event(Base):
    __tablename__ = "events"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    match_id = Column(GUID(), ForeignKey("matches.id"))
    timestamp = Column(DateTime, default=func.now())

    phase_multiplier = Column(Float, default=1.0)
    novelty_bonus = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())


class EventPlayer(Base):
    __tablename__ = "event_players"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    event_id = Column(GUID(), ForeignKey("events.id"))
    player_id = Column(GUID(), ForeignKey("players.id"))
    role_in_event = Column(String)


class EngagementMetric(Base):
    __tablename__ = "engagement_metrics"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    event_id = Column(GUID(), ForeignKey("events.id"))

    views = Column(Integer, default=0)
    retention = Column(Float, default=0.0)
    interactions = Column(Integer, default=0)
    peak_concurrent = Column(Integer, default=0)

    normalized_engagement = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())


class RivalryScore(Base):
    __tablename__ = "rivalry_scores"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    player_a = Column(GUID(), ForeignKey("players.id"))
    player_b = Column(GUID(), ForeignKey("players.id"))

    score = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=func.now())


class ClusterScore(Base):
    __tablename__ = "cluster_scores"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    event_id = Column(GUID(), ForeignKey("events.id"))
    active_nodes = Column(Integer)
    interaction_quality = Column(Float)
    normalized_cluster = Column(Float)


class HeatScore(Base):
    __tablename__ = "heat_scores"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    event_id = Column(GUID(), ForeignKey("events.id"))

    engagement = Column(Float)
    rivalry = Column(Float)
    cluster = Column(Float)
    phase = Column(Float)
    novelty = Column(Float)

    heat_index = Column(Float)
    created_at = Column(DateTime, default=func.now())


class RevenueEvent(Base):
    __tablename__ = "revenue_events"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    event_id = Column(GUID(), ForeignKey("events.id"))
    revenue = Column(Float, default=0.0)
    source = Column(String)
    created_at = Column(DateTime, default=func.now())


class CESScore(Base):
    __tablename__ = "ces_scores"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    event_id = Column(GUID(), ForeignKey("events.id"))

    heat_index = Column(Float)
    revenue = Column(Float)
    ces = Column(Float)
    created_at = Column(DateTime, default=func.now())


class HeatTimeSeries(Base):
    __tablename__ = "heat_time_series"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    event_id = Column(GUID(), nullable=False)
    player_id = Column(GUID(), nullable=True) # Optional, if we want to track specific player's heat

    timestamp = Column(DateTime, default=func.now())
    heat_index = Column(Float)

    engagement = Column(Float)
    rivalry = Column(Float)
    cluster = Column(Float)
    phase = Column(Float)
    novelty = Column(Float)
