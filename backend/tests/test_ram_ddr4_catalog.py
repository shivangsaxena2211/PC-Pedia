"""DDR4 desktop UDIMM RAM catalog import and validation tests."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from app import db
from app.catalog.catalog_validation import validate_catalog_records
from app.data.ram_slug_policy import LEGACY_RAM_SLUG_MAP
from app.models import Category, Manufacturer, Product, ProductSource, Specification
from app.services.import_service import ImportMode, import_hardware_from_path
from app.services.product_reconciliation_service import reconcile_legacy_ram_slugs
from seed_data.ram_spec_definitions import RAM_SPECS

BACKEND_ROOT = Path(__file__).resolve().parents[1]
CATALOG_FILE = (
    BACKEND_ROOT
    / "data"
    / "catalog"
    / "ram"
    / "ddr4"
    / "desktop-udimm"
    / "desktop.json"
)
GPU_CATALOG_FILE = (
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
    "corsair-vengeance-lpx-cmk8gx4m1e3200c16",
    "corsair-vengeance-lpx-cmk16gx4m2b3200c16",
    "corsair-vengeance-lpx-cmk32gx4m2e3200c16",
    "corsair-vengeance-lpx-cmk32gx4m2a2666c16",
    "kingston-fury-beast-kf432c16bb-8",
    "kingston-fury-beast-kf432c16bb1-16",
    "kingston-fury-beast-kf432c16bb1k2-32",
    "gskill-ripjaws-v-f4-3200c16d-32gvk",
    "gskill-ripjaws-v-f4-3600c18d-16gvk",
    "gskill-ripjaws-v-f4-3600c18d-32gvk",
    "crucial-crucial-ddr4-ct8g4dfra32a",
    "crucial-crucial-ddr4-ct16g4dfra32a",
]

EXPECTED_COUNT = 12


@pytest.fixture
def ram_setup(app):
    with app.app_context():
        ram = Category.query.filter_by(slug="ram").first()
        if not ram:
            ram = Category(name="RAM", slug="ram", icon="memory-stick", display_order=3)
            db.session.add(ram)
            db.session.flush()

        from app.models import SpecificationDefinition

        for group, key, display, dtype, unit, filt, comp, req, order in RAM_SPECS:
            existing = SpecificationDefinition.query.filter_by(
                category_id=ram.id, key=key
            ).first()
            if not existing:
                db.session.add(SpecificationDefinition(
                    category_id=ram.id,
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
        yield ram


def test_ddr4_catalog_file_validates():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    assert len(records) == EXPECTED_COUNT
    errors, _ = validate_catalog_records(records)
    assert errors == []


def test_ddr4_catalog_unique_canonical_slugs():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    slugs = [record["product"]["slug"] for record in records]
    assert slugs == EXPECTED_SLUGS
    assert len(slugs) == len(set(slugs))


def test_ddr4_all_records_use_official_sources():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    domains = ("corsair.com", "kingston.com", "gskill.com", "crucial.com")
    for record in records:
        assert any(domain in record["source"]["url"] for domain in domains)
        assert record["generation"] == "DDR4"
        assert record["category"] == "RAM"
        assert record["images"] == []


def test_ddr4_desktop_udimm_classification():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        by_key = {s["key"]: s["value"] for s in record["specifications"]}
        assert by_key["memory_type"] == "DDR4"
        assert by_key["form_factor"] == "UDIMM"
        assert by_key["market_segment"] == "desktop"
        assert by_key["ecc"] == "Non-ECC"
        assert by_key["registered"] == "Unbuffered"


def test_ddr4_important_official_specs():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    by_slug = {r["product"]["slug"]: r for r in records}

    def spec(slug, key):
        return next(
            s["value"] for s in by_slug[slug]["specifications"] if s["key"] == key
        )

    assert spec("corsair-vengeance-lpx-cmk16gx4m2b3200c16", "memory_speed") == "3200"
    assert spec("corsair-vengeance-lpx-cmk16gx4m2b3200c16", "total_kit_capacity") == "16"
    assert spec("corsair-vengeance-lpx-cmk16gx4m2b3200c16", "module_count") == "2"
    assert spec("kingston-fury-beast-kf432c16bb1k2-32", "total_kit_capacity") == "32"
    assert spec("kingston-fury-beast-kf432c16bb1k2-32", "cas_latency") == "16"
    assert spec("gskill-ripjaws-v-f4-3600c18d-32gvk", "memory_speed") == "3600"
    assert spec("gskill-ripjaws-v-f4-3200c16d-32gvk", "timings") == "16-18-18-38"
    assert spec("crucial-crucial-ddr4-ct8g4dfra32a", "module_capacity") == "8"


def test_ddr4_no_laptop_ecc_or_ddr5_products():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        name = record["product"]["name"].lower()
        slug = record["product"]["slug"]
        by_key = {s["key"]: s["value"] for s in record["specifications"]}
        assert "sodimm" not in name
        assert "so-dimm" not in slug
        assert by_key["form_factor"] != "SO-DIMM"
        assert "ddr5" not in name
        assert by_key["memory_type"] == "DDR4"
        assert by_key["ecc"] == "Non-ECC"


def test_ddr4_manufacturer_coverage():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    manufacturers = {r["manufacturer"] for r in records}
    assert manufacturers == {"Corsair", "Kingston", "G.Skill", "Crucial"}


def test_ddr4_legacy_slug_map():
    assert LEGACY_RAM_SLUG_MAP["fury-beast-ddr4-32gb"] == (
        "kingston-fury-beast-kf432c16bb1k2-32"
    )


def test_ddr4_import_and_idempotency(ram_setup):
    first = import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    assert first.errors == 0
    assert first.created == EXPECTED_COUNT
    assert first.updated == 0

    second = import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    assert second.errors == 0
    assert second.created == 0
    assert second.updated == EXPECTED_COUNT


def test_ddr4_legacy_reconciliation(ram_setup):
    ram = ram_setup
    kingston = Manufacturer.query.filter_by(slug="kingston").first()
    if not kingston:
        kingston = Manufacturer(name="Kingston", slug="kingston")
        db.session.add(kingston)
        db.session.flush()

    demo = Product(
        name="Kingston Fury Beast DDR4 32GB 3200MHz",
        slug="fury-beast-ddr4-32gb",
        category_id=ram.id,
        manufacturer_id=kingston.id,
        status="active",
    )
    db.session.add(demo)
    db.session.commit()

    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    result = reconcile_legacy_ram_slugs()
    assert result.merged == 1
    assert result.errors == []
    assert Product.query.filter_by(slug="fury-beast-ddr4-32gb").first() is None
    assert Product.query.filter_by(
        slug="kingston-fury-beast-kf432c16bb1k2-32"
    ).count() == 1


def test_ddr4_imported_products_have_provenance(ram_setup):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    for slug in EXPECTED_SLUGS:
        product = Product.query.filter_by(slug=slug).first()
        assert product is not None
        assert product.generation.name == "DDR4"
        sources = ProductSource.query.filter_by(product_id=product.id).all()
        assert sources
        segment = Specification.query.filter_by(
            product_id=product.id, key="market_segment"
        ).first()
        assert segment is not None
        assert segment.value == "desktop"
        form = Specification.query.filter_by(
            product_id=product.id, key="form_factor"
        ).first()
        assert form is not None
        assert form.value == "UDIMM"


def test_ddr4_api_filters(ram_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)

    listing = client.get("/api/products?category=ram")
    assert listing.status_code == 200
    assert listing.get_json()["pagination"]["total"] == EXPECTED_COUNT

    generation = client.get("/api/products?category=ram&generation=DDR4")
    assert generation.status_code == 200
    assert generation.get_json()["pagination"]["total"] == EXPECTED_COUNT

    corsair = client.get("/api/products?category=ram&manufacturer=Corsair")
    assert corsair.status_code == 200
    assert corsair.get_json()["pagination"]["total"] == 4


def test_ddr4_search_and_detail(ram_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    for query in (
        "Vengeance LPX",
        "FURY Beast",
        "Ripjaws V",
        "CT8G4DFRA32A",
        "CMK16GX4M2B3200C16",
    ):
        response = client.get("/api/search", query_string={"q": query})
        assert response.status_code == 200
        items = response.get_json()["items"]
        assert items, f"Expected search hits for {query!r}"
        # Prefer RAM hits when present; manufacturer-only queries may mix categories.
        ram_hits = [item for item in items if item.get("category_slug") == "ram"]
        assert ram_hits or items

    detail = client.get(
        "/api/products/by-slug/corsair-vengeance-lpx-cmk16gx4m2b3200c16"
    )
    assert detail.status_code == 200
    body = detail.get_json()
    assert "Corsair Vengeance LPX" in body["name"]
    assert body.get("sources")

    compare = client.get(
        "/api/compare?products="
        "corsair-vengeance-lpx-cmk16gx4m2b3200c16,"
        "kingston-fury-beast-kf432c16bb1k2-32"
    )
    assert compare.status_code == 200
    assert len(compare.get_json()["products"]) == 2


def test_gpu_catalog_unchanged_by_ram_builder():
    records = json.loads(GPU_CATALOG_FILE.read_text(encoding="utf-8"))
    errors, _ = validate_catalog_records(records)
    assert not errors
    assert len(records) == 9


def test_builder_produces_valid_ddr4_output():
    script = BACKEND_ROOT / "scripts" / "build_ram_catalog.py"
    subprocess.run([sys.executable, str(script)], cwd=BACKEND_ROOT, check=True)
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    errors, _ = validate_catalog_records(records)
    assert not errors
    assert len(records) == EXPECTED_COUNT
