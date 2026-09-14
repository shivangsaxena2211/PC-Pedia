from flask import Blueprint, jsonify, request

from app.services.product_service import compare_products

compare_bp = Blueprint("compare", __name__)


@compare_bp.route("/compare")
def compare():
    products_param = request.args.get("products", "")
    if not products_param:
        return jsonify({"error": "products parameter is required"}), 400

    slugs = [s.strip() for s in products_param.split(",") if s.strip()]
    if len(slugs) < 2:
        return jsonify({"error": "At least 2 products are required for comparison"}), 400
    if len(slugs) > 4:
        return jsonify({"error": "Maximum 4 products can be compared"}), 400

    result, error = compare_products(slugs)
    if error:
        return jsonify({"error": error}), 400

    return jsonify(result)
