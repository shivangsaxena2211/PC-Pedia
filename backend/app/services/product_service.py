from collections import defaultdict

from sqlalchemy import or_, asc, desc
from sqlalchemy.orm import joinedload

from app import db
from app.models import (
    Category,
    Manufacturer,
    Family,
    Series,
    Generation,
    Product,
    Specification,
    ProductImage,
    ProductSource,
    SpecificationDefinition,
)
from app.utils.helpers import parse_int
from app.utils.images import resolve_primary_image_url


SORT_FIELDS = {
    "name": Product.name,
    "release_date": Product.release_date,
    "created_at": Product.created_at,
    "updated_at": Product.updated_at,
}

CATEGORY_SLUG_MAP = {
    "cpu": "cpu",
    "cpus": "cpu",
    "gpu": "gpu",
    "gpus": "gpu",
    "ram": "ram",
    "motherboard": "motherboards",
    "motherboards": "motherboards",
    "ssd": "ssd",
    "ssds": "ssd",
    "psu": "psu",
    "psus": "psu",
    "cooler": "coolers",
    "coolers": "coolers",
    "aio": "aio",
    "aios": "aio",
    "fan": "fans",
    "fans": "fans",
    "case": "cases",
    "cases": "cases",
}

CATEGORY_API_ENDPOINTS = {
    "cpu": "cpus",
    "gpu": "gpus",
    "ram": "ram",
    "motherboards": "motherboards",
    "ssd": "ssds",
    "psu": "psus",
    "coolers": "coolers",
    "aio": "aios",
    "fans": "fans",
    "cases": "cases",
}

QUICK_SPEC_LIMIT = 6


def get_category_by_slug(slug: str) -> Category | None:
    normalized = CATEGORY_SLUG_MAP.get(slug.lower(), slug.lower())
    return Category.query.filter_by(slug=normalized).first()


def _product_list_options():
    """Eager-load taxonomy relationships only (safe for listings)."""
    return [
        joinedload(Product.manufacturer),
        joinedload(Product.category),
        joinedload(Product.family),
        joinedload(Product.series),
        joinedload(Product.generation),
    ]


def _product_detail_options():
    """Eager-load full product detail data."""
    return [
        *_product_list_options(),
        joinedload(Product.specifications),
        joinedload(Product.images),
        joinedload(Product.benchmarks),
        joinedload(Product.product_sources).joinedload(ProductSource.source),
    ]


def _product_compare_options():
    return [
        *_product_list_options(),
        joinedload(Product.specifications),
    ]


def _batch_load_quick_specs(product_ids: list[int], limit: int = QUICK_SPEC_LIMIT) -> dict[int, dict]:
    if not product_ids:
        return {}

    specs = (
        Specification.query.filter(Specification.product_id.in_(product_ids))
        .order_by(Specification.product_id, Specification.sort_order, Specification.id)
        .all()
    )

    category_ids = {
        row.category_id
        for row in Product.query.filter(Product.id.in_(product_ids)).all()
    }
    definitions = SpecificationDefinition.query.filter(
        SpecificationDefinition.category_id.in_(category_ids)
    ).all()
    def_map = {(d.category_id, d.key): d for d in definitions}

    result: dict[int, dict] = defaultdict(dict)
    product_categories = {
        p.id: p.category_id for p in Product.query.filter(Product.id.in_(product_ids)).all()
    }
    for spec in specs:
        bucket = result[spec.product_id]
        if len(bucket) >= limit:
            continue
        defn = def_map.get((product_categories.get(spec.product_id), spec.key))
        label = defn.display_name if defn else spec.key
        value = spec.value
        if spec.unit:
            value = f"{value} {spec.unit}"
        bucket[label] = value
    return result


def _batch_load_product_images(product_ids: list[int]) -> dict[int, list[ProductImage]]:
    if not product_ids:
        return {}

    images = (
        ProductImage.query.filter(ProductImage.product_id.in_(product_ids))
        .order_by(
            ProductImage.product_id,
            ProductImage.is_primary.desc(),
            ProductImage.sort_order,
            ProductImage.id,
        )
        .all()
    )

    grouped: dict[int, list[ProductImage]] = defaultdict(list)
    for image in images:
        grouped[image.product_id].append(image)
    return grouped


def products_to_list_dicts(products: list[Product]) -> list[dict]:
    """Serialize products for cards/listings without N+1 spec/image queries."""
    if not products:
        return []

    product_ids = [p.id for p in products]
    quick_specs_map = _batch_load_quick_specs(product_ids)
    images_map = _batch_load_product_images(product_ids)

    items = []
    for product in products:
        primary_url = resolve_primary_image_url(
            product.image_url,
            images_map.get(product.id, []),
        )
        items.append(
            product.to_dict(
                list_view=True,
                quick_specs=quick_specs_map.get(product.id, {}),
                primary_image_url_override=primary_url,
            )
        )
    return items


def build_product_query(category_slug: str | None = None, active_only: bool = True):
    query = Product.query.options(*_product_list_options())

    if active_only:
        query = query.filter(Product.status == "active")

    if category_slug:
        category = get_category_by_slug(category_slug)
        if category:
            query = query.filter(Product.category_id == category.id)

    return query


