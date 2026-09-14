"""Tests for the hardware import pipeline."""

import json

import pytest

from app import db
from app.models import (
    Category, Manufacturer, Product, Specification, ProductImage,
    SpecificationDefinition, Family,
)
from app.services.import_service import (
    HardwareImportService,
    ImportMode,
    import_hardware,
    validate_import_records,
)


CPU_RECORD = {
    "category": "CPU",
    "manufacturer": "AMD",
    "family": "Ryzen",
    "series": "Ryzen",
    "generation": "Ryzen 7000",
    "product": {
        "name": "AMD Ryzen 7 7800X3D",
        "slug": "ryzen-7-7800x3d-import-test",
        "release_date": "2023-04-06",
        "status": "active",
    },
    "specifications": [
        {"group": "Socket", "key": "socket", "value": "AM5"},
        {"group": "Core Configuration", "key": "cores", "value": "8"},
        {"group": "Core Configuration", "key": "threads", "value": "16"},
    ],
    "images": [],
}

GPU_RECORD = {
    "category": "GPU",
    "manufacturer": "NVIDIA",
    "family": "GeForce",
    "series": "GeForce RTX",
    "generation": "RTX 40 Series",
    "product": {
        "name": "NVIDIA GeForce RTX 4070 SUPER",
        "slug": "rtx-4070-super-import-test",
        "release_date": "2024-01-17",
        "status": "active",
    },
    "specifications": [
        {"group": "General", "key": "Architecture", "value": "Ada Lovelace"},
        {"group": "Compute", "key": "CUDA Cores", "value": "7168"},
        {"group": "Memory", "key": "VRAM", "value": "12", "unit": "GB"},
    ],
    "images": [],
}


@pytest.fixture
def import_catalog(app):
    with app.app_context():
        cpu = Category.query.filter_by(slug="cpu").first()
        if not cpu:
            cpu = Category(name="CPU", slug="cpu", icon="cpu", display_order=1)
            db.session.add(cpu)
        gpu = Category.query.filter_by(slug="gpu").first()
        if not gpu:
            gpu = Category(name="GPU", slug="gpu", icon="gpu", display_order=2)
            db.session.add(gpu)
        db.session.flush()

        for cat, specs in (
            (cpu, [
                ("Socket", "socket", "string"),
                ("Core Configuration", "cores", "integer"),
                ("Core Configuration", "threads", "integer"),
            ]),
            (gpu, [
                ("General", "Architecture", "string"),
                ("Compute", "CUDA Cores", "integer"),
                ("Memory", "VRAM", "string"),
            ]),
        ):
            for group, key, dtype in specs:
                if not SpecificationDefinition.query.filter_by(
                    category_id=cat.id, key=key
                ).first():
                    db.session.add(SpecificationDefinition(
                        category_id=cat.id,
                        group_name=group,
                        key=key,
                        display_name=key,
                        data_type=dtype,
                    ))
        db.session.commit()
        yield {"cpu": cpu, "gpu": gpu}


def test_valid_cpu_import(import_catalog):
    result = import_hardware([CPU_RECORD], mode=ImportMode.UPSERT)
    assert result.created == 1
    assert result.errors == 0
    product = Product.query.filter_by(slug="ryzen-7-7800x3d-import-test").first()
    assert product is not None
    assert Specification.query.filter_by(product_id=product.id).count() == 3


def test_valid_gpu_import(import_catalog):
    result = import_hardware([GPU_RECORD], mode=ImportMode.UPSERT)
    assert result.created == 1
    assert result.errors == 0


def test_duplicate_create_mode_skips(import_catalog):
    first = import_hardware([CPU_RECORD], mode=ImportMode.UPSERT)
    assert first.created == 1

    second = import_hardware([CPU_RECORD], mode=ImportMode.CREATE)
    assert second.skipped == 1
    assert second.created == 0
    assert Product.query.filter_by(slug="ryzen-7-7800x3d-import-test").count() == 1


def test_upsert_updates_existing(import_catalog):
    import_hardware([CPU_RECORD], mode=ImportMode.UPSERT)
    updated_record = {
        **CPU_RECORD,
        "product": {
            **CPU_RECORD["product"],
            "description": "Updated by upsert",
        },
    }
    result = import_hardware([updated_record], mode=ImportMode.UPSERT)
    assert result.updated == 1
    product = Product.query.filter_by(slug="ryzen-7-7800x3d-import-test").first()
    assert product.description == "Updated by upsert"


def test_invalid_taxonomy_rejected(import_catalog):
    bad_record = {
        **CPU_RECORD,
        "manufacturer": "AMD",
        "family": "Core",
        "series": "Core",
        "product": {
            "name": "Invalid AMD Core",
            "slug": "invalid-amd-core",
        },
    }
    result = import_hardware([bad_record], mode=ImportMode.UPSERT)
    assert result.errors == 1
    assert "not valid" in result.details[0].errors[0].lower()


def test_invalid_specification_type(import_catalog):
    bad_record = {
        **CPU_RECORD,
        "product": {
            **CPU_RECORD["product"],
            "slug": "invalid-spec-cpu",
            "name": "Invalid Spec CPU",
        },
        "specifications": [
            {"group": "Core Configuration", "key": "cores", "value": "eight"},
        ],
    }
    result = import_hardware([bad_record], mode=ImportMode.UPSERT)
    assert result.errors == 1
    assert "integer" in result.details[0].errors[0].lower()


