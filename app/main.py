from pathlib import Path
import os
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

# Import your existing pipeline pieces here
# Adjust these imports to your real functions
# from src.pipeline.main_live import process_audio_file
# or from src.speech.whisper_client import transcribe_file
# or from src.pipeline.item_matcher import match_items

app = FastAPI(title="Dank Burrito Audio Transcriptor")

BASE_DIR = Path("/data") if Path("/data").exists() else Path(".")
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/process")
async def process_audio(file: UploadFile = File(...)):
    allowed = {".wav", ".mp3", ".m4a", ".mp4", ".webm"}
    suffix = Path(file.filename).suffix.lower()

    if suffix not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    job_id = str(uuid.uuid4())
    input_path = UPLOAD_DIR / f"{job_id}{suffix}"

    with input_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Replace this block with your real pipeline call
        # result = process_audio_file(input_path)

        result = {
            "job_id": job_id,
            "filename": file.filename,
            "transcript": "stub transcript",
            "rows": [
                {"item": "sour cream", "quantity": 32, "unit": "oz"}
            ]
        }

        return JSONResponse(result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))