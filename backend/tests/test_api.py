"""Basic API tests for PC Hardware Database."""

import pytest

from app import create_app, db
from app.models import Category, Manufacturer, Product


@pytest.fixture
def app():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()
        cat = Category(name="CPU", slug="cpu", icon="cpu", display_order=1)
        db.session.add(cat)
        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


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
