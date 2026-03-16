"""
ASR Engine – AIHRT
OpenAI Whisper integration for speech-to-text transcription
"""

import whisper
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

# Lazy-load model (loaded once on first use)
_model = None


def get_whisper_model(model_size: str = "small"):
    global _model
    if _model is None:
        logger.info(f"Loading Whisper {model_size} model...")
        _model = whisper.load_model(model_size)
        logger.info("Whisper model loaded.")
    return _model


def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribe audio file using Whisper and extract speech metrics.

    Returns:
        {
            transcript: str,
            word_count: int,
            speech_duration: float,
            silence_duration: float,
            response_latency: float,
            asr_confidence: float,
            word_timestamps: list
        }
    """
    model = get_whisper_model()

    # Run Whisper transcription with word timestamps
    result = model.transcribe(
        audio_path,
        word_timestamps=True,
        verbose=False
    )

    transcript = result["text"].strip()
    words = []
    word_timestamps = []

    for segment in result.get("segments", []):
        for word_data in segment.get("words", []):
            words.append(word_data["word"].strip())
            word_timestamps.append({
                "word": word_data["word"].strip(),
                "start": word_data["start"],
                "end": word_data["end"],
                "probability": word_data.get("probability", 0.9),
            })

    # Compute confidence as mean word probability
    if word_timestamps:
        asr_confidence = float(np.mean([w["probability"] for w in word_timestamps]))
    else:
        asr_confidence = 0.0

    # Compute speech / silence durations
    audio, sr = librosa.load(audio_path, sr=None)
    total_duration = librosa.get_duration(y=audio, sr=sr)

    # Estimate speech duration from non-silent frames
    non_silent_intervals = librosa.effects.split(audio, top_db=30)
    speech_duration = sum((end - start) for start, end in non_silent_intervals) / sr
    silence_duration = total_duration - speech_duration

    # Response latency = time before first word
    response_latency = word_timestamps[0]["start"] if word_timestamps else total_duration

    return {
        "transcript": transcript,
        "word_count": len(words),
        "speech_duration": round(speech_duration, 3),
        "silence_duration": round(silence_duration, 3),
        "response_latency": round(response_latency, 3),
        "asr_confidence": round(asr_confidence, 4),
        "word_timestamps": word_timestamps,
    }


def extract_audio_features(audio_path: str) -> dict:
    """
    Extract acoustic micro-features using Librosa for CLI computation.

    Returns dict with pitch, energy, speech_rate features.
    """
    audio, sr = librosa.load(audio_path, sr=None)

    # Pitch contour (fundamental frequency)
    f0, voiced_flag, _ = librosa.pyin(
        audio,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sr,
    )
    f0_clean = f0[~np.isnan(f0)] if f0 is not None else np.array([0.0])
    pitch_mean = float(np.mean(f0_clean)) if len(f0_clean) > 0 else 0.0
    pitch_variance = float(np.var(f0_clean)) if len(f0_clean) > 0 else 0.0

    # RMS energy
    rms = librosa.feature.rms(y=audio)[0]
    energy_mean = float(np.mean(rms))
    energy_variance = float(np.var(rms))

    # Micro-pause detection (< 500ms silences between speech)
    non_silent = librosa.effects.split(audio, top_db=30)
    micro_pauses = 0
    pause_durations = []
    for i in range(1, len(non_silent)):
        gap = (non_silent[i][0] - non_silent[i - 1][1]) / sr
        if gap < 0.5:
            micro_pauses += 1
            pause_durations.append(gap)

    # Speech rate (rough: frames of voiced speech / total duration)
    total_duration = librosa.get_duration(y=audio, sr=sr)
    speech_length = sum((e - s) for s, e in non_silent) / sr

    return {
        "pitch_mean": round(pitch_mean, 4),
        "pitch_variance": round(pitch_variance, 4),
        "energy_mean": round(energy_mean, 6),
        "energy_variance": round(energy_variance, 6),
        "micro_pause_count": micro_pauses,
        "pause_durations": [round(p, 3) for p in pause_durations],
        "speech_length": round(speech_length, 3),
        "total_duration": round(total_duration, 3),
    }
