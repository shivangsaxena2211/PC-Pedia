"""GPU catalog foundation tests: taxonomy, specs, slugs, validation, provenance."""

import json
from pathlib import Path

import pytest

from app import db
from app.catalog.catalog_validation import (
    CPU_ALLOWED_SPEC_KEYS,
    GPU_ALLOWED_SPEC_KEYS,
    get_allowed_spec_keys,
    validate_catalog_record,
    validate_catalog_records,
)
from app.catalog.gpu_slug import (
    gpu_slug_prefix,
    is_official_gpu_source_url,
    validate_gpu_family,
    validate_gpu_manufacturer,
    validate_gpu_market_segment,
    validate_gpu_slug,
)
from app.models import Category, SpecificationDefinition
from seed_data.gpu_spec_definitions import GPU_SPECS

CATALOG_ROOT = Path(__file__).resolve().parents[1] / "data" / "catalog" / "gpu"


@pytest.fixture
def gpu_setup(app):
    with app.app_context():
        gpu = Category.query.filter_by(slug="gpu").first()
        if not gpu:
            gpu = Category(name="GPU", slug="gpu", icon="gpu", display_order=2)
            db.session.add(gpu)
            db.session.flush()

        for group, key, display, dtype, unit, filt, comp, req, order in GPU_SPECS:
            existing = SpecificationDefinition.query.filter_by(
                category_id=gpu.id, key=key
            ).first()
            if not existing:
                db.session.add(SpecificationDefinition(
                    category_id=gpu.id,
                    group_name=group,
                    key=key,
                    display_name=display,
                    data_type=dtype,
                    unit=unit,
                    filterable=filt,
                    comparable=comp,
                    required=req,
                    display_order=order,
                ))
        db.session.commit()
        yield gpu


def _minimal_gpu_record(**overrides) -> dict:
    record = {
        "category": "GPU",
        "manufacturer": "NVIDIA",
        "family": "GeForce",
        "series": "GeForce RTX",
        "generation": "RTX 40 Series",
        "source": {
            "name": "NVIDIA official product specifications",
            "url": "https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4090/",
            "date": "2026-09-16",
        },
        "product": {
            "name": "NVIDIA GeForce RTX 4090",
            "slug": "nvidia-geforce-rtx-4090",
        },
        "specifications": [
            {"group": "Identity", "key": "market_segment", "value": "desktop"},
            {"group": "Compute", "key": "cuda_cores", "value": "16384"},
        ],
        "images": [],
    }
    record.update(overrides)
    return record


def test_gpu_specification_definitions_exist(gpu_setup):
    count = SpecificationDefinition.query.filter_by(category_id=gpu_setup.id).count()
    assert count >= len(GPU_SPECS)


def test_gpu_allowed_spec_keys_include_vendor_specific_compute():
    assert "cuda_cores" in GPU_ALLOWED_SPEC_KEYS
    assert "stream_processors" in GPU_ALLOWED_SPEC_KEYS
    assert "xe_cores" in GPU_ALLOWED_SPEC_KEYS
    assert "rt_cores" in GPU_ALLOWED_SPEC_KEYS
    assert "ray_accelerators" in GPU_ALLOWED_SPEC_KEYS
    assert "xmx_engines" in GPU_ALLOWED_SPEC_KEYS


def test_cpu_allowed_spec_keys_unchanged():
    assert "socket" in CPU_ALLOWED_SPEC_KEYS
    assert "cores" in CPU_ALLOWED_SPEC_KEYS
    assert "cuda_cores" not in CPU_ALLOWED_SPEC_KEYS
    assert get_allowed_spec_keys("cpu") == CPU_ALLOWED_SPEC_KEYS
    assert get_allowed_spec_keys("gpu") == GPU_ALLOWED_SPEC_KEYS


def test_gpu_taxonomy_manufacturers_and_families():
    assert validate_gpu_manufacturer("NVIDIA") is None
    assert validate_gpu_manufacturer("AMD") is None
    assert validate_gpu_manufacturer("Intel") is None
    assert validate_gpu_manufacturer("Apple") is not None

    assert validate_gpu_family("NVIDIA", "GeForce") is None
    assert validate_gpu_family("AMD", "Radeon RX") is None
    assert validate_gpu_family("Intel", "Arc") is None
    assert validate_gpu_family("NVIDIA", "Radeon RX") is not None


