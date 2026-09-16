"""Probe candidate Intel ARK SKUs for 4th/5th Gen desktop Core CPUs."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_intel_ark_specs import fetch_sku

PROBES = [
    75123, 75043, 75048, 75047, 75046, 75045, 75044, 75049, 75050,
    80807, 80811, 80815, 80810, 80809, 80808, 80812, 80813, 80814,
    80910, 80911, 80912, 80913, 80914, 80915,
    84985, 87756, 88086, 77775, 77780, 77773, 77772, 77771,
    76617, 76616, 76663, 76664, 76615, 76614,
    83446, 83448, 83501, 83504, 84601, 84605,
    82931, 82932, 82933, 82934, 82935,
    74876, 74877, 74878, 74879, 74880,
]


def main() -> None:
    for sku in PROBES:
        try:
            data = fetch_sku(sku)
        except Exception as exc:
            print(f"{sku}: ERR {exc}", flush=True)
            continue
        if not data:
            print(f"{sku}: none", flush=True)
            continue
        print(
            f"{sku}: {data['model']} | {data.get('collection')} | "
            f"seg={data['specs'].get('market_segment')} | sock={data['specs'].get('socket')}",
            flush=True,
        )


if __name__ == "__main__":
    main()
