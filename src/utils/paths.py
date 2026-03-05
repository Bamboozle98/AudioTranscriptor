from pathlib import Path


def get_project_root() -> Path:
    # this file is src/utils/paths.py → root is two parents up from src/
    return Path(__file__).resolve().parents[2]


def ensure_output_dirs():
    root = get_project_root()
    csv_dir = root / "data" / "output" / "csv"
    xlsx_dir = root / "data" / "output" / "xlsx"
    csv_dir.mkdir(parents=True, exist_ok=True)
    xlsx_dir.mkdir(parents=True, exist_ok=True)
    return csv_dir, xlsx_dir

