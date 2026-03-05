import argparse

from src.speech.whisper_client import whisper_summon, whisper_transcribe
from src.llm.ollama_client import ollama_summon, ollama_chat_json
from src.pipeline.record_schema import (
    SYSTEM_RECORD_PARSER,
    validate_and_normalize_record,
    append_record_to_csv,
)


def build_user_prompt(transcript: str) -> str:
    return f"""Spoken text:
<<<{transcript}>>>"""


def main():
    ap = argparse.ArgumentParser(description="Voice -> Whisper -> Ollama -> CSV record append")
    ap.add_argument("--audio", required=True, help="Path to audio file (wav/mp3/m4a, etc.)")
    ap.add_argument("--csv", default="hand_records.csv", help="Output CSV file path")
    ap.add_argument("--language", default=None, help="Optional language code (e.g., en, tr)")
    ap.add_argument("--confirm", action="store_true", help="Confirm record before saving")
    args = ap.parse_args()

    # 1) Load models/config
    whisper = whisper_summon()
    ollama_cfg = ollama_summon()

    # 2) Transcribe
    transcript, segments, info = whisper_transcribe(
        whisper,
        args.audio,
        language=args.language,
        vad_filter=True,
    )

    if not transcript:
        raise SystemExit("No transcript produced. Check audio path/format.")

    # 3) Parse record via LLM (JSON)
    user_prompt = build_user_prompt(transcript)
    record = ollama_chat_json(
        cfg=ollama_cfg,
        system=SYSTEM_RECORD_PARSER,
        user=user_prompt,
        temperature=0.0,
    )

    # 4) Validate + normalize, then append to CSV
    record = validate_and_normalize_record(record)

    if args.confirm:
        print("\n--- Parsed Record ---")
        for k, v in record.items():
            print(f"{k}: {v}")
        ok = input("\nSave to CSV? (y/n): ").strip().lower()
        if ok != "y":
            print("Not saved.")
            return

    append_record_to_csv(args.csv, record)
    print(f"Saved record to {args.csv}")


if __name__ == "__main__":
    main()