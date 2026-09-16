"""Tests for catalog builder validation and determinism."""

import json
import subprocess
import sys
from pathlib import Path

from app.catalog.catalog_validation import is_valid_source_url, validate_catalog_records

BACKEND_ROOT = Path(__file__).resolve().parents[1]
CATALOG_ROOT = BACKEND_ROOT / "data" / "catalog" / "cpu"


def test_invalid_source_url_rejected():
    assert not is_valid_source_url("https://example.com/cpu")
    assert not is_valid_source_url("TODO")
    assert not is_valid_source_url("")
    assert is_valid_source_url(
        "https://www.intel.com/content/www/us/en/products/sku/236773/specifications.html"
    )


def test_intel_batches_have_unique_slugs():
    files = [
        CATALOG_ROOT / "intel" / "core" / "14th-gen" / "desktop.json",
        CATALOG_ROOT / "intel" / "core" / "13th-gen" / "desktop.json",
        CATALOG_ROOT / "intel" / "core" / "12th-gen" / "desktop.json",
        CATALOG_ROOT / "intel" / "core" / "11th-gen" / "desktop.json",
        CATALOG_ROOT / "intel" / "core" / "10th-gen" / "desktop.json",
        CATALOG_ROOT / "intel" / "core" / "9th-gen" / "desktop.json",
        CATALOG_ROOT / "intel" / "core" / "8th-gen" / "desktop.json",
        CATALOG_ROOT / "intel" / "core" / "7th-gen" / "desktop.json",
        CATALOG_ROOT / "intel" / "core" / "6th-gen" / "desktop.json",
        CATALOG_ROOT / "intel" / "core" / "5th-gen" / "desktop.json",
        CATALOG_ROOT / "intel" / "core" / "4th-gen" / "desktop.json",
    ]
    all_slugs = []
    for path in files:
        if not path.exists():
            continue
        records = json.loads(path.read_text(encoding="utf-8"))
        errors, _ = validate_catalog_records(records)
        assert not errors, f"{path}: {errors}"
        all_slugs.extend(record["product"]["slug"] for record in records)
    assert len(all_slugs) == len(set(all_slugs))


def test_builder_produces_deterministic_intel_output():
    script = BACKEND_ROOT / "scripts" / "build_cpu_catalog.py"
    subprocess.run([sys.executable, str(script)], cwd=BACKEND_ROOT, check=True)
    path = CATALOG_ROOT / "intel" / "core" / "13th-gen" / "desktop.json"
    first = path.read_text(encoding="utf-8")
    subprocess.run([sys.executable, str(script)], cwd=BACKEND_ROOT, check=True)
    second = path.read_text(encoding="utf-8")
    assert first == second


def test_validate_command_passes():
    script = BACKEND_ROOT / "scripts" / "build_cpu_catalog.py"
    result = subprocess.run(
        [sys.executable, str(script), "--validate"],
        cwd=BACKEND_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
