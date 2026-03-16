"""
NBCAM Layer 1 – Semantic Drift Mapping (SDM)
Measures reasoning stability and logical coherence.
Uses Sentence-BERT embeddings + cosine similarity.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

_model = None


def get_sbert_model():
    global _model
    if _model is None:
        logger.info("Loading Sentence-BERT model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("SBERT model loaded.")
    return _model


def split_transcript(transcript: str) -> tuple[str, str, str]:
    """Split transcript into beginning / middle / end thirds."""
    words = transcript.split()
    n = len(words)
    if n < 3:
        return transcript, transcript, transcript

    third = n // 3
    a1 = " ".join(words[:third])
    a2 = " ".join(words[third: 2 * third])
    a3 = " ".join(words[2 * third:])
    return a1, a2, a3


def compute_sdm(question: str, transcript: str) -> dict:
    """
    Compute Semantic Drift Mapping scores.

    Args:
        question: The interview question text
        transcript: Full candidate response transcript

    Returns:
        {
            css: float (0–1),    # Cognitive Stability Score
            sim1: float,
            sim2: float,
            sim3: float,
            drift_variance: float
        }
    """
    model = get_sbert_model()

    if not transcript or len(transcript.strip()) < 10:
        return {"css": 0.0, "sim1": 0.0, "sim2": 0.0, "sim3": 0.0, "drift_variance": 1.0}

    a1, a2, a3 = split_transcript(transcript)

    texts = [question, a1, a2, a3]
    embeddings = model.encode(texts, convert_to_numpy=True)

    e_q, e_a1, e_a2, e_a3 = embeddings[0], embeddings[1], embeddings[2], embeddings[3]

    def cos_sim(a, b):
        return float(cosine_similarity([a], [b])[0][0])

    sim1 = cos_sim(e_q, e_a1)
    sim2 = cos_sim(e_q, e_a2)
    sim3 = cos_sim(e_q, e_a3)

    # Semantic Coherence Score
    scs = (sim1 + sim2 + sim3) / 3

    # Drift variance – how much coherence oscillates across segments
    drift_variance = float(np.var([sim1, sim2, sim3]))

    # CSS: high coherence + low drift = high stability
    # Penalize high variance
    css = max(0.0, min(1.0, scs - drift_variance))

    return {
        "css": round(css, 4),
        "scs": round(scs, 4),
        "sim1": round(sim1, 4),
        "sim2": round(sim2, 4),
        "sim3": round(sim3, 4),
        "drift_variance": round(drift_variance, 6),
    }
