"""Merge additional verified Intel ARK SKUs into ark_desktop_8_9.json."""

from __future__ import annotations

import json
import time
from pathlib import Path

from fetch_intel_ark_specs import fetch_sku

OUT = Path(__file__).resolve().parent / "ark_desktop_8_9.json"

CANDIDATE_SKUS = (
    list(range(134860, 134920))
    + list(range(126690, 126730))
    + list(range(129920, 129980))
    + list(range(190870, 190920))
    + list(range(193735, 193750))
    + [191788, 191790, 191791, 191792, 129937, 129939, 129942, 129948]
)


def main():
    found = {}
    if OUT.exists() and OUT.read_text(encoding="utf-8").strip():
        for row in json.loads(OUT.read_text(encoding="utf-8")):
            found[row["model"]] = row

    for sku in CANDIDATE_SKUS:
        try:
            data = fetch_sku(sku)
        except Exception:
            time.sleep(0.05)
            continue
        if not data:
            continue
        collection = data.get("collection") or ""
        if "9th" not in collection and "8th" not in collection:
            continue
        if data["specs"].get("market_segment") != "Desktop":
            continue
        model = data["model"]
        if model in found:
            continue
        found[model] = data
        print(f"NEW {sku}: {model}")
        time.sleep(0.02)

    results = sorted(found.values(), key=lambda row: row["model"])
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    gen9 = sum(1 for row in results if "9th" in row.get("collection", ""))
    gen8 = sum(1 for row in results if "8th" in row.get("collection", ""))
    print(f"TOTAL {len(results)} ({gen9} 9th, {gen8} 8th)")


if __name__ == "__main__":
    main()
