"""
Interview API Routes – AIHRT
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from database.connection import get_db
from database.connection import Interview, Candidate, Response, Score
from database.schemas import InterviewCreate, InterviewResponse
from nbcam.layer4_acpt import compute_srs, generate_adaptive_question
from nbcam.fusion import aggregate_scores, generate_behavioral_insights

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=InterviewResponse)
async def create_interview(payload: InterviewCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Candidate).where(Candidate.id == payload.candidate_id))
    candidate = result.scalars().first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    interview = Interview(
        candidate_id=payload.candidate_id,
        session_id=str(uuid.uuid4()),
        status="active",
        started_at=datetime.utcnow(),
    )
    db.add(interview)
    await db.commit()
    await db.refresh(interview)
    return interview


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(interview_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalars().first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview


@router.post("/{interview_id}/complete")
async def complete_interview(interview_id: int, db: AsyncSession = Depends(get_db)):
    """
    Finalize interview:
    1. Compute SRS across all responses
    2. Aggregate scores into FCS
    3. Generate insights via LLM
    """
    # Load interview + candidate
    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalars().first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    result = await db.execute(select(Candidate).where(Candidate.id == interview.candidate_id))
    candidate = result.scalars().first()

    # Load all responses
    result = await db.execute(
        select(Response).where(Response.interview_id == interview_id).order_by(Response.id)
    )
    responses = result.scalars().all()

    if not responses:
        raise HTTPException(status_code=400, detail="No responses found for this interview")

    # Build response sequence for SRS
    response_sequence = [
        {"css": r.css or 0.5, "cli": r.cli or 0.5, "ecs": r.ecs or 0.5}
        for r in responses
    ]

    srs_result = compute_srs(response_sequence)
    srs_score = srs_result["srs"]

    # Update each response with SRS
    for r in responses:
        r.srs = srs_score
    await db.commit()

    # Aggregate final scores
    score_list = [
        {"css": r.css or 0.5, "cli": r.cli or 0.5, "ecs": r.ecs or 0.5, "srs": srs_score}
        for r in responses
    ]
    aggregated = aggregate_scores(score_list)

    # Generate LLM insights
    insights, recommendations = await generate_behavioral_insights(
        candidate_name=candidate.name,
        position=candidate.position or "General",
        avg_css=aggregated["avg_css"],
        avg_cli=aggregated["avg_cli"],
        avg_ecs=aggregated["avg_ecs"],
        avg_srs=aggregated["avg_srs"],
        fcs=aggregated["fcs"],
    )

    # Save Score record
    score_record = Score(
        interview_id=interview_id,
        avg_css=aggregated["avg_css"],
        avg_cli=aggregated["avg_cli"],
        avg_ecs=aggregated["avg_ecs"],
        avg_srs=aggregated["avg_srs"],
        fcs=aggregated["fcs"],
        weights=aggregated["weights"],
        behavioral_insights=insights,
        recommendations=recommendations,
    )
    db.add(score_record)

    # Mark interview complete
    interview.status = "completed"
    interview.completed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(score_record)

    return {
        "interview_id": interview_id,
        "status": "completed",
        "scores": aggregated,
        "srs_detail": srs_result,
        "behavioral_insights": insights,
        "recommendations": recommendations,
    }


@router.post("/{interview_id}/adaptive-question")
async def get_adaptive_question(
    interview_id: int,
    question_text: str,
    candidate_response: str,
    difficulty: int = 2,
    db: AsyncSession = Depends(get_db),
):
    """Generate an adaptive follow-up question using ACPT."""
    follow_up = await generate_adaptive_question(
        original_question=question_text,
        candidate_response=candidate_response,
        difficulty_level=difficulty,
    )
    return {"adaptive_question": follow_up, "difficulty": difficulty}
