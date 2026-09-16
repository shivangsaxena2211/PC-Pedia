"""NVIDIA GeForce RTX 40 Series desktop catalog import and validation tests."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from app import db
from app.catalog.catalog_validation import validate_catalog_records
from app.models import Category, Product, ProductSource, Specification
from app.services.import_service import ImportMode, import_hardware_from_path
from seed_data.gpu_spec_definitions import GPU_SPECS

BACKEND_ROOT = Path(__file__).resolve().parents[1]
CATALOG_FILE = (
    BACKEND_ROOT
    / "data"
    / "catalog"
    / "gpu"
    / "nvidia"
    / "geforce"
    / "rtx-40-series"
    / "desktop.json"
)

EXPECTED_SLUGS = [
    "nvidia-geforce-rtx-4090",
    "nvidia-geforce-rtx-4080-super",
    "nvidia-geforce-rtx-4080",
    "nvidia-geforce-rtx-4070-ti-super",
    "nvidia-geforce-rtx-4070-ti",
    "nvidia-geforce-rtx-4070-super",
    "nvidia-geforce-rtx-4070",
    "nvidia-geforce-rtx-4060-ti",
    "nvidia-geforce-rtx-4060",
]


@pytest.fixture
def rtx40_setup(app):
    with app.app_context():
        gpu = Category.query.filter_by(slug="gpu").first()
        if not gpu:
            gpu = Category(name="GPU", slug="gpu", icon="gpu", display_order=2)
            db.session.add(gpu)
            db.session.flush()

        from app.models import SpecificationDefinition

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


def test_rtx40_catalog_file_validates():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    assert len(records) == 9
    errors, _ = validate_catalog_records(records)
    assert errors == []


def test_rtx40_catalog_unique_canonical_slugs():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    slugs = [record["product"]["slug"] for record in records]
    assert slugs == EXPECTED_SLUGS
    assert len(slugs) == len(set(slugs))


def test_rtx40_all_records_use_nvidia_official_sources():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        url = record["source"]["url"]
        assert "nvidia.com" in url
        assert record["source"]["name"] == "NVIDIA official product specifications"


def test_rtx40_desktop_market_segment():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        segment = next(
            s["value"]
            for s in record["specifications"]
            if s["key"] == "market_segment"
        )
        assert segment == "desktop"


def test_rtx40_cuda_cores_present_for_all_models():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        cuda = next(
            (s for s in record["specifications"] if s["key"] == "cuda_cores"),
            None,
        )
        assert cuda is not None
        assert int(cuda["value"]) > 0


def test_rtx40_no_integer_rt_or_tensor_core_counts():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        keys = {s["key"] for s in record["specifications"]}
        assert "rt_cores" not in keys
        assert "tensor_cores" not in keys


def test_rtx40_import_and_idempotency(rtx40_setup):
    catalog_path = str(CATALOG_FILE)
    first = import_hardware_from_path(
        catalog_path, mode=ImportMode.UPSERT, dry_run=False
    )
    assert first.errors == 0
    assert first.created == 9

    second = import_hardware_from_path(
        catalog_path, mode=ImportMode.UPSERT, dry_run=False
    )
    assert second.errors == 0
    assert second.created == 0


def test_rtx40_imported_products_have_provenance(rtx40_setup):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    for slug in EXPECTED_SLUGS:
        product = Product.query.filter_by(slug=slug).first()
        assert product is not None
        assert product.manufacturer.name == "NVIDIA"
        assert product.generation.name == "RTX 40 Series"
        sources = ProductSource.query.filter_by(product_id=product.id).all()
        assert sources
        assert any("nvidia.com" in (s.source.url or "") for s in sources)
        segment = Specification.query.filter_by(
            product_id=product.id, key="market_segment"
        ).first()
        assert segment is not None
        assert segment.value == "desktop"


def test_rtx40_generation_filtering(rtx40_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    response = client.get("/api/products?category=gpu&generation=RTX+40+Series")
    assert response.status_code == 200
    data = response.get_json()
    slugs = {item["slug"] for item in data["data"]}
    for slug in EXPECTED_SLUGS:
        assert slug in slugs


def test_builder_produces_valid_rtx40_output():
    script = BACKEND_ROOT / "scripts" / "build_gpu_catalog.py"
    subprocess.run([sys.executable, str(script)], cwd=BACKEND_ROOT, check=True)
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    errors, _ = validate_catalog_records(records)
    assert not errors
