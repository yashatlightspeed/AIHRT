"""
Pydantic Schemas – AIHRT API
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# ── Candidates ───────────────────────────────────────────────────────────────

class CandidateCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    position: Optional[str] = None


class CandidateResponse(CandidateCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Questions ────────────────────────────────────────────────────────────────

class QuestionCreate(BaseModel):
    text: str
    difficulty: int = 1
    category: Optional[str] = None
    adaptive: bool = False
    follow_up_of: Optional[int] = None


class QuestionResponse(QuestionCreate):
    id: int

    class Config:
        from_attributes = True


# ── Interviews ───────────────────────────────────────────────────────────────

class InterviewCreate(BaseModel):
    candidate_id: int


class InterviewResponse(BaseModel):
    id: int
    candidate_id: int
    session_id: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Audio / ASR ───────────────────────────────────────────────────────────────

class ASRResult(BaseModel):
    transcript: str
    word_count: int
    speech_duration: float
    silence_duration: float
    response_latency: float
    asr_confidence: float
    word_timestamps: List[Dict[str, Any]] = []


# ── NBCAM Scores ──────────────────────────────────────────────────────────────

class NBCAMScores(BaseModel):
    css: float   # 0–1
    cli: float   # 0–1
    ecs: float   # 0–1
    srs: float   # 0–1
    audio_features: Dict[str, Any] = {}


class FinalScore(BaseModel):
    avg_css: float
    avg_cli: float
    avg_ecs: float
    avg_srs: float
    fcs: float           # 0–100
    weights: Dict[str, float]
    behavioral_insights: str
    recommendations: str


# ── Responses ────────────────────────────────────────────────────────────────

class ResponseSubmit(BaseModel):
    interview_id: int
    question_id: int
    session_id: str


class ResponseResult(BaseModel):
    id: int
    transcript: str
    css: float
    cli: float
    ecs: float
    srs: Optional[float]
    asr_confidence: float

    class Config:
        from_attributes = True


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardData(BaseModel):
    candidate: CandidateResponse
    interview: InterviewResponse
    final_score: Optional[FinalScore]
    response_timeline: List[Dict[str, Any]]
