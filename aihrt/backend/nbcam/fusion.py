"""
Score Fusion Layer – AIHRT
Combines CSS, CLI, ECS, SRS into Final Cognitive Score (FCS).
Also generates behavioral insights and recommendations.
"""

import numpy as np
import os
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

# Default weights (equal; can be tuned via regression)
DEFAULT_WEIGHTS = {
    "w1": 0.25,   # CSS weight
    "w2": 0.25,   # CLI weight (inverted: lower CLI = better)
    "w3": 0.25,   # ECS weight
    "w4": 0.25,   # SRS weight
}


def compute_fcs(
    css: float,
    cli: float,
    ecs: float,
    srs: float,
    weights: dict = None,
) -> float:
    """
    Compute Final Cognitive Score (FCS) on 0–100 scale.

    FCS = (w1·CSS + w2·(1-CLI) + w3·ECS + w4·SRS) × 100
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    w1 = weights.get("w1", 0.25)
    w2 = weights.get("w2", 0.25)
    w3 = weights.get("w3", 0.25)
    w4 = weights.get("w4", 0.25)

    fcs = (w1 * css + w2 * (1.0 - cli) + w3 * ecs + w4 * srs) * 100
    return round(max(0.0, min(100.0, fcs)), 2)


def aggregate_scores(response_scores: list[dict]) -> dict:
    """
    Aggregate per-response scores into interview-level scores.

    Args:
        response_scores: list of {css, cli, ecs, srs, ...}

    Returns:
        {avg_css, avg_cli, avg_ecs, avg_srs, fcs}
    """
    if not response_scores:
        return {"avg_css": 0.0, "avg_cli": 0.0, "avg_ecs": 0.0, "avg_srs": 0.0, "fcs": 0.0}

    avg_css = float(np.mean([r["css"] for r in response_scores]))
    avg_cli = float(np.mean([r["cli"] for r in response_scores]))
    avg_ecs = float(np.mean([r["ecs"] for r in response_scores]))
    avg_srs = float(np.mean([r.get("srs", 0.5) for r in response_scores]))

    fcs = compute_fcs(avg_css, avg_cli, avg_ecs, avg_srs)

    return {
        "avg_css": round(avg_css, 4),
        "avg_cli": round(avg_cli, 4),
        "avg_ecs": round(avg_ecs, 4),
        "avg_srs": round(avg_srs, 4),
        "fcs": fcs,
        "weights": DEFAULT_WEIGHTS,
    }


async def generate_behavioral_insights(
    candidate_name: str,
    position: str,
    avg_css: float,
    avg_cli: float,
    avg_ecs: float,
    avg_srs: float,
    fcs: float,
) -> tuple[str, str]:
    """
    Use LLM to generate behavioral insights and recommendations.

    Returns:
        (behavioral_insights_text, recommendations_text)
    """
    prompt = f"""You are an expert organizational psychologist and AI recruiter.
Analyze the following cognitive assessment scores for a candidate applying for: {position}

Candidate: {candidate_name}

Neuro-Behavioral Cognitive Alignment Model (NBCAM) Results:
- Cognitive Stability Score (CSS): {avg_css:.2f}/1.0
  (Measures reasoning coherence and semantic drift under questioning)
- Cognitive Load Index (CLI): {avg_cli:.2f}/1.0
  (Estimates cognitive strain – LOWER is better)
- Emotional Consistency Score (ECS): {avg_ecs:.2f}/1.0
  (Measures alignment between spoken and emotional content)
- Stress Resilience Score (SRS): {avg_srs:.2f}/1.0
  (Performance stability under increasing pressure)
- Final Cognitive Score (FCS): {fcs:.1f}/100

Generate TWO sections:

**BEHAVIORAL INSIGHTS** (3–4 sentences):
Describe the candidate's cognitive and behavioral profile based on the scores.
Be specific about patterns observed (e.g. cognitive masking, reasoning drift, emotional authenticity).

**RECOMMENDATIONS** (3–4 actionable bullet points):
Provide concrete hiring recommendations, areas to probe further, and development suggestions.

Format response as:
INSIGHTS: [insights text]
RECOMMENDATIONS: [recommendations text]"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.6,
        )
        content = response.choices[0].message.content.strip()

        insights = ""
        recommendations = ""

        if "INSIGHTS:" in content and "RECOMMENDATIONS:" in content:
            parts = content.split("RECOMMENDATIONS:")
            insights = parts[0].replace("INSIGHTS:", "").strip()
            recommendations = parts[1].strip()
        else:
            insights = content
            recommendations = "See full analysis above."

        return insights, recommendations

    except Exception as e:
        logger.warning(f"Insight generation failed: {e}")
        insights = f"CSS: {avg_css:.2f} | CLI: {avg_cli:.2f} | ECS: {avg_ecs:.2f} | SRS: {avg_srs:.2f}"
        recommendations = "Review scores manually with qualified assessors."
        return insights, recommendations
