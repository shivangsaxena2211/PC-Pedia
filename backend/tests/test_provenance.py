"""Tests for data provenance models and import persistence."""

import pytest

from app import db
from app.models import (
    Category, DataSource, Product, ProductSource, SpecificationDefinition,
)
from app.services.import_service import import_hardware, ImportMode
from app.services.source_service import resolve_or_create_data_source, upsert_product_source


CPU_RECORD = {
    "category": "CPU",
    "manufacturer": "AMD",
    "family": "Ryzen",
    "series": "Ryzen",
    "generation": "Ryzen 7000",
    "source": {
        "name": "AMD official product specifications",
        "url": "https://www.amd.com/en/products/processors/desktops/ryzen/7000-series/amd-ryzen-7-7800x3d.html",
        "date": "2023-04-06",
        "notes": "AMD desktop processor product page",
    },
    "product": {
        "name": "AMD Ryzen 7 7800X3D",
        "slug": "provenance-cpu-test",
        "release_date": "2023-04-06",
        "status": "active",
    },
    "specifications": [
        {"group": "Socket", "key": "socket", "value": "AM5"},
        {"group": "Core Configuration", "key": "cores", "value": "8"},
    ],
    "images": [],
}


@pytest.fixture
def cpu_catalog(app):
    with app.app_context():
        cpu = Category.query.filter_by(slug="cpu").first()
        if not cpu:
            cpu = Category(name="CPU", slug="cpu", icon="cpu", display_order=1)
            db.session.add(cpu)
            db.session.flush()
        for group, key, display, dtype in [
            ("Socket", "socket", "Socket", "string"),
            ("Core Configuration", "cores", "Total Cores", "integer"),
        ]:
            if not SpecificationDefinition.query.filter_by(category_id=cpu.id, key=key).first():
                db.session.add(SpecificationDefinition(
                    category_id=cpu.id,
                    group_name=group,
                    key=key,
                    display_name=display,
                    data_type=dtype,
                ))
        db.session.commit()
        yield cpu


def test_source_creation(cpu_catalog):
    source = resolve_or_create_data_source(
        "AMD official product specifications",
        url="https://www.amd.com/en/products/processors/desktops/ryzen/7000-series/amd-ryzen-7-7800x3d.html",
    )
    assert source.id is not None
    assert source.slug == "amd-official-product-specifications"


def test_duplicate_source_handling(cpu_catalog):
    first = resolve_or_create_data_source("AMD official product specifications")
    second = resolve_or_create_data_source("AMD official product specifications")
    assert first.id == second.id
    assert DataSource.query.count() == 1


def test_source_import_persists(cpu_catalog):
    result = import_hardware([CPU_RECORD], mode=ImportMode.UPSERT)
    assert result.created == 1

    product = Product.query.filter_by(slug="provenance-cpu-test").first()
    assert product is not None
    links = ProductSource.query.filter_by(product_id=product.id).all()
    assert len(links) == 1
    assert links[0].source.name == "AMD official product specifications"
    assert links[0].source_date.isoformat() == "2023-04-06"


def test_source_update_on_upsert(cpu_catalog):
    import_hardware([CPU_RECORD], mode=ImportMode.UPSERT)
    updated = {
        **CPU_RECORD,
        "source": {
            **CPU_RECORD["source"],
            "notes": "Updated source notes",
        },
    }
    result = import_hardware([updated], mode=ImportMode.UPSERT)
    assert result.updated == 1

    product = Product.query.filter_by(slug="provenance-cpu-test").first()
    link = ProductSource.query.filter_by(product_id=product.id).first()
    assert link.notes == "Updated source notes"


def test_product_source_relationship(cpu_catalog):
    from app.models import Manufacturer

    mfr = Manufacturer(name="Intel", slug="intel-provenance")
    db.session.add(mfr)
    db.session.flush()

    product = Product(
        name="Source Link CPU",
        slug="source-link-cpu",
        category_id=cpu_catalog.id,
        manufacturer_id=mfr.id,
        status="active",
    )
    db.session.add(product)
    db.session.flush()

    upsert_product_source(product.id, {
        "name": "Intel ARK",
        "url": "https://www.intel.com",
        "date": "2024-01-01",
    })
    db.session.commit()

    link = ProductSource.query.filter_by(product_id=product.id).first()
    assert link.source.name == "Intel ARK"
