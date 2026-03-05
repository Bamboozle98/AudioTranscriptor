from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable, Set

import requests
from bs4 import BeautifulSoup

MENU_PAGES = [
    "https://www.dankburrito.com/menu/burritos/",
    "https://www.dankburrito.com/menu/bowls/",
    "https://www.dankburrito.com/menu/salads-copy/",
    "https://www.dankburrito.com/menu/add-ons-sides-drinks/",
    "https://www.dankburrito.com/menu/little-danksters/",
]

# Words we DON'T want as "items"
STOP_EXACT = {
    "menu", "burritos", "tacos", "bowls", "salads", "sides & drinks", "kids' meals", "dessert",
    "order now", "rewards", "facebook", "twitter", "instagram", "youtube", "email",
    "faq", "email signup", "join us", "contact", "privacy policy",
    "powered by bentobox", "main content starts here", "skip to main content",
    "toggle navigation", "close", "submit",
    "hot", "medium", "mild", "spicy", "protein",
}

# Ingredient-ish tokens to pull from description lines
INGREDIENT_SPLIT = re.compile(r"[,|]")  # comma or pipe
JUNK_LINE = re.compile(r"^(\$?\d+(\.\d{2})?|leave this field blank)$", re.I)

def fetch_text(url: str) -> str:
    r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # remove obvious non-content
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text("\n")
    text = re.sub(r"[ \t]+", " ", text)
    return text

def clean_line(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s

def is_probable_item_title(line: str) -> bool:
    low = line.lower()
    if low in STOP_EXACT:
        return False
    if JUNK_LINE.match(line):
        return False
    # short title-like lines, no commas, not too long
    if 2 <= len(line) <= 40 and "," not in line and "|" not in line:
        # many item titles on these pages are Title Case
        if line[:1].isupper() and any(ch.isalpha() for ch in line):
            return True
    return False

def extract_items_from_page(text: str) -> Set[str]:
    lines = [clean_line(ln) for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]

    titles: Set[str] = set()
    ingredients: Set[str] = set()

    for ln in lines:
        if is_probable_item_title(ln):
            titles.add(ln)

        # pull ingredient phrases from description-y lines
        if "," in ln or "|" in ln:
            parts = [clean_line(p) for p in INGREDIENT_SPLIT.split(ln)]
            for p in parts:
                low = p.lower()
                if low in STOP_EXACT:
                    continue
                if JUNK_LINE.match(p):
                    continue
                # keep ingredient-like phrases
                if 3 <= len(p) <= 35 and any(ch.isalpha() for ch in p):
                    ingredients.add(p)

    # You likely weigh ingredients/sauces more than entree names.
    return titles | ingredients

def main():
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "data" / "menu"
    out_dir.mkdir(parents=True, exist_ok=True)

    all_items: Set[str] = set()
    for url in MENU_PAGES:
        text = fetch_text(url)
        all_items |= extract_items_from_page(text)

    # final cleanup pass
    cleaned = []
    for item in all_items:
        low = item.lower()
        if low in STOP_EXACT:
            continue
        if "enter a valid" in low:
            continue
        cleaned.append(item)

    cleaned = sorted(set(cleaned), key=lambda x: x.lower())

    out_path = out_dir / "menu_items.json"
    out_path.write_text(json.dumps(cleaned, indent=2), encoding="utf-8")
    print(f"Wrote {len(cleaned)} items to {out_path}")


if __name__ == "__main__":
    main()
