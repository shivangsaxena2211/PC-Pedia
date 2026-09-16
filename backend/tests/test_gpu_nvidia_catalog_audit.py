"""Cross-generation audit tests for the verified NVIDIA GeForce desktop GPU catalog."""

import json
import re
from pathlib import Path

import pytest

from app import db
from app.catalog.catalog_validation import validate_catalog_records
from app.models import Category, Product, ProductSource, Specification, SpecificationDefinition
from app.services.import_service import ImportMode, import_hardware_from_path
from seed_data.gpu_spec_definitions import GPU_SPECS

BACKEND_ROOT = Path(__file__).resolve().parents[1]
CATALOG_ROOT = BACKEND_ROOT / "data" / "catalog" / "gpu" / "nvidia" / "geforce"

GENERATION_COUNTS = {
    "gtx-10-series": ("GTX 10 Series", 9),
    "gtx-16-series": ("GTX 16 Series", 7),
    "rtx-20-series": ("RTX 20 Series", 8),
    "rtx-30-series": ("RTX 30 Series", 10),
    "rtx-40-series": ("RTX 40 Series", 9),
}

VERIFIED_NVIDIA_TOTAL = 43
SLUG_PATTERN = re.compile(r"^nvidia-geforce-(gtx|rtx)-[a-z0-9-]+$")


def _load_generation_records(folder: str) -> list[dict]:
    path = CATALOG_ROOT / folder / "desktop.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _load_all_verified_records() -> list[dict]:
    records: list[dict] = []
    for folder in GENERATION_COUNTS:
        records.extend(_load_generation_records(folder))
    return records


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


def test_verified_nvidia_inventory_counts():
    total = 0
    for folder, (generation, expected) in GENERATION_COUNTS.items():
        records = _load_generation_records(folder)
        assert len(records) == expected, f"{folder}: expected {expected}, got {len(records)}"
        for record in records:
            assert record["generation"] == generation
        total += len(records)
    assert total == VERIFIED_NVIDIA_TOTAL


def test_verified_nvidia_catalog_validates():
    records = _load_all_verified_records()
    errors, _ = validate_catalog_records(records)
    assert errors == []


def test_verified_nvidia_no_duplicate_slugs_or_names():
    records = _load_all_verified_records()
    slugs = [record["product"]["slug"] for record in records]
    names = [record["product"]["name"] for record in records]
    assert len(slugs) == len(set(slugs))
    assert len(names) == len(set(names))


def test_verified_nvidia_slug_convention():
    records = _load_all_verified_records()
    for record in records:
        slug = record["product"]["slug"]
        assert SLUG_PATTERN.match(slug)
        assert slug.startswith("nvidia-geforce-")


def test_verified_nvidia_taxonomy_consistency():
    records = _load_all_verified_records()
    for record in records:
        assert record["manufacturer"] == "NVIDIA"
        assert record["family"] == "GeForce"
        assert record["series"] in {"GeForce GTX", "GeForce RTX"}
        if record["generation"].startswith("GTX"):
            assert record["series"] == "GeForce GTX"
        else:
            assert record["series"] == "GeForce RTX"
        segment = next(
            spec["value"]
            for spec in record["specifications"]
            if spec["key"] == "market_segment"
        )
        assert segment == "desktop"


def test_verified_nvidia_provenance_and_images():
    records = _load_all_verified_records()
    for record in records:
        source = record["source"]
        assert source["name"] == "NVIDIA official product specifications"
        assert "nvidia.com" in source["url"]
        assert record["images"] == []


def test_verified_nvidia_no_mobile_products():
    records = _load_all_verified_records()
    for record in records:
        name = record["product"]["name"].lower()
        slug = record["product"]["slug"]
        assert "laptop" not in name
        assert "mobile" not in name
        assert "max-q" not in slug


@pytest.mark.parametrize(
    "variant_slugs",
    [
        [
            "nvidia-geforce-gtx-1050-2gb",
            "nvidia-geforce-gtx-1050-3gb",
            "nvidia-geforce-gtx-1050-ti",
        ],
        ["nvidia-geforce-gtx-1060-3gb", "nvidia-geforce-gtx-1060-6gb"],
        ["nvidia-geforce-gtx-1650", "nvidia-geforce-gtx-1650-gddr6"],
        ["nvidia-geforce-rtx-2060", "nvidia-geforce-rtx-2060-12gb"],
        ["nvidia-geforce-rtx-3050-6gb", "nvidia-geforce-rtx-3050-8gb"],
    ],
)
def test_verified_nvidia_documented_variants_present(variant_slugs):
    slugs = {record["product"]["slug"] for record in _load_all_verified_records()}
    for slug in variant_slugs:
        assert slug in slugs


def _import_all_verified_catalogs() -> None:
    for folder in GENERATION_COUNTS:
        import_hardware_from_path(
            str(CATALOG_ROOT / folder / "desktop.json"),
            mode=ImportMode.UPSERT,
        )


def test_verified_nvidia_database_inventory(gpu_setup):
    records = _load_all_verified_records()
    catalog_slugs = {record["product"]["slug"] for record in records}
    _import_all_verified_catalogs()

    gpu = Category.query.filter_by(slug="gpu").first()
    nvidia_products = [
        product
        for product in Product.query.filter_by(category_id=gpu.id).all()
        if product.manufacturer and product.manufacturer.name == "NVIDIA"
    ]
    assert len(nvidia_products) == VERIFIED_NVIDIA_TOTAL
    assert {product.slug for product in nvidia_products} == catalog_slugs

    for product in nvidia_products:
        sources = ProductSource.query.filter_by(product_id=product.id).all()
        assert sources
        assert any("nvidia.com" in (source.source_url or "") for source in sources)
        segment = Specification.query.filter_by(
            product_id=product.id, key="market_segment"
        ).first()
        assert segment is not None
        assert segment.value == "desktop"


def test_verified_nvidia_api_generation_counts(gpu_setup, client):
    _import_all_verified_catalogs()
    expected = {
        "GTX+10+Series": 9,
        "GTX+16+Series": 7,
        "RTX+20+Series": 8,
        "RTX+30+Series": 10,
        "RTX+40+Series": 9,
    }
    for generation, count in expected.items():
        response = client.get(f"/api/products?category=gpu&generation={generation}")
        assert response.status_code == 200
        body = response.get_json()
        assert len(body["data"]) == count
        assert body["pagination"]["total"] == count

    response = client.get("/api/products?category=gpu&manufacturer=NVIDIA")
    assert response.status_code == 200
    body = response.get_json()
    assert body["pagination"]["total"] == VERIFIED_NVIDIA_TOTAL
