"""
Questions API Routes – AIHRT
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.connection import get_db, Question
from database.schemas import QuestionCreate, QuestionResponse

router = APIRouter()


@router.post("/", response_model=QuestionResponse)
async def create_question(payload: QuestionCreate, db: AsyncSession = Depends(get_db)):
    question = Question(**payload.model_dump())
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


@router.get("/", response_model=list[QuestionResponse])
async def list_questions(category: str = None, db: AsyncSession = Depends(get_db)):
    query = select(Question).order_by(Question.difficulty)
    if category:
        query = query.where(Question.category == category)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Question).where(Question.id == question_id))
    q = result.scalars().first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return q


@router.post("/seed")
async def seed_questions(db: AsyncSession = Depends(get_db)):
    """Seed database with sample interview questions."""
    sample_questions = [
        {"text": "Tell me about a time you had to solve a complex problem under tight deadlines.", "difficulty": 1, "category": "behavioral"},
        {"text": "Describe your approach to making decisions when you don't have all the information you need.", "difficulty": 2, "category": "cognitive"},
        {"text": "How do you handle situations where your team disagrees with your technical decision?", "difficulty": 2, "category": "leadership"},
        {"text": "Walk me through how you would design a distributed system that needs to handle 10 million concurrent users.", "difficulty": 4, "category": "technical"},
        {"text": "If you had to defend a decision that later turned out to be wrong, how would you approach that conversation?", "difficulty": 3, "category": "behavioral"},
        {"text": "What's a deeply-held professional belief you hold that most of your colleagues would disagree with?", "difficulty": 3, "category": "cognitive"},
        {"text": "How do you prioritize when everything is marked as urgent?", "difficulty": 2, "category": "cognitive"},
        {"text": "Describe a situation where you had to rapidly change your approach mid-project.", "difficulty": 3, "category": "adaptability"},
    ]

    added = []
    for q_data in sample_questions:
        q = Question(**q_data)
        db.add(q)
        added.append(q_data["text"][:50])

    await db.commit()
    return {"seeded": len(added), "questions": added}
