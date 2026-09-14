"""Tests for seed/catalog CPU product reconciliation."""

import pytest

from app import db
from app.models import Category, Manufacturer, Product, Specification
from app.services.product_reconciliation_service import reconcile_legacy_cpu_slugs


@pytest.fixture
def intel_cpu_setup(app):
    with app.app_context():
        cpu = Category.query.filter_by(slug="cpu").first()
        if not cpu:
            cpu = Category(name="CPU", slug="cpu", icon="cpu", display_order=1)
            db.session.add(cpu)
            db.session.flush()
        intel = Manufacturer.query.filter_by(slug="intel").first()
        if not intel:
            intel = Manufacturer(name="Intel", slug="intel")
            db.session.add(intel)
            db.session.flush()
        yield {"cpu": cpu, "intel": intel}


def test_merge_legacy_slug_into_canonical(intel_cpu_setup):
    cpu = intel_cpu_setup["cpu"]
    intel = intel_cpu_setup["intel"]

    demo = Product(
        name="Intel Core i9-14900K",
        slug="core-i9-14900k",
        category_id=cpu.id,
        manufacturer_id=intel.id,
        status="active",
    )
    canonical = Product(
        name="Intel Core i9-14900K",
        slug="intel-core-i9-14900k",
        category_id=cpu.id,
        manufacturer_id=intel.id,
        status="active",
    )
    db.session.add_all([demo, canonical])
    db.session.flush()
    db.session.add(Specification(
        product_id=demo.id, group_name="Socket", key="socket", value="LGA 1700", sort_order=0
    ))
    db.session.commit()

    result = reconcile_legacy_cpu_slugs()
    assert result.merged == 1
    assert Product.query.filter_by(slug="core-i9-14900k").first() is None
    assert Product.query.filter_by(slug="intel-core-i9-14900k").count() == 1


def test_rename_legacy_slug_when_canonical_missing(intel_cpu_setup):
    cpu = intel_cpu_setup["cpu"]
    intel = intel_cpu_setup["intel"]

    demo = Product(
        name="Intel Core i7-14700K",
        slug="core-i7-14700k",
        category_id=cpu.id,
        manufacturer_id=intel.id,
        status="active",
    )
    db.session.add(demo)
    db.session.commit()

    result = reconcile_legacy_cpu_slugs()
    assert result.renamed == 1
    assert Product.query.filter_by(slug="intel-core-i7-14700k").first() is not None


def test_search_no_duplicate_legacy_and_canonical(client, intel_cpu_setup):
    cpu = intel_cpu_setup["cpu"]
    intel = intel_cpu_setup["intel"]

    db.session.add(Product(
        name="Intel Core i9-14900K",
        slug="core-i9-14900k",
        category_id=cpu.id,
        manufacturer_id=intel.id,
        status="active",
        is_popular=True,
    ))
    db.session.add(Product(
        name="Intel Core i9-14900K",
        slug="intel-core-i9-14900k",
        category_id=cpu.id,
        manufacturer_id=intel.id,
        status="active",
        is_popular=True,
    ))
    db.session.commit()

    reconcile_legacy_cpu_slugs()

    response = client.get("/api/search?q=14900K")
    assert response.status_code == 200
    items = response.get_json()["items"]
    slugs = [item["slug"] for item in items if "14900" in item["name"]]
    assert slugs.count("intel-core-i9-14900k") == 1
    assert "core-i9-14900k" not in slugs
