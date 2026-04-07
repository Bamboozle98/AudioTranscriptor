from pathlib import Path
import uuid

from src.speech.whisper_client import whisper_summon, whisper_transcribe
from src.llm.llm_client import llm_summon, llm_chat_json
from src.pipeline.item_matcher import ItemMatcher, load_measurable_items
from src.pipeline.item_aliases import apply_aliases
from src.pipeline.record_schema import (
    SYSTEM_RECORD_PARSER,
    validate_and_normalize_record,
    append_records_to_csv,
    append_records_to_xlsx,
)
from src.utils.paths import ensure_output_dirs


measurable = load_measurable_items()
matcher = ItemMatcher(measurable, threshold=85)


def build_user_prompt(transcript: str) -> str:
    return f"Spoken text:\n<<<{transcript}>>>"


def process_audio_file(
    audio_path: str | Path,
    save_csv: bool = True,
    save_xlsx: bool = False,
) -> dict:
    audio_path = Path(audio_path)
    session_id = uuid.uuid4().hex[:10]

    csv_dir, xlsx_dir = ensure_output_dirs()
    csv_path = csv_dir / "weigh_ins.csv"
    xlsx_path = xlsx_dir / "weigh_ins.xlsx"

    whisper = whisper_summon()
    llm_cfg = llm_summon()

    transcript, segments, info = whisper_transcribe(
        whisper,
        str(audio_path),
        language=None,
        vad_filter=True,
    )

    transcript = (transcript or "").strip()
    if not transcript:
        return {
            "session_id": session_id,
            "transcript": "",
            "normalized_transcript": "",
            "records": [],
            "message": "No transcript detected.",
        }

    transcript = apply_aliases(transcript)

    raw = llm_chat_json(
        cfg=llm_cfg,
        system=SYSTEM_RECORD_PARSER,
        user=build_user_prompt(transcript),
        temperature=0.0,
    )

    if not isinstance(raw, list):
        raise ValueError("Model did not return a JSON list.")

    normalized = []
    skipped = []

    for r in raw:
        try:
            rec = validate_and_normalize_record(r, session_id=session_id)

            corrected, score, changed = matcher.correct(rec["item"])
            if corrected:
                rec["item"] = corrected
            else:
                skipped.append({
                    "record": r,
                    "reason": f"Unmatched/empty item: {rec['item']}"
                })
                continue

            normalized.append(rec)

        except Exception as e:
            skipped.append({
                "record": r,
                "reason": str(e),
            })

    if save_csv and normalized:
        append_records_to_csv(str(csv_path), normalized)

    if save_xlsx and normalized:
        append_records_to_xlsx(str(xlsx_path), normalized)

    return {
        "session_id": session_id,
        "transcript": transcript,
        "segments": segments,
        "records": normalized,
        "skipped": skipped,
        "csv_path": str(csv_path) if save_csv else None,
        "xlsx_path": str(xlsx_path) if save_xlsx else None,
    }


if __name__ == "__main__":
    result = process_audio_file("sample.wav")
    print(result)