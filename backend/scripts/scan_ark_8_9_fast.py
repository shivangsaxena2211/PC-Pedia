"""Fast targeted Intel ARK scan for 8th/9th gen desktop CPUs."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_intel_ark_specs import fetch_sku

OUT = Path(__file__).resolve().parent / "ark_desktop_8_9.json"

RANGES = [
    (134850, 134950, "9th"),
    (186590, 187200, "9th"),
    (190850, 191900, "9th"),
    (192900, 194100, "9th"),
    (126600, 127100, "8th"),
]


def main():
    found: dict[str, dict] = {}
    if OUT.exists() and OUT.read_text(encoding="utf-8").strip():
        for row in json.loads(OUT.read_text(encoding="utf-8")):
            found[row["model"]] = row

    for start, end, hint in RANGES:
        print(f"Scanning {start}-{end} ({hint})...", flush=True)
        for sku in range(start, end):
            try:
                data = fetch_sku(sku)
            except Exception:
                continue
            if not data or hint not in (data.get("collection") or ""):
                continue
            if data["specs"].get("market_segment") != "Desktop":
                continue
            model = data["model"]
            if model in found:
                continue
            found[model] = data
            print(f"FOUND {sku}: {model}", flush=True)
            time.sleep(0.01)

    results = sorted(found.values(), key=lambda row: row["model"])
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    gen9 = sum(1 for row in results if "9th" in row.get("collection", ""))
    gen8 = sum(1 for row in results if "8th" in row.get("collection", ""))
    print(f"Wrote {len(results)} records ({gen9} 9th, {gen8} 8th)", flush=True)


if __name__ == "__main__":
    main()
