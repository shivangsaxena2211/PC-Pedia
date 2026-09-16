"""Tests for seed/catalog GPU product reconciliation."""

import pytest

from app import db
from app.data.gpu_slug_policy import LEGACY_GPU_SLUG_MAP
from app.models import Category, Manufacturer, Product, ProductSource, Specification
from app.models.data_source import DataSource
from app.services.product_reconciliation_service import reconcile_legacy_gpu_slugs


@pytest.fixture
def nvidia_gpu_setup(app):
    with app.app_context():
        gpu = Category.query.filter_by(slug="gpu").first()
        if not gpu:
            gpu = Category(name="GPU", slug="gpu", icon="gpu", display_order=2)
            db.session.add(gpu)
            db.session.flush()
        nvidia = Manufacturer.query.filter_by(slug="nvidia").first()
        if not nvidia:
            nvidia = Manufacturer(name="NVIDIA", slug="nvidia")
            db.session.add(nvidia)
            db.session.flush()
        yield {"gpu": gpu, "nvidia": nvidia}


def test_legacy_gpu_slug_map_covers_known_duplicates():
    assert LEGACY_GPU_SLUG_MAP["rtx-4090"] == "nvidia-geforce-rtx-4090"
    assert LEGACY_GPU_SLUG_MAP["rtx-4070-super"] == "nvidia-geforce-rtx-4070-super"


def test_merge_legacy_gpu_slug_into_canonical(nvidia_gpu_setup):
    gpu = nvidia_gpu_setup["gpu"]
    nvidia = nvidia_gpu_setup["nvidia"]

    demo = Product(
        name="NVIDIA GeForce RTX 4090",
        slug="rtx-4090",
        category_id=gpu.id,
        manufacturer_id=nvidia.id,
        status="active",
        is_popular=True,
    )
    canonical = Product(
        name="NVIDIA GeForce RTX 4090",
        slug="nvidia-geforce-rtx-4090",
        category_id=gpu.id,
        manufacturer_id=nvidia.id,
        status="active",
        is_popular=True,
    )
    db.session.add_all([demo, canonical])
    db.session.flush()

    source = DataSource(
        name="NVIDIA official product specifications",
        slug="nvidia-official-product-specifications-test",
        url="https://www.nvidia.com",
    )
    db.session.add(source)
    db.session.flush()
    db.session.add(ProductSource(
        product_id=canonical.id,
        source_id=source.id,
        source_url="https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4090/",
    ))
    db.session.add(Specification(
        product_id=canonical.id,
        group_name="Compute",
        key="cuda_cores",
        value="16384",
        sort_order=0,
    ))
    db.session.add(Specification(
        product_id=demo.id,
        group_name="General",
        key="Architecture",
        value="Ada Lovelace",
        sort_order=0,
    ))
    db.session.commit()

    result = reconcile_legacy_gpu_slugs()
    assert result.merged == 1
    assert result.errors == []
    assert Product.query.filter_by(slug="rtx-4090").first() is None
    kept = Product.query.filter_by(slug="nvidia-geforce-rtx-4090").one()
    assert ProductSource.query.filter_by(product_id=kept.id).count() == 1
    assert Specification.query.filter_by(
        product_id=kept.id, key="cuda_cores"
    ).count() == 1


def test_gpu_reconciliation_idempotent(nvidia_gpu_setup):
    gpu = nvidia_gpu_setup["gpu"]
    nvidia = nvidia_gpu_setup["nvidia"]

    db.session.add(Product(
        name="NVIDIA GeForce RTX 4070 SUPER",
        slug="rtx-4070-super",
        category_id=gpu.id,
        manufacturer_id=nvidia.id,
        status="active",
    ))
    db.session.add(Product(
        name="NVIDIA GeForce RTX 4070 SUPER",
        slug="nvidia-geforce-rtx-4070-super",
        category_id=gpu.id,
        manufacturer_id=nvidia.id,
        status="active",
    ))
    db.session.commit()

    first = reconcile_legacy_gpu_slugs()
    assert first.merged == 1

    second = reconcile_legacy_gpu_slugs()
    assert second.merged == 0
    assert second.skipped >= 1
    assert Product.query.filter_by(slug="nvidia-geforce-rtx-4070-super").count() == 1


def test_search_no_duplicate_legacy_and_canonical_gpu(client, nvidia_gpu_setup):
    gpu = nvidia_gpu_setup["gpu"]
    nvidia = nvidia_gpu_setup["nvidia"]

    db.session.add(Product(
        name="NVIDIA GeForce RTX 4090",
        slug="rtx-4090",
        category_id=gpu.id,
        manufacturer_id=nvidia.id,
        status="active",
        is_popular=True,
    ))
    db.session.add(Product(
        name="NVIDIA GeForce RTX 4090",
        slug="nvidia-geforce-rtx-4090",
        category_id=gpu.id,
        manufacturer_id=nvidia.id,
        status="active",
        is_popular=True,
    ))
    db.session.commit()

    reconcile_legacy_gpu_slugs()

    response = client.get("/api/search?q=RTX+4090")
    assert response.status_code == 200
    items = response.get_json()["items"]
    slugs = [item["slug"] for item in items if "4090" in item["name"]]
    assert slugs.count("nvidia-geforce-rtx-4090") == 1
    assert "rtx-4090" not in slugs


def test_non_duplicate_demo_gpus_not_in_legacy_map():
    assert "rx-7900-xtx" not in LEGACY_GPU_SLUG_MAP
    assert "arc-a770" not in LEGACY_GPU_SLUG_MAP
