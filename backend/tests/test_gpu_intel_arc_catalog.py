"""Intel Arc A-Series desktop catalog import and validation tests."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from app import db
from app.catalog.catalog_validation import validate_catalog_records
from app.data.gpu_slug_policy import LEGACY_GPU_SLUG_MAP
from app.models import Category, Manufacturer, Product, ProductSource, Specification
from app.services.import_service import ImportMode, import_hardware_from_path
from app.services.product_reconciliation_service import reconcile_legacy_gpu_slugs
from seed_data.gpu_spec_definitions import GPU_SPECS

BACKEND_ROOT = Path(__file__).resolve().parents[1]
CATALOG_FILE = (
    BACKEND_ROOT
    / "data"
    / "catalog"
    / "gpu"
    / "intel"
    / "arc"
    / "a-series"
    / "desktop.json"
)
RX7000_CATALOG_FILE = (
    BACKEND_ROOT
    / "data"
    / "catalog"
    / "gpu"
    / "amd"
    / "radeon"
    / "rx-7000-series"
    / "desktop.json"
)
NVIDIA_CATALOG_FILE = (
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
    "intel-arc-a770",
    "intel-arc-a750",
    "intel-arc-a580",
    "intel-arc-a380",
    "intel-arc-a310",
]


@pytest.fixture
def intel_arc_setup(app):
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


def test_intel_arc_catalog_file_validates():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    assert len(records) == 5
    errors, _ = validate_catalog_records(records)
    assert errors == []


def test_intel_arc_catalog_unique_canonical_slugs():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    slugs = [record["product"]["slug"] for record in records]
    assert slugs == EXPECTED_SLUGS
    assert len(slugs) == len(set(slugs))


def test_intel_arc_all_records_use_intel_official_sources():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        assert "intel.com" in record["source"]["url"]
        assert record["source"]["name"] == "Intel official product specifications"
        assert record["generation"] == "Arc A-Series"
        assert record["architecture"] == "Xe HPG"
        assert record["manufacturer"] == "Intel"
        assert record["family"] == "Arc"
        assert record["series"] == "Arc A-Series"


def test_intel_arc_desktop_market_segment():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        segment = next(
            s["value"] for s in record["specifications"] if s["key"] == "market_segment"
        )
        assert segment == "desktop"


def test_intel_arc_important_official_specs():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    by_slug = {r["product"]["slug"]: r for r in records}

    def spec(slug, key):
        return next(
            s["value"] for s in by_slug[slug]["specifications"] if s["key"] == key
        )

    assert spec("intel-arc-a770", "xe_cores") == "32"
    assert spec("intel-arc-a770", "tbp") == "225"
    assert spec("intel-arc-a750", "xe_cores") == "28"
    assert spec("intel-arc-a750", "vram_capacity") == "8"
    assert spec("intel-arc-a580", "xe_cores") == "24"
    assert spec("intel-arc-a380", "vram_capacity") == "6"
    assert spec("intel-arc-a310", "vram_capacity") == "4"
    assert spec("intel-arc-a310", "xe_cores") == "6"


def test_intel_arc_a770_memory_variant_handling():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    by_slug = {r["product"]["slug"]: r for r in records}
    a770_specs = {s["key"] for s in by_slug["intel-arc-a770"]["specifications"]}
    assert "vram_capacity" not in a770_specs
    assert "memory_speed" not in a770_specs
    assert "memory_bandwidth" not in a770_specs


def test_intel_arc_no_mobile_pro_or_aib_products():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        name = record["product"]["name"].lower()
        slug = record["product"]["slug"]
        assert "laptop" not in name
        assert "mobile" not in name
        assert not slug.endswith("m")
        assert "arc pro" not in name
        assert "flex" not in name
        assert "max" not in name or "a310" in slug
        assert slug.startswith("intel-arc-a")


def test_intel_arc_legacy_slug_map():
    assert LEGACY_GPU_SLUG_MAP["arc-a770"] == "intel-arc-a770"


def test_intel_arc_import_and_idempotency(intel_arc_setup):
    first = import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    assert first.errors == 0
    assert first.created == 5
    assert first.updated == 0

    second = import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    assert second.errors == 0
    assert second.created == 0
    assert second.updated == 5


def test_intel_arc_legacy_a770_reconciliation(intel_arc_setup):
    gpu = intel_arc_setup
    intel = Manufacturer.query.filter_by(slug="intel").first()
    if not intel:
        intel = Manufacturer(name="Intel", slug="intel")
        db.session.add(intel)
        db.session.flush()

    demo = Product(
        name="Intel Arc A770",
        slug="arc-a770",
        category_id=gpu.id,
        manufacturer_id=intel.id,
        status="active",
    )
    db.session.add(demo)
    db.session.commit()

    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    result = reconcile_legacy_gpu_slugs()
    assert result.merged == 1
    assert result.errors == []
    assert Product.query.filter_by(slug="arc-a770").first() is None
    canonical = Product.query.filter_by(slug="intel-arc-a770").one()
    assert canonical.name == "Intel Arc A770"


def test_intel_arc_imported_products_have_provenance(intel_arc_setup):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    for slug in EXPECTED_SLUGS:
        product = Product.query.filter_by(slug=slug).first()
        assert product is not None
        assert product.manufacturer.name == "Intel"
        assert product.family.name == "Arc"
        assert product.generation.name == "Arc A-Series"
        sources = ProductSource.query.filter_by(product_id=product.id).all()
        assert sources
        assert any("intel.com" in (s.source_url or "") for s in sources)
        segment = Specification.query.filter_by(
            product_id=product.id, key="market_segment"
        ).first()
        assert segment is not None
        assert segment.value == "desktop"


def test_intel_arc_generation_filtering(intel_arc_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    response = client.get("/api/products?category=gpu&generation=Arc+A-Series")
    assert response.status_code == 200
    slugs = {item["slug"] for item in response.get_json()["data"]}
    for slug in EXPECTED_SLUGS:
        assert slug in slugs


def test_intel_arc_intel_and_family_filters(intel_arc_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    intel = client.get("/api/products?category=gpu&manufacturer=Intel")
    assert intel.status_code == 200
    assert intel.get_json()["pagination"]["total"] == 5

    family = client.get("/api/products?category=gpu&family=Arc")
    assert family.status_code == 200
    assert family.get_json()["pagination"]["total"] == 5


def test_intel_arc_search_and_compare(intel_arc_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    for query in (
        "Arc A770",
        "Arc A750",
        "Arc A580",
        "Arc A380",
        "Arc A310",
    ):
        response = client.get("/api/search", query_string={"q": query})
        assert response.status_code == 200
        names = [item["name"] for item in response.get_json()["items"]]
        assert any(query in name for name in names)

    detail = client.get("/api/products/by-slug/intel-arc-a770")
    assert detail.status_code == 200
    body = detail.get_json()
    assert body["name"] == "Intel Arc A770"
    assert body.get("sources")
    assert body.get("related_products") is not None

    compare = client.get(
        "/api/compare?products=intel-arc-a770,intel-arc-a750"
    )
    assert compare.status_code == 200
    assert len(compare.get_json()["products"]) == 2


def test_rx7000_catalog_still_valid_after_intel_arc_builder():
    records = json.loads(RX7000_CATALOG_FILE.read_text(encoding="utf-8"))
    errors, _ = validate_catalog_records(records)
    assert not errors
    assert len(records) == 7


def test_nvidia_catalog_still_valid_after_intel_arc_builder():
    records = json.loads(NVIDIA_CATALOG_FILE.read_text(encoding="utf-8"))
    errors, _ = validate_catalog_records(records)
    assert not errors
    assert len(records) == 9


def test_builder_produces_valid_intel_arc_output():
    script = BACKEND_ROOT / "scripts" / "build_gpu_catalog.py"
    subprocess.run([sys.executable, str(script)], cwd=BACKEND_ROOT, check=True)
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    errors, _ = validate_catalog_records(records)
    assert not errors
    assert len(records) == 5
