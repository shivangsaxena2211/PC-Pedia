"""Pytest fixtures for PC Hardware Database."""

import pytest

from app import create_app, db
from app.models import Category, Manufacturer, Product
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
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
