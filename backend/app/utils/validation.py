"""Backend validation helpers for API requests."""

import json
from datetime import datetime

from app import db
from app.models import (
    Category, Manufacturer, Family, Series, Generation, Product,
    SpecificationDefinition,
)
from app.models.product_image import IMAGE_TYPES
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
    if field_id and not db.session.get(model, field_id):
        raise ValidationError(f"Invalid {field_name}: ID {field_id} not found")


def validate_taxonomy_consistency(data: dict):
    """Ensure family/series/generation belong to the selected product hierarchy."""
    errors = {}
    category_id = data.get("category_id")
    manufacturer_id = data.get("manufacturer_id")

    family = None
    series = None

    if data.get("family_id"):
        family = db.session.get(Family, data["family_id"])
        if not family:
            errors["family_id"] = "Family not found"
        elif family.category_id != category_id:
            errors["family_id"] = "Family does not belong to the selected category"
        elif family.manufacturer_id != manufacturer_id:
            errors["family_id"] = "Family does not belong to the selected manufacturer"

    if data.get("series_id"):
        series = db.session.get(Series, data["series_id"])
        if not series:
            errors["series_id"] = "Series not found"
        elif series.category_id != category_id:
            errors["series_id"] = "Series does not belong to the selected category"
        elif series.manufacturer_id != manufacturer_id:
            errors["series_id"] = "Series does not belong to the selected manufacturer"
        elif data.get("family_id") and series.family_id != data["family_id"]:
            errors["series_id"] = "Series does not belong to the selected family"
        elif not data.get("family_id") and family and series.family_id != family.id:
            errors["series_id"] = "Series does not belong to the selected family"

    if data.get("generation_id"):
        generation = db.session.get(Generation, data["generation_id"])
        if not generation:
            errors["generation_id"] = "Generation not found"
        elif data.get("series_id") and generation.series_id != data["series_id"]:
            errors["generation_id"] = "Generation does not belong to the selected series"
        elif not data.get("series_id") and series and generation.series_id != series.id:
            errors["generation_id"] = "Generation does not belong to the selected series"

    if errors:
        raise ValidationError("Taxonomy validation failed", errors)


def validate_product_images(images: list[dict] | None):
    if not images:
        return

    errors = []
    for index, image in enumerate(images):
        image_type = image.get("image_type", "primary")
        if image_type not in IMAGE_TYPES:
            errors.append(
                f"Image {index + 1}: invalid image_type '{image_type}'. "
                f"Allowed: {', '.join(IMAGE_TYPES)}"
            )
        url = (image.get("url") or "").strip()
        if not url:
            errors.append(f"Image {index + 1}: url is required")

    if errors:
        raise ValidationError("Image validation failed", {"images": errors})


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

    validate_taxonomy_consistency(data)
    validate_product_images(data.get("images"))

    slug = data.get("slug") or data["name"].lower().replace(" ", "-")
    q = Product.query.filter_by(
        category_id=data["category_id"],
        manufacturer_id=data["manufacturer_id"],
        slug=slug,
    )
    if product_id:
        q = q.filter(Product.id != product_id)
    if q.first():
        raise ValidationError(
            f"Product with slug '{slug}' already exists in this category/manufacturer"
        )

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

        if not defn:
            continue

        if defn.data_type not in DATA_TYPES:
            continue

        if defn.data_type == "integer":
            try:
                int(str(value).replace(",", ""))
            except ValueError:
                errors.append(f"Specification '{key}' must be an integer")

        elif defn.data_type == "decimal":
            try:
                float(str(value).replace(",", ""))
            except ValueError:
                errors.append(f"Specification '{key}' must be a decimal number")

        elif defn.data_type == "boolean":
            if str(value).lower() not in ("true", "false", "yes", "no", "1", "0"):
                errors.append(f"Specification '{key}' must be a boolean")

        elif defn.data_type == "date":
            try:
                datetime.fromisoformat(str(value)[:10])
            except ValueError:
                errors.append(f"Specification '{key}' must be a valid date (YYYY-MM-DD)")

        elif defn.data_type == "enum" and defn.enum_values:
            try:
                allowed = json.loads(defn.enum_values)
            except json.JSONDecodeError:
                allowed = []
            if allowed and str(value) not in allowed:
                errors.append(
                    f"Specification '{key}' must be one of: {', '.join(allowed)}"
                )

    if errors:
        raise ValidationError("Specification validation failed", {"specifications": errors})
