"""Cross-vendor audit for the verified NVIDIA, AMD, and Intel Arc GPU catalogs."""

import json
import re
from pathlib import Path

import pytest

from app import db
from app.catalog.catalog_validation import validate_catalog_records
from app.catalog.gpu_slug import validate_gpu_slug
from app.data.gpu_slug_policy import LEGACY_GPU_SLUG_MAP
from app.models import Category, Product, ProductSource, Specification, SpecificationDefinition
from app.services.import_service import ImportMode, import_hardware_from_path
from app.services.product_reconciliation_service import reconcile_legacy_gpu_slugs
from scripts.build_gpu_catalog import collect_catalog_records, dry_run_import
from seed_data.gpu_spec_definitions import GPU_SPECS

BACKEND_ROOT = Path(__file__).resolve().parents[1]
CATALOG_ROOT = BACKEND_ROOT / "data" / "catalog" / "gpu"
CPU_CATALOG_ROOT = BACKEND_ROOT / "data" / "catalog" / "cpu"

VERIFIED_GPU_TOTAL = 67

MANUFACTURER_COUNTS = {
    "NVIDIA": 43,
    "AMD": 19,
    "Intel": 5,
}

GENERATION_COUNTS = {
    "GTX 10 Series": 9,
    "GTX 16 Series": 7,
    "RTX 20 Series": 8,
    "RTX 30 Series": 10,
    "RTX 40 Series": 9,
    "RX 6000 Series": 12,
    "RX 7000 Series": 7,
    "Arc A-Series": 5,
}

CATALOG_BATCHES = [
    CATALOG_ROOT / "nvidia" / "geforce" / "gtx-10-series" / "desktop.json",
    CATALOG_ROOT / "nvidia" / "geforce" / "gtx-16-series" / "desktop.json",
    CATALOG_ROOT / "nvidia" / "geforce" / "rtx-20-series" / "desktop.json",
    CATALOG_ROOT / "nvidia" / "geforce" / "rtx-30-series" / "desktop.json",
    CATALOG_ROOT / "nvidia" / "geforce" / "rtx-40-series" / "desktop.json",
    CATALOG_ROOT / "amd" / "radeon" / "rx-6000-series" / "desktop.json",
    CATALOG_ROOT / "amd" / "radeon" / "rx-7000-series" / "desktop.json",
    CATALOG_ROOT / "intel" / "arc" / "a-series" / "desktop.json",
]

NVIDIA_VARIANT_GROUPS = [
    [
        "nvidia-geforce-gtx-1050-2gb",
        "nvidia-geforce-gtx-1050-3gb",
        "nvidia-geforce-gtx-1050-ti",
    ],
    ["nvidia-geforce-gtx-1060-3gb", "nvidia-geforce-gtx-1060-6gb"],
    ["nvidia-geforce-gtx-1650", "nvidia-geforce-gtx-1650-gddr6"],
    ["nvidia-geforce-rtx-2060", "nvidia-geforce-rtx-2060-12gb"],
    ["nvidia-geforce-rtx-3050-6gb", "nvidia-geforce-rtx-3050-8gb"],
]

AMD_REFRESH_VARIANTS = [
    "amd-radeon-rx-6950-xt",
    "amd-radeon-rx-6750-xt",
    "amd-radeon-rx-6650-xt",
]

SEARCH_QUERIES = [
    ("RTX 4090", "NVIDIA GeForce RTX 4090"),
    ("RTX 3090", "NVIDIA GeForce RTX 3090"),
    ("GTX 1080 Ti", "NVIDIA GeForce GTX 1080 Ti"),
    ("GTX 1660 SUPER", "NVIDIA GeForce GTX 1660 SUPER"),
    ("RX 7900 XTX", "AMD Radeon RX 7900 XTX"),
    ("RX 6950 XT", "AMD Radeon RX 6950 XT"),
    ("RX 6700 XT", "AMD Radeon RX 6700 XT"),
    ("RX 6600", "AMD Radeon RX 6600"),
    ("Arc A770", "Intel Arc A770"),
    ("Arc A750", "Intel Arc A750"),
    ("Arc A580", "Intel Arc A580"),
    ("Arc A380", "Intel Arc A380"),
    ("Arc A310", "Intel Arc A310"),
]


def _load_all_verified_records() -> list[dict]:
    return collect_catalog_records(CATALOG_ROOT)


def _count_cpu_catalog_records() -> int:
    total = 0
    for path in CPU_CATALOG_ROOT.glob("**/*.json"):
        if path.name == "schema.json":
            continue
        text = path.read_text(encoding="utf-8").strip()
        if not text or text == "[]":
            continue
        total += len(json.loads(text))
    return total


@pytest.fixture
def gpu_audit_setup(app):
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


