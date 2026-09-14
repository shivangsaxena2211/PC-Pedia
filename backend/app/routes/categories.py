from flask import Blueprint, request, jsonify

from app.services.taxonomy_service import (
    get_categories,
    get_category_detail,
    get_families,
    get_series_for_category,
    get_generations_for_category,
    get_specification_definitions,
)
from app.utils.responses import list_response, error_response

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/categories")
def list_categories():
    include_counts = request.args.get("counts", "").lower() in ("1", "true")
    return list_response(get_categories(include_counts=include_counts))


@categories_bp.route("/categories/<slug>")
def get_category(slug):
    category = get_category_detail(slug)
    if not category:
        return error_response("Category not found", 404)
    return jsonify(category)


@categories_bp.route("/categories/<slug>/families")
def category_families(slug):
    manufacturer = request.args.get("manufacturer")
    return list_response(get_families(slug, manufacturer))


@categories_bp.route("/categories/<slug>/series")
def category_series(slug):
    family = request.args.get("family")
    manufacturer = request.args.get("manufacturer")
    return list_response(get_series_for_category(slug, family, manufacturer))


@categories_bp.route("/categories/<slug>/generations")
def category_generations(slug):
    series = request.args.get("series")
    family = request.args.get("family")
    return list_response(get_generations_for_category(slug, series, family))


@categories_bp.route("/specification-definitions")
def spec_definitions():
    category = request.args.get("category")
    if not category:
        return error_response("category parameter is required")
    return list_response(get_specification_definitions(category))


@categories_bp.route("/categories/<slug>/specification-definitions")
def category_spec_definitions(slug):
    return list_response(get_specification_definitions(slug))
