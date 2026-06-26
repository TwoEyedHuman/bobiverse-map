#!/usr/bin/env python3
"""Convert 'Bobiverse PITs - PITs.csv' to web/src/lib/data/bobs.json."""

import csv
import json
from pathlib import Path

MONTHS = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
}

REPO_ROOT = Path(__file__).parent
CSV_PATH = REPO_ROOT / "Bobiverse PITs - PITs.csv"
OUT_PATH = REPO_ROOT / "web" / "src" / "lib" / "data" / "bobs.json"


def parse_assumed_date(raw: str) -> str:
    """Convert 'Mon/YYYY' → 'YYYY-MM-01'."""
    parts = raw.strip().split("/")
    if len(parts) != 2:
        raise ValueError(f"Unexpected Assumed Date format: {raw!r}")
    mon, year = parts
    month_num = MONTHS.get(mon)
    if not month_num:
        raise ValueError(f"Unknown month abbreviation: {mon!r}")
    return f"{year}-{month_num}-01"


def main() -> None:
    records = []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            assumed_date = parse_assumed_date(row["Assumed Date"])
            record: dict = {
                "bob": row["Bob"].strip(),
                "system": row["System"].strip(),
                "assumed_date": assumed_date,
            }
            dead_val = row.get("Dead", "").strip().lower()
            if dead_val in ("true", "yes", "1"):
                record["dead"] = True
            records.append(record)

    OUT_PATH.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} records to {OUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
