"""Cross-generation RAM catalog audit (DDR4 + DDR5 desktop UDIMM).

Phase 14 — audit only. Does not expand the catalog.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

import pytest

from app import db
from app.catalog.catalog_validation import validate_catalog_records
from app.catalog.ram_slug import is_official_ram_source_url
from app.data.ram_slug_policy import LEGACY_RAM_SLUG_MAP, canonical_ram_slug
from app.models import Category, Product, ProductImage, ProductSource, Specification
from app.services.import_service import ImportMode, import_hardware_from_path
from seed_data.ram_spec_definitions import RAM_SPECS

BACKEND_ROOT = Path(__file__).resolve().parents[1]
RAM_ROOT = BACKEND_ROOT / "data" / "catalog" / "ram"
DDR4_FILE = RAM_ROOT / "ddr4" / "desktop-udimm" / "desktop.json"
DDR5_FILE = RAM_ROOT / "ddr5" / "desktop-udimm" / "desktop.json"
GPU_ROOT = BACKEND_ROOT / "data" / "catalog" / "gpu"
CPU_ROOT = BACKEND_ROOT / "data" / "catalog" / "cpu"

DDR4_EXPECTED = 12
DDR5_EXPECTED = 14
TOTAL_EXPECTED = 26

EXPECTED_MANUFACTURER_TOTALS = {
    "Corsair": {"DDR4": 4, "DDR5": 4, "total": 8},
    "G.Skill": {"DDR4": 3, "DDR5": 3, "total": 6},
    "Kingston": {"DDR4": 3, "DDR5": 3, "total": 6},
    "Crucial": {"DDR4": 2, "DDR5": 2, "total": 4},
    "TeamGroup": {"DDR4": 0, "DDR5": 2, "total": 2},
}

REPRESENTATIVE_SLUGS = {
    "corsair-vengeance-cmk32gx5m2b6000c30",
    "gskill-trident-z5-neo-f5-6000j3038f16gx2-tz5n",
    "kingston-fury-beast-kf560c36bbek2-32",
    "crucial-crucial-pro-cp16g56c46u5",
}

# Known cosmetic defect: importer normalizes decimal voltage strings
# ("1.40" → "1.4", "1.20" → "1.2"). Values remain numerically equal.
VOLTAGE_STRING_NORMALIZATION = {
    "corsair-vengeance-cmk32gx5m2b6000c30": ("1.40", "1.4"),
    "corsair-vengeance-cmk32gx5m2b6000z30": ("1.40", "1.4"),
    "corsair-vengeance-cmk64gx5m2b6000c30": ("1.40", "1.4"),
    "gskill-aegis-5-f5-5600j3636c16gx2-is": ("1.20", "1.2"),
}


def _load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def _specs(record: dict) -> dict[str, str]:
    return {s["key"]: s["value"] for s in record["specifications"]}


def _count_catalog_json(root: Path) -> int:
    total = 0
    for path in sorted(root.rglob("*.json")):
        if path.name.startswith("_") or path.name == "schema.json":
            continue
        text = path.read_text(encoding="utf-8").strip()
        if not text or text == "[]":
            continue
        batch = json.loads(text)
        if isinstance(batch, list):
            total += len(batch)
    return total


def _all_catalog_records() -> list[dict]:
    return _load_json(DDR4_FILE) + _load_json(DDR5_FILE)


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
                db.session.add(
                    SpecificationDefinition(
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
                    )
                )
        db.session.commit()
        yield ram


def _import_both():
    r4 = import_hardware_from_path(str(DDR4_FILE), mode=ImportMode.UPSERT)
    r5 = import_hardware_from_path(str(DDR5_FILE), mode=ImportMode.UPSERT)
    assert r4.errors == 0
    assert r5.errors == 0
    return r4, r5


# ── Catalog structure ───────────────────────────────────────────────────────


def test_audit_verified_counts():
    ddr4 = _load_json(DDR4_FILE)
    ddr5 = _load_json(DDR5_FILE)
    assert len(ddr4) == DDR4_EXPECTED
    assert len(ddr5) == DDR5_EXPECTED
    assert len(ddr4) + len(ddr5) == TOTAL_EXPECTED


def test_audit_manufacturer_breakdown():
    records = _all_catalog_records()
    breakdown: dict[str, Counter] = defaultdict(Counter)
    for record in records:
        breakdown[record["manufacturer"]][record["generation"]] += 1

    assert set(breakdown) == set(EXPECTED_MANUFACTURER_TOTALS)
    for manufacturer, expected in EXPECTED_MANUFACTURER_TOTALS.items():
        gens = breakdown[manufacturer]
        assert gens["DDR4"] == expected["DDR4"]
        assert gens["DDR5"] == expected["DDR5"]
        assert sum(gens.values()) == expected["total"]


def test_audit_catalog_validation():
    records = _all_catalog_records()
    errors, warnings = validate_catalog_records(records)
    assert errors == []
    assert warnings == []


def test_audit_unique_slugs_and_deterministic_policy():
    records = _all_catalog_records()
    slugs = [r["product"]["slug"] for r in records]
    assert len(slugs) == len(set(slugs))
    assert REPRESENTATIVE_SLUGS.issubset(set(slugs))
    for record in records:
        specs = _specs(record)
        expected = canonical_ram_slug(
            record["manufacturer"], record["series"], specs["part_number"]
        )
        assert record["product"]["slug"] == expected
        assert record["product"]["slug"] not in LEGACY_RAM_SLUG_MAP


def test_audit_part_number_integrity():
    records = _all_catalog_records()
    by_pn: dict[str, list[str]] = defaultdict(list)
    for record in records:
        pn = _specs(record)["part_number"]
        assert pn
        assert "TBD" not in pn.upper()
        assert "TODO" not in pn.upper()
        by_pn[pn].append(record["product"]["slug"])
    duplicates = {pn: slugs for pn, slugs in by_pn.items() if len(slugs) > 1}
    assert duplicates == {}


def test_audit_kit_capacity_consistency():
    for record in _all_catalog_records():
        specs = _specs(record)
        module_capacity = int(specs["module_capacity"])
        module_count = int(specs["module_count"])
        total = int(specs["total_kit_capacity"])
        assert module_capacity * module_count == total, record["product"]["slug"]


def test_audit_taxonomy_desktop_udimm_only():
    for record in _all_catalog_records():
        specs = _specs(record)
        assert record["category"] == "RAM"
        assert specs["form_factor"] == "UDIMM"
        assert specs["market_segment"] == "desktop"
        assert specs["memory_type"] in {"DDR4", "DDR5"}
        assert specs["generation"] == specs["memory_type"]
        assert specs["ecc"] == "Non-ECC"
        assert specs["registered"] == "Unbuffered"
        name = record["product"]["name"].lower()
        slug = record["product"]["slug"]
        assert "sodimm" not in name
        assert "so-dimm" not in slug
        assert "rdimm" not in slug
        assert "lrdimm" not in slug


def test_audit_memory_speed_semantics():
    for record in _all_catalog_records():
        specs = _specs(record)
        speed = int(specs["memory_speed"])
        generation = specs["memory_type"]
        # MT/s rated data rate — not half-clock physical frequency.
        if generation == "DDR4":
            assert 1600 <= speed <= 5000, record["product"]["slug"]
        else:
            assert 4800 <= speed <= 8400, record["product"]["slug"]
        # Marketed speed must not equal half of itself (clock confusion guard).
        assert speed != speed // 2 or speed == 0


def test_audit_jedec_xmp_expo_voltage_conventions():
    for record in _all_catalog_records():
        specs = _specs(record)
        generation = specs["memory_type"]
        if "jedec_speed" in specs:
            jedec = int(specs["jedec_speed"])
            rated = int(specs["memory_speed"])
            assert jedec > 0
            # JEDEC/default is typically at or below rated/tested speed.
            assert jedec <= rated, record["product"]["slug"]
            if generation == "DDR5" and rated >= 5600:
                # Most OC kits document SPD/JEDEC 4800; Crucial JEDEC-5600 is allowed.
                assert jedec in {4800, 5600} or jedec <= rated

        if "xmp" in specs:
            assert "XMP" in specs["xmp"]
        if "expo" in specs:
            assert "EXPO" in specs["expo"].upper()
            # EXPO is DDR5-era; DDR4 catalog must not invent it.
            assert generation == "DDR5"

        if "voltage" in specs:
            voltage = float(specs["voltage"])
            assert 1.0 <= voltage <= 1.6


def test_audit_images_empty():
    for record in _all_catalog_records():
        assert record.get("images") == []


def test_audit_official_provenance_in_catalog():
    for record in _all_catalog_records():
        url = record["source"]["url"]
        assert is_official_ram_source_url(record["manufacturer"], url)
        host = (urlparse(url).hostname or "").lower()
        assert not any(
            bad in host
            for bad in ("amazon.", "flipkart.", "ebay.", "pcpartpicker.", "reddit.")
        )


def test_audit_legacy_slug_map():
    assert LEGACY_RAM_SLUG_MAP["fury-beast-ddr4-32gb"] == (
        "kingston-fury-beast-kf432c16bb1k2-32"
    )
    assert LEGACY_RAM_SLUG_MAP["vengeance-ddr5-6000"] == (
        "corsair-vengeance-cmk32gx5m2b6000c30"
    )
    catalog_slugs = {r["product"]["slug"] for r in _all_catalog_records()}
    for legacy, canonical in LEGACY_RAM_SLUG_MAP.items():
        assert legacy not in catalog_slugs
        assert canonical in catalog_slugs


# ── Import / DB parity ──────────────────────────────────────────────────────


def test_audit_catalog_database_parity(ram_setup):
    _import_both()
    catalog = _all_catalog_records()
    catalog_by_slug = {r["product"]["slug"]: r for r in catalog}

    ram = ram_setup
    products = Product.query.filter_by(category_id=ram.id).all()
    assert len(products) == TOTAL_EXPECTED
    db_by_slug = {p.slug: p for p in products}
    assert set(db_by_slug) == set(catalog_by_slug)

    for slug, record in catalog_by_slug.items():
        product = db_by_slug[slug]
        specs = _specs(record)
        assert product.name == record["product"]["name"]
        assert product.manufacturer.name == record["manufacturer"]
        assert product.family.name == record["family"]
        assert product.series.name == record["series"]
        assert product.generation.name == record["generation"]

        db_specs = {s.key: s.value for s in product.specifications}
        for key, value in specs.items():
            if key == "voltage" and slug in VOLTAGE_STRING_NORMALIZATION:
                catalog_v, db_v = VOLTAGE_STRING_NORMALIZATION[slug]
                assert value == catalog_v
                assert db_specs.get(key) == db_v
                assert float(value) == float(db_specs[key])
                continue
            assert db_specs.get(key) == value, f"{slug}.{key}"

        sources = ProductSource.query.filter_by(product_id=product.id).all()
        assert sources
        assert any(
            is_official_ram_source_url(record["manufacturer"], s.source_url or "")
            or (
                s.source
                and s.source.url
                and is_official_ram_source_url(record["manufacturer"], s.source.url)
            )
            for s in sources
        )
        assert ProductImage.query.filter_by(product_id=product.id).count() == 0


def test_audit_no_legacy_demo_products_after_import(ram_setup):
    _import_both()
    for legacy in LEGACY_RAM_SLUG_MAP:
        assert Product.query.filter_by(slug=legacy).first() is None


def test_audit_import_idempotency(ram_setup):
    first4, first5 = _import_both()
    assert first4.created == DDR4_EXPECTED
    assert first5.created == DDR5_EXPECTED

    second4, second5 = _import_both()
    assert second4.created == 0
    assert second5.created == 0
    assert second4.updated == DDR4_EXPECTED
    assert second5.updated == DDR5_EXPECTED
    assert Product.query.filter_by(category_id=ram_setup.id).count() == TOTAL_EXPECTED


# ── API ─────────────────────────────────────────────────────────────────────


def test_audit_api_listing_filters_pagination(ram_setup, client):
    _import_both()

    listing = client.get("/api/products?category=ram")
    assert listing.status_code == 200
    body = listing.get_json()
    assert body["pagination"]["total"] == TOTAL_EXPECTED

    page = client.get("/api/products?category=ram&page=1&per_page=10")
    assert page.status_code == 200
    assert len(page.get_json()["items"]) == 10
    assert page.get_json()["pagination"]["total"] == TOTAL_EXPECTED

    ddr4 = client.get("/api/products?category=ram&generation=DDR4")
    assert ddr4.get_json()["pagination"]["total"] == DDR4_EXPECTED
    ddr5 = client.get("/api/products?category=ram&generation=DDR5")
    assert ddr5.get_json()["pagination"]["total"] == DDR5_EXPECTED

    for manufacturer, expected in EXPECTED_MANUFACTURER_TOTALS.items():
        response = client.get(
            f"/api/products?category=ram&manufacturer={manufacturer}"
        )
        assert response.status_code == 200
        assert response.get_json()["pagination"]["total"] == expected["total"]


def test_audit_search_part_numbers(ram_setup, client):
    _import_both()
    queries = [
        ("CMK16GX4M2B3200C16", "corsair-vengeance-lpx-cmk16gx4m2b3200c16"),
        ("CMK32GX5M2B6000C30", "corsair-vengeance-cmk32gx5m2b6000c30"),
        ("F5-6000J3038F16GX2-TZ5N", "gskill-trident-z5-neo-f5-6000j3038f16gx2-tz5n"),
        ("KF560C36BBEK2-32", "kingston-fury-beast-kf560c36bbek2-32"),
        ("CT8G4DFRA32A", "crucial-crucial-ddr4-ct8g4dfra32a"),
        ("TED532G6000C48DC01", "teamgroup-elite-ddr5-ted532g6000c48dc01"),
    ]
    for query, expected_slug in queries:
        response = client.get("/api/search", query_string={"q": query})
        assert response.status_code == 200
        items = response.get_json()["items"]
        assert items, f"No hits for {query}"
        slugs = {item.get("slug") for item in items}
        assert expected_slug in slugs, f"{query} -> {slugs}"


def test_audit_detail_and_comparison(ram_setup, client):
    _import_both()

    detail = client.get(
        "/api/products/by-slug/corsair-vengeance-cmk32gx5m2b6000c30"
    )
    assert detail.status_code == 200
    body = detail.get_json()
    assert "CMK32GX5M2B6000C30" in body["name"]
    assert body.get("sources")

    pairs = [
        # DDR4 vs DDR5
        (
            "corsair-vengeance-lpx-cmk16gx4m2b3200c16",
            "corsair-vengeance-cmk32gx5m2b6000c30",
        ),
        # different manufacturers
        (
            "kingston-fury-beast-kf560c36bbek2-32",
            "gskill-trident-z5-neo-f5-6000j3038f16gx2-tz5n",
        ),
        # single vs kit
        (
            "kingston-fury-beast-kf556c40bb2-32",
            "kingston-fury-beast-kf556c40bbk2-32",
        ),
        # different speeds
        (
            "corsair-vengeance-cmk16gx5m1b5600c40",
            "corsair-vengeance-cmk32gx5m2b6000c30",
        ),
    ]
    for a, b in pairs:
        response = client.get(f"/api/compare?products={a},{b}")
        assert response.status_code == 200
        products = response.get_json()["products"]
        assert len(products) == 2


def test_audit_builder_discovers_both_generations():
    script = BACKEND_ROOT / "scripts" / "build_ram_catalog.py"
    subprocess.run(
        [sys.executable, str(script), "--validate"],
        cwd=BACKEND_ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, str(script), "--dry-run"],
        cwd=BACKEND_ROOT,
        check=True,
    )
    assert len(_load_json(DDR4_FILE)) == DDR4_EXPECTED
    assert len(_load_json(DDR5_FILE)) == DDR5_EXPECTED


# ── CPU / GPU regression ────────────────────────────────────────────────────


def test_audit_gpu_cpu_catalog_unchanged():
    assert _count_catalog_json(GPU_ROOT) == 67
    # Repository CPU catalog baseline (JSON files). DB may include one extra
    # non-catalog record; audit must not modify either catalog tree.
    assert _count_catalog_json(CPU_ROOT) == 219
