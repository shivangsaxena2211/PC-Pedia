from flask import Blueprint, jsonify, request

from app.models import Manufacturer, Series, Generation

manufacturers_bp = Blueprint("manufacturers", __name__)


@manufacturers_bp.route("/manufacturers")
def list_manufacturers():
    category_slug = request.args.get("category")
    query = Manufacturer.query

    if category_slug:
        from app.services.product_service import get_category_by_slug
        from app.models import Product

        category = get_category_by_slug(category_slug)
        if category:
            query = (
                query.join(Product)
                .filter(Product.category_id == category.id)
                .distinct()
            )

    manufacturers = query.order_by(Manufacturer.display_order, Manufacturer.name).all()
    items = [m.to_dict() for m in manufacturers]
    return jsonify({"data": items, "items": items})


@manufacturers_bp.route("/manufacturers/<slug>")
def get_manufacturer(slug):
    manufacturer = Manufacturer.query.filter_by(slug=slug).first_or_404()
    return jsonify(manufacturer.to_dict())


@manufacturers_bp.route("/series")
def list_series():
    manufacturer_id = request.args.get("manufacturer_id")
    category_id = request.args.get("category_id")
    query = Series.query

    if manufacturer_id:
        query = query.filter_by(manufacturer_id=manufacturer_id)
    if category_id:
        query = query.filter_by(category_id=category_id)

    series_list = query.order_by(Series.display_order, Series.name).all()
    items = [s.to_dict() for s in series_list]
    return jsonify({"data": items, "items": items})


@manufacturers_bp.route("/generations")
def list_generations():
    series_id = request.args.get("series_id")
    query = Generation.query

    if series_id:
        query = query.filter_by(series_id=series_id)

    generations = query.order_by(Generation.display_order, Generation.name).all()
    items = [g.to_dict() for g in generations]
    return jsonify({"data": items, "items": items})
