from pathlib import Path
import os


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_runtime_root() -> Path:
    runtime_root = Path(os.getenv("RUNTIME_DATA_DIR", "/data"))
    if runtime_root.exists():
        return runtime_root
    return get_project_root() / "data"


def ensure_output_dirs():
    root = get_runtime_root()
    csv_dir = root / "output" / "csv"
    xlsx_dir = root / "output" / "xlsx"
    csv_dir.mkdir(parents=True, exist_ok=True)
    xlsx_dir.mkdir(parents=True, exist_ok=True)
    return csv_dir, xlsx_dir