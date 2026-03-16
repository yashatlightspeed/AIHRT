"""
Scores API Routes – AIHRT
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.connection import get_db, Score, Interview, Candidate, Response

router = APIRouter()


@router.get("/{interview_id}")
async def get_scores(interview_id: int, db: AsyncSession = Depends(get_db)):
    """Get final scores for an interview."""
    result = await db.execute(select(Score).where(Score.interview_id == interview_id))
    score = result.scalars().first()
    if not score:
        raise HTTPException(status_code=404, detail="Scores not yet computed. Complete the interview first.")

    return {
        "interview_id": interview_id,
        "avg_css": score.avg_css,
        "avg_cli": score.avg_cli,
        "avg_ecs": score.avg_ecs,
        "avg_srs": score.avg_srs,
        "fcs": score.fcs,
        "weights": score.weights,
        "behavioral_insights": score.behavioral_insights,
        "recommendations": score.recommendations,
        "computed_at": score.computed_at,
    }


@router.get("/dashboard/{interview_id}")
async def get_dashboard_data(interview_id: int, db: AsyncSession = Depends(get_db)):
    """Full dashboard data including timeline of response scores."""
    result = await db.execute(
        select(Interview).where(Interview.id == interview_id)
    )
    interview = result.scalars().first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    result = await db.execute(select(Candidate).where(Candidate.id == interview.candidate_id))
    candidate = result.scalars().first()

    result = await db.execute(select(Score).where(Score.interview_id == interview_id))
    score = result.scalars().first()

    result = await db.execute(
        select(Response).where(Response.interview_id == interview_id).order_by(Response.id)
    )
    responses = result.scalars().all()

    timeline = [
        {
            "response_num": i + 1,
            "question_id": r.question_id,
            "transcript_preview": (r.transcript or "")[:120],
            "css": r.css,
            "cli": r.cli,
            "ecs": r.ecs,
            "srs": r.srs,
            "recorded_at": r.recorded_at,
        }
        for i, r in enumerate(responses)
    ]

    return {
        "candidate": {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "position": candidate.position,
        },
        "interview": {
            "id": interview.id,
            "session_id": interview.session_id,
            "status": interview.status,
            "started_at": interview.started_at,
            "completed_at": interview.completed_at,
        },
        "final_score": {
            "avg_css": score.avg_css if score else None,
            "avg_cli": score.avg_cli if score else None,
            "avg_ecs": score.avg_ecs if score else None,
            "avg_srs": score.avg_srs if score else None,
            "fcs": score.fcs if score else None,
            "behavioral_insights": score.behavioral_insights if score else None,
            "recommendations": score.recommendations if score else None,
        } if score else None,
        "response_timeline": timeline,
    }


@router.get("/candidates/{candidate_id}/history")
async def get_candidate_history(candidate_id: int, db: AsyncSession = Depends(get_db)):
    """Get all interview scores for a candidate."""
    result = await db.execute(
        select(Interview, Score)
        .join(Score, Score.interview_id == Interview.id, isouter=True)
        .where(Interview.candidate_id == candidate_id)
        .order_by(Interview.created_at.desc())
    )
    rows = result.all()

    return [
        {
            "interview_id": interview.id,
            "status": interview.status,
            "created_at": interview.created_at,
            "fcs": score.fcs if score else None,
        }
        for interview, score in rows
    ]
