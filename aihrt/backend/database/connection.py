"""
Database Models – AIHRT
PostgreSQL via SQLAlchemy async
"""

from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, Boolean
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://aihrt:aihrt_password@localhost:5432/aihrt_db"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ── Models ──────────────────────────────────────────────────────────────────

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    position = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    interviews = relationship("Interview", back_populates="candidate")


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    session_id = Column(String(100), unique=True, nullable=False)
    status = Column(String(50), default="pending")   # pending | active | completed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="interviews")
    responses = relationship("Response", back_populates="interview")
    scores = relationship("Score", back_populates="interview", uselist=False)


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    difficulty = Column(Integer, default=1)   # 1–5
    category = Column(String(100))
    adaptive = Column(Boolean, default=False)
    follow_up_of = Column(Integer, ForeignKey("questions.id"), nullable=True)

    responses = relationship("Response", back_populates="question")


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)

    # ASR outputs
    transcript = Column(Text)
    word_count = Column(Integer)
    speech_duration = Column(Float)
    silence_duration = Column(Float)
    response_latency = Column(Float)
    asr_confidence = Column(Float)

    # Audio features (stored as JSON)
    audio_features = Column(JSON)

    # NBCAM layer scores
    css = Column(Float)   # Cognitive Stability Score
    cli = Column(Float)   # Cognitive Load Index
    ecs = Column(Float)   # Emotional Consistency Score
    srs = Column(Float)   # Stress Resilience Score

    audio_path = Column(String(500))
    recorded_at = Column(DateTime, default=datetime.utcnow)

    interview = relationship("Interview", back_populates="responses")
    question = relationship("Question", back_populates="responses")


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False, unique=True)

    # Aggregated scores
    avg_css = Column(Float)
    avg_cli = Column(Float)
    avg_ecs = Column(Float)
    avg_srs = Column(Float)

    # Final Cognitive Score (0–100)
    fcs = Column(Float)

    # Weights used
    weights = Column(JSON)

    # Insights and recommendations
    behavioral_insights = Column(Text)
    recommendations = Column(Text)

    computed_at = Column(DateTime, default=datetime.utcnow)

    interview = relationship("Interview", back_populates="scores")
