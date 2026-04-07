from pathlib import Path
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from src.pipeline.main_live import process_audio_file


app = FastAPI(title="Dank Burrito Audio API")

BASE_DIR = Path("/data") if Path("/data").exists() else Path(".")
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/process")
async def process_audio(file: UploadFile = File(...)):
    allowed = {".wav", ".mp3", ".m4a", ".mp4", ".webm"}
    suffix = Path(file.filename or "").suffix.lower()

    if suffix not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    job_id = str(uuid.uuid4())
    input_path = UPLOAD_DIR / f"{job_id}{suffix}"

    try:
        with input_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = process_audio_file(
            audio_path=input_path,
            save_csv=True,
            save_xlsx=False,
        )

        return JSONResponse(
            {
                "ok": True,
                "job_id": job_id,
                "filename": file.filename,
                **result,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))