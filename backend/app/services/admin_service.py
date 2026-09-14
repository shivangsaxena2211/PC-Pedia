from datetime import datetime

from app import db
from app.models import (
    Category,
    Manufacturer,
    Family,
    Series,
    Generation,
    Product,
    Specification,
    SpecificationDefinition,
    Benchmark,
    ProductImage,
)
from app.models.product_image import IMAGE_TYPES
from app.utils.helpers import slugify
from app.utils.validation import (
    ValidationError,
    validate_product_data,
    validate_specifications,
)


def create_manufacturer(data: dict):
    manufacturer = Manufacturer(
        name=data["name"],
        slug=data.get("slug") or slugify(data["name"]),
        logo_url=data.get("logo_url"),
        website=data.get("website"),
        description=data.get("description"),
        display_order=data.get("display_order", 0),
    )
    db.session.add(manufacturer)
    db.session.commit()
    return manufacturer


def create_category(data: dict):
    category = Category(
        name=data["name"],
        slug=data.get("slug") or slugify(data["name"]),
        description=data.get("description"),
        icon=data.get("icon"),
        display_order=data.get("display_order", 0),
    )
    db.session.add(category)
    db.session.commit()
    return category


def create_family(data: dict):
    family = Family(
        name=data["name"],
        slug=data.get("slug") or slugify(data["name"]),
        manufacturer_id=data["manufacturer_id"],
        category_id=data["category_id"],
        description=data.get("description"),
        display_order=data.get("display_order", 0),
    )
    db.session.add(family)
    db.session.commit()
    return family


def create_series(data: dict):
    family_id = data.get("family_id")
    manufacturer_id = data.get("manufacturer_id")
    category_id = data.get("category_id")

    if family_id:
        family = Family.query.get(family_id)
        if family:
            manufacturer_id = family.manufacturer_id
            category_id = family.category_id

    series = Series(
        name=data["name"],
        slug=data.get("slug") or slugify(data["name"]),
        family_id=family_id,
        manufacturer_id=manufacturer_id,
        category_id=category_id,
        description=data.get("description"),
        display_order=data.get("display_order", 0),
    )
    db.session.add(series)
    db.session.commit()
    return series


def create_generation(data: dict):
    release_date = data.get("release_date")
    if release_date and isinstance(release_date, str):
        release_date = datetime.strptime(release_date, "%Y-%m-%d").date()

    generation = Generation(
        name=data["name"],
        slug=data.get("slug") or slugify(data["name"]),
        series_id=data["series_id"],
        architecture=data.get("architecture"),
        release_year=data.get("release_year"),
        release_date=release_date,
        description=data.get("description"),
        display_order=data.get("display_order", 0),
    )
    db.session.add(generation)
    db.session.commit()
    return generation


def create_specification_definition(data: dict):
    defn = SpecificationDefinition(
        category_id=data["category_id"],
        group_name=data.get("group_name", "General"),
        key=data["key"],
        display_name=data.get("display_name") or data["key"],
        data_type=data.get("data_type", "string"),
        unit=data.get("unit"),
        filterable=data.get("filterable", False),
        comparable=data.get("comparable", True),
        required=data.get("required", False),
        display_order=data.get("display_order", 0),
        enum_values=data.get("enum_values"),
    )
    db.session.add(defn)
    db.session.commit()
    return defn


def _save_product_images(product: Product, images: list[dict]):
    if images is None:
        return
    ProductImage.query.filter_by(product_id=product.id).delete()
    for i, img in enumerate(images):
        url = (img.get("url") or "").strip()
        if not url:
            continue
        image_type = img.get("image_type", "primary")
        if image_type not in IMAGE_TYPES:
            image_type = "primary"
        db.session.add(
            ProductImage(
                product_id=product.id,
                url=url,
                alt_text=img.get("alt_text") or product.name,
                image_type=image_type,
                is_primary=img.get("is_primary", image_type == "primary"),
                sort_order=img.get("sort_order", i),
            )
        )


def create_product(data: dict):
    validate_product_data(data)
    if data.get("specifications"):
        validate_specifications(data["category_id"], data["specifications"])

    release_date = data.get("release_date")
    if release_date and isinstance(release_date, str):
        release_date = datetime.strptime(release_date, "%Y-%m-%d").date()

    product = Product(
        name=data["name"],
        slug=data.get("slug") or slugify(data["name"]),
        manufacturer_id=data["manufacturer_id"],
        category_id=data["category_id"],
        family_id=data.get("family_id"),
        series_id=data.get("series_id"),
        generation_id=data.get("generation_id"),
        architecture=data.get("architecture"),
        description=data.get("description"),
        release_date=release_date,
        image_url=data.get("image_url"),
        status=data.get("status", "active"),
        is_popular=data.get("is_popular", False),
    )
    db.session.add(product)
    db.session.flush()

    for i, spec in enumerate(data.get("specifications", [])):
        db.session.add(
            Specification(
                product_id=product.id,
                group_name=spec.get("group_name") or spec.get("group", "General"),
                key=spec["key"],
                value=str(spec["value"]),
                unit=spec.get("unit"),
                sort_order=spec.get("sort_order", i),
            )
        )

    for bench in data.get("benchmarks", []):
        db.session.add(
            Benchmark(
                product_id=product.id,
                name=bench["name"],
                score=bench.get("score"),
                unit=bench.get("unit"),
                source=bench.get("source"),
                notes=bench.get("notes"),
            )
        )

    if data.get("images"):
        _save_product_images(product, data["images"])

    if data.get("source"):
        from app.services.source_service import upsert_product_source
        upsert_product_source(product.id, data["source"])

    db.session.commit()
    return product


def update_product(product_id: int, data: dict):
    product = Product.query.get_or_404(product_id)
    validate_product_data({**product.to_dict(), **data}, product_id=product_id)

    for field in (
        "name", "slug", "manufacturer_id", "category_id", "family_id",
        "series_id", "generation_id", "architecture", "description",
        "image_url", "is_popular", "status",
    ):
        if field in data:
            setattr(product, field, data[field])

    if "release_date" in data:
        rd = data["release_date"]
        if rd and isinstance(rd, str):
            product.release_date = datetime.strptime(rd, "%Y-%m-%d").date()
        else:
            product.release_date = rd

    if "specifications" in data:
        validate_specifications(product.category_id, data["specifications"])
        Specification.query.filter_by(product_id=product.id).delete()
        for i, spec in enumerate(data["specifications"]):
            db.session.add(
                Specification(
                    product_id=product.id,
                    group_name=spec.get("group_name") or spec.get("group", "General"),
                    key=spec["key"],
                    value=str(spec["value"]),
                    unit=spec.get("unit"),
                    sort_order=spec.get("sort_order", i),
                )
            )

    if "images" in data:
        _save_product_images(product, data["images"])

    if data.get("source"):
        from app.services.source_service import upsert_product_source
        upsert_product_source(product.id, data["source"])

    db.session.commit()
    return product


def delete_product(product_id: int):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