def test_canonical_gpu_slug_policy():
    assert gpu_slug_prefix("NVIDIA", "GeForce") == "nvidia-geforce"
    assert validate_gpu_slug("nvidia-geforce-rtx-4090", "NVIDIA", "GeForce") is None
    assert validate_gpu_slug("amd-radeon-rx-7900-xtx", "AMD", "Radeon RX") is None
    assert validate_gpu_slug("intel-arc-a770", "Intel", "Arc") is None
    assert validate_gpu_slug("rtx-4090", "NVIDIA", "GeForce") is not None
    assert validate_gpu_slug("NVIDIA-GEFORCE-RTX-4090", "NVIDIA", "GeForce") is not None


def test_gpu_market_segment_classification():
    assert validate_gpu_market_segment("desktop") is None
    assert validate_gpu_market_segment("mobile") is None
    assert validate_gpu_market_segment("workstation") is None
    assert validate_gpu_market_segment("datacenter") is None
    assert validate_gpu_market_segment("laptop") is not None
    assert validate_gpu_market_segment(None) is not None


def test_manufacturer_specific_specs_coexist_in_one_batch():
    nvidia = _minimal_gpu_record()
    amd = _minimal_gpu_record(
        manufacturer="AMD",
        family="Radeon RX",
        product={"name": "AMD Radeon RX 7900 XTX", "slug": "amd-radeon-rx-7900-xtx"},
        source={
            "name": "AMD official product specifications",
            "url": "https://www.amd.com/en/products/graphics/amd-radeon-rx-7900xtx",
        },
        specifications=[
            {"group": "Identity", "key": "market_segment", "value": "desktop"},
            {"group": "Compute", "key": "stream_processors", "value": "6144"},
        ],
    )
    intel = _minimal_gpu_record(
        manufacturer="Intel",
        family="Arc",
        product={"name": "Intel Arc A770", "slug": "intel-arc-a770"},
        source={
            "name": "Intel official product specifications",
            "url": "https://www.intel.com/content/www/us/en/products/sku/230957/intel-arc-a770-graphics/overview.html",
        },
        specifications=[
            {"group": "Identity", "key": "market_segment", "value": "desktop"},
            {"group": "Compute", "key": "xe_cores", "value": "32"},
        ],
    )
    errors, _ = validate_catalog_records([nvidia, amd, intel])
    assert errors == []


def test_gpu_provenance_requires_official_source():
    record = _minimal_gpu_record(
        source={
            "name": "Third-party review",
            "url": "https://www.techpowerup.com/review/example",
        }
    )
    errors = validate_catalog_record(record)
    assert any("official manufacturer source" in e for e in errors)


def test_official_gpu_source_domains():
    assert is_official_gpu_source_url(
        "NVIDIA", "https://www.nvidia.com/en-us/geforce/graphics-cards/"
    )
    assert is_official_gpu_source_url("AMD", "https://www.amd.com/en/products/graphics/")
    assert is_official_gpu_source_url(
        "Intel", "https://www.intel.com/content/www/us/en/products/sku/230957/"
    )
    assert not is_official_gpu_source_url("NVIDIA", "https://www.techpowerup.com/")


def test_gpu_catalog_validation_rejects_invalid_specs():
    record = _minimal_gpu_record(
        specifications=[
            {"group": "Identity", "key": "market_segment", "value": "desktop"},
            {"group": "Compute", "key": "cuda_cores", "value": "not-a-number"},
        ]
    )
    errors = validate_catalog_record(record)
    assert any("cuda_cores" in e and "integer" in e for e in errors)


def test_gpu_catalog_validation_rejects_duplicate_slugs():
    a = _minimal_gpu_record()
    b = _minimal_gpu_record()
    errors, _ = validate_catalog_records([a, b])
    assert any("Duplicate slug" in e for e in errors)


def test_gpu_catalog_directory_structure_exists():
    assert (CATALOG_ROOT / "README.md").is_file()
    assert (CATALOG_ROOT / "schema.json").is_file()
    assert (CATALOG_ROOT / "nvidia" / "geforce").is_dir()
    assert (CATALOG_ROOT / "amd" / "radeon").is_dir()
    assert (CATALOG_ROOT / "intel" / "arc").is_dir()


def test_gpu_schema_documents_record_shape():
    schema = json.loads((CATALOG_ROOT / "schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["category"]["const"] == "GPU"
    assert "nvidia" in schema["properties"]["product"]["properties"]["slug"]["pattern"]


def test_build_gpu_catalog_validate_script():
    import subprocess
    import sys

    script = Path(__file__).resolve().parents[1] / "scripts" / "build_gpu_catalog.py"
    result = subprocess.run(
        [sys.executable, str(script), "--validate"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
