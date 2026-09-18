"""DDR5 desktop UDIMM RAM catalog import and validation tests."""

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
    / "ddr5"
    / "desktop-udimm"
    / "desktop.json"
)
DDR4_CATALOG_FILE = (
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
    "corsair-vengeance-cmk32gx5m2b6000c30",
    "corsair-vengeance-cmk32gx5m2b6000z30",
    "corsair-vengeance-cmk64gx5m2b6000c30",
    "corsair-vengeance-cmk16gx5m1b5600c40",
    "gskill-trident-z5-neo-f5-6000j3038f16gx2-tz5n",
    "gskill-trident-z5-neo-f5-6000j3238f16gx2-tz5n",
    "gskill-aegis-5-f5-5600j3636c16gx2-is",
    "kingston-fury-beast-kf556c40bbk2-32",
    "kingston-fury-beast-kf556c40bb2-32",
    "kingston-fury-beast-kf560c36bbek2-32",
    "crucial-crucial-ddr5-ct16g56c46u5",
    "crucial-crucial-pro-cp16g56c46u5",
    "teamgroup-elite-ddr5-ted532g6000c48dc01",
    "teamgroup-elite-ddr5-ted516g6000c4801",
]

EXPECTED_COUNT = 14
DDR4_EXPECTED_COUNT = 12


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


def test_ddr5_catalog_file_validates():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    assert len(records) == EXPECTED_COUNT
    errors, _ = validate_catalog_records(records)
    assert errors == []


def test_ddr5_catalog_unique_canonical_slugs():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    slugs = [record["product"]["slug"] for record in records]
    assert slugs == EXPECTED_SLUGS
    assert len(slugs) == len(set(slugs))


def test_ddr5_no_slug_collision_with_ddr4():
    ddr5 = {
        r["product"]["slug"]
        for r in json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    }
    ddr4 = {
        r["product"]["slug"]
        for r in json.loads(DDR4_CATALOG_FILE.read_text(encoding="utf-8"))
    }
    assert ddr5.isdisjoint(ddr4)


def test_ddr5_all_records_use_official_sources():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    domains = (
        "corsair.com",
        "kingston.com",
        "gskill.com",
        "crucial.com",
        "teamgroupinc.com",
    )
    for record in records:
        assert any(domain in record["source"]["url"] for domain in domains)
        assert record["generation"] == "DDR5"
        assert record["category"] == "RAM"
        assert record["images"] == []


def test_ddr5_desktop_udimm_classification():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        by_key = {s["key"]: s["value"] for s in record["specifications"]}
        assert by_key["memory_type"] == "DDR5"
        assert by_key["form_factor"] == "UDIMM"
        assert by_key["market_segment"] == "desktop"
        assert by_key["generation"] == "DDR5"
        assert by_key["ecc"] == "Non-ECC"
        assert by_key["registered"] == "Unbuffered"


def test_ddr5_important_official_specs():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    by_slug = {r["product"]["slug"]: r for r in records}

    def spec(slug, key):
        return next(
            s["value"] for s in by_slug[slug]["specifications"] if s["key"] == key
        )

    assert spec("corsair-vengeance-cmk32gx5m2b6000c30", "memory_speed") == "6000"
    assert spec("corsair-vengeance-cmk32gx5m2b6000c30", "jedec_speed") == "4800"
    assert spec("corsair-vengeance-cmk32gx5m2b6000c30", "cas_latency") == "30"
    assert spec("corsair-vengeance-cmk32gx5m2b6000c30", "module_count") == "2"
    assert spec("corsair-vengeance-cmk32gx5m2b6000z30", "expo") == "AMD EXPO"
    assert spec(
        "gskill-trident-z5-neo-f5-6000j3038f16gx2-tz5n", "timings"
    ) == "30-38-38-96"
    assert spec("kingston-fury-beast-kf560c36bbek2-32", "memory_speed") == "6000"
    assert spec("kingston-fury-beast-kf560c36bbek2-32", "cas_latency") == "36"
    assert spec("crucial-crucial-pro-cp16g56c46u5", "xmp") == "XMP 3.0"
    assert spec("teamgroup-elite-ddr5-ted532g6000c48dc01", "cas_latency") == "48"
    assert spec("corsair-vengeance-cmk32gx5m2b6000c30", "part_number") == (
        "CMK32GX5M2B6000C30"
    )


def test_ddr5_no_laptop_ecc_or_ddr4_products():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        name = record["product"]["name"].lower()
        slug = record["product"]["slug"]
        by_key = {s["key"]: s["value"] for s in record["specifications"]}
        assert "sodimm" not in name
        assert "so-dimm" not in slug
        assert by_key["form_factor"] != "SO-DIMM"
        assert "ddr4" not in name
        assert by_key["memory_type"] == "DDR5"
        assert by_key["ecc"] == "Non-ECC"


