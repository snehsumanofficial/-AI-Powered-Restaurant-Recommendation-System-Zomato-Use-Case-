from __future__ import annotations

import argparse
import json

from src.phases.phase1.settings import load_settings
from src.phases.phase2.loader import _load_hf_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect dataset schema and sample rows.")
    parser.add_argument("--samples", type=int, default=3, help="Number of rows to print")
    args = parser.parse_args()

    settings = load_settings()
    rows = _load_hf_rows(settings)
    if not rows:
        print("Dataset returned zero rows")
        return

    keys = sorted({key for row in rows for key in row.keys()})
    print("Columns:")
    for key in keys:
        print(f"- {key}")

    print("\nSample rows:")
    for row in rows[: args.samples]:
        print(json.dumps(row, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
