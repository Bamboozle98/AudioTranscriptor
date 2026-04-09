from pathlib import Path
import csv

from src.utils.paths import get_runtime_root, get_project_root


def load_inventory_catalog() -> list[str]:
    project_root = get_project_root()
    inventory_dir = project_root / "data" / "processed" / "inventory_lists"

    files = [
        "boh_f_p.csv",
        "coolers.csv",
        "features.csv",
        "lobby_line.csv",
        "merch.csv",
        "truck.csv",
    ]

    items = set()

    for filename in files:
        path = inventory_dir / filename
        if not path.exists():
            continue

        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                for cell in row:
                    value = (cell or "").strip()
                    if value and value.lower() not in {"item", "items", "name"}:
                        items.add(value)

    return sorted(items)