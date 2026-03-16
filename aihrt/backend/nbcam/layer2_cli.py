"""
NBCAM Layer 2 – Cognitive Load Index (CLI)
Estimates cognitive strain using acoustic micro-features.
"""

import numpy as np
import re
import logging

logger = logging.getLogger(__name__)

FILLER_WORDS = {
    "um", "uh", "er", "ah", "hmm", "like", "you know", "sort of",
    "kind of", "basically", "literally", "actually", "i mean", "right",
    "so", "well", "anyway"
}


def count_filler_words(transcript: str) -> int:
    transcript_lower = transcript.lower()
    count = 0
    for filler in FILLER_WORDS:
        count += len(re.findall(r'\b' + re.escape(filler) + r'\b', transcript_lower))
    return count


def compute_cli(
    audio_features: dict,
    transcript: str,
    response_latency: float,
    word_count: int,
) -> dict:
    """
    Compute Cognitive Load Index using weighted additive model.
    Each feature is independently normalized to 0-1 then combined.
    Higher CLI = higher cognitive strain.
    """
    speech_length = max(audio_features.get("speech_length", 1.0), 0.01)
    micro_pauses  = audio_features.get("micro_pause_count", 0)
    pitch_variance = audio_features.get("pitch_variance", 0.0)
    total_duration = audio_features.get("total_duration", 1.0)

    # 1. Filler word rate (0-1) — high fillers = high load
    filler_count = count_filler_words(transcript)
    filler_rate  = min(filler_count / max(word_count, 1) / 0.15, 1.0)

    # 2. Micro pause rate (0-1) — normalize: >3 pauses/sec = max load
    micro_pause_rate = min((micro_pauses / speech_length) / 3.0, 1.0)

    # 3. Response latency (0-1) — >5 seconds before speaking = max load
    latency_norm = min(response_latency / 5.0, 1.0)

    # 4. Pitch variance (0-1) — high variance = stressed voice
    # Typical range 0-3000 Hz²
    pitch_var_norm = min(pitch_variance / 3000.0, 1.0)

    # 5. Speech rate penalty — very slow (<1 wps) or very fast (>4 wps) = load
    speech_rate = word_count / speech_length
    if speech_rate < 1.0:
        rate_penalty = min((1.0 - speech_rate), 1.0)
    elif speech_rate > 4.0:
        rate_penalty = min((speech_rate - 4.0) / 4.0, 1.0)
    else:
        rate_penalty = 0.0

    # Weighted combination
    cli = (
        filler_rate      * 0.30 +
        micro_pause_rate * 0.25 +
        latency_norm     * 0.20 +
        pitch_var_norm   * 0.15 +
        rate_penalty     * 0.10
    )

    cli = round(max(0.0, min(1.0, cli)), 4)

    return {
        "cli": cli,
        "breakdown": {
            "filler_count":       filler_count,
            "filler_rate":        round(filler_rate, 4),
            "micro_pause_rate":   round(micro_pause_rate, 4),
            "latency_norm":       round(latency_norm, 4),
            "pitch_var_norm":     round(pitch_var_norm, 4),
            "speech_rate_wps":    round(speech_rate, 2),
            "rate_penalty":       round(rate_penalty, 4),
        },
    }