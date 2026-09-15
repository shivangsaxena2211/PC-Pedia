"""CPU catalog, taxonomy, filtering, and batch import tests."""

import json
from pathlib import Path

import pytest

from app import db
from app.models import Category, Product, SpecificationDefinition
from app.services.import_service import import_hardware, import_hardware_from_path, ImportMode
from seed_data.cpu_spec_definitions import CPU_SPECS

CATALOG_ROOT = Path(__file__).resolve().parents[1] / "data" / "catalog" / "cpu"


@pytest.fixture
def cpu_setup(app):
    with app.app_context():
        cpu = Category.query.filter_by(slug="cpu").first()
        if not cpu:
            cpu = Category(name="CPU", slug="cpu", icon="cpu", display_order=1)
            db.session.add(cpu)
            db.session.flush()

        for group, key, display, dtype, unit, filt, comp, req, order in CPU_SPECS:
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
    assert count >= 48


def test_valid_intel_taxonomy_record(cpu_setup):
    record = {
        "category": "CPU",
        "manufacturer": "Intel",
        "family": "Core",
        "series": "Core",
        "generation": "14th Generation",
        "product": {"name": "Taxonomy Intel CPU", "slug": "taxonomy-intel-cpu"},
        "specifications": [{"group": "Socket", "key": "socket", "value": "LGA 1700"}],
        "images": [],
    }
    result = import_hardware([record], mode=ImportMode.UPSERT)
    assert result.errors == 0


def test_valid_core_ultra_taxonomy_record(cpu_setup):
    record = {
        "category": "CPU",
        "manufacturer": "Intel",
        "family": "Core Ultra",
        "series": "Core Ultra",
        "generation": "Series 1",
        "product": {"name": "Taxonomy Core Ultra CPU", "slug": "taxonomy-core-ultra-cpu"},
        "specifications": [],
        "images": [],
    }
    result = import_hardware([record], mode=ImportMode.UPSERT)
    assert result.errors == 0


def test_valid_amd_ryzen_7000_taxonomy_record(cpu_setup):
    record = {
        "category": "CPU",
        "manufacturer": "AMD",
        "family": "Ryzen",
        "series": "Ryzen",
        "generation": "Ryzen 7000",
        "product": {"name": "Taxonomy Ryzen CPU", "slug": "taxonomy-ryzen-7000-cpu"},
        "specifications": [{"group": "Socket", "key": "socket", "value": "AM5"}],
        "images": [],
    }
    result = import_hardware([record], mode=ImportMode.UPSERT)
    assert result.errors == 0


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


def test_intel_14th_gen_batch_import(cpu_setup):
    result = import_hardware_from_path(
        "data/catalog/cpu/intel/core/14th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    assert result.errors == 0
    assert result.created + result.updated >= 13
    assert Product.query.filter_by(slug="intel-core-i9-14900k").first() is not None


def test_amd_ryzen_7000_batch_import(cpu_setup):
    result = import_hardware_from_path(
        "data/catalog/cpu/amd/ryzen/7000/desktop.json",
        mode=ImportMode.UPSERT,
    )
    assert result.errors == 0
    assert result.created + result.updated >= 12
    assert Product.query.filter_by(slug="amd-ryzen-7-7800x3d").first() is not None


def test_duplicate_cpu_upsert_is_idempotent(cpu_setup):
    import_hardware_from_path(
        "data/catalog/cpu/amd/ryzen/7000/desktop.json",
        mode=ImportMode.UPSERT,
    )
    first_count = Product.query.filter_by(slug="amd-ryzen-7-7800x3d").count()
    result = import_hardware_from_path(
        "data/catalog/cpu/amd/ryzen/7000/desktop.json",
        mode=ImportMode.UPSERT,
    )
    second_count = Product.query.filter_by(slug="amd-ryzen-7-7800x3d").count()
    assert first_count == 1
    assert second_count == 1
    assert result.created == 0
    assert result.updated >= 1


def test_catalog_batch_dry_run(cpu_setup):
    result = import_hardware_from_path(
        "data/catalog/cpu/intel/core/14th-gen/desktop.json",
        dry_run=True,
    )
    assert result.dry_run is True
    assert result.valid_records == 13
    assert result.invalid_records == 0


def test_catalog_records_have_sources():
    intel_path = CATALOG_ROOT / "intel" / "core" / "14th-gen" / "desktop.json"
    records = json.loads(intel_path.read_text(encoding="utf-8"))
    assert len(records) == 13
    for record in records:
        assert record.get("source", {}).get("url")
        assert record.get("source", {}).get("name") == "Intel ARK"
        assert record["images"] == []


def test_cpu_filtering_by_socket(client, cpu_setup):
    import_hardware_from_path(
        "data/catalog/cpu/amd/ryzen/7000/desktop.json",
        mode=ImportMode.UPSERT,
    )
    response = client.get("/api/cpus?spec_socket=AM5&limit=50")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) >= 1


