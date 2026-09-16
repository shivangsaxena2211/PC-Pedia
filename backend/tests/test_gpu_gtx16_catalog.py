"""NVIDIA GeForce GTX 16 Series desktop catalog import and validation tests."""

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
    / "gtx-16-series"
    / "desktop.json"
)
RTX20_CATALOG_FILE = (
    BACKEND_ROOT
    / "data"
    / "catalog"
    / "gpu"
    / "nvidia"
    / "geforce"
    / "rtx-20-series"
    / "desktop.json"
)
RTX30_CATALOG_FILE = (
    BACKEND_ROOT
    / "data"
    / "catalog"
    / "gpu"
    / "nvidia"
    / "geforce"
    / "rtx-30-series"
    / "desktop.json"
)
RTX40_CATALOG_FILE = (
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
    "nvidia-geforce-gtx-1660-ti",
    "nvidia-geforce-gtx-1660-super",
    "nvidia-geforce-gtx-1660",
    "nvidia-geforce-gtx-1650-super",
    "nvidia-geforce-gtx-1650",
    "nvidia-geforce-gtx-1650-gddr6",
    "nvidia-geforce-gtx-1630",
]


@pytest.fixture
def gtx16_setup(app):
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


def test_gtx16_catalog_file_validates():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    assert len(records) == 7
    errors, _ = validate_catalog_records(records)
    assert errors == []


def test_gtx16_catalog_unique_canonical_slugs():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    slugs = [record["product"]["slug"] for record in records]
    assert slugs == EXPECTED_SLUGS
    assert len(slugs) == len(set(slugs))


def test_gtx16_all_records_use_nvidia_official_sources():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        assert "nvidia.com" in record["source"]["url"]
        assert record["source"]["name"] == "NVIDIA official product specifications"
        assert record["generation"] == "GTX 16 Series"
        assert record["architecture"] == "Turing"
        assert record["series"] == "GeForce GTX"


def test_gtx16_desktop_market_segment():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        segment = next(
            s["value"] for s in record["specifications"] if s["key"] == "market_segment"
        )
        assert segment == "desktop"


def test_gtx16_cuda_cores_present():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        keys = {s["key"] for s in record["specifications"]}
        assert "cuda_cores" in keys


def test_gtx16_no_mobile_or_aib_products():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        name = record["product"]["name"].lower()
        slug = record["product"]["slug"]
        assert "laptop" not in name
        assert "mobile" not in name
        assert "max-q" not in name
        assert slug.startswith("nvidia-geforce-gtx-")


def test_gtx16_1650_memory_variants_split():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    by_slug = {r["product"]["slug"]: r for r in records}
    gddr5 = next(
        s["value"]
        for s in by_slug["nvidia-geforce-gtx-1650"]["specifications"]
        if s["key"] == "vram_type"
    )
    gddr6 = next(
        s["value"]
        for s in by_slug["nvidia-geforce-gtx-1650-gddr6"]["specifications"]
        if s["key"] == "vram_type"
    )
    assert gddr5 == "GDDR5"
    assert gddr6 == "GDDR6"


def test_gtx16_import_and_idempotency(gtx16_setup):
    catalog_path = str(CATALOG_FILE)
    first = import_hardware_from_path(catalog_path, mode=ImportMode.UPSERT)
    assert first.errors == 0
    assert first.created == 7
    assert first.updated == 0

    second = import_hardware_from_path(catalog_path, mode=ImportMode.UPSERT)
    assert second.errors == 0
    assert second.created == 0
    assert second.updated == 7


def test_gtx16_imported_products_have_provenance(gtx16_setup):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    for slug in EXPECTED_SLUGS:
        product = Product.query.filter_by(slug=slug).first()
        assert product is not None
        assert product.manufacturer.name == "NVIDIA"
        assert product.generation.name == "GTX 16 Series"
        sources = ProductSource.query.filter_by(product_id=product.id).all()
        assert sources
        assert any("nvidia.com" in (s.source_url or "") for s in sources)
        segment = Specification.query.filter_by(
            product_id=product.id, key="market_segment"
        ).first()
        assert segment is not None
        assert segment.value == "desktop"


def test_gtx16_generation_filtering(gtx16_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    response = client.get("/api/products?category=gpu&generation=GTX+16+Series")
    assert response.status_code == 200
    slugs = {item["slug"] for item in response.get_json()["data"]}
    for slug in EXPECTED_SLUGS:
        assert slug in slugs


def test_gtx16_search_and_compare(gtx16_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    for query in ("GTX 1660", "GTX 1650", "GTX 1630"):
        response = client.get("/api/search", query_string={"q": query})
        assert response.status_code == 200
        names = [item["name"] for item in response.get_json()["items"]]
        assert any(query in name for name in names)

    detail = client.get("/api/products/by-slug/nvidia-geforce-gtx-1660-ti")
    assert detail.status_code == 200
    body = detail.get_json()
    assert body["name"] == "NVIDIA GeForce GTX 1660 Ti"
    assert body.get("sources")
    assert body.get("related_products") is not None

    compare = client.get(
        "/api/compare?products=nvidia-geforce-gtx-1660-ti,nvidia-geforce-gtx-1660-super"
    )
    assert compare.status_code == 200
    assert len(compare.get_json()["products"]) == 2


def test_rtx_catalogs_still_valid_after_gtx16_builder():
    for path, count in (
        (RTX20_CATALOG_FILE, 8),
        (RTX30_CATALOG_FILE, 10),
        (RTX40_CATALOG_FILE, 9),
    ):
        records = json.loads(path.read_text(encoding="utf-8"))
        errors, _ = validate_catalog_records(records)
        assert not errors
        assert len(records) == count


def test_builder_produces_valid_gtx16_output():
    script = BACKEND_ROOT / "scripts" / "build_gpu_catalog.py"
    subprocess.run([sys.executable, str(script)], cwd=BACKEND_ROOT, check=True)
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    errors, _ = validate_catalog_records(records)
    assert not errors
    assert len(records) == 7
