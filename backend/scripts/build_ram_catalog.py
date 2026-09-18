"""
Build verified RAM catalog JSON from curated manufacturer data.

Usage:
    python scripts/build_ram_catalog.py
    python scripts/build_ram_catalog.py --validate
    python scripts/build_ram_catalog.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.catalog.catalog_validation import validate_catalog_records
from app.data.ram_slug_policy import canonical_ram_slug
from data.catalog.ram.verified_ddr4_desktop_udimm import (
    DDR4_DESKTOP_UDIMM,
    VERIFIED_DATE as DDR4_VERIFIED_DATE,
)
from data.catalog.ram.verified_ddr5_desktop_udimm import (
    DDR5_DESKTOP_UDIMM,
    VERIFIED_DATE as DDR5_VERIFIED_DATE,
)

CATALOG_ROOT = BACKEND_ROOT / "data" / "catalog" / "ram"

SPEC_GROUPS = {
    "memory_type": "Identity",
    "form_factor": "Identity",
    "market_segment": "Identity",
    "product_family": "Identity",
    "generation": "Identity",
    "part_number": "Identity",
    "module_capacity": "Capacity",
    "total_kit_capacity": "Capacity",
    "module_count": "Capacity",
    "memory_speed": "Performance",
    "jedec_speed": "Performance",
    "cas_latency": "Performance",
    "timings": "Performance",
    "voltage": "Performance",
    "ecc": "Features",
    "registered": "Features",
    "xmp": "Features",
    "expo": "Features",
    "pin_count": "Physical",
    "module_height": "Physical",
}

SPEC_UNITS = {
    "module_capacity": "GB",
    "total_kit_capacity": "GB",
    "memory_speed": "MT/s",
    "jedec_speed": "MT/s",
    "voltage": "V",
    "module_height": "mm",
}


class CatalogBuildError(Exception):
    pass


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


def build_ram_record(entry: dict, *, verified_date: str) -> dict:
    manufacturer = entry["manufacturer"]
    series = entry["series"]
    part_number = entry["part_number"]
    specs = dict(entry["specs"])
    generation = specs.get("generation", "DDR4")
    slug = canonical_ram_slug(manufacturer, series, part_number)
    record = {
        "category": "RAM",
        "manufacturer": manufacturer,
        "family": entry["family"],
        "series": series,
        "generation": generation,
        "source": {
            "name": entry.get("source_name", "Official manufacturer product specifications"),
            "url": entry["source_url"],
            "date": verified_date,
            "notes": (
                "Specifications verified against official manufacturer product "
                "pages or datasheets. memory_speed is the manufacturer tested/"
                "rated data rate in MT/s (typically XMP/EXPO profile speed). "
                "voltage is the tested profile voltage when documented; "
                "SPD/JEDEC voltage is not stored separately."
            ),
        },
        "product": {
            "name": entry["name"],
            "slug": slug,
            "description": (
                f"{entry['name']} desktop {generation} UDIMM memory "
                f"(part {part_number})."
            ),
            "status": "active",
            "is_popular": entry.get("is_popular", False),
        },
        "images": [],
        "specifications": _specs_from_dict(specs),
        "benchmarks": [],
    }
    errors, _ = validate_catalog_records([record])
    if errors:
        raise CatalogBuildError(
            f"RAM {part_number} validation failed: {'; '.join(errors)}"
        )
    return record


def build_ddr4_desktop_udimm_batch() -> list[dict]:
    return [
        build_ram_record(entry, verified_date=DDR4_VERIFIED_DATE)
        for entry in DDR4_DESKTOP_UDIMM
    ]


def build_ddr5_desktop_udimm_batch() -> list[dict]:
    return [
        build_ram_record(entry, verified_date=DDR5_VERIFIED_DATE)
        for entry in DDR5_DESKTOP_UDIMM
    ]


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
        print("No RAM catalog records found.")
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
    write_catalog(
        CATALOG_ROOT / "ddr4" / "desktop-udimm" / "desktop.json",
        build_ddr4_desktop_udimm_batch(),
    )
    write_catalog(
        CATALOG_ROOT / "ddr5" / "desktop-udimm" / "desktop.json",
        build_ddr5_desktop_udimm_batch(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="RAM catalog builder")
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
