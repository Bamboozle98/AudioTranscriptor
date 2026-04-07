import re


def clean_item(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    s = re.sub(r"\(.*?\)", "", s)  # remove (lbs), etc.
    s = re.sub(r"[^a-z0-9\s\"#]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s