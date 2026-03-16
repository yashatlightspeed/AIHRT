"""
NBCAM Layer 3 – Emotion–Content Alignment Matrix (ECAM)
Detects mismatch between spoken emotion and textual emotion.

Audio emotion: derived from acoustic features (pitch, energy, tempo)
Text emotion: lightweight transformer classifier
This approach is faster, requires no large model downloads,
and is well-validated in affective computing literature.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import librosa
import logging

logger = logging.getLogger(__name__)

_text_emotion_pipeline = None

EMOTION_LABELS = ["anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"]


def get_text_emotion_model():
    global _text_emotion_pipeline
    if _text_emotion_pipeline is None:
        from transformers import pipeline
        logger.info("Loading text emotion classifier...")
        _text_emotion_pipeline = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=None,
            device=-1,
        )
        logger.info("Text emotion model loaded.")
    return _text_emotion_pipeline


def text_to_emotion_vector(transcript: str) -> np.ndarray:
    if not transcript or len(transcript.strip()) < 5:
        return np.ones(len(EMOTION_LABELS)) / len(EMOTION_LABELS)
    try:
        clf = get_text_emotion_model()
        results = clf(transcript[:512])[0]
        scores = {r["label"].lower(): r["score"] for r in results}
        vector = np.array([scores.get(label, 0.0) for label in EMOTION_LABELS])
        vector /= vector.sum() + 1e-9
        return vector
    except Exception as e:
        logger.warning(f"Text emotion failed: {e}")
        return np.ones(len(EMOTION_LABELS)) / len(EMOTION_LABELS)


def audio_to_emotion_vector_acoustic(audio_path: str) -> np.ndarray:
    """
    Estimate emotion from acoustic features (pitch, energy, speech rate).
    Based on dimensional arousal/valence model (Schuller et al., 2013).
    """
    try:
        audio, sr = librosa.load(audio_path, sr=16000, mono=True)

        f0, _, _ = librosa.pyin(audio, fmin=80, fmax=400, sr=sr)
        f0_vals = f0[~np.isnan(f0)] if f0 is not None else np.array([150.0])
        pitch_mean = float(np.mean(f0_vals)) if len(f0_vals) > 0 else 150.0
        pitch_var  = float(np.var(f0_vals))  if len(f0_vals) > 0 else 0.0

        rms = librosa.feature.rms(y=audio)[0]
        energy_mean = float(np.mean(rms))

        non_silent  = librosa.effects.split(audio, top_db=30)
        speech_dur  = sum((e - s) for s, e in non_silent) / sr
        total_dur   = librosa.get_duration(y=audio, sr=sr)
        speech_ratio = speech_dur / max(total_dur, 0.01)

        centroid      = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        centroid_mean = float(np.mean(centroid))

        pitch_norm    = min(pitch_mean / 400.0, 1.0)
        pitch_var_norm = min(pitch_var / 5000.0, 1.0)
        energy_norm   = min(energy_mean / 0.1, 1.0)
        centroid_norm = min(centroid_mean / 4000.0, 1.0)

        arousal = pitch_norm * 0.4 + energy_norm * 0.4 + pitch_var_norm * 0.2
        valence = speech_ratio * 0.5 + centroid_norm * 0.5

        anger   = arousal * (1 - valence) * 0.8
        joy     = arousal * valence * 0.9
        surprise = arousal * valence * 0.5 + pitch_var_norm * 0.3
        sadness = (1 - arousal) * (1 - valence) * 0.8
        fear    = (1 - valence) * pitch_var_norm * 0.5
        neutral = max(0.0, 1.0 - arousal * 0.6 - (1 - valence) * 0.4)
        disgust = (1 - valence) * 0.2

        vector = np.array([anger, disgust, fear, joy, neutral, sadness, surprise])
        vector = np.clip(vector, 0.0, 1.0)
        vector /= vector.sum() + 1e-9
        return vector

    except Exception as e:
        logger.warning(f"Acoustic emotion estimation failed: {e}")
        v = np.array([0.05, 0.05, 0.05, 0.15, 0.55, 0.10, 0.05])
        return v / v.sum()


def compute_ecam(transcript: str, audio_path: str) -> dict:
    """
    Compute Emotional Consistency Score (ECS).
    ECS = cosine_similarity(TextEmotionVector, AcousticEmotionVector)
    """
    text_vector  = text_to_emotion_vector(transcript)
    audio_vector = audio_to_emotion_vector_acoustic(audio_path)

    ecs = float(cosine_similarity([text_vector], [audio_vector])[0][0])
    ecs = max(0.0, min(1.0, ecs))

    text_emotions  = {label: round(float(text_vector[i]),  4) for i, label in enumerate(EMOTION_LABELS)}
    audio_emotions = {label: round(float(audio_vector[i]), 4) for i, label in enumerate(EMOTION_LABELS)}

    dominant_text  = EMOTION_LABELS[int(np.argmax(text_vector))]
    dominant_audio = EMOTION_LABELS[int(np.argmax(audio_vector))]

    return {
        "ecs": round(ecs, 4),
        "text_emotions":  text_emotions,
        "audio_emotions": audio_emotions,
        "dominant_text_emotion":  dominant_text,
        "dominant_audio_emotion": dominant_audio,
        "emotion_mismatch": dominant_text != dominant_audio,
        "method": "acoustic_feature_based",
    }