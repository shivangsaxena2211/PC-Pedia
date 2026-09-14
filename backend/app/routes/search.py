from flask import Blueprint, jsonify, request

from app.services.product_service import search_products
from app.utils.helpers import parse_int

search_bp = Blueprint("search", __name__)


@search_bp.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Search query is required", "items": []}), 400

    limit = parse_int(request.args.get("limit"), 20)
    results = search_products(query, limit)
    return jsonify({"query": query, "items": results, "total": len(results)})
