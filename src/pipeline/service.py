from pathlib import Path

from src.speech.whisper_client import transcribe_audio_file
from src.utils.normalize_text import normalize_text
from src.pipeline.item_matcher import extract_records_from_text

def process_audio_file(input_path: str) -> dict:
    input_path = Path(input_path)

    transcript = transcribe_audio_file(input_path)
    cleaned = normalize_text(transcript)
    rows = extract_records_from_text(cleaned)

    return {
        "transcript": transcript,
        "normalized_text": cleaned,
        "rows": rows,
    }