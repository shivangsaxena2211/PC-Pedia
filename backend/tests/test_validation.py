"""Validation and architecture tests."""

import pytest

from app import db
from app.models import (
    Category, Manufacturer, Family, Series, Generation,
    SpecificationDefinition, Product,
)
from app.utils.validation import (
    ValidationError,
    validate_product_data,
    validate_specifications,
    validate_product_images,
)


@pytest.fixture
def taxonomy(app):
    with app.app_context():
        cpu = Category.query.filter_by(slug="cpu").first()
        gpu = Category(name="GPU", slug="gpu", icon="gpu", display_order=2)
        intel = Manufacturer(name="Intel", slug="intel")
        amd = Manufacturer(name="AMD", slug="amd")
        db.session.add_all([cpu, gpu, intel, amd])
        db.session.flush()

        intel_family = Family(
            name="Core", slug="core", manufacturer_id=intel.id, category_id=cpu.id
        )
        amd_family = Family(
            name="Ryzen", slug="ryzen", manufacturer_id=amd.id, category_id=cpu.id
        )
        db.session.add_all([intel_family, amd_family])
        db.session.flush()

        intel_series = Series(
            name="Core i7", slug="core-i7",
            family_id=intel_family.id, manufacturer_id=intel.id, category_id=cpu.id,
        )
        amd_series = Series(
            name="Ryzen 7", slug="ryzen-7",
            family_id=amd_family.id, manufacturer_id=amd.id, category_id=cpu.id,
        )
        db.session.add_all([intel_series, amd_series])
        db.session.commit()

        yield {
            "cpu": cpu,
            "gpu": gpu,
            "intel": intel,
            "amd": amd,
            "intel_family": intel_family,
            "amd_family": amd_family,
            "intel_series": intel_series,
            "amd_series": amd_series,
        }


def test_taxonomy_mismatch_rejected(taxonomy):
    with pytest.raises(ValidationError) as exc:
        validate_product_data({
            "name": "Bad CPU",
            "manufacturer_id": taxonomy["intel"].id,
            "category_id": taxonomy["cpu"].id,
            "family_id": taxonomy["amd_family"].id,
        })
    assert "family_id" in exc.value.errors


def test_series_manufacturer_mismatch_rejected(taxonomy):
    with pytest.raises(ValidationError) as exc:
        validate_product_data({
            "name": "Bad CPU",
            "manufacturer_id": taxonomy["intel"].id,
            "category_id": taxonomy["cpu"].id,
            "family_id": taxonomy["intel_family"].id,
            "series_id": taxonomy["amd_series"].id,
        })
    assert "series_id" in exc.value.errors


def test_invalid_spec_integer_rejected(taxonomy):
    db.session.add(
        SpecificationDefinition(
            category_id=taxonomy["cpu"].id,
            group_name="Performance",
            key="Cores",
            display_name="Cores",
            data_type="integer",
        )
    )
    db.session.commit()

    with pytest.raises(ValidationError) as exc:
        validate_specifications(taxonomy["cpu"].id, [
            {"key": "Cores", "value": "eight bananas"},
        ])
    assert "integer" in str(exc.value.errors).lower()


def test_invalid_image_type_rejected():
    with pytest.raises(ValidationError):
        validate_product_images([
            {"url": "https://example.com/image.jpg", "image_type": "invalid-type"},
        ])


def test_product_list_excludes_full_image_array(client, app, taxonomy):
    with app.app_context():
        product = Product(
            name="Test CPU",
            slug="test-cpu",
            category_id=taxonomy["cpu"].id,
            manufacturer_id=taxonomy["intel"].id,
            family_id=taxonomy["intel_family"].id,
            status="active",
        )
        db.session.add(product)
        db.session.commit()

    response = client.get("/api/products?category=cpu&limit=10")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) >= 1
    item = data["data"][0]
    assert "primary_image_url" in item
    assert "images" not in item
    assert "specifications" not in item
    assert "quick_specs" in item


def test_product_detail_includes_images(client, app, taxonomy):
    with app.app_context():
        product = Product(
            name="Detail CPU",
            slug="detail-cpu",
            category_id=taxonomy["cpu"].id,
            manufacturer_id=taxonomy["intel"].id,
            status="active",
            image_url="https://example.com/cpu.jpg",
        )
        db.session.add(product)
        db.session.commit()
        product_id = product.id

    response = client.get(f"/api/products/{product_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["image_url"] == "https://example.com/cpu.jpg"
    assert "images" in data
    assert "specifications" in data