def test_verified_gpu_inventory_totals():
    records = _load_all_verified_records()
    assert len(records) == VERIFIED_GPU_TOTAL

    by_manufacturer: dict[str, int] = {}
    by_generation: dict[str, int] = {}
    for record in records:
        by_manufacturer[record["manufacturer"]] = by_manufacturer.get(record["manufacturer"], 0) + 1
        by_generation[record["generation"]] = by_generation.get(record["generation"], 0) + 1

    assert by_manufacturer == MANUFACTURER_COUNTS
    assert by_generation == GENERATION_COUNTS


def test_verified_gpu_catalog_validates():
    records = _load_all_verified_records()
    errors, _ = validate_catalog_records(records)
    assert errors == []


def test_verified_gpu_no_duplicate_slugs_or_names():
    records = _load_all_verified_records()
    slugs = [record["product"]["slug"] for record in records]
    names = [record["product"]["name"] for record in records]
    assert len(slugs) == len(set(slugs))
    assert len(names) == len(set(names))


def test_verified_gpu_canonical_slug_policy():
    records = _load_all_verified_records()
    for record in records:
        slug = record["product"]["slug"]
        manufacturer = record["manufacturer"]
        family = record["family"]
        assert validate_gpu_slug(slug, manufacturer, family) is None
        if manufacturer == "NVIDIA":
            assert slug.startswith("nvidia-geforce-")
        elif manufacturer == "AMD":
            assert slug.startswith("amd-radeon-rx-")
        elif manufacturer == "Intel":
            assert slug.startswith("intel-arc-a")


def test_verified_gpu_taxonomy_consistency():
    records = _load_all_verified_records()
    for record in records:
        manufacturer = record["manufacturer"]
        assert manufacturer in MANUFACTURER_COUNTS
        if manufacturer == "NVIDIA":
            assert record["family"] == "GeForce"
            assert record["series"] in {"GeForce GTX", "GeForce RTX"}
        elif manufacturer == "AMD":
            assert record["family"] == "Radeon RX"
            assert record["series"] == "Radeon RX"
        elif manufacturer == "Intel":
            assert record["family"] == "Arc"
            assert record["series"] == "Arc A-Series"
        segment = next(
            spec["value"]
            for spec in record["specifications"]
            if spec["key"] == "market_segment"
        )
        assert segment == "desktop"


def test_verified_gpu_provenance_and_images():
    records = _load_all_verified_records()
    official_domains = {
        "NVIDIA": "nvidia.com",
        "AMD": "amd.com",
        "Intel": "intel.com",
    }
    for record in records:
        manufacturer = record["manufacturer"]
        source = record["source"]
        assert official_domains[manufacturer] in source["url"]
        assert record["images"] == []


def test_verified_gpu_no_mobile_workstation_or_demo_products():
    records = _load_all_verified_records()
    blocked_terms = ("laptop", "mobile", "workstation", "datacenter", "instinct", "quadro")
    for record in records:
        name = record["product"]["name"].lower()
        slug = record["product"]["slug"]
        for term in blocked_terms:
            assert term not in name
        assert "max-q" not in slug
        assert slug not in LEGACY_GPU_SLUG_MAP


@pytest.mark.parametrize("variant_slugs", NVIDIA_VARIANT_GROUPS)
def test_verified_nvidia_documented_variants_present(variant_slugs):
    slugs = {record["product"]["slug"] for record in _load_all_verified_records()}
    for slug in variant_slugs:
        assert slug in slugs


def test_verified_amd_refresh_variants_present():
    slugs = {record["product"]["slug"] for record in _load_all_verified_records()}
    for slug in AMD_REFRESH_VARIANTS:
        assert slug in slugs


def test_verified_intel_a770_single_canonical_identity():
    records = _load_all_verified_records()
    intel_slugs = [
        record["product"]["slug"]
        for record in records
        if record["manufacturer"] == "Intel"
    ]
    assert intel_slugs.count("intel-arc-a770") == 1
    assert "intel-arc-a770-8gb" not in intel_slugs
    assert "intel-arc-a770-16gb" not in intel_slugs


def _import_all_verified_gpu_catalogs() -> None:
    for path in CATALOG_BATCHES:
        import_hardware_from_path(str(path), mode=ImportMode.UPSERT)


