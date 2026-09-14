"""Backend validation helpers for API requests."""

from app import db
from app.models import (
    Category, Manufacturer, Family, Series, Generation, Product,
    SpecificationDefinition,
)
from app.models.specification_definition import DATA_TYPES


class ValidationError(Exception):
    def __init__(self, message: str, errors: dict | None = None):
        super().__init__(message)
        self.message = message
        self.errors = errors or {}


def validate_required(data: dict, fields: list[str]) -> dict:
    errors = {}
    for field in fields:
        if not data.get(field):
            errors[field] = "This field is required"
    if errors:
        raise ValidationError("Validation failed", errors)
    return data


def validate_slug_unique(model, slug: str, **filters):
    query = model.query.filter_by(slug=slug, **filters)
    existing = query.first()
    if existing:
        raise ValidationError(f"Slug '{slug}' already exists for this scope")


def validate_foreign_key(model, field_id: int, field_name: str):
    if field_id and not model.query.get(field_id):
        raise ValidationError(f"Invalid {field_name}: ID {field_id} not found")


def validate_product_data(data: dict, product_id: int | None = None):
    errors = {}
    required = ["name", "manufacturer_id", "category_id"]
    for field in required:
        if not data.get(field):
            errors[field] = "Required"

    if errors:
        raise ValidationError("Validation failed", errors)

    validate_foreign_key(Category, data["category_id"], "category")
    validate_foreign_key(Manufacturer, data["manufacturer_id"], "manufacturer")

    if data.get("family_id"):
        validate_foreign_key(Family, data["family_id"], "family")
    if data.get("series_id"):
        validate_foreign_key(Series, data["series_id"], "series")
    if data.get("generation_id"):
        validate_foreign_key(Generation, data["generation_id"], "generation")

    slug = data.get("slug") or data["name"].lower().replace(" ", "-")
    q = Product.query.filter_by(
        category_id=data["category_id"],
        manufacturer_id=data["manufacturer_id"],
        slug=slug,
    )
    if product_id:
        q = q.filter(Product.id != product_id)
    if q.first():
        raise ValidationError(f"Product with slug '{slug}' already exists in this category/manufacturer")

    if data.get("status") and data["status"] not in ("active", "draft", "discontinued"):
        raise ValidationError("Invalid status. Must be active, draft, or discontinued")

    return data


def validate_specifications(category_id: int, specs: list[dict]):
    definitions = SpecificationDefinition.query.filter_by(category_id=category_id).all()
    def_map = {d.key: d for d in definitions}
    errors = []

    for spec in specs:
        key = spec.get("key")
        value = spec.get("value")
        if not key or value is None:
            errors.append(f"Specification missing key or value: {spec}")
            continue

        defn = def_map.get(key)
        if defn and defn.required and not str(value).strip():
            errors.append(f"Required specification '{key}' is empty")

        if defn and defn.data_type == "integer":
            try:
                int(str(value).replace(",", ""))
            except ValueError:
                errors.append(f"Specification '{key}' must be an integer")

        if defn and defn.data_type == "decimal":
            try:
                float(str(value).replace(",", ""))
            except ValueError:
                errors.append(f"Specification '{key}' must be a decimal number")

        if defn and defn.data_type == "boolean":
            if str(value).lower() not in ("true", "false", "yes", "no", "1", "0"):
                errors.append(f"Specification '{key}' must be a boolean")

    if errors:
        raise ValidationError("Specification validation failed", {"specifications": errors})
