"""Fast targeted Intel ARK scan for 4th/5th gen desktop Core CPUs."""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_intel_ark_specs import fetch_sku

OUT = Path(__file__).resolve().parent / "ark_desktop_4_5.json"
EXCL_OUT = Path(__file__).resolve().parent / "ark_desktop_4_5_excluded.txt"

# Seed known ARK IDs discovered via Intel product pages / prior probes.
SEED_SKUS = [
    # Broadwell desktop Core (LGA1150)
    88040,  # i7-5775C
    88095,  # i5-5675C
    # Haswell / Haswell Refresh Core desktop
    75122, 75123, 75038, 75043, 75048, 75047, 75045, 75044, 75049, 75050,
    77656, 77771, 77769, 77486, 77491, 77490,
    80807, 80811, 80815, 80810, 80809, 80808, 80812, 80813, 80814, 80817,
    81209, 81207, 78928, 78927,
]

RANGES = [
    (74850, 75250, "4th"),
    (77450, 77550, "4th"),
    (77600, 77850, "4th"),
    (78900, 79050, "4th"),
    (80750, 80950, "4th"),
    (81180, 81250, "4th"),
    (87950, 88200, "5th"),
]

CORE_MODEL = re.compile(r"^I[357]-\d{4}[A-Z]*$", re.IGNORECASE)


def is_core_desktop(data: dict) -> tuple[bool, str]:
    collection = data.get("collection") or ""
    model = (data.get("model") or "").upper()
    segment = (data.get("specs") or {}).get("market_segment") or ""
    socket = (data.get("specs") or {}).get("socket") or ""

    if "Desktop" not in segment:
        return False, "not desktop segment"
    if not CORE_MODEL.match(model):
        return False, "not Core i3/i5/i7 model"
    if model.endswith("TE"):
        return False, "embedded TE SKU"
    if "X-series" in collection or "Xeon" in collection:
        return False, "X-series/Xeon"
    if "Pentium" in collection or "Celeron" in collection:
        return False, "Pentium/Celeron"
    if "2011" in socket:
        return False, "LGA2011 HEDT"
    if socket and "1150" not in socket:
        return False, f"non-LGA1150 socket ({socket})"
    return True, ""


def ingest(sku: int, hint: str | None, found: dict[str, dict], excluded: list[str]) -> None:
    try:
        data = fetch_sku(sku)
    except Exception as exc:
        excluded.append(f"{sku} fetch_error | {exc}")
        return
    if not data:
        return
    collection = data.get("collection") or ""
    if hint and hint not in collection:
        return
    ok, reason = is_core_desktop(data)
    if not ok:
        excluded.append(f"{sku} {data.get('model')} | {collection} | {reason}")
        return
    model = data["model"]
    if model in found:
        return
    found[model] = data
    print(
        f"FOUND {sku}: {model} | {collection} | sock={(data.get('specs') or {}).get('socket')}",
        flush=True,
    )


def main() -> None:
    found: dict[str, dict] = {}
    excluded: list[str] = []

    print("Seeding known SKUs...", flush=True)
    for sku in SEED_SKUS:
        ingest(sku, None, found, excluded)
        time.sleep(0.05)

    for start, end, hint in RANGES:
        print(f"Scanning {start}-{end} ({hint})...", flush=True)
        for sku in range(start, end):
            ingest(sku, hint, found, excluded)
            time.sleep(0.01)

    results = sorted(found.values(), key=lambda row: row["model"])
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    gen5 = sum(1 for row in results if "5th" in row.get("collection", ""))
    gen4 = sum(1 for row in results if "4th" in row.get("collection", ""))
    print(f"Wrote {len(results)} records ({gen5} 5th, {gen4} 4th)", flush=True)

    unique_excl = sorted(set(excluded))
    EXCL_OUT.write_text("\n".join(unique_excl), encoding="utf-8")
    print(f"Wrote {len(unique_excl)} exclusions to {EXCL_OUT.name}", flush=True)


if __name__ == "__main__":
    main()