def test_verified_gpu_database_inventory_and_catalog_parity(gpu_audit_setup):
    records = _load_all_verified_records()
    catalog_by_slug = {record["product"]["slug"]: record for record in records}
    _import_all_verified_gpu_catalogs()

    gpu = Category.query.filter_by(slug="gpu").first()
    products = Product.query.filter_by(category_id=gpu.id).all()
    assert len(products) == VERIFIED_GPU_TOTAL
    assert {product.slug for product in products} == set(catalog_by_slug)

    for product in products:
        record = catalog_by_slug[product.slug]
        assert product.name == record["product"]["name"]
        assert product.manufacturer.name == record["manufacturer"]
        assert product.family.name == record["family"]
        assert product.generation.name == record["generation"]
        catalog_specs = {spec["key"]: spec["value"] for spec in record["specifications"]}
        db_specs = {
            spec.key: spec.value
            for spec in Specification.query.filter_by(product_id=product.id).all()
            if spec.key in catalog_specs
        }
        assert db_specs == catalog_specs

        sources = ProductSource.query.filter_by(product_id=product.id).all()
        assert sources
        domain = {"NVIDIA": "nvidia.com", "AMD": "amd.com", "Intel": "intel.com"}[
            product.manufacturer.name
        ]
        assert any(domain in (source.source_url or "") for source in sources)


def test_verified_gpu_no_legacy_demo_slugs_remain(gpu_audit_setup):
    _import_all_verified_gpu_catalogs()
    reconcile_legacy_gpu_slugs()
    for legacy_slug in LEGACY_GPU_SLUG_MAP:
        assert Product.query.filter_by(slug=legacy_slug).first() is None
    assert Product.query.filter_by(slug="intel-arc-a770").count() == 1
    assert Product.query.filter_by(slug="arc-a770").count() == 0


def test_verified_gpu_import_idempotency(gpu_audit_setup):
    _import_all_verified_gpu_catalogs()
    first_total = Product.query.join(Category).filter(Category.slug == "gpu").count()

    second_created = 0
    second_updated = 0
    for path in CATALOG_BATCHES:
        result = import_hardware_from_path(str(path), mode=ImportMode.UPSERT)
        second_created += result.created
        second_updated += result.updated
        assert result.errors == 0

    assert second_created == 0
    assert Product.query.join(Category).filter(Category.slug == "gpu").count() == first_total


def test_verified_gpu_builder_dry_run():
    assert dry_run_import(CATALOG_ROOT) == 0


def test_verified_gpu_api_generation_and_manufacturer_counts(gpu_audit_setup, client):
    _import_all_verified_gpu_catalogs()
    generation_queries = {
        "GTX+10+Series": 9,
        "GTX+16+Series": 7,
        "RTX+20+Series": 8,
        "RTX+30+Series": 10,
        "RTX+40+Series": 9,
        "RX+6000+Series": 12,
        "RX+7000+Series": 7,
        "Arc+A-Series": 5,
    }
    for generation, count in generation_queries.items():
        response = client.get(f"/api/products?category=gpu&generation={generation}")
        assert response.status_code == 200
        body = response.get_json()
        assert body["pagination"]["total"] == count
        assert len(body["data"]) == count

    for manufacturer, count in MANUFACTURER_COUNTS.items():
        response = client.get(f"/api/products?category=gpu&manufacturer={manufacturer}")
        assert response.status_code == 200
        assert response.get_json()["pagination"]["total"] == count

    response = client.get("/api/products?category=gpu")
    assert response.status_code == 200
    assert response.get_json()["pagination"]["total"] == VERIFIED_GPU_TOTAL


@pytest.mark.parametrize("query,expected_name", SEARCH_QUERIES)
def test_verified_gpu_search_returns_expected_product(gpu_audit_setup, client, query, expected_name):
    _import_all_verified_gpu_catalogs()
    response = client.get("/api/search", query_string={"q": query})
    assert response.status_code == 200
    names = [item["name"] for item in response.get_json()["items"]]
    assert expected_name in names


def test_verified_gpu_product_detail_compare_and_family_filters(gpu_audit_setup, client):
    _import_all_verified_gpu_catalogs()

    detail = client.get("/api/products/by-slug/intel-arc-a770")
    assert detail.status_code == 200
    body = detail.get_json()
    assert body["name"] == "Intel Arc A770"
    assert body.get("sources")
    assert body.get("related_products") is not None

    compare = client.get(
        "/api/compare?products=nvidia-geforce-rtx-4090,amd-radeon-rx-7900-xtx,intel-arc-a770"
    )
    assert compare.status_code == 200
    assert len(compare.get_json()["products"]) == 3

    radeon = client.get("/api/products?category=gpu&family=Radeon+RX")
    assert radeon.status_code == 200
    assert radeon.get_json()["pagination"]["total"] == MANUFACTURER_COUNTS["AMD"]

    arc = client.get("/api/products?category=gpu&family=Arc")
    assert arc.status_code == 200
    assert arc.get_json()["pagination"]["total"] == MANUFACTURER_COUNTS["Intel"]


def test_cpu_catalog_isolation_from_gpu_audit():
    catalog_count = _count_cpu_catalog_records()
    assert catalog_count > 0
