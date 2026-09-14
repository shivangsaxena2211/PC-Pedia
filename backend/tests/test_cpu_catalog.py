"""CPU catalog, taxonomy, and filtering tests."""

import pytest

from app import db
from app.models import Category, Manufacturer, Product, SpecificationDefinition
from app.services.import_service import import_hardware, import_hardware_from_path, ImportMode
from seed_data.cpu_spec_definitions import CPU_SPECS


@pytest.fixture
def cpu_setup(app):
    with app.app_context():
        cpu = Category.query.filter_by(slug="cpu").first()
        if not cpu:
            cpu = Category(name="CPU", slug="cpu", icon="cpu", display_order=1)
            db.session.add(cpu)
            db.session.flush()

        for group, key, display, dtype, unit, filt, comp, req, order in CPU_SPECS[:10]:
            existing = SpecificationDefinition.query.filter_by(
                category_id=cpu.id, key=key
            ).first()
            if not existing:
                db.session.add(SpecificationDefinition(
                    category_id=cpu.id,
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
        yield cpu


def test_cpu_specification_definitions_exist(cpu_setup):
    count = SpecificationDefinition.query.filter_by(category_id=cpu_setup.id).count()
    assert count >= 10


def test_cpu_catalog_import(client, cpu_setup):
    result = import_hardware_from_path(
        "data/catalog/cpu/amd/ryzen/example.json",
        mode=ImportMode.UPSERT,
    )
    assert result.errors == 0
    assert result.created >= 1
    assert Product.query.filter_by(slug="amd-ryzen-7-7800x3d").first() is not None


def test_cpu_filtering_by_socket(client, cpu_setup):
    import_hardware_from_path(
        "data/catalog/cpu/amd/ryzen/example.json",
        mode=ImportMode.UPSERT,
    )
    response = client.get("/api/cpus?spec_socket=AM5&limit=50")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) >= 1


def test_cpu_product_detail_includes_sources(client, cpu_setup):
    import_hardware_from_path(
        "data/catalog/cpu/amd/ryzen/example.json",
        mode=ImportMode.UPSERT,
    )
    response = client.get("/api/products/cpu/amd/amd-ryzen-7-7800x3d")
    assert response.status_code == 200
    payload = response.get_json()
    assert "sources" in payload
    assert len(payload["sources"]) >= 1


def test_invalid_cpu_taxonomy_rejected(cpu_setup):
    bad_record = {
        "category": "CPU",
        "manufacturer": "AMD",
        "family": "Core",
        "series": "Core",
        "product": {"name": "Bad CPU", "slug": "bad-cpu-taxonomy"},
        "specifications": [],
        "images": [],
    }
    result = import_hardware([bad_record], mode=ImportMode.UPSERT)
    assert result.errors == 1
