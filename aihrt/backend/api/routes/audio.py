"""
Audio API Routes – AIHRT
Handles audio upload, ASR, and full NBCAM pipeline execution.
"""

import os
import uuid
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import aiofiles
import logging

from database.connection import get_db
from database.connection import Response, Interview, Question
from nbcam.asr_engine import transcribe_audio, extract_audio_features
from nbcam.layer1_sdm import compute_sdm
from nbcam.layer2_cli import compute_cli
from nbcam.layer3_ecam import compute_ecam

router = APIRouter()
logger = logging.getLogger(__name__)

AUDIO_STORAGE_DIR = Path(os.getenv("AUDIO_STORAGE_DIR", "/tmp/aihrt_audio"))
AUDIO_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload/{session_id}")
async def upload_audio(
    session_id: str,
    question_id: int = Form(...),
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Upload audio response for a given session + question.
    Runs ASR + NBCAM layers 1–3.
    Returns partial scores immediately; SRS computed after full interview.
    """
    # Validate interview session
    result = await db.execute(
        select(Interview).where(Interview.session_id == session_id)
    )
    interview = result.scalars().first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview session not found")

    # Validate question
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalars().first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Save audio file
    audio_filename = f"{session_id}_{question_id}_{uuid.uuid4().hex[:8]}.wav"
    audio_path = AUDIO_STORAGE_DIR / audio_filename

    async with aiofiles.open(audio_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # ── Run Pipeline ─────────────────────────────────────────────────────────

    try:
        # Stage 2: ASR
        logger.info(f"Running ASR on {audio_path}")
        asr = transcribe_audio(str(audio_path))

        # Audio feature extraction
        audio_feats = extract_audio_features(str(audio_path))

        # Layer 1: SDM – Semantic Drift Mapping
        sdm = compute_sdm(question.text, asr["transcript"])
        css = sdm["css"]

        # Layer 2: CLI – Cognitive Load Index
        cli_result = compute_cli(
            audio_features=audio_feats,
            transcript=asr["transcript"],
            response_latency=asr["response_latency"],
            word_count=asr["word_count"],
        )
        cli = cli_result["cli"]

        # Layer 3: ECAM – Emotion-Content Alignment
        ecam = compute_ecam(asr["transcript"], str(audio_path))
        ecs = ecam["ecs"]

        # ── Persist Response ──────────────────────────────────────────────────

        response_record = Response(
            interview_id=interview.id,
            question_id=question_id,
            transcript=asr["transcript"],
            word_count=asr["word_count"],
            speech_duration=asr["speech_duration"],
            silence_duration=asr["silence_duration"],
            response_latency=asr["response_latency"],
            asr_confidence=asr["asr_confidence"],
            audio_features={
                **audio_feats,
                "cli_breakdown": cli_result["breakdown"],
                "sdm_detail": {k: v for k, v in sdm.items() if k != "css"},
                "ecam_detail": {k: v for k, v in ecam.items() if k != "ecs"},
            },
            css=css,
            cli=cli,
            ecs=ecs,
            audio_path=str(audio_path),
        )
        db.add(response_record)
        await db.commit()
        await db.refresh(response_record)

        return {
            "response_id": response_record.id,
            "transcript": asr["transcript"],
            "asr": {
                "word_count": asr["word_count"],
                "speech_duration": asr["speech_duration"],
                "confidence": asr["asr_confidence"],
            },
            "scores": {
                "css": css,
                "cli": cli,
                "ecs": ecs,
            },
            "sdm": sdm,
            "ecam": {
                "dominant_text_emotion": ecam["dominant_text_emotion"],
                "dominant_audio_emotion": ecam["dominant_audio_emotion"],
                "mismatch": ecam["emotion_mismatch"],
            },
        }

    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/responses/{interview_id}")
async def get_responses(interview_id: int, db: AsyncSession = Depends(get_db)):
    """Get all responses for an interview with scores."""
    result = await db.execute(
        select(Response).where(Response.interview_id == interview_id)
    )
    responses = result.scalars().all()
    return [
        {
            "id": r.id,
            "question_id": r.question_id,
            "transcript": r.transcript,
            "css": r.css,
            "cli": r.cli,
            "ecs": r.ecs,
            "srs": r.srs,
            "recorded_at": r.recorded_at,
        }
        for r in responses
    ]
