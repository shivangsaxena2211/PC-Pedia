"""NVIDIA GeForce GTX 10 Series desktop catalog import and validation tests."""

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
    / "gtx-10-series"
    / "desktop.json"
)
GTX16_CATALOG_FILE = (
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
    "nvidia-geforce-gtx-1080-ti",
    "nvidia-geforce-gtx-1080",
    "nvidia-geforce-gtx-1070-ti",
    "nvidia-geforce-gtx-1070",
    "nvidia-geforce-gtx-1060-6gb",
    "nvidia-geforce-gtx-1060-3gb",
    "nvidia-geforce-gtx-1050-ti",
    "nvidia-geforce-gtx-1050-2gb",
    "nvidia-geforce-gtx-1050-3gb",
]


@pytest.fixture
def gtx10_setup(app):
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


def test_gtx10_catalog_file_validates():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    assert len(records) == 9
    errors, _ = validate_catalog_records(records)
    assert errors == []


def test_gtx10_catalog_unique_canonical_slugs():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    slugs = [record["product"]["slug"] for record in records]
    assert slugs == EXPECTED_SLUGS
    assert len(slugs) == len(set(slugs))


def test_gtx10_all_records_use_nvidia_official_sources():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        assert "nvidia.com" in record["source"]["url"]
        assert record["source"]["name"] == "NVIDIA official product specifications"
        assert record["generation"] == "GTX 10 Series"
        assert record["architecture"] == "Pascal"
        assert record["series"] == "GeForce GTX"
        assert record["manufacturer"] == "NVIDIA"


def test_gtx10_desktop_market_segment():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        segment = next(
            s["value"] for s in record["specifications"] if s["key"] == "market_segment"
        )
        assert segment == "desktop"


def test_gtx10_important_official_specs():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    by_slug = {r["product"]["slug"]: r for r in records}

    def spec(slug, key):
        return next(
            s["value"] for s in by_slug[slug]["specifications"] if s["key"] == key
        )

    assert spec("nvidia-geforce-gtx-1080-ti", "cuda_cores") == "3584"
    assert spec("nvidia-geforce-gtx-1080-ti", "vram_capacity") == "11"
    assert spec("nvidia-geforce-gtx-1080-ti", "vram_type") == "GDDR5X"
    assert spec("nvidia-geforce-gtx-1080-ti", "tbp") == "250"

    assert spec("nvidia-geforce-gtx-1080", "cuda_cores") == "2560"
    assert spec("nvidia-geforce-gtx-1080", "vram_capacity") == "8"

    assert spec("nvidia-geforce-gtx-1070-ti", "cuda_cores") == "2432"
    assert spec("nvidia-geforce-gtx-1070", "cuda_cores") == "1920"

    assert spec("nvidia-geforce-gtx-1060-6gb", "cuda_cores") == "1280"
    assert spec("nvidia-geforce-gtx-1060-6gb", "vram_capacity") == "6"
    assert spec("nvidia-geforce-gtx-1060-3gb", "cuda_cores") == "1152"
    assert spec("nvidia-geforce-gtx-1060-3gb", "vram_capacity") == "3"

    assert spec("nvidia-geforce-gtx-1050-ti", "cuda_cores") == "768"
    assert spec("nvidia-geforce-gtx-1050-ti", "vram_capacity") == "4"
    assert spec("nvidia-geforce-gtx-1050-2gb", "cuda_cores") == "640"
    assert spec("nvidia-geforce-gtx-1050-3gb", "memory_bus_width") == "96"


def test_gtx10_variant_handling():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    by_slug = {r["product"]["slug"]: r for r in records}
    assert "nvidia-geforce-gtx-1060-6gb" in by_slug
    assert "nvidia-geforce-gtx-1060-3gb" in by_slug
    assert "nvidia-geforce-gtx-1050-2gb" in by_slug
    assert "nvidia-geforce-gtx-1050-3gb" in by_slug
    assert "nvidia-geforce-gtx-1050-ti" in by_slug
    # No Founders Edition / AIB / OEM 5GB products
    names = " ".join(r["product"]["name"].lower() for r in records)
    assert "founders" not in names
    assert "5gb" not in names


def test_gtx10_no_mobile_or_aib_products():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        name = record["product"]["name"].lower()
        slug = record["product"]["slug"]
        assert "laptop" not in name
        assert "mobile" not in name
        assert "max-q" not in name
        assert "titan" not in name
        assert slug.startswith("nvidia-geforce-gtx-")


def test_gtx10_import_and_idempotency(gtx10_setup):
    catalog_path = str(CATALOG_FILE)
    first = import_hardware_from_path(catalog_path, mode=ImportMode.UPSERT)
    assert first.errors == 0
    assert first.created == 9
    assert first.updated == 0

    second = import_hardware_from_path(catalog_path, mode=ImportMode.UPSERT)
    assert second.errors == 0
    assert second.created == 0
    assert second.updated == 9


def test_gtx10_imported_products_have_provenance(gtx10_setup):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    for slug in EXPECTED_SLUGS:
        product = Product.query.filter_by(slug=slug).first()
        assert product is not None
        assert product.manufacturer.name == "NVIDIA"
        assert product.generation.name == "GTX 10 Series"
        sources = ProductSource.query.filter_by(product_id=product.id).all()
        assert sources
        assert any("nvidia.com" in (s.source_url or "") for s in sources)
        segment = Specification.query.filter_by(
            product_id=product.id, key="market_segment"
        ).first()
        assert segment is not None
        assert segment.value == "desktop"


def test_gtx10_generation_filtering(gtx10_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    response = client.get("/api/products?category=gpu&generation=GTX+10+Series")
    assert response.status_code == 200
    slugs = {item["slug"] for item in response.get_json()["data"]}
    for slug in EXPECTED_SLUGS:
        assert slug in slugs


def test_gtx10_search_and_compare(gtx10_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    for query in (
        "GTX 1080 Ti",
        "GTX 1080",
        "GTX 1070 Ti",
        "GTX 1070",
        "GTX 1060",
        "GTX 1050 Ti",
        "GTX 1050",
    ):
        response = client.get("/api/search", query_string={"q": query})
        assert response.status_code == 200
        names = [item["name"] for item in response.get_json()["items"]]
        assert any(query.split()[0] in name and query.split()[-1] in name for name in names) or any(
            query in name for name in names
        )

    detail = client.get("/api/products/by-slug/nvidia-geforce-gtx-1080-ti")
    assert detail.status_code == 200
    body = detail.get_json()
    assert body["name"] == "NVIDIA GeForce GTX 1080 Ti"
    assert body.get("sources")
    assert body.get("related_products") is not None

    compare = client.get(
        "/api/compare?products=nvidia-geforce-gtx-1080-ti,nvidia-geforce-gtx-1080"
    )
    assert compare.status_code == 200
    assert len(compare.get_json()["products"]) == 2


def test_prior_gpu_catalogs_still_valid_after_gtx10():
    for path, count in (
        (GTX16_CATALOG_FILE, 7),
        (RTX20_CATALOG_FILE, 8),
        (RTX30_CATALOG_FILE, 10),
        (RTX40_CATALOG_FILE, 9),
    ):
        records = json.loads(path.read_text(encoding="utf-8"))
        errors, _ = validate_catalog_records(records)
        assert not errors
        assert len(records) == count


def test_builder_produces_valid_gtx10_output():
    script = BACKEND_ROOT / "scripts" / "build_gpu_catalog.py"
    subprocess.run([sys.executable, str(script)], cwd=BACKEND_ROOT, check=True)
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    errors, _ = validate_catalog_records(records)
    assert not errors
    assert len(records) == 9
