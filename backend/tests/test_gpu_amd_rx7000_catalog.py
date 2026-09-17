"""AMD Radeon RX 7000 Series desktop catalog import and validation tests."""

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
    "amd-radeon-rx-7900-xtx",
    "amd-radeon-rx-7900-xt",
    "amd-radeon-rx-7900-gre",
    "amd-radeon-rx-7800-xt",
    "amd-radeon-rx-7700-xt",
    "amd-radeon-rx-7600-xt",
    "amd-radeon-rx-7600",
]


@pytest.fixture
def rx7000_setup(app):
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


def test_rx7000_catalog_file_validates():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    assert len(records) == 7
    errors, _ = validate_catalog_records(records)
    assert errors == []


def test_rx7000_catalog_unique_canonical_slugs():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    slugs = [record["product"]["slug"] for record in records]
    assert slugs == EXPECTED_SLUGS
    assert len(slugs) == len(set(slugs))


def test_rx7000_all_records_use_amd_official_sources():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        assert "amd.com" in record["source"]["url"]
        assert record["source"]["name"] == "AMD official product specifications"
        assert record["generation"] == "RX 7000 Series"
        assert record["architecture"] == "RDNA 3"
        assert record["manufacturer"] == "AMD"
        assert record["family"] == "Radeon RX"
        assert record["series"] == "Radeon RX"


def test_rx7000_desktop_market_segment():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        segment = next(
            s["value"] for s in record["specifications"] if s["key"] == "market_segment"
        )
        assert segment == "desktop"


def test_rx7000_important_official_specs():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    by_slug = {r["product"]["slug"]: r for r in records}

    def spec(slug, key):
        return next(
            s["value"] for s in by_slug[slug]["specifications"] if s["key"] == key
        )

    assert spec("amd-radeon-rx-7900-xtx", "compute_units") == "96"
    assert spec("amd-radeon-rx-7900-xtx", "stream_processors") == "6144"
    assert spec("amd-radeon-rx-7900-xtx", "vram_capacity") == "24"
    assert spec("amd-radeon-rx-7900-xtx", "tbp") == "355"

    assert spec("amd-radeon-rx-7900-gre", "compute_units") == "80"
    assert spec("amd-radeon-rx-7900-gre", "vram_capacity") == "16"

    assert spec("amd-radeon-rx-7600-xt", "vram_capacity") == "16"
    assert spec("amd-radeon-rx-7600", "vram_capacity") == "8"


def test_rx7600_xt_memory_variant_not_merged_with_rx7600():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    by_slug = {r["product"]["slug"]: r for r in records}
    xt_vram = next(
        s["value"]
        for s in by_slug["amd-radeon-rx-7600-xt"]["specifications"]
        if s["key"] == "vram_capacity"
    )
    base_vram = next(
        s["value"]
        for s in by_slug["amd-radeon-rx-7600"]["specifications"]
        if s["key"] == "vram_capacity"
    )
    assert xt_vram == "16"
    assert base_vram == "8"


def test_rx7000_no_mobile_pro_or_aib_products():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        name = record["product"]["name"].lower()
        slug = record["product"]["slug"]
        assert "laptop" not in name
        assert "mobile" not in name
        assert "max-q" not in slug
        assert "radeon pro" not in name
        assert "instinct" not in name
        assert slug.startswith("amd-radeon-rx-")


def test_rx7900_xtx_legacy_slug_mapped():
    assert LEGACY_GPU_SLUG_MAP["rx-7900-xtx"] == "amd-radeon-rx-7900-xtx"


def test_rx7000_import_reconcile_and_idempotency(rx7000_setup):
    gpu = rx7000_setup
    amd = Manufacturer.query.filter_by(slug="amd").first()
    if not amd:
        amd = Manufacturer(name="AMD", slug="amd")
        db.session.add(amd)
        db.session.flush()

    db.session.add(Product(
        name="AMD Radeon RX 7900 XTX",
        slug="rx-7900-xtx",
        category_id=gpu.id,
        manufacturer_id=amd.id,
        status="active",
        is_popular=True,
    ))
    db.session.commit()

    first = import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    assert first.errors == 0
    assert first.created == 7
    assert first.updated == 0

    reconcile = reconcile_legacy_gpu_slugs()
    assert reconcile.merged == 1
    assert Product.query.filter_by(slug="rx-7900-xtx").first() is None
    assert Product.query.filter_by(slug="amd-radeon-rx-7900-xtx").count() == 1

    second = import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    assert second.errors == 0
    assert second.created == 0
    assert second.updated == 7


def test_rx7000_imported_products_have_provenance(rx7000_setup):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    for slug in EXPECTED_SLUGS:
        product = Product.query.filter_by(slug=slug).first()
        assert product is not None
        assert product.manufacturer.name == "AMD"
        assert product.family.name == "Radeon RX"
        assert product.generation.name == "RX 7000 Series"
        sources = ProductSource.query.filter_by(product_id=product.id).all()
        assert sources
        assert any("amd.com" in (s.source_url or "") for s in sources)
        segment = Specification.query.filter_by(
            product_id=product.id, key="market_segment"
        ).first()
        assert segment is not None
        assert segment.value == "desktop"


def test_rx7000_generation_filtering(rx7000_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    response = client.get("/api/products?category=gpu&generation=RX+7000+Series")
    assert response.status_code == 200
    slugs = {item["slug"] for item in response.get_json()["data"]}
    for slug in EXPECTED_SLUGS:
        assert slug in slugs


def test_rx7000_amd_and_family_filters(rx7000_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    amd = client.get("/api/products?category=gpu&manufacturer=AMD")
    assert amd.status_code == 200
    assert amd.get_json()["pagination"]["total"] == 7

    family = client.get("/api/products?category=gpu&family=Radeon+RX")
    assert family.status_code == 200
    assert family.get_json()["pagination"]["total"] == 7


def test_rx7000_search_and_compare(rx7000_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    for query in (
        "RX 7900 XTX",
        "RX 7900 XT",
        "RX 7900 GRE",
        "RX 7800 XT",
        "RX 7700 XT",
        "RX 7600 XT",
        "RX 7600",
    ):
        response = client.get("/api/search", query_string={"q": query})
        assert response.status_code == 200
        names = [item["name"] for item in response.get_json()["items"]]
        assert any(query in name for name in names)

    detail = client.get("/api/products/by-slug/amd-radeon-rx-7900-xtx")
    assert detail.status_code == 200
    body = detail.get_json()
    assert body["name"] == "AMD Radeon RX 7900 XTX"
    assert body.get("sources")
    assert body.get("related_products") is not None

    compare = client.get(
        "/api/compare?products=amd-radeon-rx-7900-xtx,amd-radeon-rx-7900-xt"
    )
    assert compare.status_code == 200
    assert len(compare.get_json()["products"]) == 2


def test_nvidia_catalog_still_valid_after_rx7000_builder():
    records = json.loads(NVIDIA_CATALOG_FILE.read_text(encoding="utf-8"))
    errors, _ = validate_catalog_records(records)
    assert not errors
    assert len(records) == 9


def test_intel_arc_legacy_slug_not_in_rx7000_legacy_map():
    assert "arc-a770" not in LEGACY_GPU_SLUG_MAP


def test_builder_produces_valid_rx7000_output():
    script = BACKEND_ROOT / "scripts" / "build_gpu_catalog.py"
    subprocess.run([sys.executable, str(script)], cwd=BACKEND_ROOT, check=True)
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    errors, _ = validate_catalog_records(records)
    assert not errors
    assert len(records) == 7
