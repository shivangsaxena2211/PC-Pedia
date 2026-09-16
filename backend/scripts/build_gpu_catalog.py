"""
GPU catalog builder and validation entry point.

Phase 1: directory infrastructure and validation only. No external fetch or
product generation. Future phases will add verified source modules and JSON output.

Usage:
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

CATALOG_ROOT = BACKEND_ROOT / "data" / "catalog" / "gpu"


def collect_catalog_records(root: Path = CATALOG_ROOT) -> list[dict]:
    """Load all non-empty JSON catalog batches under the GPU tree."""
    records: list[dict] = []
    for path in sorted(root.glob("**/*.json")):
        if path.name == "schema.json":
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
    """Validate each JSON batch file. Returns non-zero exit code if any fail."""
    errors_found = 0
    for path in sorted(root.glob("**/*.json")):
        if path.name == "schema.json":
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
    """Validate all records as if preparing for import."""
    records = collect_catalog_records(root)
    if not records:
        print("No GPU catalog records found (expected in Phase 1).")
        return 0
    errors, warnings = validate_catalog_records(records)
    for warning in warnings:
        print(f"warning: {warning}")
    if errors:
        for err in errors:
            print(f"error: {err}")
        return 1
    print(f"Dry run OK: {len(records)} record(s) ready for import.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="GPU catalog validation (Phase 1)")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate all JSON files under data/catalog/gpu/",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate collected records as a single import batch",
    )
    args = parser.parse_args()

    if args.validate:
        return validate_catalog_tree()
    if args.dry_run:
        return dry_run_import()

    parser.print_help()
    print("\nPhase 1: use --validate or --dry-run. No build output yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