def test_cpu_search(client, cpu_setup):
    import_hardware_from_path(
        "data/catalog/cpu/intel/core/14th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    for query in ("14900K", "Core i9-14900K"):
        response = client.get(f"/api/search?q={query}")
        assert response.status_code == 200
        results = response.get_json()
        items = results.get("items", results.get("data", []))
        assert any("14900" in item.get("name", "") for item in items)


def test_cpu_product_detail_includes_sources(client, cpu_setup):
    import_hardware_from_path(
        "data/catalog/cpu/amd/ryzen/7000/desktop.json",
        mode=ImportMode.UPSERT,
    )
    response = client.get("/api/products/cpu/amd/amd-ryzen-7-7800x3d")
    assert response.status_code == 200
    payload = response.get_json()
    assert "sources" in payload
    assert len(payload["sources"]) >= 1
    assert payload.get("related_products") is not None


def test_intel_13th_gen_batch_import(cpu_setup):
    result = import_hardware_from_path(
        "data/catalog/cpu/intel/core/13th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    assert result.errors == 0
    assert result.created + result.updated >= 13
    assert Product.query.filter_by(slug="intel-core-i9-13900k").first() is not None


def test_intel_12th_gen_batch_import(cpu_setup):
    result = import_hardware_from_path(
        "data/catalog/cpu/intel/core/12th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    assert result.errors == 0
    assert result.created + result.updated >= 12
    assert Product.query.filter_by(slug="intel-core-i9-12900k").first() is not None


def test_intel_product_detail_page(client, cpu_setup):
    import_hardware_from_path(
        "data/catalog/cpu/intel/core/14th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    response = client.get("/api/products/cpu/intel/intel-core-i9-14900k")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["name"] == "Intel Core i9-14900K"
    assert payload.get("specification_groups")
    assert len(payload.get("sources", [])) >= 1


def test_intel_11th_gen_batch_import(cpu_setup):
    result = import_hardware_from_path(
        "data/catalog/cpu/intel/core/11th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    assert result.errors == 0
    assert result.created + result.updated >= 19
    assert Product.query.filter_by(slug="intel-core-i9-11900k").first() is not None


def test_intel_10th_gen_batch_import(cpu_setup):
    result = import_hardware_from_path(
        "data/catalog/cpu/intel/core/10th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    assert result.errors == 0
    assert result.created + result.updated >= 24
    assert Product.query.filter_by(slug="intel-core-i9-10900k").first() is not None


def test_intel_10th_and_11th_gen_taxonomy(cpu_setup):
    for generation in ("10th Generation", "11th Generation"):
        record = {
            "category": "CPU",
            "manufacturer": "Intel",
            "family": "Core",
            "series": "Core",
            "generation": generation,
            "product": {
                "name": f"Taxonomy Intel {generation}",
                "slug": f"taxonomy-intel-{generation.split()[0].lower()}-gen",
            },
            "specifications": [{"group": "Socket", "key": "socket", "value": "LGA 1200"}],
            "images": [],
        }
        result = import_hardware([record], mode=ImportMode.UPSERT)
        assert result.errors == 0


def test_intel_11th_gen_search(client, cpu_setup):
    import_hardware_from_path(
        "data/catalog/cpu/intel/core/11th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    for query in ("11900K", "11700K", "11600K"):
        response = client.get(f"/api/search?q={query}")
        assert response.status_code == 200
        results = response.get_json()
        items = results.get("items", results.get("data", []))
        assert any(query.replace("K", "") in item.get("name", "").replace("-", "") for item in items)


def test_intel_10th_gen_search(client, cpu_setup):
    import_hardware_from_path(
        "data/catalog/cpu/intel/core/10th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    for query in ("10900K", "10700K", "10600K"):
        response = client.get(f"/api/search?q={query}")
        assert response.status_code == 200
        results = response.get_json()
        items = results.get("items", results.get("data", []))
        assert any(query.replace("K", "") in item.get("name", "").replace("-", "") for item in items)


def test_intel_11th_gen_product_detail(client, cpu_setup):
    import_hardware_from_path(
        "data/catalog/cpu/intel/core/11th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    response = client.get("/api/products/cpu/intel/intel-core-i9-11900k")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["name"] == "Intel Core i9-11900K"
    assert payload.get("generation") == "11th Generation"
    assert len(payload.get("sources", [])) >= 1
    assert payload.get("related_products") is not None


def test_intel_9th_gen_batch_import(cpu_setup):
    result = import_hardware_from_path(
        "data/catalog/cpu/intel/core/9th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    assert result.errors == 0
    assert result.created + result.updated >= 26
    assert Product.query.filter_by(slug="intel-core-i9-9900k").first() is not None


def test_intel_8th_gen_batch_import(cpu_setup):
    result = import_hardware_from_path(
        "data/catalog/cpu/intel/core/8th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    assert result.errors == 0
    assert result.created + result.updated >= 15
    assert Product.query.filter_by(slug="intel-core-i7-8700k").first() is not None


def test_intel_8th_and_9th_gen_taxonomy(cpu_setup):
    for generation in ("8th Generation", "9th Generation"):
        record = {
            "category": "CPU",
            "manufacturer": "Intel",
            "family": "Core",
            "series": "Core",
            "generation": generation,
            "product": {
                "name": f"Taxonomy Intel {generation}",
                "slug": f"taxonomy-intel-{generation.split()[0].lower()}-gen",
            },
            "specifications": [{"group": "Socket", "key": "socket", "value": "LGA 1151"}],
            "images": [],
        }
        result = import_hardware([record], mode=ImportMode.UPSERT)
        assert result.errors == 0


def test_intel_9th_gen_search(client, cpu_setup):
    import_hardware_from_path(
        "data/catalog/cpu/intel/core/9th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    for query in ("9900K", "9700K", "9600K"):
        response = client.get(f"/api/search?q={query}")
        assert response.status_code == 200
        results = response.get_json()
        items = results.get("items", results.get("data", []))
        assert any(query.replace("K", "") in item.get("name", "").replace("-", "") for item in items)


def test_intel_8th_gen_search(client, cpu_setup):
    import_hardware_from_path(
        "data/catalog/cpu/intel/core/8th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    for query in ("8700K", "8600K"):
        response = client.get(f"/api/search?q={query}")
        assert response.status_code == 200
        results = response.get_json()
        items = results.get("items", results.get("data", []))
        assert any(query.replace("K", "") in item.get("name", "").replace("-", "") for item in items)


def test_intel_9th_gen_product_detail(client, cpu_setup):
    import_hardware_from_path(
        "data/catalog/cpu/intel/core/9th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    response = client.get("/api/products/cpu/intel/intel-core-i9-9900k")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["name"] == "Intel Core i9-9900K"
    assert payload.get("generation") == "9th Generation"
    assert len(payload.get("sources", [])) >= 1
    assert payload.get("related_products") is not None


def test_intel_8th_gen_product_detail(client, cpu_setup):
    import_hardware_from_path(
        "data/catalog/cpu/intel/core/8th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    response = client.get("/api/products/cpu/intel/intel-core-i7-8700k")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["name"] == "Intel Core i7-8700K"
    assert payload.get("generation") == "8th Generation"
    assert len(payload.get("sources", [])) >= 1


def test_intel_10th_gen_product_detail(client, cpu_setup):
    import_hardware_from_path(
        "data/catalog/cpu/intel/core/10th-gen/desktop.json",
        mode=ImportMode.UPSERT,
    )
    response = client.get("/api/products/cpu/intel/intel-core-i9-10900k")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["name"] == "Intel Core i9-10900K"
    assert payload.get("generation") == "10th Generation"
    assert len(payload.get("sources", [])) >= 1
