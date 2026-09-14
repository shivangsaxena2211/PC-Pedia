"""Consistent API response helpers."""

from flask import jsonify


def paginated_response(data, pagination, extra=None):
    response = {
        "data": data,
        "pagination": {
            "page": pagination["page"],
            "limit": pagination["per_page"],
            "total": pagination["total"],
            "pages": pagination["pages"],
            "has_next": pagination["has_next"],
            "has_prev": pagination["has_prev"],
        },
    }
    if extra:
        response.update(extra)
    return jsonify(response)


def list_response(items, key="data"):
    return jsonify({key: items})


def error_response(message, status=400, errors=None):
    body = {"error": message}
    if errors:
        body["errors"] = errors
    return jsonify(body), status
