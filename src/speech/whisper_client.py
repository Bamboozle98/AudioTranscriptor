from faster_whisper import WhisperModel
import numpy as np
import os
from pathlib import Path

CACHE_BASE = Path(os.getenv("HF_HOME", "/tmp/hf_cache"))
CACHE_BASE.mkdir(parents=True, exist_ok=True)

os.environ.setdefault("HF_HOME", str(CACHE_BASE))
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(CACHE_BASE / "hub"))
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")


def whisper_summon(
    model_name: str = "large-v3",
    device: str = "cuda",
    compute_type: str = "float16",
):
    """
    Create and return a Faster-Whisper model instance.
    """
    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    return model


def whisper_transcribe_audio(
    model,
    audio: np.ndarray,
    language: str | None = None,
    task: str = "transcribe",
    vad_filter: bool = True,
):
    """
    Transcribe from an in-memory waveform (float32 mono at ~16kHz).
    Returns (full_text, segments, info).
    """
    segments_iter, info = model.transcribe(
        audio,
        language=language,
        task=task,
        vad_filter=vad_filter,
    )

    segments = []
    parts = []
    for s in segments_iter:
        text = (s.text or "").strip()
        if text:
            parts.append(text)
        segments.append({"start": float(s.start), "end": float(s.end), "text": text})

    return " ".join(parts).strip(), segments, info


def whisper_transcribe(
    model: WhisperModel,
    audio_path: str,
    language: str | None = None,
    task: str = "transcribe",
    vad_filter: bool = True,
):
    """
    Transcribe an audio file and return:
      - full_text: str
      - segments: list of dicts with start/end/text
    """
    segments_iter, info = model.transcribe(
        audio_path,
        language=language,
        task=task,
        vad_filter=vad_filter,
    )

    segments = []
    parts = []
    for s in segments_iter:
        text = (s.text or "").strip()
        if text:
            parts.append(text)
        segments.append(
            {
                "start": float(s.start),
                "end": float(s.end),
                "text": text,
            }
        )

    full_text = " ".join(parts).strip()
    return full_text, segments, info