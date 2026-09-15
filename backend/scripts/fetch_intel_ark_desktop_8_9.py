"""Batch-fetch verified Intel ARK desktop CPUs for 8th and 9th generations."""

from __future__ import annotations

import json
import time
from pathlib import Path

from fetch_intel_ark_specs import fetch_sku

OUT = Path(__file__).resolve().parent / "ark_desktop_8_9.json"


def scan_ranges() -> list[dict]:
    ranges = [
        (186500, 187200, "9th"),
        (193600, 194100, "9th"),
        (126500, 127200, "8th"),
    ]
    found: dict[str, dict] = {}
    for start, end, hint in ranges:
        for sku in range(start, end):
            try:
                data = fetch_sku(sku)
                if not data:
                    continue
                if hint not in (data.get("collection") or ""):
                    continue
                if data["specs"].get("market_segment") != "Desktop":
                    continue
                model = data["model"]
                if model in found:
                    continue
                found[model] = data
                print(f"FOUND {sku}: {model}")
            except Exception as exc:
                print(f"ERR {sku}: {exc}")
            time.sleep(0.05)
    return sorted(found.values(), key=lambda row: row["model"])


def main():
    results = scan_ranges()
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    gen9 = sum(1 for row in results if "9th" in row.get("collection", ""))
    gen8 = sum(1 for row in results if "8th" in row.get("collection", ""))
    print(f"Wrote {len(results)} records ({gen9} 9th, {gen8} 8th) to {OUT}")


if __name__ == "__main__":
    main()
