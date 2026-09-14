from flask import Blueprint, jsonify, request

from app.models import (
    Category, Manufacturer, Family, Series, Generation, Product,
    SpecificationDefinition,
)
from app.services import admin_service
from app.services.import_service import HardwareImportService
from app.utils.validation import ValidationError
from app.utils.responses import error_response

admin_bp = Blueprint("admin", __name__)


def _handle_validation(fn):
    try:
        return fn()
    except ValidationError as e:
        return error_response(e.message, 400, e.errors)


@admin_bp.route("/dashboard")
def dashboard():
    return jsonify({
        "products": Product.query.count(),
        "categories": Category.query.count(),
        "manufacturers": Manufacturer.query.count(),
        "families": Family.query.count(),
        "series": Series.query.count(),
        "generations": Generation.query.count(),
        "specification_definitions": SpecificationDefinition.query.count(),
    })


@admin_bp.route("/manufacturers", methods=["GET", "POST"])
def admin_manufacturers():
    if request.method == "GET":
        items = Manufacturer.query.order_by(Manufacturer.display_order, Manufacturer.name).all()
        return jsonify({"data": [m.to_dict() for m in items]})

    data = request.get_json()
    if not data or not data.get("name"):
        return error_response("name is required")

    return _handle_validation(lambda: (
        jsonify(admin_service.create_manufacturer(data).to_dict()), 201
    ))


@admin_bp.route("/categories", methods=["GET", "POST"])
def admin_categories():
    if request.method == "GET":
        items = Category.query.order_by(Category.display_order, Category.name).all()
        return jsonify({"data": [c.to_dict() for c in items]})

    data = request.get_json()
    if not data or not data.get("name"):
        return error_response("name is required")

    return _handle_validation(lambda: (
        jsonify(admin_service.create_category(data).to_dict()), 201
    ))


@admin_bp.route("/families", methods=["GET", "POST"])
def admin_families():
    if request.method == "GET":
        items = Family.query.order_by(Family.display_order, Family.name).all()
        return jsonify({"data": [f.to_dict() for f in items]})

    data = request.get_json()
    required = ["name", "manufacturer_id", "category_id"]
    if not data or not all(data.get(f) for f in required):
        return error_response(f"Required fields: {', '.join(required)}")

    return _handle_validation(lambda: (
        jsonify(admin_service.create_family(data).to_dict()), 201
    ))


@admin_bp.route("/series", methods=["GET", "POST"])
def admin_series():
    if request.method == "GET":
        items = Series.query.order_by(Series.display_order, Series.name).all()
        return jsonify({"data": [s.to_dict() for s in items]})

    data = request.get_json()
    if not data or not data.get("name"):
        return error_response("name is required")
    if not data.get("family_id") and not (data.get("manufacturer_id") and data.get("category_id")):
        return error_response("family_id or (manufacturer_id + category_id) required")

    return _handle_validation(lambda: (
        jsonify(admin_service.create_series(data).to_dict()), 201
    ))


@admin_bp.route("/generations", methods=["GET", "POST"])
def admin_generations():
    if request.method == "GET":
        items = Generation.query.order_by(Generation.display_order, Generation.name).all()
        return jsonify({"data": [g.to_dict() for g in items]})

    data = request.get_json()
    if not data or not data.get("name") or not data.get("series_id"):
        return error_response("name and series_id are required")

    return _handle_validation(lambda: (
        jsonify(admin_service.create_generation(data).to_dict()), 201
    ))


@admin_bp.route("/specification-definitions", methods=["GET", "POST"])
def admin_spec_definitions():
    if request.method == "GET":
        category_id = request.args.get("category_id")
        query = SpecificationDefinition.query
        if category_id:
            query = query.filter_by(category_id=category_id)
        items = query.order_by(
            SpecificationDefinition.group_name,
            SpecificationDefinition.display_order,
        ).all()
        return jsonify({"data": [d.to_dict() for d in items]})

    data = request.get_json()
    if not data or not data.get("category_id") or not data.get("key"):
        return error_response("category_id and key are required")

    return _handle_validation(lambda: (
        jsonify(admin_service.create_specification_definition(data).to_dict()), 201
    ))


@admin_bp.route("/products", methods=["GET", "POST"])
def admin_products():
    if request.method == "GET":
        items = Product.query.order_by(Product.name).all()
        return jsonify({"data": [p.to_dict() for p in items]})

    data = request.get_json()
    required = ["name", "manufacturer_id", "category_id"]
    if not data or not all(data.get(f) for f in required):
        return error_response(f"Required fields: {', '.join(required)}")

    return _handle_validation(lambda: (
        jsonify(admin_service.create_product(data).to_dict(include_specs=True)), 201
    ))


@admin_bp.route("/products/<int:product_id>", methods=["GET", "PUT", "DELETE"])
def admin_product_detail(product_id):
    product = Product.query.get(product_id)
    if not product:
        return error_response("Product not found", 404)

    if request.method == "GET":
        return jsonify(product.to_dict(include_specs=True))

    if request.method == "PUT":
        data = request.get_json()
        return _handle_validation(lambda: jsonify(
            admin_service.update_product(product_id, data).to_dict(include_specs=True)
        ))

    admin_service.delete_product(product_id)
    return jsonify({"message": "Product deleted"}), 200


@admin_bp.route("/import", methods=["POST"])
def admin_import():
    data = request.get_json()
    if not data or not isinstance(data, list):
        return error_response("Expected JSON array of records")

    service = HardwareImportService()
    result = service.import_batch(data)
    return jsonify(result.to_dict())