def test_ddr5_manufacturer_coverage():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    manufacturers = {r["manufacturer"] for r in records}
    assert manufacturers == {
        "Corsair",
        "G.Skill",
        "Kingston",
        "Crucial",
        "TeamGroup",
    }


def test_ddr5_legacy_slug_map():
    assert LEGACY_RAM_SLUG_MAP["vengeance-ddr5-6000"] == (
        "corsair-vengeance-cmk32gx5m2b6000c30"
    )


def test_ddr5_import_and_idempotency(ram_setup):
    first = import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    assert first.errors == 0
    assert first.created == EXPECTED_COUNT
    assert first.updated == 0

    second = import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    assert second.errors == 0
    assert second.created == 0
    assert second.updated == EXPECTED_COUNT


def test_ddr5_legacy_reconciliation(ram_setup):
    ram = ram_setup
    corsair = Manufacturer.query.filter_by(slug="corsair").first()
    if not corsair:
        corsair = Manufacturer(name="Corsair", slug="corsair")
        db.session.add(corsair)
        db.session.flush()

    demo = Product(
        name="Corsair Vengeance DDR5 32GB 6000MHz",
        slug="vengeance-ddr5-6000",
        category_id=ram.id,
        manufacturer_id=corsair.id,
        status="active",
        is_popular=True,
    )
    db.session.add(demo)
    db.session.commit()

    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    result = reconcile_legacy_ram_slugs()
    assert result.merged == 1
    assert result.errors == []
    assert Product.query.filter_by(slug="vengeance-ddr5-6000").first() is None
    canonical = Product.query.filter_by(
        slug="corsair-vengeance-cmk32gx5m2b6000c30"
    ).first()
    assert canonical is not None
    assert canonical.is_popular is True


def test_ddr5_imported_products_have_provenance(ram_setup):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    for slug in EXPECTED_SLUGS:
        product = Product.query.filter_by(slug=slug).first()
        assert product is not None
        assert product.generation.name == "DDR5"
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


def test_ddr5_api_filters(ram_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)

    listing = client.get("/api/products?category=ram")
    assert listing.status_code == 200
    assert listing.get_json()["pagination"]["total"] == EXPECTED_COUNT

    generation = client.get("/api/products?category=ram&generation=DDR5")
    assert generation.status_code == 200
    assert generation.get_json()["pagination"]["total"] == EXPECTED_COUNT

    corsair = client.get("/api/products?category=ram&manufacturer=Corsair")
    assert corsair.status_code == 200
    assert corsair.get_json()["pagination"]["total"] == 4


def test_ddr5_search_and_detail(ram_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    for query in (
        "Vengeance",
        "CMK32GX5M2B6000C30",
        "Trident Z5 Neo",
        "F5-6000J3038F16GX2-TZ5N",
        "FURY Beast",
        "KF560C36BBEK2-32",
        "CP16G56C46U5",
        "TED532G6000C48DC01",
    ):
        response = client.get("/api/search", query_string={"q": query})
        assert response.status_code == 200
        items = response.get_json()["items"]
        assert items, f"Expected search hits for {query!r}"
        ram_hits = [item for item in items if item.get("category_slug") == "ram"]
        assert ram_hits or items

    detail = client.get(
        "/api/products/by-slug/corsair-vengeance-cmk32gx5m2b6000c30"
    )
    assert detail.status_code == 200
    body = detail.get_json()
    assert "Corsair Vengeance" in body["name"]
    assert "CMK32GX5M2B6000C30" in body["name"]
    assert body.get("sources")

    compare = client.get(
        "/api/compare?products="
        "corsair-vengeance-cmk32gx5m2b6000c30,"
        "gskill-trident-z5-neo-f5-6000j3038f16gx2-tz5n"
    )
    assert compare.status_code == 200
    assert len(compare.get_json()["products"]) == 2


def test_ddr4_regression_catalog_unchanged():
    records = json.loads(DDR4_CATALOG_FILE.read_text(encoding="utf-8"))
    errors, _ = validate_catalog_records(records)
    assert errors == []
    assert len(records) == DDR4_EXPECTED_COUNT


def test_gpu_catalog_unchanged_by_ram_builder():
    records = json.loads(GPU_CATALOG_FILE.read_text(encoding="utf-8"))
    errors, _ = validate_catalog_records(records)
    assert not errors
    assert len(records) == 9


def test_builder_produces_valid_ddr5_output():
    script = BACKEND_ROOT / "scripts" / "build_ram_catalog.py"
    subprocess.run([sys.executable, str(script)], cwd=BACKEND_ROOT, check=True)
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    errors, _ = validate_catalog_records(records)
    assert not errors
    assert len(records) == EXPECTED_COUNT
    ddr4 = json.loads(DDR4_CATALOG_FILE.read_text(encoding="utf-8"))
    assert len(ddr4) == DDR4_EXPECTED_COUNT
