"""
Build verified GPU catalog JSON from curated NVIDIA official data.

Usage:
    python scripts/build_gpu_catalog.py
    python scripts/build_gpu_catalog.py --validate
    python scripts/build_gpu_catalog.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.catalog.catalog_validation import validate_catalog_records
from data.catalog.gpu.verified_nvidia_rtx_40_gen import (
    NVIDIA_RTX_40_DESKTOP,
    VERIFIED_DATE,
)

CATALOG_ROOT = BACKEND_ROOT / "data" / "catalog" / "gpu"

SPEC_GROUPS = {
    "architecture": "Identity",
    "gpu_die": "Identity",
    "codename": "Identity",
    "generation": "Identity",
    "product_family": "Identity",
    "market_segment": "Identity",
    "launch_msrp": "Identity",
    "process_node": "Process",
    "compute_units": "Compute",
    "shader_units": "Compute",
    "cuda_cores": "Compute",
    "stream_processors": "Compute",
    "xe_cores": "Compute",
    "rt_cores": "Compute",
    "tensor_cores": "Compute",
    "ray_accelerators": "Compute",
    "xmx_engines": "Compute",
    "ray_tracing_units": "Compute",
    "base_clock": "Clocks",
    "boost_clock": "Clocks",
    "game_clock": "Clocks",
    "memory_clock": "Clocks",
    "vram_capacity": "Memory",
    "vram_type": "Memory",
    "memory_bus_width": "Memory",
    "memory_speed": "Memory",
    "memory_bandwidth": "Memory",
    "tdp": "Power",
    "tbp": "Power",
    "board_power": "Power",
    "recommended_psu": "Power",
    "pci_express": "Interface",
    "display_outputs": "Interface",
    "maximum_displays": "Interface",
    "slot_width": "Physical",
    "length": "Physical",
    "height": "Physical",
    "power_connectors": "Physical",
}

SPEC_UNITS = {
    "launch_msrp": "USD",
    "process_node": "nm",
    "base_clock": "MHz",
    "boost_clock": "MHz",
    "game_clock": "MHz",
    "memory_clock": "MHz",
    "vram_capacity": "GB",
    "memory_bus_width": "bit",
    "memory_speed": "Gbps",
    "memory_bandwidth": "GB/s",
    "tdp": "W",
    "tbp": "W",
    "board_power": "W",
    "recommended_psu": "W",
    "length": "mm",
    "height": "mm",
}


class CatalogBuildError(Exception):
    pass


def _model_slug(model: str) -> str:
    return f"nvidia-geforce-{model.lower().replace(' ', '-')}"


def _specs_from_dict(specs: dict) -> list[dict]:
    entries = []
    for key in sorted(specs.keys()):
        value = specs[key]
        if value is None or value == "":
            continue
        if key not in SPEC_GROUPS:
            raise CatalogBuildError(f"Unknown specification key '{key}'")
        entry = {"group": SPEC_GROUPS[key], "key": key, "value": str(value)}
        unit = SPEC_UNITS.get(key)
        if unit:
            entry["unit"] = unit
        entries.append(entry)
    return entries


def build_nvidia_record(entry: dict) -> dict:
    model = entry["model"]
    specs = dict(entry["specs"])
    specs["launch_msrp"] = entry["launch_msrp"]

    name = f"NVIDIA GeForce {model}"
    slug = _model_slug(model)
    record = {
        "category": "GPU",
        "manufacturer": "NVIDIA",
        "family": "GeForce",
        "series": "GeForce RTX",
        "generation": "RTX 40 Series",
        "architecture": specs.get("architecture", "Ada Lovelace"),
        "source": {
            "name": "NVIDIA official product specifications",
            "url": entry["source_url"],
            "date": VERIFIED_DATE,
            "notes": (
                "Specifications verified against NVIDIA GeForce product "
                "specification pages on nvidia.com."
            ),
        },
        "product": {
            "name": name,
            "slug": slug,
            "description": (
                f"NVIDIA GeForce {model} desktop graphics card based on the "
                f"Ada Lovelace architecture."
            ),
            "release_date": entry["release_date"],
            "status": "active",
            "is_popular": entry.get("is_popular", False),
            "architecture": specs.get("architecture", "Ada Lovelace"),
        },
        "images": [],
        "specifications": _specs_from_dict(specs),
        "benchmarks": [],
    }
    errors, _ = validate_catalog_records([record])
    if errors:
        raise CatalogBuildError(f"NVIDIA {model} validation failed: {'; '.join(errors)}")
    return record


def build_rtx_40_desktop_batch() -> list[dict]:
    return [build_nvidia_record(entry) for entry in NVIDIA_RTX_40_DESKTOP]


def write_catalog(path: Path, records: list[dict]) -> None:
    errors, warnings = validate_catalog_records(records)
    if errors:
        raise CatalogBuildError(f"{path}: {'; '.join(errors)}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} records to {path}")


def collect_catalog_records(root: Path = CATALOG_ROOT) -> list[dict]:
    """Load all non-empty JSON catalog batches under the GPU tree."""
    records: list[dict] = []
    for path in sorted(root.glob("**/*.json")):
        if path.name in {"schema.json"} or path.name.startswith("_"):
            continue
        text = path.read_text(encoding="utf-8").strip()
        if not text or text == "[]":
            continue
        batch = json.loads(text)
        if not isinstance(batch, list):
            raise ValueError(f"{path}: catalog file must contain a JSON array")
        records.extend(batch)
    return records


def validate_catalog_tree(root: Path = CATALOG_ROOT) -> int:
    errors_found = 0
    for path in sorted(root.glob("**/*.json")):
        if path.name in {"schema.json"} or path.name.startswith("_"):
            continue
        text = path.read_text(encoding="utf-8").strip()
        if not text or text == "[]":
            print(f"SKIP {path} (empty)")
            continue
        records = json.loads(text)
        errors, warnings = validate_catalog_records(records)
        if errors:
            errors_found += len(errors)
            print(f"FAIL {path}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"OK {path} ({len(records)} records)")
        for warning in warnings:
            print(f"  warning: {warning}")
    return 1 if errors_found else 0


def dry_run_import(root: Path = CATALOG_ROOT) -> int:
    records = collect_catalog_records(root)
    if not records:
        print("No GPU catalog records found.")
        return 1
    errors, warnings = validate_catalog_records(records)
    for warning in warnings:
        print(f"warning: {warning}")
    if errors:
        for err in errors:
            print(f"error: {err}")
        return 1
    print(f"Dry run OK: {len(records)} record(s) ready for import.")
    return 0


def build_all() -> None:
    records = build_rtx_40_desktop_batch()
    output = (
        CATALOG_ROOT / "nvidia" / "geforce" / "rtx-40-series" / "desktop.json"
    )
    write_catalog(output, records)


def main() -> int:
    parser = argparse.ArgumentParser(description="GPU catalog builder")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.validate:
        return validate_catalog_tree()
    if args.dry_run:
        return dry_run_import()
    build_all()
    return validate_catalog_tree()


if __name__ == "__main__":
    raise SystemExit(main())
