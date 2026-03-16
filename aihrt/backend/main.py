"""
AIHRT – Artificially Intelligent Head Recruiter Technology
FastAPI Backend Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from api.routes import candidates, interviews, audio, scores, questions
from database.connection import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AIHRT backend...")
    await init_db()
    yield
    logger.info("Shutting down AIHRT backend...")


app = FastAPI(
    title="AIHRT – AI Head Recruiter Technology",
    description="Neuro-Behavioral Cognitive Alignment Model (NBCAM) Interview Assessment API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(interviews.router, prefix="/api/interviews", tags=["Interviews"])
app.include_router(audio.router, prefix="/api/audio", tags=["Audio Processing"])
app.include_router(scores.router, prefix="/api/scores", tags=["Scores"])
app.include_router(questions.router, prefix="/api/questions", tags=["Questions"])


@app.get("/")
async def root():
    return {"message": "AIHRT API Online", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
