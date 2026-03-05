import json
import re
import unicodedata
from pathlib import Path
from typing import Optional, Tuple

from rapidfuzz import process, fuzz


# High-value manual fixes (optional but helpful)
MANUAL_ALIASES = {
    "bond me": "banh mi",
    "bahn me": "banh mi",
    "ban me": "banh mi",
    "chipotle, aioli": "chipotle aioli",
}


def _norm(s: str) -> str:
    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def load_measurable_items() -> list[str]:
    root = Path(__file__).resolve().parents[2]  # project root
    path = root / "data" / "menu" / "measurable_items.json"
    return json.loads(path.read_text(encoding="utf-8"))


class ItemMatcher:
    def __init__(self, items: list[str], threshold: int = 85):
        self.items = items
        self.threshold = threshold
        self._items_norm = [_norm(x) for x in items]

    def correct(self, raw_item: str) -> Tuple[str, int, bool]:
        """
        Returns (corrected_item, score, changed)
        - If below threshold, returns original (cleaned) item and score.
        """
        raw = (raw_item or "").strip()
        if not raw:
            return "", 0, False

        # apply manual alias first
        aliased = MANUAL_ALIASES.get(_norm(raw), raw)

        query = _norm(aliased)
        if not query:
            return aliased.strip(), 0, False

        match = process.extractOne(query, self._items_norm, scorer=fuzz.WRatio)
        if not match:
            return aliased.strip(), 0, False

        _best_norm, score, idx = match
        if score >= self.threshold:
            corrected = self.items[idx]
            return corrected, int(score), (_norm(corrected) != _norm(aliased))
        else:
            return aliased.strip(), int(score), False