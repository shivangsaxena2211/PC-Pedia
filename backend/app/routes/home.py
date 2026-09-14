from flask import Blueprint, jsonify

from app.models import Manufacturer
from app.services.product_service import get_popular_products, get_latest_products

home_bp = Blueprint("home", __name__)


@home_bp.route("/home")
def home_data():
    popular = [p.to_dict() for p in get_popular_products(8)]
    latest = [p.to_dict() for p in get_latest_products(8)]
    manufacturers = (
        Manufacturer.query.order_by(Manufacturer.name).limit(12).all()
    )

    return jsonify({
        "popular": popular,
        "latest": latest,
        "manufacturers": [m.to_dict() for m in manufacturers],
    })
