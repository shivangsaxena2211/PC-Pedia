"""AMD Radeon RX 6000 Series desktop catalog import and validation tests."""

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
    / "amd"
    / "radeon"
    / "rx-6000-series"
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
    "amd-radeon-rx-6950-xt",
    "amd-radeon-rx-6900-xt",
    "amd-radeon-rx-6800-xt",
    "amd-radeon-rx-6800",
    "amd-radeon-rx-6750-xt",
    "amd-radeon-rx-6700-xt",
    "amd-radeon-rx-6700",
    "amd-radeon-rx-6650-xt",
    "amd-radeon-rx-6600-xt",
    "amd-radeon-rx-6600",
    "amd-radeon-rx-6500-xt",
    "amd-radeon-rx-6400",
]


@pytest.fixture
def rx6000_setup(app):
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


def test_rx6000_catalog_file_validates():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    assert len(records) == 12
    errors, _ = validate_catalog_records(records)
    assert errors == []


def test_rx6000_catalog_unique_canonical_slugs():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    slugs = [record["product"]["slug"] for record in records]
    assert slugs == EXPECTED_SLUGS
    assert len(slugs) == len(set(slugs))


def test_rx6000_all_records_use_amd_official_sources():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        assert "amd.com" in record["source"]["url"]
        assert record["source"]["name"] == "AMD official product specifications"
        assert record["generation"] == "RX 6000 Series"
        assert record["architecture"] == "RDNA 2"
        assert record["manufacturer"] == "AMD"
        assert record["family"] == "Radeon RX"
        assert record["series"] == "Radeon RX"


def test_rx6000_desktop_market_segment():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    for record in records:
        segment = next(
            s["value"] for s in record["specifications"] if s["key"] == "market_segment"
        )
        assert segment == "desktop"


def test_rx6000_important_official_specs():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    by_slug = {r["product"]["slug"]: r for r in records}

    def spec(slug, key):
        return next(
            s["value"] for s in by_slug[slug]["specifications"] if s["key"] == key
        )

    assert spec("amd-radeon-rx-6950-xt", "compute_units") == "80"
    assert spec("amd-radeon-rx-6950-xt", "tbp") == "335"
    assert spec("amd-radeon-rx-6900-xt", "stream_processors") == "5120"
    assert spec("amd-radeon-rx-6800", "vram_capacity") == "16"
    assert spec("amd-radeon-rx-6700", "vram_capacity") == "10"
    assert spec("amd-radeon-rx-6700-xt", "vram_capacity") == "12"
    assert spec("amd-radeon-rx-6600-xt", "compute_units") == "32"
    assert spec("amd-radeon-rx-6400", "vram_capacity") == "4"


def test_rx6000_variant_handling():
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    slugs = {r["product"]["slug"] for r in records}
    assert "amd-radeon-rx-6700-xt" in slugs
    assert "amd-radeon-rx-6700" in slugs
    assert "amd-radeon-rx-6600-xt" in slugs
    assert "amd-radeon-rx-6600" in slugs
    assert "amd-radeon-rx-6950-xt" in slugs
    assert "amd-radeon-rx-6900-xt" in slugs


def test_rx6000_no_mobile_pro_or_aib_products():
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


def test_rx6000_import_and_idempotency(rx6000_setup):
    first = import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    assert first.errors == 0
    assert first.created == 12
    assert first.updated == 0

    second = import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    assert second.errors == 0
    assert second.created == 0
    assert second.updated == 12


def test_rx6000_imported_products_have_provenance(rx6000_setup):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    for slug in EXPECTED_SLUGS:
        product = Product.query.filter_by(slug=slug).first()
        assert product is not None
        assert product.manufacturer.name == "AMD"
        assert product.family.name == "Radeon RX"
        assert product.generation.name == "RX 6000 Series"
        sources = ProductSource.query.filter_by(product_id=product.id).all()
        assert sources
        assert any("amd.com" in (s.source_url or "") for s in sources)
        segment = Specification.query.filter_by(
            product_id=product.id, key="market_segment"
        ).first()
        assert segment is not None
        assert segment.value == "desktop"


def test_rx6000_generation_filtering(rx6000_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    response = client.get("/api/products?category=gpu&generation=RX+6000+Series")
    assert response.status_code == 200
    slugs = {item["slug"] for item in response.get_json()["data"]}
    for slug in EXPECTED_SLUGS:
        assert slug in slugs


def test_rx6000_amd_and_family_filters(rx6000_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    amd = client.get("/api/products?category=gpu&manufacturer=AMD")
    assert amd.status_code == 200
    assert amd.get_json()["pagination"]["total"] == 12

    family = client.get("/api/products?category=gpu&family=Radeon+RX")
    assert family.status_code == 200
    assert family.get_json()["pagination"]["total"] == 12


def test_rx6000_search_and_compare(rx6000_setup, client):
    import_hardware_from_path(str(CATALOG_FILE), mode=ImportMode.UPSERT)
    for query in (
        "RX 6950 XT",
        "RX 6900 XT",
        "RX 6800 XT",
        "RX 6800",
        "RX 6750 XT",
        "RX 6700 XT",
        "RX 6700",
        "RX 6650 XT",
        "RX 6600 XT",
        "RX 6600",
        "RX 6500 XT",
        "RX 6400",
    ):
        response = client.get("/api/search", query_string={"q": query})
        assert response.status_code == 200
        names = [item["name"] for item in response.get_json()["items"]]
        assert any(query in name for name in names)

    detail = client.get("/api/products/by-slug/amd-radeon-rx-6900-xt")
    assert detail.status_code == 200
    body = detail.get_json()
    assert body["name"] == "AMD Radeon RX 6900 XT"
    assert body.get("sources")
    assert body.get("related_products") is not None

    compare = client.get(
        "/api/compare?products=amd-radeon-rx-6900-xt,amd-radeon-rx-6800-xt"
    )
    assert compare.status_code == 200
    assert len(compare.get_json()["products"]) == 2


def test_rx7000_catalog_still_valid_after_rx6000_builder():
    records = json.loads(RX7000_CATALOG_FILE.read_text(encoding="utf-8"))
    errors, _ = validate_catalog_records(records)
    assert not errors
    assert len(records) == 7


def test_nvidia_catalog_still_valid_after_rx6000_builder():
    records = json.loads(NVIDIA_CATALOG_FILE.read_text(encoding="utf-8"))
    errors, _ = validate_catalog_records(records)
    assert not errors
    assert len(records) == 9


def test_intel_arc_legacy_slug_unchanged():
    from app.data.gpu_slug_policy import LEGACY_GPU_SLUG_MAP
    assert "arc-a770" not in LEGACY_GPU_SLUG_MAP


def test_builder_produces_valid_rx6000_output():
    script = BACKEND_ROOT / "scripts" / "build_gpu_catalog.py"
    subprocess.run([sys.executable, str(script)], cwd=BACKEND_ROOT, check=True)
    records = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    errors, _ = validate_catalog_records(records)
    assert not errors
    assert len(records) == 12
