"""
NBCAM Layer 4 – Adaptive Cognitive Pressure Testing (ACPT)
Measures stability under increasing question difficulty.
Uses GPT/LLaMA to generate follow-up questions with escalating pressure.
"""

import numpy as np
import os
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

ADAPTIVE_SYSTEM_PROMPT = """You are an expert technical interviewer conducting a cognitive stress evaluation.
Your role is to generate a follow-up question that:
1. Escalates the complexity of the original topic
2. Introduces a mild contradiction or challenge to the candidate's previous answer
3. Reduces cognitive comfort by narrowing the expected scope of response

Keep the follow-up question concise (1–2 sentences). Do not explain your reasoning."""


async def generate_adaptive_question(
    original_question: str,
    candidate_response: str,
    difficulty_level: int = 2,
) -> str:
    """
    Generate an adaptive follow-up question using LLM.

    Args:
        original_question: The base question
        candidate_response: What the candidate said
        difficulty_level: 1–5 (escalating pressure)

    Returns:
        Follow-up question string
    """
    pressure_descriptors = {
        1: "slightly more challenging",
        2: "moderately harder with a mild contradiction",
        3: "significantly harder, introducing ambiguity",
        4: "high pressure with a strong contradiction",
        5: "extreme cognitive pressure, questioning core assumptions",
    }
    descriptor = pressure_descriptors.get(difficulty_level, "harder")

    user_prompt = f"""Original Question: {original_question}

Candidate's Response: {candidate_response}

Generate a {descriptor} follow-up question that tests deeper reasoning and introduces cognitive pressure."""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": ADAPTIVE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"LLM adaptive question generation failed: {e}")
        return f"Can you elaborate further and defend your position with a concrete counter-example?"


def compute_srs(response_sequence: list[dict]) -> dict:
    """
    Compute Stress Resilience Score from a sequence of responses.

    Each response dict should contain:
        - css: float
        - cli: float
        - ecs: float
        - difficulty: int

    SRS = 1 - volatility_score
    Lower volatility across escalating difficulty = higher resilience.

    Returns:
        {srs: float (0–1), volatility: float, trend: str}
    """
    if len(response_sequence) < 2:
        # Not enough data – return neutral score
        return {"srs": 0.5, "volatility": 0.5, "trend": "insufficient_data"}

    css_seq = [r["css"] for r in response_sequence]
    cli_seq = [r["cli"] for r in response_sequence]
    ecs_seq = [r["ecs"] for r in response_sequence]

    # Compute variance (instability) across each metric under pressure
    css_volatility = float(np.std(css_seq))
    cli_volatility = float(np.std(cli_seq))
    ecs_volatility = float(np.std(ecs_seq))

    # Combined volatility (weighted: CSS most important for resilience)
    combined_volatility = (0.5 * css_volatility) + (0.3 * cli_volatility) + (0.2 * ecs_volatility)

    # Normalize volatility to 0–1 range (max expected std = 0.5)
    normalized_volatility = min(combined_volatility / 0.5, 1.0)

    # SRS = inverse of volatility
    srs = 1.0 - normalized_volatility

    # Trend: is performance improving or degrading under pressure?
    css_trend = css_seq[-1] - css_seq[0]
    if css_trend > 0.05:
        trend = "improving"
    elif css_trend < -0.05:
        trend = "degrading"
    else:
        trend = "stable"

    return {
        "srs": round(max(0.0, min(1.0, srs)), 4),
        "volatility": round(normalized_volatility, 4),
        "css_volatility": round(css_volatility, 4),
        "cli_volatility": round(cli_volatility, 4),
        "ecs_volatility": round(ecs_volatility, 4),
        "trend": trend,
    }
