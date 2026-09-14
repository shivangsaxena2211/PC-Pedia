"""Basic API tests for PC Hardware Database."""

import pytest

from app import db
from app.models import Category, Manufacturer, Product


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


def test_categories(client):
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) >= 1


def test_search_empty_query(client):
    response = client.get("/api/search")
    assert response.status_code == 400


def test_search_no_results(client):
    response = client.get("/api/search?q=nonexistentproduct12345")
    assert response.status_code == 200
    data = response.get_json()
    assert data["items"] == []


def test_products_pagination(client):
    response = client.get("/api/products?category=cpu&page=1&limit=10")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert "pagination" in data
    assert data["pagination"]["page"] == 1


def test_compare_validation(client):
    response = client.get("/api/compare?products=onlyone")
    assert response.status_code == 400


def test_compare_different_categories(client, app):
    with app.app_context():
        cat_cpu = Category.query.filter_by(slug="cpu").first()
        cat_gpu = Category(slug="gpu", name="GPU", display_order=2)
        db.session.add(cat_gpu)
        mfr = Manufacturer(name="Test", slug="test")
        db.session.add(mfr)
        db.session.flush()

        p1 = Product(
            name="CPU1", slug="cpu1", category_id=cat_cpu.id,
            manufacturer_id=mfr.id, status="active",
        )
        p2 = Product(
            name="GPU1", slug="gpu1", category_id=cat_gpu.id,
            manufacturer_id=mfr.id, status="active",
        )
        db.session.add_all([p1, p2])
        db.session.commit()

    response = client.get("/api/compare?products=cpu1,gpu1")
    assert response.status_code == 400
    data = response.get_json()
    assert "different categories" in data["error"].lower()


def test_product_by_path_not_found(client):
    response = client.get("/api/products/cpu/amd/nonexistent-product")
    assert response.status_code == 404


def test_products_pagination_limit(client, app):
    with app.app_context():
        cat = Category.query.filter_by(slug="cpu").first()
        mfr = Manufacturer(name="Paginate Mfr", slug="paginate-mfr")
        db.session.add(mfr)
        db.session.flush()
        for i in range(15):
            db.session.add(Product(
                name=f"CPU {i}",
                slug=f"cpu-{i}",
                category_id=cat.id,
                manufacturer_id=mfr.id,
                status="active",
            ))
        db.session.commit()

    response = client.get("/api/products?category=cpu&page=1&limit=5")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) == 5
    assert data["pagination"]["limit"] == 5
    assert data["pagination"]["total"] >= 15


def test_search_by_product_name(client, app):
    with app.app_context():
        cat = Category.query.filter_by(slug="cpu").first()
        mfr = Manufacturer(name="AMD", slug="amd-search")
        db.session.add(mfr)
        db.session.flush()
        db.session.add(Product(
            name="AMD Ryzen 7 7800X3D",
            slug="ryzen-7-7800x3d",
            category_id=cat.id,
            manufacturer_id=mfr.id,
            architecture="Zen 4",
            status="active",
        ))
        db.session.commit()

    response = client.get("/api/search?q=7800X3D")
    assert response.status_code == 200
    data = response.get_json()
    names = [item["name"] for item in data["items"]]
    assert any("7800X3D" in name for name in names)