def apply_filters(query, params: dict):
    manufacturer = params.get("manufacturer")
    family = params.get("family")
    series = params.get("series")
    generation = params.get("generation")
    search = params.get("search") or params.get("q")
    architecture = params.get("architecture")
    is_popular = params.get("popular")
    status = params.get("status")

    if manufacturer:
        query = query.join(Manufacturer).filter(
            or_(
                Manufacturer.slug == manufacturer.lower(),
                Manufacturer.name.ilike(f"%{manufacturer}%"),
            )
        )

    if family:
        query = query.join(Family).filter(
            or_(
                Family.slug == family.lower(),
                Family.name.ilike(f"%{family}%"),
            )
        )

    if series:
        query = query.join(Series).filter(
            or_(
                Series.slug == series.lower(),
                Series.name.ilike(f"%{series}%"),
            )
        )

    if generation:
        query = query.join(Generation).filter(
            or_(
                Generation.slug == generation.lower(),
                Generation.name.ilike(f"%{generation}%"),
            )
        )

    if architecture:
        query = query.filter(Product.architecture.ilike(f"%{architecture}%"))

    if search:
        search_term = f"%{search}%"
        query = (
            query.outerjoin(Manufacturer)
            .outerjoin(Family, Product.family_id == Family.id)
            .outerjoin(Series, Product.series_id == Series.id)
            .outerjoin(Generation, Product.generation_id == Generation.id)
            .filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.architecture.ilike(search_term),
                    Product.description.ilike(search_term),
                    Manufacturer.name.ilike(search_term),
                    Family.name.ilike(search_term),
                    Series.name.ilike(search_term),
                    Generation.name.ilike(search_term),
                )
            )
        )

    if is_popular is not None and str(is_popular).lower() in ("1", "true", "yes"):
        query = query.filter(Product.is_popular.is_(True))

    if status:
        query = query.filter(Product.status == status)

    spec_filters = {k[5:]: v for k, v in params.items() if k.startswith("spec_") and v}
    for spec_key, spec_value in spec_filters.items():
        alias = db.aliased(Specification)
        query = query.join(alias, Product.specifications).filter(
            alias.key == spec_key,
            alias.value.ilike(f"%{spec_value}%"),
        )

    return query


def apply_sorting(query, sort: str | None, order: str | None = None):
    if not sort:
        return query.order_by(desc(Product.release_date), Product.name)

    descending = sort.startswith("-")
    field_name = sort.lstrip("-")
    column = SORT_FIELDS.get(field_name, Product.name)

    if order:
        descending = order.lower() == "desc"

    if descending:
        return query.order_by(desc(column))
    return query.order_by(asc(column))


def paginate_query(query, page: int = 1, limit: int = 24, list_view: bool = True):
    page = max(1, parse_int(page, 1))
    limit = min(max(1, parse_int(limit, 24)), 100)

    pagination = query.paginate(page=page, per_page=limit, error_out=False)

    items = (
        products_to_list_dicts(pagination.items)
        if list_view
        else [p.to_dict() for p in pagination.items]
    )

    pagination_data = {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }

    return {
        "data": items,
        "items": items,
        "pagination": pagination_data,
    }


def get_products(category_slug: str | None, params: dict):
    query = build_product_query(category_slug)
    query = apply_filters(query, params)
    query = apply_sorting(query, params.get("sort"), params.get("order"))
    return paginate_query(query, params.get("page"), params.get("limit"))


def get_product_by_id(product_id: int) -> Product | None:
    return (
        Product.query.options(*_product_detail_options())
        .filter_by(id=product_id)
        .first()
    )


def get_product_by_slug(slug: str) -> Product | None:
    return (
        Product.query.options(*_product_detail_options())
        .filter_by(slug=slug)
        .first()
    )


def get_product_by_path(
    category_slug: str, manufacturer_slug: str, product_slug: str
) -> Product | None:
    category = get_category_by_slug(category_slug)
    if not category:
        return None

    return (
        Product.query.options(*_product_detail_options())
        .join(Manufacturer)
        .filter(
            Product.category_id == category.id,
            Manufacturer.slug == manufacturer_slug,
            Product.slug == product_slug,
        )
        .first()
    )


def get_related_products(product: Product, limit: int = 4):
    if not product.category_id:
        return []

    query = (
        Product.query.options(*_product_list_options())
        .filter(
            Product.category_id == product.category_id,
            Product.id != product.id,
            Product.status == "active",
        )
    )

    if product.family_id:
        query = query.filter(Product.family_id == product.family_id)
    elif product.manufacturer_id:
        query = query.filter(Product.manufacturer_id == product.manufacturer_id)

    return query.order_by(desc(Product.is_popular), Product.release_date).limit(limit).all()


