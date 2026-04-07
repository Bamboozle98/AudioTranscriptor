from pathlib import Path
import re
import pdfplumber
import pandas as pd
from src.utils.paths import get_project_root

PROJECT_ROOT = get_project_root()

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "inventory_list_pdfs"
OUT_DIR = PROJECT_ROOT / "data" / "processed" / "inventory_lists"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def clean_text(x) -> str:
    if x is None:
        return ""
    x = str(x).strip()
    x = re.sub(r"\s+", " ", x)
    return x


def parse_price(x):
    x = clean_text(x).replace("$", "").replace(",", "")
    try:
        return float(x)
    except ValueError:
        return None


def parse_count(x):
    x = clean_text(x).replace(",", "")
    try:
        return float(x)
    except ValueError:
        return None


def safe_slug(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def is_noise_row(cells: list[str]) -> bool:
    joined = " ".join(cells).lower().strip()
    if not joined:
        return True

    noise_prefixes = [
        "item report by",
        "count",
        "page ",
        "inventory count",
        "generated",
        "printed",
        "location:",
        "date:",
    ]
    return any(joined.startswith(x) for x in noise_prefixes)


def is_section_row(cells: list[str]) -> bool:
    non_empty = [c for c in cells if c]
    if len(non_empty) != 1:
        return False

    text = non_empty[0]
    if not text:
        return False

    if parse_price(text) is not None:
        return False

    if parse_count(text) is not None:
        return False

    if len(text) > 80:
        return False

    return True


def parse_data_row(cells: list[str]):
    non_empty = [c for c in cells if c]
    if len(non_empty) < 4:
        return None

    item = non_empty[0]
    report_by = non_empty[1]
    price = parse_price(non_empty[2])
    count = parse_count(non_empty[3])

    if not item or price is None or count is None:
        return None

    return {
        "item": item,
        "report_by": report_by,
        "price": price,
        "count": count,
    }


def extract_inventory_pdf(pdf_path: Path) -> pd.DataFrame:
    rows = []
    current_section = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()

            if not tables:
                continue

            for table in tables:
                if not table:
                    continue

                for raw_row in table:
                    cells = [clean_text(c) for c in raw_row]

                    if is_noise_row(cells):
                        continue

                    if is_section_row(cells):
                        current_section = [c for c in cells if c][0]
                        continue

                    parsed = parse_data_row(cells)
                    if parsed is None:
                        continue

                    rows.append(
                        {
                            "source_pdf": pdf_path.name,
                            "page": page_num,
                            "raw_section": current_section,
                            "item": parsed["item"],
                            "report_by": parsed["report_by"],
                            "price": parsed["price"],
                            "count": parsed["count"],
                        }
                    )

    return pd.DataFrame(rows)


def save_outputs(df: pd.DataFrame, pdf_path: Path):
    stem = safe_slug(pdf_path.stem)

    master_csv = OUT_DIR / f"{stem}.csv"
    df.to_csv(master_csv, index=False)

    if "raw_section" in df.columns:
        for section, group in df.groupby("raw_section"):
            if not section:
                continue
            sec_slug = safe_slug(section)
            group.to_csv(OUT_DIR / f"{stem}__{sec_slug}.csv", index=False)


def process_all_pdfs():
    pdf_files = sorted(RAW_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDFs found in {RAW_DIR}")
        return

    print(f"Found {len(pdf_files)} PDFs")

    for pdf_path in pdf_files:
        print(f"\nProcessing {pdf_path.name}...")
        try:
            df = extract_inventory_pdf(pdf_path)

            if df.empty:
                print("  No structured rows found.")
                continue

            save_outputs(df, pdf_path)
            print(f"  Saved {len(df)} rows.")

        except Exception as e:
            print(f"  Failed: {e}")


if __name__ == "__main__":
    process_all_pdfs()