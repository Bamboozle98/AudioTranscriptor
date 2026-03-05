from src.audio.mic_capture import list_input_devices, record_until_enter
from src.speech.whisper_client import whisper_summon, whisper_transcribe_audio
from src.llm.ollama_client import ollama_summon, ollama_chat_json
from src.pipeline.item_matcher import ItemMatcher, load_measurable_items
from src.pipeline.item_aliases import apply_aliases
from src.pipeline.record_schema import (
    SYSTEM_RECORD_PARSER,
    validate_and_normalize_record,
    append_records_to_csv,
    append_records_to_xlsx,
)
from src.utils.paths import ensure_output_dirs

import uuid
session_id = uuid.uuid4().hex[:10]  # short but unique per session
print(f"Session ID: {session_id}")
measurable = load_measurable_items()
matcher = ItemMatcher(measurable, threshold=85)


def build_user_prompt(transcript: str) -> str:
    return f"Spoken text:\n<<<{transcript}>>>"


def main():
    # --- ensure output dirs ---
    csv_dir, xlsx_dir = ensure_output_dirs()
    csv_path = csv_dir / "weigh_ins.csv"
    xlsx_path = xlsx_dir / "weigh_ins.xlsx"

    whisper = whisper_summon()
    ollama_cfg = ollama_summon()

    print("Live mode.")
    print("Press ENTER to start recording an entry.")
    print("Press ENTER again to stop.")
    print("Type 'q' then ENTER at the prompt to quit.\n")

    while True:
        cmd = input("Ready (ENTER to start, 'q' to quit) > ").strip().lower()
        if cmd == "q":
            break

        # Record user-controlled duration
        audio = record_until_enter(samplerate=16000, device=None, channels=1)

        if audio.size == 0:
            print("No audio captured.\n")
            continue

        # Whisper
        transcript, segments, info = whisper_transcribe_audio(
            whisper,
            audio,
            language=None,
            vad_filter=True,
        )

        transcript = (transcript or "").strip()
        if not transcript:
            print("No transcript detected.\n")
            continue

        transcript = apply_aliases(transcript)
        print(f"\nTranscript (normalized): {transcript}")

        print(f"\nTranscript: {transcript}")

        # Ollama → list of records
        raw = ollama_chat_json(
            cfg=ollama_cfg,
            system=SYSTEM_RECORD_PARSER,
            user=build_user_prompt(transcript),
            temperature=0.0,
        )

        if not isinstance(raw, list):
            print("Model did not return a JSON list. Skipping.\n")
            continue

        normalized = []
        for r in raw:
            try:
                rec = validate_and_normalize_record(r, session_id=session_id)

                corrected, score, changed = matcher.correct(rec["item"])
                if corrected:
                    if changed:
                        print(f"Item corrected: '{rec['item']}' -> '{corrected}' (score={score})")
                    rec["item"] = corrected
                else:
                    print(f"Unmatched/empty item, skipped: {rec['item']}")
                    continue

                normalized.append(rec)

            except Exception as e:
                print(f"Skipped bad record {r} ({e})")

        # Save BOTH
        append_records_to_csv(str(csv_path), normalized)
        append_records_to_xlsx(str(xlsx_path), normalized)

        print(f"Saved {len(normalized)} record(s) to:")
        print(f"  CSV : {csv_path}")
        print(f"  XLSX: {xlsx_path}\n")


if __name__ == "__main__":
    main()