def search_products(query: str, limit: int = 20):
    if not query or len(query.strip()) < 1:
        return []

    search_term = f"%{query.strip()}%"
    results = (
        Product.query.options(*_product_list_options())
        .outerjoin(Manufacturer)
        .outerjoin(Family, Product.family_id == Family.id)
        .outerjoin(Series, Product.series_id == Series.id)
        .outerjoin(Generation, Product.generation_id == Generation.id)
        .filter(
            Product.status == "active",
            or_(
                Product.name.ilike(search_term),
                Product.architecture.ilike(search_term),
                Manufacturer.name.ilike(search_term),
                Family.name.ilike(search_term),
                Series.name.ilike(search_term),
                Generation.name.ilike(search_term),
            ),
        )
        .order_by(desc(Product.is_popular), Product.name)
        .limit(min(limit, 50))
        .all()
    )

    list_dicts = products_to_list_dicts(results)
    search_items = []
    for product, data in zip(results, list_dicts):
        search_items.append(
            {
                "id": product.id,
                "name": product.name,
                "slug": product.slug,
                "url_path": product.url_path,
                "category": product.category.name if product.category else None,
                "category_slug": product.category.slug if product.category else None,
                "manufacturer": product.manufacturer.name if product.manufacturer else None,
                "manufacturer_slug": product.manufacturer.slug if product.manufacturer else None,
                "family": product.family.name if product.family else None,
                "series": product.series.name if product.series else None,
                "generation": product.generation.name if product.generation else None,
                "architecture": product.architecture,
                "image_url": product.image_url,
                "primary_image_url": data.get("primary_image_url"),
                "quick_specs": data.get("quick_specs", {}),
            }
        )
    return search_items


def compare_products(slugs: list[str], product_ids: list[int] | None = None):
    if not slugs and not product_ids:
        return None, "No products specified"

    query = Product.query.options(*_product_compare_options())

    if product_ids:
        products = query.filter(Product.id.in_(product_ids)).all()
    else:
        products = query.filter(Product.slug.in_(slugs)).all()
        if len(products) != len(slugs):
            found = {p.slug for p in products}
            missing = [s for s in slugs if s not in found]
            return None, f"Products not found: {', '.join(missing)}"

    if len(products) < 2:
        return None, "At least 2 products are required for comparison"

    categories = {p.category_id for p in products}
    if len(categories) > 1:
        return None, "Cannot compare products from different categories"

    category_id = products[0].category_id
    comparable_defs = {
        d.key: d
        for d in SpecificationDefinition.query.filter_by(
            category_id=category_id, comparable=True
        ).all()
    }

    all_spec_keys = set()
    for product in products:
        for spec in product.specifications:
            if comparable_defs and spec.key not in comparable_defs:
                continue
            all_spec_keys.add((spec.group_name, spec.key))

    comparison_specs = []
    for group_name, key in sorted(all_spec_keys):
        display_name = key
        if key in comparable_defs:
            display_name = comparable_defs[key].display_name

        row = {
            "group": group_name,
            "key": key,
            "display_name": display_name,
            "values": {},
        }
        values = []
        for product in products:
            value = next(
                (
                    s.value
                    for s in product.specifications
                    if s.group_name == group_name and s.key == key
                ),
                "—",
            )
            row["values"][product.slug] = value
            values.append(value)

        row["all_same"] = len(set(values)) <= 1
        comparison_specs.append(row)

    return {
        "category": products[0].category.name if products[0].category else None,
        "category_slug": products[0].category.slug if products[0].category else None,
        "products": products_to_list_dicts(products),
        "comparison": comparison_specs,
    }, None


def get_popular_products(limit: int = 8):
    return (
        Product.query.options(*_product_list_options())
        .filter(Product.is_popular.is_(True), Product.status == "active")
        .order_by(desc(Product.release_date))
        .limit(limit)
        .all()
    )


def get_latest_products(limit: int = 8):
    return (
        Product.query.options(*_product_list_options())
        .filter(Product.status == "active")
        .order_by(desc(Product.created_at))
        .limit(limit)
        .all()
    )


def get_filter_options(category_slug: str):
    from app.services.taxonomy_service import get_specification_definitions

    category = get_category_by_slug(category_slug)
    if not category:
        return {}

    manufacturers = (
        db.session.query(Manufacturer)
        .join(Product)
        .filter(Product.category_id == category.id)
        .distinct()
        .order_by(Manufacturer.display_order, Manufacturer.name)
        .all()
    )

    families = (
        db.session.query(Family)
        .filter(Family.category_id == category.id)
        .order_by(Family.display_order, Family.name)
        .all()
    )

    series_list = (
        db.session.query(Series)
        .join(Family)
        .filter(Family.category_id == category.id)
        .distinct()
        .order_by(Series.display_order, Series.name)
        .all()
    )

    generations = (
        db.session.query(Generation)
        .join(Series)
        .join(Family)
        .filter(Family.category_id == category.id)
        .distinct()
        .order_by(Generation.display_order, Generation.name)
        .all()
    )

    spec_definitions = get_specification_definitions(category_slug)
    filterable_specs = [d for d in spec_definitions if d.get("filterable")]

    return {
        "manufacturers": [m.to_dict() for m in manufacturers],
        "families": [f.to_dict() for f in families],
        "series": [s.to_dict() for s in series_list],
        "generations": [g.to_dict() for g in generations],
        "specification_definitions": spec_definitions,
        "filterable_specifications": filterable_specs,
    }
