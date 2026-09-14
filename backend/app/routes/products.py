from flask import Blueprint, request, jsonify

from app.schemas.product_schema import product_detail, grouped_specifications
from app.services.product_service import (
    get_products,
    get_product_by_id,
    get_product_by_slug,
    get_product_by_path,
    get_related_products,
    get_filter_options,
    CATEGORY_SLUG_MAP,
    CATEGORY_API_ENDPOINTS,
)
from app.utils.responses import paginated_response, error_response

products_bp = Blueprint("products", __name__)

CATEGORY_ENDPOINTS = list(CATEGORY_API_ENDPOINTS.values())


def _category_products(category_key):
    slug = CATEGORY_SLUG_MAP.get(category_key, category_key)
    result = get_products(slug, request.args.to_dict())
    filters = get_filter_options(slug)
    return paginated_response(result["data"], result["pagination"], extra={"filters": filters})


for endpoint in CATEGORY_ENDPOINTS:
    products_bp.add_url_rule(
        f"/{endpoint}",
        endpoint,
        lambda cat=endpoint: _category_products(cat),
        methods=["GET"],
    )


@products_bp.route("/products")
def list_products():
    category = request.args.get("category")
    result = get_products(category, request.args.to_dict())
    extra = {}
    if category:
        extra["filters"] = get_filter_options(category)
    return paginated_response(result["data"], result["pagination"], extra=extra or None)


@products_bp.route("/products/<int:product_id>")
def get_product_by_id_route(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return error_response("Product not found", 404)

    data = product_detail(product)
    data["specification_groups"] = grouped_specifications(product)
    data["related_products"] = [p.to_dict() for p in get_related_products(product)]
    data["url_path"] = product.url_path
    return jsonify(data)


@products_bp.route("/products/by-slug/<slug>")
def get_product_by_slug_route(slug):
    product = get_product_by_slug(slug)
    if not product:
        return error_response("Product not found", 404)

    data = product_detail(product)
    data["specification_groups"] = grouped_specifications(product)
    data["related_products"] = [p.to_dict() for p in get_related_products(product)]
    data["url_path"] = product.url_path
    return jsonify(data)


@products_bp.route("/products/<category>/<manufacturer>/<slug>")
def get_product_by_path_route(category, manufacturer, slug):
    product = get_product_by_path(category, manufacturer, slug)
    if not product:
        return error_response("Product not found", 404)

    data = product_detail(product)
    data["specification_groups"] = grouped_specifications(product)
    data["related_products"] = [p.to_dict() for p in get_related_products(product)]
    data["url_path"] = product.url_path
    return jsonify(data)


# Legacy endpoint - kept for backward compatibility
@products_bp.route("/products/<slug>")
def get_product_legacy(slug):
    if slug.isdigit():
        return get_product_by_id_route(int(slug))
    product = get_product_by_slug(slug)
    if not product:
        return error_response("Product not found", 404)

    data = product_detail(product)
    data["specification_groups"] = grouped_specifications(product)
    data["related_products"] = [p.to_dict() for p in get_related_products(product)]
    data["url_path"] = product.url_path
    return jsonify(data)
