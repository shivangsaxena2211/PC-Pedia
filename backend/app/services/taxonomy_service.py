"""Taxonomy query service for categories, families, series, generations."""

from sqlalchemy.orm import joinedload

from app.models import Category, Manufacturer, Family, Series, Generation, Product
from app.services.product_service import get_category_by_slug


def get_categories(include_counts=False):
    cats = Category.query.order_by(Category.display_order, Category.name).all()
    return [c.to_dict(include_counts=include_counts) for c in cats]


def get_category_detail(slug: str):
    category = get_category_by_slug(slug)
    if not category:
        return None
    return category.to_dict(include_counts=True)


def get_manufacturers_for_category(category_slug: str | None = None):
    query = Manufacturer.query
    if category_slug:
        category = get_category_by_slug(category_slug)
        if category:
            query = (
                query.join(Product)
                .filter(Product.category_id == category.id)
                .distinct()
            )
    manufacturers = query.order_by(Manufacturer.display_order, Manufacturer.name).all()
    return [m.to_dict() for m in manufacturers]


def get_families(category_slug: str, manufacturer_slug: str | None = None):
    category = get_category_by_slug(category_slug)
    if not category:
        return []

    query = Family.query.filter_by(category_id=category.id).options(
        joinedload(Family.manufacturer)
    )
    if manufacturer_slug:
        query = query.join(Manufacturer).filter(Manufacturer.slug == manufacturer_slug)

    families = query.order_by(Family.display_order, Family.name).all()
    return [f.to_dict() for f in families]


def get_series_for_category(
    category_slug: str,
    family_slug: str | None = None,
    manufacturer_slug: str | None = None,
):
    category = get_category_by_slug(category_slug)
    if not category:
        return []

    query = (
        Series.query.join(Family)
        .filter(Family.category_id == category.id)
        .options(joinedload(Series.family))
    )

    if family_slug:
        query = query.filter(Family.slug == family_slug)
    if manufacturer_slug:
        query = query.join(Manufacturer).filter(Manufacturer.slug == manufacturer_slug)

    series_list = query.order_by(Series.display_order, Series.name).all()
    return [s.to_dict() for s in series_list]


def get_generations_for_category(
    category_slug: str,
    series_slug: str | None = None,
    family_slug: str | None = None,
):
    category = get_category_by_slug(category_slug)
    if not category:
        return []

    query = (
        Generation.query.join(Series)
        .join(Family)
        .filter(Family.category_id == category.id)
        .options(joinedload(Generation.series))
    )

    if series_slug:
        query = query.filter(Series.slug == series_slug)
    if family_slug:
        query = query.filter(Family.slug == family_slug)

    generations = query.order_by(Generation.display_order, Generation.name).all()
    return [g.to_dict() for g in generations]


def get_specification_definitions(category_slug: str):
    category = get_category_by_slug(category_slug)
    if not category:
        return []

    from app.models import SpecificationDefinition

    defs = (
        SpecificationDefinition.query.filter_by(category_id=category.id)
        .order_by(
            SpecificationDefinition.group_name,
            SpecificationDefinition.display_order,
        )
        .all()
    )
    return [d.to_dict() for d in defs]