def test_invalid_image_url_rejected(import_catalog):
    bad_record = {
        **CPU_RECORD,
        "product": {
            **CPU_RECORD["product"],
            "slug": "invalid-image-cpu",
            "name": "Invalid Image CPU",
        },
        "images": [{"url": "not-a-valid-url", "type": "primary", "is_primary": True}],
    }
    result = import_hardware([bad_record], mode=ImportMode.UPSERT)
    assert result.errors == 1


def test_fallback_svg_url_rejected(import_catalog):
    bad_record = {
        **CPU_RECORD,
        "product": {
            **CPU_RECORD["product"],
            "slug": "fallback-image-cpu",
            "name": "Fallback Image CPU",
        },
        "images": [{
            "url": "/images/hardware/cpu.svg",
            "type": "primary",
            "is_primary": True,
        }],
    }
    result = import_hardware([bad_record], mode=ImportMode.UPSERT)
    assert result.errors == 1
    assert "fallback" in result.details[0].errors[0].lower()


def test_multiple_primary_images_rejected(import_catalog):
    bad_record = {
        **CPU_RECORD,
        "product": {
            **CPU_RECORD["product"],
            "slug": "multi-primary-cpu",
            "name": "Multi Primary CPU",
        },
        "images": [
            {"url": "https://example.com/a.jpg", "is_primary": True},
            {"url": "https://example.com/b.jpg", "is_primary": True},
        ],
    }
    result = import_hardware([bad_record], mode=ImportMode.UPSERT)
    assert result.errors == 1
    assert "multiple" in result.details[0].errors[0].lower()


def test_dry_run_does_not_persist(import_catalog):
    before = Product.query.count()
    result = import_hardware(
        [{
            **CPU_RECORD,
            "product": {
                **CPU_RECORD["product"],
                "slug": "dry-run-only-cpu",
                "name": "Dry Run CPU",
            },
        }],
        dry_run=True,
    )
    assert result.dry_run is True
    assert result.errors == 0
    assert Product.query.count() == before
    assert Product.query.filter_by(slug="dry-run-only-cpu").first() is None


def test_validate_import_records_api_shape(import_catalog):
    result = validate_import_records([CPU_RECORD])
    payload = result.to_dict()
    assert payload["total"] == 1
    assert "details" in payload


def test_transaction_isolation_between_records(import_catalog):
    good = {
        **GPU_RECORD,
        "product": {
            **GPU_RECORD["product"],
            "slug": "isolation-good-gpu",
            "name": "Isolation Good GPU",
        },
    }
    bad = {
        **CPU_RECORD,
        "product": {
            **CPU_RECORD["product"],
            "slug": "isolation-bad-cpu",
            "name": "Isolation Bad CPU",
        },
        "specifications": [
            {"group": "Core Configuration", "key": "cores", "value": "not-a-number"},
        ],
    }
    result = import_hardware([bad, good], mode=ImportMode.UPSERT)
    assert result.errors == 1
    assert result.created == 1
    assert Product.query.filter_by(slug="isolation-good-gpu").first() is not None
    assert Product.query.filter_by(slug="isolation-bad-cpu").first() is None


def test_specifications_merge_without_replace(import_catalog):
    import_hardware([CPU_RECORD], mode=ImportMode.UPSERT)
    partial = {
        **CPU_RECORD,
        "specifications": [
            {"group": "Socket", "key": "socket", "value": "AM5"},
        ],
    }
    import_hardware([partial], mode=ImportMode.UPSERT)
    product = Product.query.filter_by(slug="ryzen-7-7800x3d-import-test").first()
    keys = {spec.key for spec in product.specifications}
    assert "cores" in keys
    assert "threads" in keys


def test_image_import_adds_product_image(import_catalog):
    record = {
        **CPU_RECORD,
        "product": {
            **CPU_RECORD["product"],
            "slug": "image-import-cpu",
            "name": "Image Import CPU",
        },
        "images": [{
            "url": "https://example.com/cpu.jpg",
            "type": "primary",
            "alt_text": "Image Import CPU",
            "is_primary": True,
            "sort_order": 1,
        }],
    }
    result = import_hardware([record], mode=ImportMode.UPSERT)
    assert result.created == 1
    product = Product.query.filter_by(slug="image-import-cpu").first()
    assert product.image_url == "https://example.com/cpu.jpg"
    assert ProductImage.query.filter_by(product_id=product.id).count() == 1


def test_csv_row_conversion():
    row = {
        "category": "CPU",
        "manufacturer": "AMD",
        "family": "Ryzen",
        "series": "Ryzen",
        "generation": "Ryzen 7000",
        "name": "CSV CPU",
        "slug": "csv-cpu",
        "spec_cores": "8",
        "spec_socket": "AM5",
    }
    record = HardwareImportService.csv_row_to_record(row)
    assert record["product"]["name"] == "CSV CPU"
    assert any(spec["key"] == "cores" for spec in record["specifications"])


def test_admin_import_validate_endpoint(client, import_catalog):
    response = client.post(
        "/api/admin/import/validate",
        json=[CPU_RECORD],
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "valid" in data
    assert "summary" in data


def test_admin_import_endpoint(client, import_catalog):
    record = {
        **CPU_RECORD,
        "product": {
            **CPU_RECORD["product"],
            "slug": "admin-import-cpu",
            "name": "Admin Import CPU",
        },
    }
    response = client.post("/api/admin/import?mode=upsert", json=[record])
    assert response.status_code == 200
    data = response.get_json()
    assert data["created"] == 1
    assert Product.query.filter_by(slug="admin-import-cpu").first() is not None
